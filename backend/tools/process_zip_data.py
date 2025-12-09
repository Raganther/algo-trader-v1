import pandas as pd
import zipfile
import os
import glob
import re

def process_zip_data(symbol, zip_dir="zipdata", output_dir="backend/data"):
    print(f"--- Processing {symbol} Zip Data ---")
    
    # Find all zip files for the symbol
    # Pattern: HISTDATA_COM_ASCII_SYMBOL_M1*.zip
    pattern = os.path.join(zip_dir, f"HISTDATA_COM_ASCII_{symbol}_M1*.zip")
    zip_files = sorted(glob.glob(pattern))
    
    if not zip_files:
        print(f"No zip files found for {symbol} in {zip_dir}")
        return

    dfs = []
    
    for zip_path in zip_files:
        print(f"Processing {os.path.basename(zip_path)}...")
        try:
            with zipfile.ZipFile(zip_path, 'r') as z:
                # Assume the CSV inside has a similar name or is the only CSV
                csv_files = [f for f in z.namelist() if f.endswith('.csv')]
                if not csv_files:
                    print(f"  No CSV found in {zip_path}")
                    continue
                
                # Use the first CSV found
                csv_name = csv_files[0]
                with z.open(csv_name) as f:
                    # Read CSV (Semicolon separated, no header usually for HistData.com)
                    # Format: 20020101 000000;Open;High;Low;Close;Volume
                    df = pd.read_csv(f, sep=';', names=['DateStr', 'Open', 'High', 'Low', 'Close', 'Volume'])
                    
                    # Parse Date
                    df['Date'] = pd.to_datetime(df['DateStr'], format='%Y%m%d %H%M%S')
                    df.set_index('Date', inplace=True)
                    df.drop(columns=['DateStr'], inplace=True)
                    
                    dfs.append(df)
        except Exception as e:
            print(f"  Error processing {zip_path}: {e}")

    if not dfs:
        print("No data processed.")
        return

    # Combine
    print("Concatenating data...")
    full_df = pd.concat(dfs).sort_index()
    # Remove duplicates if any
    full_df = full_df[~full_df.index.duplicated(keep='first')]
    
    print(f"Combined Data: {len(full_df)} 1-minute candles.")
    print(f"Range: {full_df.index.min()} to {full_df.index.max()}")
    
    # Resample and Save All Timeframes
    timeframes = {
        '1m': None, # Original
        '5m': '5min',
        '15m': '15min',
        '1h': '1h',
        '4h': '4h',
        '1d': '1D'
    }

    ohlc_dict = {
        'Open': 'first',
        'High': 'max',
        'Low': 'min',
        'Close': 'last',
        'Volume': 'sum'
    }

    # Yahoo Finance format symbol for filename (e.g., GBPCHF=X)
    yf_symbol = f"{symbol}=X"
    start_year = full_df.index.min().year
    end_year = full_df.index.max().year
    # Use current date for end if it goes into 2025
    end_date_str = full_df.index.max().strftime('%Y-%m-%d')

    for tf_name, rule in timeframes.items():
        print(f"Processing {tf_name}...")
        
        if rule:
            df_resampled = full_df.resample(rule).agg(ohlc_dict).dropna()
        else:
            df_resampled = full_df
            
        # Filename format: SYMBOL=X_START_END_TF.csv
        # We'll use a fixed start/end in filename for consistency or dynamic?
        # Let's use dynamic to be accurate.
        filename = f"{yf_symbol}_{start_year}-01-01_{end_date_str}_{tf_name}.csv"
        output_path = os.path.join(output_dir, filename)
        
        df_resampled.to_csv(output_path)
        print(f"Saved {tf_name} to {output_path} ({len(df_resampled)} candles)")

if __name__ == "__main__":
    # Default to GBPCHF if run directly
    process_zip_data("GBPCHF")
