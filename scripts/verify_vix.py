from backend.engine.alpaca_loader import AlpacaDataLoader
import pandas as pd

def verify_vix():
    loader = AlpacaDataLoader()
    print("Attempting to fetch VIX...")
    
    # Try VIX Index
    try:
        vix = loader.fetch_data("VIX", "1d", "2024-01-01", "2024-01-10")
        if not vix.empty:
            print("Success! Fetched VIX Index.")
            print(vix.head())
            return
    except Exception as e:
        print(f"Failed to fetch VIX Index: {e}")
        
    # Try VIXY (ETF Proxy)
    print("Attempting to fetch VIXY (ETF)...")
    try:
        vixy = loader.fetch_data("VIXY", "1d", "2024-01-01", "2024-01-10")
        if not vixy.empty:
            print("Success! Fetched VIXY ETF.")
            print(vixy.head())
            return
    except Exception as e:
        print(f"Failed to fetch VIXY ETF: {e}")

if __name__ == "__main__":
    verify_vix()
