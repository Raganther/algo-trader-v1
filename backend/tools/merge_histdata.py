import os
import zipfile
import pandas as pd
import glob

def merge_histdata_zips(source_dir, output_file, symbol="USDJPY=X"):
    """
    Unzips HistData.com ZIP files, reads the CSVs, and merges them into a single master CSV.
    """
    print(f"Processing ZIP files in: {source_dir}")
    
    zip_files = sorted(glob.glob(os.path.join(source_dir, "*.zip")))
    if not zip_files:
        print("No ZIP files found.")
        return

    all_dfs = []
    
    for zip_path in zip_files:
        print(f"Processing {os.path.basename(zip_path)}...")
        try:
            with zipfile.ZipFile(zip_path, 'r') as z:
                # HistData zips usually contain one CSV
                csv_filename = z.namelist()[0]
                if not csv_filename.endswith('.csv'):
                    print(f"  Skipping non-CSV file: {csv_filename}")
                    continue
                
                with z.open(csv_filename) as f:
                    # HistData Format: 20000103 000000;102.130000;102.130000;102.130000;102.130000;0
                    # Separator is usually ';'
                    # No header usually
                    df = pd.read_csv(f, sep=';', header=None, names=['DateTime', 'Open', 'High', 'Low', 'Close', 'Volume'])
                    
                    # Parse DateTime
                    # Format is usually YYYYMMDD HHMMSS
                    df['Date'] = pd.to_datetime(df['DateTime'], format='%Y%m%d %H%M%S')
                    df.set_index('Date', inplace=True)
                    df.drop(columns=['DateTime'], inplace=True)
                    
                    all_dfs.append(df)
                    print(f"  -> Loaded {len(df)} rows")
        except Exception as e:
            print(f"  Error processing {zip_path}: {e}")

    if not all_dfs:
        print("No data loaded.")
        return

    print("Merging all dataframes...")
    master_df = pd.concat(all_dfs).sort_index()
    
    # Remove duplicates if any
    master_df = master_df[~master_df.index.duplicated(keep='first')]
    
    print(f"Total rows: {len(master_df)}")
    print(f"Date Range: {master_df.index.min()} to {master_df.index.max()}")
    
    # Save to Master CSV
    master_df.to_csv(output_file)
    print(f"Saved master file to: {output_file}")

if __name__ == "__main__":
    SOURCE_DIR = "usdjpy"
    OUTPUT_FILE = "backend/data/USDJPY=X_2000-01-01_2025-11-25_1m.csv"
    
    merge_histdata_zips(SOURCE_DIR, OUTPUT_FILE)
