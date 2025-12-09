import pandas as pd
import zipfile
import os

def process_gbpjpy():
    print("--- Processing GBPJPY Zip Data (2023-2024) ---")
    
    # Files to process
    zip_files = [
        ("zipdata/HISTDATA_COM_ASCII_GBPJPY_M12023.zip", "DAT_ASCII_GBPJPY_M1_2023.csv"),
        ("zipdata/HISTDATA_COM_ASCII_GBPJPY_M12024.zip", "DAT_ASCII_GBPJPY_M1_2024.csv")
    ]
    
    dfs = []
    
    for zip_path, csv_name in zip_files:
        print(f"Processing {zip_path}...")
        try:
            with zipfile.ZipFile(zip_path, 'r') as z:
                with z.open(csv_name) as f:
                    # Read CSV (Semicolon separated, no header)
                    df = pd.read_csv(f, sep=';', names=['DateStr', 'Open', 'High', 'Low', 'Close', 'Volume'])
                    
                    # Parse Date: 20230101 170000
                    df['Date'] = pd.to_datetime(df['DateStr'], format='%Y%m%d %H%M%S')
                    df.set_index('Date', inplace=True)
                    df.drop(columns=['DateStr'], inplace=True)
                    
                    dfs.append(df)
        except Exception as e:
            print(f"Error processing {zip_path}: {e}")
            return

    if not dfs:
        print("No data processed.")
        return

    # Combine
    full_df = pd.concat(dfs).sort_index()
    print(f"Combined Data: {len(full_df)} 1-minute candles.")
    
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

    for tf_name, rule in timeframes.items():
        print(f"Processing {tf_name}...")
        
        if rule:
            df_resampled = full_df.resample(rule).agg(ohlc_dict).dropna()
        else:
            df_resampled = full_df
            
        output_path = f"backend/data/GBPJPY=X_2023-01-01_2024-12-31_{tf_name}.csv"
        df_resampled.to_csv(output_path)
        print(f"Saved {tf_name} to {output_path} ({len(df_resampled)} candles)")

if __name__ == "__main__":
    process_gbpjpy()
