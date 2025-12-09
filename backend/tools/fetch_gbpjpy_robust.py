import yfinance as yf
import pandas as pd
import time

def fetch_data_robust():
    symbol = "GBPJPY=X"
    # Try a shorter period first to test
    start_date = "2024-01-01"
    end_date = "2024-12-31"
    interval = "1h" # Try 1h instead of 15m to reduce request load
    
    print(f"Attempting to download {symbol} ({interval})...")
    try:
        data = yf.download(symbol, start=start_date, end=end_date, interval=interval, progress=False)
        
        if isinstance(data.columns, pd.MultiIndex):
            data.columns = data.columns.get_level_values(0)
            
        if not data.empty:
            filename = f"backend/data/{symbol}_{start_date}_{end_date}_{interval}.csv"
            data.to_csv(filename)
            print(f"Success! Saved to {filename}")
            return True
        else:
            print("Empty data returned.")
            return False
            
    except Exception as e:
        print(f"Error: {e}")
        return False

if __name__ == "__main__":
    fetch_data_robust()
