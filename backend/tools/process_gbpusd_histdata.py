import os
import zipfile
import pandas as pd
from datetime import datetime
import glob

def process_gbpusd_data():
    input_dir = "GBPUSD_CSV"
    output_dir = "backend/data"
    os.makedirs(output_dir, exist_ok=True)
    
    output_file = os.path.join(output_dir, "GBPUSD=X_2000-01-01_2025-11-25_1m.csv")
    
    all_dfs = []
    
    # Get all zip files
    zip_files = sorted(glob.glob(os.path.join(input_dir, "*.zip")))
    print(f"Found {len(zip_files)} zip files.")
    
    for zip_path in zip_files:
        print(f"Processing {zip_path}...")
        try:
            with zipfile.ZipFile(zip_path, 'r') as z:
                # Find the CSV/TXT file inside
                csv_files = [f for f in z.namelist() if f.endswith('.csv') or f.endswith('.txt')]
                if not csv_files:
                    print(f"Warning: No CSV/TXT found in {zip_path}")
                    continue
                
                # Usually there's only one data file
                file_name = csv_files[0]
                with z.open(file_name) as f:
                    # HistData format is usually: 20000103 000000;1.614700;1.615000;1.614600;1.615000;0
                    # Or sometimes comma separated.
                    # We'll try to detect or assume semi-colon based on common HistData format.
                    
                    # Read first few lines to detect format
                    head = [f.readline().decode('utf-8').strip() for _ in range(5)]
                    f.seek(0)
                    print(f"  Sample lines from {file_name}: {head[0]}")
                    
                    # Determine separator
                    sep = ';' if ';' in head[0] else ','
                    
                    df = pd.read_csv(f, sep=sep, header=None)
                    
                    # HistData Format Variations:
                    # Type 1: 20000530 175900;1.497300;... (Space in date col?) No, usually "20000530 175900" is one token if sep is ;
                    # Type 2: 20180101 170000;...
                    # Type 3: 20220103 000000;...
                    
                    # Check column count
                    cols = len(df.columns)
                    print(f"  Columns: {cols}")
                    
                    if cols == 6:
                        # Format: DateTime, Open, High, Low, Close, Volume
                        # DateTime is likely "YYYYMMDD HHMMSS"
                        df.columns = ['DateStr', 'Open', 'High', 'Low', 'Close', 'Volume']
                        df['Date'] = pd.to_datetime(df['DateStr'], format='%Y%m%d %H%M%S')
                    elif cols == 7:
                         # Format: Date, Time, Open, High, Low, Close, Volume
                         # Date: YYYY.MM.DD or YYYYMMDD
                         # Time: HH:MM
                         df.columns = ['DateStr', 'TimeStr', 'Open', 'High', 'Low', 'Close', 'Volume']
                         df['Date'] = pd.to_datetime(df['DateStr'].astype(str) + ' ' + df['TimeStr'].astype(str))
                    else:
                        print(f"  Unknown format with {cols} columns. Skipping.")
                        continue

                    df = df[['Date', 'Open', 'High', 'Low', 'Close', 'Volume']]
                    df.set_index('Date', inplace=True)
                    
                    print(f"  Loaded {len(df)} rows. Range: {df.index[0]} to {df.index[-1]}")
                    all_dfs.append(df)
                    
        except Exception as e:
            print(f"Error processing {zip_path}: {e}")

    if all_dfs:
        print("Merging dataframes...")
        full_df = pd.concat(all_dfs)
        full_df.sort_index(inplace=True)
        
        # Remove duplicates
        full_df = full_df[~full_df.index.duplicated(keep='first')]
        
        print(f"Saving to {output_file}...")
        full_df.to_csv(output_file)
        print(f"Saved {len(full_df)} rows.")
    else:
        print("No data processed.")

if __name__ == "__main__":
    process_gbpusd_data()
