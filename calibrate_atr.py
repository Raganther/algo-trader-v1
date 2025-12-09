from backend.engine.alpaca_loader import AlpacaDataLoader
from alpaca.data.enums import DataFeed
from alpaca.data.requests import StockBarsRequest
from alpaca.data.timeframe import TimeFrame, TimeFrameUnit
from backend.indicators.atr import atr
import pandas as pd
import numpy as np

def calibrate_atr():
    try:
        loader = AlpacaDataLoader()
        print("Fetching SPY 5m Data (2020-2024) for Calibration...")
        
        # Fetch representative sample (Volatile 2020 + Calm 2021 + Bear 2022)
        request_params = StockBarsRequest(
            symbol_or_symbols=["SPY"],
            timeframe=TimeFrame(5, TimeFrameUnit.Minute),
            start="2020-01-01",
            end="2024-12-31",
            feed=DataFeed.SIP
        )
        bars = loader.stock_client.get_stock_bars(request_params)
        df = bars.df.reset_index()
        
        # Calculate ATR
        # Ensure columns are correct case
        df = df.rename(columns={'high': 'High', 'low': 'Low', 'close': 'Close'})
        
        print("Calculating ATR...")
        df['atr'] = atr(df['High'], df['Low'], df['Close'], 14)
        
        # Calculate ATR %
        df['atr_pct'] = (df['atr'] / df['Close']) * 100
        
        # Drop NaNs
        clean_atr = df['atr_pct'].dropna()
        
        print("\n=== ATR% Distribution (5m) ===")
        print(clean_atr.describe(percentiles=[0.1, 0.25, 0.5, 0.75, 0.9, 0.95, 0.99]))
        
        # Suggest Threshold
        # We want to catch "High Volatility" events.
        # Maybe top 25%?
        p75 = clean_atr.quantile(0.75)
        print(f"\nSuggested 'High Vol' Threshold (75th percentile): {p75:.4f}%")
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    calibrate_atr()
