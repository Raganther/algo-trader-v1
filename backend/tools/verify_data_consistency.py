import pandas as pd
import random

def verify_consistency(file_1m, file_1h):
    print(f"Verifying data consistency between:\n  1m: {file_1m}\n  1h: {file_1h}")
    
    # Load 1m and 1h data
    df_1m = pd.read_csv(file_1m, parse_dates=['Date'], index_col='Date')
    df_1h = pd.read_csv(file_1h, parse_dates=['Date'], index_col='Date')
    
    print(f"Loaded {len(df_1m)} 1m rows and {len(df_1h)} 1h rows.")
    
    # Pick 5 random 1h candles to verify
    if len(df_1h) < 5:
        print("Not enough data to verify.")
        return

    sample_indices = random.sample(list(df_1h.index), 5)
    
    for idx in sample_indices:
        h1_candle = df_1h.loc[idx]
        
        # Define the 1h range (e.g., 10:00 to 10:59)
        start_time = idx
        end_time = idx + pd.Timedelta(minutes=59)
        
        # Get 1m candles in this range
        m1_chunk = df_1m.loc[start_time:end_time]
        
        if m1_chunk.empty:
            print(f"WARNING: No 1m data found for 1h candle at {idx}")
            continue
            
        # Calculate expected values
        expected_open = m1_chunk.iloc[0]['Open']
        expected_high = m1_chunk['High'].max()
        expected_low = m1_chunk['Low'].min()
        expected_close = m1_chunk.iloc[-1]['Close']
        
        # Compare
        print(f"\nChecking 1h Candle: {idx}")
        print(f"  Open:  1h={h1_candle['Open']:.5f} vs Calc={expected_open:.5f} ... {'OK' if abs(h1_candle['Open'] - expected_open) < 0.00001 else 'FAIL'}")
        print(f"  High:  1h={h1_candle['High']:.5f} vs Calc={expected_high:.5f} ... {'OK' if abs(h1_candle['High'] - expected_high) < 0.00001 else 'FAIL'}")
        print(f"  Low:   1h={h1_candle['Low']:.5f} vs Calc={expected_low:.5f} ... {'OK' if abs(h1_candle['Low'] - expected_low) < 0.00001 else 'FAIL'}")
        print(f"  Close: 1h={h1_candle['Close']:.5f} vs Calc={expected_close:.5f} ... {'OK' if abs(h1_candle['Close'] - expected_close) < 0.00001 else 'FAIL'}")
        
    print("\nVerification Complete.")

import argparse
import os

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Verify consistency between 1m and 1h data.")
    parser.add_argument("file_1m", help="Path to the 1m CSV file")
    parser.add_argument("file_1h", help="Path to the 1h CSV file")
    
    args = parser.parse_args()
    
    if os.path.exists(args.file_1m) and os.path.exists(args.file_1h):
        verify_consistency(args.file_1m, args.file_1h)
    else:
        print("One or both files not found.")
