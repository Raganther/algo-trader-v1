from backend.engine.data_loader import DataLoader

def test_loading():
    loader = DataLoader()
    
    print("--- Testing GBPUSD Loading ---")
    data_gbp, meta_gbp = loader.fetch_ohlcv("GBPUSD=X", "2020-01-01", "2020-01-05", "1h")
    if not data_gbp.empty:
        print("Success!")
        print(data_gbp.head())
        print(f"First Close: {data_gbp['Close'].iloc[0]}")
    else:
        print("Failed to load GBPUSD")

    print("\n--- Testing EURUSD 15m Loading ---")
    data_eur, meta_eur = loader.fetch_ohlcv("EURUSD=X", "2020-01-01", "2020-01-05", "15m")
    if not data_eur.empty:
        print("Success!")
        print(data_eur.head())
        print(f"First Close: {data_eur['Close'].iloc[0]}")
    else:
        print("Failed to load EURUSD 15m")

if __name__ == "__main__":
    test_loading()
