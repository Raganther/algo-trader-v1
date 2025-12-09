import yfinance as yf
from datetime import datetime, timedelta

def test_1m_data():
    symbol = "EURUSD=X"
    # Try fetching last 7 days (limit for 1m data usually)
    end_date = datetime.now()
    start_date = end_date - timedelta(days=7)
    
    print(f"Fetching 1m data for {symbol} from {start_date.date()} to {end_date.date()}...")
    data = yf.download(symbol, start=start_date, end=end_date, interval="1m", progress=False)
    
    if not data.empty:
        print(f"Success! Rows: {len(data)}")
        print(data.head())
        print(data.tail())
    else:
        print("Failed to fetch 1m data.")

    # Try fetching a date in 2024 (older than 30 days)
    start_2024 = "2024-01-01"
    end_2024 = "2024-01-08"
    print(f"\nFetching 1m data for {symbol} from {start_2024} to {end_2024}...")
    data_2024 = yf.download(symbol, start=start_2024, end=end_2024, interval="1m", progress=False)
    
    if not data_2024.empty:
        print(f"Success! Rows: {len(data_2024)}")
    else:
        print("Failed to fetch 1m data for older dates (expected).")

if __name__ == "__main__":
    test_1m_data()
