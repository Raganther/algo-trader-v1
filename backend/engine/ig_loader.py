"""
IG Data Loader — Fetches historical OHLCV data from IG REST API.
Drop-in alternative to AlpacaDataLoader for gold/forex spread betting data.
"""

import os
import pandas as pd
from datetime import datetime, timedelta
from dotenv import load_dotenv

load_dotenv()


class IGDataLoader:
    """
    Fetches historical market data from IG using the trading-ig library.
    Returns DataFrames in the same format as AlpacaDataLoader:
    Index: DatetimeIndex, Columns: [Open, High, Low, Close, Volume]
    """

    # IG resolution mapping (trading-ig format)
    RESOLUTION_MAP = {
        '1m': '1Min',
        '5m': '5Min',
        '15m': '15Min',
        '30m': '30Min',
        '1h': '1H',
        '4h': '4H',
        '1d': 'D',
    }

    # Common epic shortcuts (can be overridden via search)
    EPIC_MAP = {
        'GOLD': 'CS.D.USCGC.TODAY.IP',       # Spot Gold (USD) — DFB
        'XAUUSD': 'CS.D.USCGC.TODAY.IP',
        'EURUSD': 'CS.D.EURUSD.MINI.IP',     # EUR/USD Mini
        'GBPUSD': 'CS.D.GBPUSD.MINI.IP',     # GBP/USD Mini
        'USDJPY': 'CS.D.USDJPY.MINI.IP',     # USD/JPY Mini
        'EURGBP': 'CS.D.EURGBP.MINI.IP',     # EUR/GBP Mini
        'SILVER': 'CS.D.USCSI.TODAY.IP',      # Spot Silver
        'XAGUSD': 'CS.D.USCSI.TODAY.IP',
    }

    def __init__(self):
        self.api_key = os.getenv('IG_API_KEY')
        self.username = os.getenv('IG_USERNAME')
        self.password = os.getenv('IG_PASSWORD')
        self.acc_type = os.getenv('IG_ACC_TYPE', 'LIVE')

        if not all([self.api_key, self.username, self.password]):
            raise ValueError("IG credentials not found in .env (need IG_API_KEY, IG_USERNAME, IG_PASSWORD)")

        self.ig_service = None  # Lazy init

    def _connect(self):
        """Lazy connection — only authenticates when first needed."""
        if self.ig_service is not None:
            return

        from trading_ig import IGService

        self.ig_service = IGService(
            username=self.username,
            password=self.password,
            api_key=self.api_key,
            acc_type=self.acc_type,
        )
        self.ig_service.create_session()
        print(f"✅ Connected to IG API ({self.acc_type} account)")

    def search_epic(self, search_term):
        """
        Search IG markets to find epic codes.
        Returns list of dicts with 'epic', 'instrumentName', 'instrumentType'.
        """
        self._connect()
        results = self.ig_service.search_markets(search_term)
        if results is not None and not results.empty:
            return results[['epic', 'instrumentName', 'instrumentType']].to_dict('records')
        return []

    def _resolve_epic(self, symbol):
        """Map a symbol string to an IG epic code."""
        symbol_upper = symbol.upper().replace('/', '')

        # Check shortcut map first
        if symbol_upper in self.EPIC_MAP:
            return self.EPIC_MAP[symbol_upper]

        # If it looks like an epic (contains dots), verify it directly
        if '.' in symbol:
            try:
                self._connect()
                # fast check - just see if we can get details
                details = self.ig_service.fetch_market_by_epic(symbol)
                if details:
                    return symbol
            except Exception:
                pass # Fall back to search if validation fails

        # Fall back to search
        print(f"Epic not in map for '{symbol}', searching IG...")
        self._connect()
        results = self.ig_service.search_markets(symbol)
        if results is not None and not results.empty:
            epic = results.iloc[0]['epic']
            print(f"  Found: {epic} ({results.iloc[0]['instrumentName']})")
            return epic

        raise ValueError(f"Could not find IG epic for symbol '{symbol}'")

    def fetch_data(self, symbol, timeframe, start_date, end_date):
        """
        Fetch historical OHLCV data from IG.

        Args:
            symbol: e.g. 'GOLD', 'XAUUSD', 'EURUSD', or a raw IG epic
            timeframe: '1m', '5m', '15m', '1h', '4h', '1d'
            start_date: str 'YYYY-MM-DD' or datetime
            end_date: str 'YYYY-MM-DD' or datetime

        Returns:
            DataFrame with DatetimeIndex and columns [Open, High, Low, Close, Volume]
        """
        self._connect()

        epic = self._resolve_epic(symbol)
        resolution = self.RESOLUTION_MAP.get(timeframe, 'HOUR')

        # Ensure datetime format IG expects
        if isinstance(start_date, str):
            start_dt = datetime.strptime(start_date, '%Y-%m-%d')
        else:
            start_dt = start_date

        if isinstance(end_date, str):
            end_dt = datetime.strptime(end_date, '%Y-%m-%d')
        else:
            end_dt = end_date

        # Try passing datetime objects directly first
        print(f"Fetching IG data: {symbol} ({epic}) | {timeframe} ({resolution}) | {start_dt} to {end_dt}")

        try:
            response = self.ig_service.fetch_historical_prices_by_epic_and_date_range(
                epic=epic,
                resolution=resolution,
                start_date=start_dt,
                end_date=end_dt,
            )
        except Exception as e:
            # Fallback: Try "YYYY/MM/DD HH:MM:SS" format
            print(f"⚠️ Datetime object failed ({e}), trying string format...")
            start_str = start_dt.strftime('%Y/%m/%d %H:%M:%S')
            end_str = end_dt.strftime('%Y/%m/%d %H:%M:%S')
            try:
                response = self.ig_service.fetch_historical_prices_by_epic_and_date_range(
                    epic=epic,
                    resolution=resolution,
                    start_date=start_str,
                    end_date=end_str,
                )
            except Exception as e2:
                print(f"❌ IG API error: {e2}")
                return pd.DataFrame()

        if response is None or 'prices' not in response:
            print("⚠️ No price data returned from IG")
            return pd.DataFrame()

        prices_df = response['prices']

        if prices_df.empty:
            print("⚠️ Empty price data from IG")
            return pd.DataFrame()

        return self._process_df(prices_df)

    def _process_df(self, df):
        """
        Convert IG price DataFrame to our standard format.
        IG returns multi-level columns: (bid/ask/last, Open/High/Low/Close)
        We use 'mid' prices (avg of bid/ask) or 'last' if available.
        """
        result = pd.DataFrame()

        # IG typically returns columns like:
        # ('bid', 'Open'), ('bid', 'High'), ('bid', 'Low'), ('bid', 'Close')
        # ('ask', 'Open'), ('ask', 'High'), ('ask', 'Low'), ('ask', 'Close')
        # ('last', 'Open'), etc.
        # We want mid prices for accuracy

        if isinstance(df.columns, pd.MultiIndex):
            # Multi-level columns
            # Prioritize mid-price (Bid/Ask) for Forex/CFDs/Gold
            if 'bid' in df.columns.get_level_values(0) and 'ask' in df.columns.get_level_values(0):
                # Calculate mid price
                for col in ['Open', 'High', 'Low', 'Close']:
                    bid = pd.to_numeric(df[('bid', col)], errors='coerce')
                    ask = pd.to_numeric(df[('ask', col)], errors='coerce')
                    result[col] = (bid + ask) / 2
            elif 'last' in df.columns.get_level_values(0):
                # Use 'last' traded prices (e.g. for stocks if Bid/Ask missing)
                for col in ['Open', 'High', 'Low', 'Close']:
                    result[col] = pd.to_numeric(df[('last', col)], errors='coerce')
            elif 'bid' in df.columns.get_level_values(0):
                for col in ['Open', 'High', 'Low', 'Close']:
                    result[col] = pd.to_numeric(df[('bid', col)], errors='coerce')
            else:
                # Unknown structure — try first level
                level0 = df.columns.get_level_values(0)[0]
                for col in ['Open', 'High', 'Low', 'Close']:
                    result[col] = pd.to_numeric(df[(level0, col)], errors='coerce')
        else:
            # Flat columns
            for col in ['Open', 'High', 'Low', 'Close']:
                if col in df.columns:
                    result[col] = pd.to_numeric(df[col], errors='coerce')

        # Volume — IG may or may not provide this
        if isinstance(df.columns, pd.MultiIndex):
            vol_cols = [c for c in df.columns if 'volume' in str(c).lower() or 'Volume' in str(c)]
            if vol_cols:
                result['Volume'] = pd.to_numeric(df[vol_cols[0]], errors='coerce').fillna(0)
            else:
                result['Volume'] = 0
        elif 'Volume' in df.columns:
            result['Volume'] = pd.to_numeric(df['Volume'], errors='coerce').fillna(0)
        elif 'volume' in df.columns:
            result['Volume'] = pd.to_numeric(df['volume'], errors='coerce').fillna(0)
        else:
            result['Volume'] = 0

        # Use the original index (should be DatetimeIndex from trading-ig)
        result.index = df.index

        # Ensure DatetimeIndex
        if not isinstance(result.index, pd.DatetimeIndex):
            result.index = pd.to_datetime(result.index)

        result.index.name = 'Date'

        # Drop any rows with NaN OHLC
        result = result.dropna(subset=['Open', 'High', 'Low', 'Close'])

        return result[['Open', 'High', 'Low', 'Close', 'Volume']]

    def get_data(self, symbol, timeframe, limit=200):
        """Convenience method to get last N candles (mirrors AlpacaDataLoader)."""
        now = datetime.now()

        # Calculate rough lookback with buffer for weekends
        if timeframe == '1m':
            delta = timedelta(minutes=limit * 3)
        elif timeframe == '5m':
            delta = timedelta(minutes=5 * limit * 3)
        elif timeframe == '15m':
            delta = timedelta(minutes=15 * limit * 3)
        elif timeframe == '1h':
            delta = timedelta(hours=limit * 3)
        elif timeframe == '4h':
            delta = timedelta(hours=4 * limit * 3)
        else:
            delta = timedelta(days=limit * 2)

        start = now - delta
        df = self.fetch_data(symbol, timeframe, start, now)

        if not df.empty:
            df = df.tail(limit)

        return df
