import pandas as pd
import os

def resample_data(input_file, symbol="EURUSD=X"):
    """
    Resamples 1m OHLCV data into multiple timeframes.
    """
    print(f"Loading master 1m data from: {input_file}")
    
    # Load 1m Data
    try:
        df = pd.read_csv(input_file, parse_dates=['Date'], index_col='Date')
    except Exception as e:
        print(f"Error loading file: {e}")
        return

    print(f"Loaded {len(df)} rows. Range: {df.index.min()} to {df.index.max()}")

    # Define Timeframes to generate
    timeframes = {
        "5m": "5min",
        "15m": "15min",
        "1h": "1H",
        "4h": "4H",
        "1d": "1D"
    }

    base_dir = os.path.dirname(input_file)
    filename_parts = os.path.basename(input_file).split('_')
    # Assuming format: SYMBOL_START_END_1m.csv
    # We want to preserve SYMBOL_START_END and change the suffix
    
    # Robust filename parsing
    date_range_str = f"{filename_parts[1]}_{filename_parts[2]}"
    
    for tf_name, tf_code in timeframes.items():
        print(f"Generating {tf_name} data...")
        
        # Resample Logic
        resampled = df.resample(tf_code).agg({
            'Open': 'first',
            'High': 'max',
            'Low': 'min',
            'Close': 'last',
            'Volume': 'sum'
        }).dropna()

        # Save to CSV
        output_filename = f"{symbol}_{date_range_str}_{tf_name}.csv"
        output_path = os.path.join(base_dir, output_filename)
        
        resampled.to_csv(output_path)
        print(f"  -> Saved {output_path} ({len(resampled)} rows)")

    print("Done! All timeframes generated.")

import argparse

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Resample 1m OHLCV data to other timeframes.")
    parser.add_argument("file", help="Path to the master 1m CSV file")
    parser.add_argument("--symbol", default="EURUSD=X", help="Symbol name (default: EURUSD=X)")
    
    args = parser.parse_args()
    
    # If file is just a filename, look in backend/data
    if not os.path.isabs(args.file) and not os.path.exists(args.file):
        potential_path = os.path.join("backend/data", args.file)
        if os.path.exists(potential_path):
            args.file = potential_path
    
    if os.path.exists(args.file):
        resample_data(args.file, symbol=args.symbol)
    else:
        print(f"File not found: {args.file}")
