from backend.engine.alpaca_loader import AlpacaDataLoader
from alpaca.data.enums import DataFeed
from alpaca.data.requests import StockBarsRequest
from alpaca.data.timeframe import TimeFrame, TimeFrameUnit
import pandas as pd

try:
    loader = AlpacaDataLoader()
    print("Loader initialized.")
    
    symbol = "SPY"
    start = "2016-01-01"
    end = "2016-01-05"
    
    # Manually construct request to override feed
    request_params = StockBarsRequest(
        symbol_or_symbols=[symbol],
        timeframe=TimeFrame(5, TimeFrameUnit.Minute),
        start=start,
        end=end,
        feed=DataFeed.SIP 
    )
    
    print(f"Fetching {symbol} (SIP)...")
    bars = loader.stock_client.get_stock_bars(request_params)
    df = bars.df
    
    if df.empty:
        print("Result: Empty DataFrame")
    else:
        print(f"Result: {len(df)} rows")
        print(df.head())
        
except Exception as e:
    print(f"Error: {e}")
