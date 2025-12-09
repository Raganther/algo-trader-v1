import yfinance as yf
import pandas as pd

try:
    print("Attempting to download EURUSD=X data...")
    data = yf.download("EURUSD=X", start="2023-01-01", end="2023-12-31", progress=False)
    
    if data.empty:
        print("Error: Data is empty.")
    else:
        print("Success! Data downloaded.")
        print(data.head())
except Exception as e:
    print(f"Error: {e}")
