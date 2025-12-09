import pandas as pd
import os

def compare_data():
    print("--- Comparing 1m Data vs 15m Cache ---")
    
    # Paths
    file_1m = "backend/data/EURUSD=X_2014-01-01_2025-12-31_1m.csv"
    file_15m = "backend/data/EURUSD=X_2014-01-01_2025-12-31_15m.csv"
    
    if not os.path.exists(file_1m) or not os.path.exists(file_15m):
        print("Error: Data files not found.")
        return

    # Load 1m Data
    print(f"Loading 1m data from {file_1m}...")
    df_1m = pd.read_csv(file_1m, parse_dates=['Date'], index_col='Date')
    print(f"  Rows: {len(df_1m)}")
    
    # Load 15m Data
    print(f"Loading 15m data from {file_15m}...")
    df_15m = pd.read_csv(file_15m, parse_dates=['Date'], index_col='Date')
    print(f"  Rows: {len(df_15m)}")
    
    # Resample 1m to 15m
    print("Resampling 1m data to 15m...")
    df_1m_resampled = df_1m.resample('15min').agg({
        'Open': 'first',
        'High': 'max',
        'Low': 'min',
        'Close': 'last',
        'Volume': 'sum'
    }).dropna()
    
    print(f"  Resampled Rows: {len(df_1m_resampled)}")
    
    # Align Data (Intersection of indices)
    common_index = df_1m_resampled.index.intersection(df_15m.index)
    print(f"Common Rows: {len(common_index)}")
    
    if len(common_index) == 0:
        print("Error: No overlapping data found!")
        return
        
    df1 = df_1m_resampled.loc[common_index]
    df2 = df_15m.loc[common_index]
    
    # Calculate Differences
    diff = (df1 - df2).abs()
    
    print("\n--- Comparison Results (Absolute Difference) ---")
    print(diff.describe())
    
    # Check for significant discrepancies (> 1 pip = 0.0001)
    threshold = 0.0001
    bad_rows = diff[(diff['Open'] > threshold) | (diff['Close'] > threshold)]
    
    print(f"\nRows with difference > {threshold}: {len(bad_rows)}")
    
    if len(bad_rows) > 0:
        print("\nSample Discrepancies:")
        print(bad_rows.head())
        print("\nDetailed View (1m Resampled vs 15m Cache):")
        for idx in bad_rows.head().index:
            print(f"\nTime: {idx}")
            print(f"  1m Resampled: O={df1.loc[idx]['Open']:.5f}, H={df1.loc[idx]['High']:.5f}, L={df1.loc[idx]['Low']:.5f}, C={df1.loc[idx]['Close']:.5f}")
            print(f"  15m Cache   : O={df2.loc[idx]['Open']:.5f}, H={df2.loc[idx]['High']:.5f}, L={df2.loc[idx]['Low']:.5f}, C={df2.loc[idx]['Close']:.5f}")
            print(f"  Diff        : O={diff.loc[idx]['Open']:.5f}, H={diff.loc[idx]['High']:.5f}, L={diff.loc[idx]['Low']:.5f}, C={diff.loc[idx]['Close']:.5f}")
    else:
        print("\nSUCCESS: Data aligns perfectly (within 1 pip).")

if __name__ == "__main__":
    compare_data()
