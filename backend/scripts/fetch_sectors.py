import yfinance as yf
import pandas as pd
import os

DATA_DIR = "backend/data"
SECTORS = ['XLK', 'XLF', 'XLV', 'XLY', 'XLP', 'XLE', 'XLI', 'XLB', 'XLRE', 'XLU']
START_DATE = "2023-01-01"
END_DATE = "2024-12-31"
TIMEFRAME = "1h"

def fetch_and_save():
    if not os.path.exists(DATA_DIR):
        os.makedirs(DATA_DIR)
        
    for sector in SECTORS:
        import time
        time.sleep(2)
        print(f"Fetching {sector}...")
        try:
            # yfinance download
            df = yf.download(sector, start=START_DATE, end=END_DATE, interval=TIMEFRAME, progress=False)
            
            if not df.empty:
                # Format to match system CSV format: Date,Open,High,Low,Close,Volume
                # yfinance returns MultiIndex columns sometimes or just standard.
                # Reset index to get Date/Datetime
                df.reset_index(inplace=True)
                
                # Rename columns if needed (yfinance usually gives: Datetime, Open, High, Low, Close, Adj Close, Volume)
                # We need to ensure standard naming
                df.rename(columns={"Datetime": "Date"}, inplace=True)
                
                # Select columns
                cols = ["Date", "Open", "High", "Low", "Close", "Volume"]
                df = df[cols]
                
                # Save
                filename = f"{sector}_{START_DATE}_{END_DATE}_{TIMEFRAME}.csv"
                filepath = os.path.join(DATA_DIR, filename)
                df.to_csv(filepath, index=False)
                print(f"Saved {filepath}")
            else:
                print(f"Warning: No data for {sector}")
                
        except Exception as e:
            print(f"Error fetching {sector}: {e}")

if __name__ == "__main__":
    fetch_and_save()
