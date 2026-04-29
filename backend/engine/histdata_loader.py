"""HistData spot price loader.

Pulls 1-minute OHLC bars for FX/commodity pairs from histdata.com via the
`histdata` PyPI package, caches the per-year ZIPs locally, and exposes a
fetch_data() interface that mirrors AlpacaDataLoader.

Timestamps in the source CSV are America/New_York local time (ET, with DST)
delivered as semicolon-separated `YYYYMMDD HHMMSS;O;H;L;C;V` lines.
We convert to UTC and (by default) restrict to US ETF market hours
(13:30–20:00 UTC) so the bar set is comparable to what the live ETF bots see.

Volume is always 0 for these spot instruments — strategy logic that relies
on volume must not be used with HistData symbols.
"""

import os
import io
import zipfile
from datetime import datetime
from pathlib import Path

import pandas as pd

try:
    from histdata import api as histdata_api
except ImportError:
    histdata_api = None


CACHE_DIR = Path(__file__).resolve().parent.parent / "data" / "histdata"

# Default symbol mapping: our canonical name -> HistData pair code
SYMBOL_MAP = {
    "XAUUSD": "xauusd",
    "XAGUSD": "xagusd",
    "WTIUSD": "wtiusd",
    "BCOUSD": "bcousd",
    "SPXUSD": "spxusd",
    "NSXUSD": "nsxusd",
}

# US ETF regular trading hours, in UTC after DST switch (post-Mar-2026).
# Live runner gate at backend/runner.py:929-934 uses 13:30–20:00 UTC.
RTH_START_UTC_HHMM = (13, 30)
RTH_END_UTC_HHMM = (20, 0)


class HistDataLoader:
    def __init__(self, cache_dir=CACHE_DIR, restrict_to_rth=True):
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.restrict_to_rth = restrict_to_rth
        if histdata_api is None:
            raise ImportError("histdata package not installed. Run: pip install histdata")

    def _zip_path(self, symbol, year):
        pair = SYMBOL_MAP.get(symbol, symbol.lower())
        return self.cache_dir / f"DAT_ASCII_{pair.upper()}_M1_{year}.zip"

    def _ensure_year(self, symbol, year):
        """Download year ZIP if not already cached."""
        path = self._zip_path(symbol, year)
        if path.exists() and path.stat().st_size > 0:
            return path
        pair = SYMBOL_MAP.get(symbol, symbol.lower())
        print(f"  fetching {symbol} {year} from histdata.com ...")
        histdata_api.download_hist_data(
            year=str(year),
            month=None,
            pair=pair,
            time_frame="M1",
            platform="ASCII",
            output_directory=str(self.cache_dir),
            verbose=False,
        )
        if not path.exists():
            raise FileNotFoundError(f"Expected {path} after download — got nothing")
        return path

    def _ensure_current_year_months(self, symbol, year):
        """For the current year, HistData requires per-month requests."""
        pair = SYMBOL_MAP.get(symbol, symbol.lower())
        zips = []
        for month in range(1, 13):
            mpath = self.cache_dir / f"DAT_ASCII_{pair.upper()}_M1_{year}{month:02d}.zip"
            if mpath.exists() and mpath.stat().st_size > 0:
                zips.append(mpath)
                continue
            try:
                histdata_api.download_hist_data(
                    year=str(year),
                    month=str(month),
                    pair=pair,
                    time_frame="M1",
                    platform="ASCII",
                    output_directory=str(self.cache_dir),
                    verbose=False,
                )
                if mpath.exists():
                    zips.append(mpath)
            except Exception:
                # Future months not yet available — skip silently
                continue
        return zips

    def _read_zip(self, zip_path):
        """Parse a HistData ASCII M1 ZIP into a DataFrame with UTC index."""
        with zipfile.ZipFile(zip_path, "r") as zf:
            csv_name = next((n for n in zf.namelist() if n.endswith(".csv")), None)
            if csv_name is None:
                return pd.DataFrame()
            with zf.open(csv_name) as f:
                df = pd.read_csv(
                    f,
                    sep=";",
                    header=None,
                    names=["ts_local", "Open", "High", "Low", "Close", "Volume"],
                    dtype={"ts_local": str},
                )

        if df.empty:
            return df

        ts = pd.to_datetime(df["ts_local"], format="%Y%m%d %H%M%S")
        # HistData times are America/New_York local (ET, DST-aware).
        ts = ts.dt.tz_localize("America/New_York", ambiguous="NaT", nonexistent="shift_forward")
        ts = ts.dt.tz_convert("UTC")
        df.index = ts
        df = df.drop(columns=["ts_local"])
        df = df[~df.index.isna()]
        return df

    def fetch_data(self, symbol, timeframe, start, end):
        """Return a DataFrame of OHLCV bars between start and end (UTC).

        timeframe: '1m' returns raw 1-minute bars. '15m', '5m', '1h', '1d' resample.
        """
        start_ts = pd.Timestamp(start, tz="UTC") if pd.Timestamp(start).tz is None else pd.Timestamp(start)
        end_ts = pd.Timestamp(end, tz="UTC") if pd.Timestamp(end).tz is None else pd.Timestamp(end)
        if start_ts.tz is None:
            start_ts = start_ts.tz_localize("UTC")
        if end_ts.tz is None:
            end_ts = end_ts.tz_localize("UTC")

        current_year = datetime.now().year
        years = list(range(start_ts.year, min(end_ts.year, current_year) + 1))

        frames = []
        for year in years:
            try:
                if year < current_year:
                    zip_path = self._ensure_year(symbol, year)
                    frame = self._read_zip(zip_path)
                else:
                    zips = self._ensure_current_year_months(symbol, year)
                    parts = [self._read_zip(z) for z in zips]
                    frame = pd.concat(parts) if parts else pd.DataFrame()
                if not frame.empty:
                    frames.append(frame)
            except Exception as e:
                print(f"  warning: {symbol} {year} failed: {e}")

        if not frames:
            return pd.DataFrame()

        df = pd.concat(frames).sort_index()
        df = df[~df.index.duplicated(keep="first")]
        df = df.loc[(df.index >= start_ts) & (df.index <= end_ts)]

        if self.restrict_to_rth:
            df = self._filter_rth(df)

        if timeframe and timeframe != "1m":
            df = self._resample(df, timeframe)

        return df

    def _filter_rth(self, df):
        if df.empty:
            return df
        # 13:30 <= time_of_day < 20:00 (UTC)
        h = df.index.hour
        m = df.index.minute
        minutes = h * 60 + m
        start_min = RTH_START_UTC_HHMM[0] * 60 + RTH_START_UTC_HHMM[1]
        end_min = RTH_END_UTC_HHMM[0] * 60 + RTH_END_UTC_HHMM[1]
        mask = (minutes >= start_min) & (minutes < end_min)
        return df.loc[mask]

    def _resample(self, df, timeframe):
        if df.empty:
            return df
        rule = {"5m": "5min", "15m": "15min", "1h": "1h", "1d": "1D"}.get(timeframe, timeframe)
        ohlc = {"Open": "first", "High": "max", "Low": "min", "Close": "last", "Volume": "sum"}
        return df.resample(rule).agg(ohlc).dropna()
