import zipfile
import os
import pandas as pd
import glob
from datetime import datetime

# Configuration
# Configuration
DATA_DIR = "/Users/alistairelliman/DEV/gemini 3 test/zipdata"
OUTPUT_DIR = "backend/data"

def process_data(pair_filter=None):
    print("Starting HistData processing...")
    
    # Find all zip files
    pattern = "*.zip"
    if pair_filter:
        pattern = f"*{pair_filter}*.zip"
        
    zip_files = sorted(glob.glob(os.path.join(DATA_DIR, pattern)))
    print(f"Found {len(zip_files)} zip files matching '{pattern}'.")
    
    all_dfs = []
    
    for zip_path in zip_files:
        print(f"Processing {os.path.basename(zip_path)}...")
        try:
            with zipfile.ZipFile(zip_path, 'r') as z:
                # Find CSV inside
                csv_files = [f for f in z.namelist() if f.endswith('.csv')]
                if not csv_files:
                    print(f"  WARNING: No CSV found in {zip_path}")
                    continue
                
                csv_filename = csv_files[0]
                
                # Read CSV
                with z.open(csv_filename) as f:
                    # HistData format: 20210103 170000;1.223960;...
                    df = pd.read_csv(f, sep=';', header=None, 
                                     names=['DateTime', 'Open', 'High', 'Low', 'Close', 'Volume'])
                    
                    # Parse DateTime
                    # Format: YYYYMMDD HHMMSS
                    df['Date'] = pd.to_datetime(df['DateTime'], format='%Y%m%d %H%M%S')
                    
                    # Drop original DateTime column and Volume (usually 0 or tick volume, keep if needed)
                    # We'll keep Volume but drop the string DateTime
                    df = df.drop(columns=['DateTime'])
                    
                    # Reorder columns to standard format: Date, Open, High, Low, Close, Volume
                    df = df[['Date', 'Open', 'High', 'Low', 'Close', 'Volume']]
                    
                    all_dfs.append(df)
                    print(f"  -> Loaded {len(df)} rows.")
                    
        except Exception as e:
            print(f"  ERROR processing {zip_path}: {e}")

    if not all_dfs:
        print("No data loaded!")
        return

    print("Concatenating data...")
    full_df = pd.concat(all_dfs)
    
    print("Sorting by Date...")
    full_df = full_df.sort_values('Date')
    
    # Reset index
    full_df = full_df.reset_index(drop=True)
    
    print(f"Total rows: {len(full_df)}")
    print(f"Date Range: {full_df['Date'].min()} to {full_df['Date'].max()}")
    
    # Determine Output Filename
    # e.g. AUDJPY=X_2002-01-01_2025-11-25_1m.csv
    start_date = full_df['Date'].min().strftime('%Y-%m-%d')
    end_date = full_df['Date'].max().strftime('%Y-%m-%d')
    
    # Extract pair name from filter or first zip
    pair_name = "UNKNOWN"
    if pair_filter:
        pair_name = pair_filter
    
    # HistData uses "AUDJPY", we want "AUDJPY=X"
    symbol = f"{pair_name}=X"
    
    output_filename = f"{symbol}_{start_date}_{end_date}_1m.csv"
    output_path = os.path.join(OUTPUT_DIR, output_filename)
    
    # Save to CSV
    print(f"Saving to {output_path}...")
    full_df.to_csv(output_path, index=False)
    print("Done!")

if __name__ == "__main__":
    import sys
    pair = sys.argv[1] if len(sys.argv) > 1 else None
    process_data(pair)
