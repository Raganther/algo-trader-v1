import yfinance as yf
import pandas as pd
from datetime import datetime
import time

class LiveDataLoader:
    def __init__(self, symbol: str, interval: str = "1m"):
        self.symbol = symbol
        self.interval = interval
        self.last_timestamp = None

    def fetch_latest_candle(self):
        """
        Fetch the most recent completed candle.
        Returns (timestamp, row) or None if no new data.
        """
        try:
            # Fetch last 1 day to ensure we get the latest candle
            # yfinance '1m' data is available for last 7 days
            df = yf.download(self.symbol, period="1d", interval=self.interval, progress=False)
            
            if df.empty:
                print(f"Warning: No live data received for {self.symbol}")
                return None
                
            # Get the last row
            last_row = df.iloc[-1]
            last_timestamp = last_row.name
            
            # Check if it's a new candle
            if self.last_timestamp is None or last_timestamp > self.last_timestamp:
                self.last_timestamp = last_timestamp
                
                # Convert to standard dictionary format
                candle = {
                    'Open': float(last_row['Open']),
                    'High': float(last_row['High']),
                    'Low': float(last_row['Low']),
                    'Close': float(last_row['Close']),
                    'Volume': float(last_row['Volume'])
                }
                return last_timestamp, candle
            
            return None
            
        except Exception as e:
            print(f"Error fetching live data: {e}")
            return None

    def fetch_current_price(self):
        """
        Fetch the absolute latest price (ticker).
        """
        try:
            ticker = yf.Ticker(self.symbol)
            # fast_info is faster than history
            price = ticker.fast_info.last_price
            return price
        except Exception as e:
            print(f"Error fetching current price: {e}")
            return None

    def fetch_recent_history(self, days: int = 5) -> pd.DataFrame:
        """
        Fetch recent historical data to initialize strategy state.
        """
        try:
            df = yf.download(self.symbol, period=f"{days}d", interval=self.interval, progress=False)
            if df.empty:
                print(f"Warning: No historical data received for {self.symbol}")
                return None
            
            # Handle MultiIndex columns (e.g. ('Close', 'EURUSD=X'))
            if isinstance(df.columns, pd.MultiIndex):
                df.columns = df.columns.droplevel(1)
                
            return df
        except Exception as e:
            print(f"Error fetching history: {e}")
            return None
