"""Clean data loading with resampling for backtesting.

Extracts and centralises the resampling logic that was duplicated
in runner.py's run_backtest() and worker_task().
"""

import pandas as pd
from backend.engine.alpaca_loader import AlpacaDataLoader

# Timeframes that require fetching a finer resolution and resampling
RESAMPLE_MAP = {
    "5m": "1m",
    "15m": "1m",
    "4h": "1h",
}

# Pandas resample aliases
PANDAS_ALIAS = {
    "5m": "5min",
    "15m": "15min",
    "4h": "4h",
}


def load_backtest_data(symbol: str, timeframe: str, start: str, end: str) -> pd.DataFrame:
    """Fetch OHLCV data from Alpaca, resampling if needed.

    Handles:
    - 5m/15m: fetch 1m, resample
    - 4h: fetch 1h, resample
    - 1m/1h/1d: fetch directly

    Returns a DataFrame with columns [Open, High, Low, Close, Volume]
    indexed by datetime, ready to pass to Backtester.
    """
    loader = AlpacaDataLoader()

    fetch_tf = RESAMPLE_MAP.get(timeframe, timeframe)
    data = loader.fetch_data(symbol, fetch_tf, start, end)

    if data is None or data.empty:
        return pd.DataFrame()

    # Resample if we fetched a finer resolution
    if timeframe in RESAMPLE_MAP:
        resample_alias = PANDAS_ALIAS.get(timeframe, timeframe)
        ohlc_dict = {
            "Open": "first",
            "High": "max",
            "Low": "min",
            "Close": "last",
            "Volume": "sum",
        }
        data = data.resample(resample_alias).agg(ohlc_dict).dropna()

    return data
