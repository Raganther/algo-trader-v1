import yfinance as yf
import pandas as pd

def test_hourly_fetch():
    symbol = "EURUSD=X"
    # yfinance hourly data is limited to 730 days. 
    # Let's try fetching the last 60 days to be safe for this test.
    end_date = pd.Timestamp.now()
    start_date = end_date - pd.Timedelta(days=59)
    
    print(f"Fetching hourly data for {symbol} from {start_date.date()} to {end_date.date()}...")
    
    try:
        data = yf.download(symbol, start=start_date, end=end_date, interval="1h", progress=False)
        
        if not data.empty:
            print("Successfully fetched hourly data!")
            print(data.head())
            print(f"Rows: {len(data)}")
        else:
            print("Fetched data is empty.")
            
    except Exception as e:
        print(f"Error fetching data: {e}")

if __name__ == "__main__":
    test_hourly_fetch()
