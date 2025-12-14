import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta
import os

class DataLoader:
    def __init__(self, data_dir="backend/data"):
        self.data_dir = data_dir

    def fetch_ohlcv(self, symbol: str, start_date: str, end_date: str, interval: str = "1d") -> tuple[pd.DataFrame, dict]:
        """
        Fetch OHLCV data. Tries local cache first, then yfinance.
        Returns: (data, metadata)
        """
        # Clean symbol for filename (e.g., EURUSD=X -> EURUSD=X.csv)
        safe_symbol = symbol.replace("/", "_")
        cache_file = f"{safe_symbol}_{start_date}_{end_date}_{interval}.csv"
        
        # 1. Try Local Cache (Smart Lookup & Stitching)
        # Check if any file(s) cover the requested range
        found_dfs = []
        try:
            # Ensure data_dir exists
            if not os.path.exists(self.data_dir):
                print(f"Data directory not found: {self.data_dir}")
            else:
            else:
                for filename in os.listdir(self.data_dir):
                    # Check for CSV or GZ
                    is_csv = filename.endswith(f"_{interval}.csv")
                    is_gz = filename.endswith(f"_{interval}.csv.gz")
                    
                    if (filename.startswith(f"{safe_symbol}_") and (is_csv or is_gz)):
                        # Remove extension
                        if is_gz:
                            clean_name = filename.replace(".csv.gz", "")
                        else:
                            clean_name = filename.replace(".csv", "")
                            
                        parts = clean_name.split("_")
                        if len(parts) >= 4:
                            file_start = parts[-3]
                            file_end = parts[-2]
                            
                            # Check for OVERLAP: (StartA <= EndB) and (EndA >= StartB)
                            if file_start <= end_date and file_end >= start_date:
                                # print(f"Found overlapping cache file: {filename}")
                                file_path = os.path.join(self.data_dir, filename)
                                try:
                                    # Pandas handles gzip automatically if extension is .gz
                                    data = pd.read_csv(file_path, index_col=0, parse_dates=True)
                                
                                    # Normalize columns (lowercase to Title Case)
                                    data.columns = [c.capitalize() for c in data.columns]
                                    if 'Tick_volume' in data.columns:
                                        data.rename(columns={'Tick_volume': 'Volume'}, inplace=True)
                                        
                                    # Normalize Prices (Handle "points" format from ejtraderLabs)
                                    if not data.empty:
                                        first_close = data['Close'].iloc[0]
                                        if first_close > 500: # Arbitrary threshold to detect non-standard pricing
                                            if "JPY" in symbol:
                                                scale_factor = 1000.0
                                            else:
                                                scale_factor = 100000.0
                                            
                                            cols_to_scale = ['Open', 'High', 'Low', 'Close']
                                            for col in cols_to_scale:
                                                if col in data.columns:
                                                    data[col] = data[col] / scale_factor
                                    
                                    found_dfs.append(data)
                                except Exception as e:
                                    print(f"Error reading {filename}: {e}")

                if found_dfs:
                    # Stitch all found files
                    full_df = pd.concat(found_dfs)
                    full_df = full_df.sort_index()
                    full_df = full_df[~full_df.index.duplicated(keep='first')]
                    
                    # Filter to requested range
                    mask = (full_df.index >= start_date) & (full_df.index <= end_date)
                    filtered_data = full_df.loc[mask]
                    
                    if not filtered_data.empty:
                        metadata = {"source": "Local Cache (Stitched)", "symbol": symbol, "start": start_date, "end": end_date}
                        return filtered_data, metadata
                        
        except Exception as e:
            print(f"Cache lookup error: {e}")

        # Strict check fallback (legacy)
        if os.path.exists(cache_file):
            print(f"Loading {symbol} from cache...")
            data = pd.read_csv(cache_file, index_col=0, parse_dates=True)
            metadata = {"source": "Local Cache (CSV)", "symbol": symbol, "start": start_date, "end": end_date}
            return data, metadata

        # 2. Strict Local Data Policy
        # User requested NO Yahoo Finance and NO Mock Data.
        print(f"No local data found for {symbol} covering {start_date} to {end_date}.")
        raise FileNotFoundError(f"STRICT MODE: No local CSV data found for {symbol}. Yahoo Finance and Mock Data are disabled.")

    def _generate_mock_data(self, start_date, end_date, interval="1d"):
        freq_map = {"1d": "D", "1h": "h", "15m": "15min", "5m": "5min", "1m": "1min"}
        freq = freq_map.get(interval, "D")
        
        dates = pd.date_range(start=start_date, end=end_date, freq=freq)
        import numpy as np
        # Generate random walk
        steps = np.random.normal(loc=0.0001, scale=0.01, size=len(dates))
        prices = 1.10 * (1 + steps).cumprod()
        
        data = pd.DataFrame({
            "Open": prices,
            "High": prices * 1.005,
            "Low": prices * 0.995,
            "Close": prices,
            "Volume": 100000
        }, index=dates)
        return data

    def fetch_economic_events(self, start_date: str, end_date: str, currency: str = "USD") -> pd.DataFrame:
        """
        Fetch economic events from local CSV file.
        """
        csv_path = 'backend/data_csv/economic_calendar.csv'
        if not os.path.exists(csv_path):
            print(f"Economic calendar CSV not found at {csv_path}")
            return pd.DataFrame()

        try:
            # Load from CSV
            df = pd.read_csv(csv_path)
            
            # Parse DateTime with timezone handling
            # The CSV has offsets like +03:30. We'll convert to UTC and then remove timezone for simple backtesting alignment
            df['DateTime'] = pd.to_datetime(df['DateTime'], utc=True).dt.tz_localize(None)
            df.rename(columns={'DateTime': 'date', 'Currency': 'currency', 'Impact': 'impact', 'Event': 'event', 'Actual': 'actual', 'Forecast': 'forecast', 'Previous': 'previous'}, inplace=True)
            
            # Filter by date range
            mask = (df['date'] >= pd.to_datetime(start_date)) & (df['date'] <= pd.to_datetime(end_date))
            df = df.loc[mask].copy()
            
            # Filter by Currency (allow list or single)
            if currency:
                currencies = [c.strip() for c in currency.split(',')]
                df = df[df['currency'].isin(currencies)]
            
            # Filter by High Impact
            df = df[df['impact'].str.contains("High", case=False, na=False)]
            
            # Clean and Parse Values (Actual, Forecast)
            def clean_value(val):
                if pd.isna(val) or val == '':
                    return None
                val = str(val).strip()
                multiplier = 1.0
                if val.endswith('%'):
                    val = val[:-1]
                elif val.endswith('K'):
                    multiplier = 1000.0
                    val = val[:-1]
                elif val.endswith('M'):
                    multiplier = 1000000.0
                    val = val[:-1]
                elif val.endswith('B'):
                    multiplier = 1000000000.0
                    val = val[:-1]
                elif val.endswith('T'):
                    multiplier = 1000000000000.0
                    val = val[:-1]
                
                try:
                    return float(val.replace(',', '')) * multiplier
                except:
                    return None

            df['actual_val'] = df['actual'].apply(clean_value)
            df['forecast_val'] = df['forecast'].apply(clean_value)
            
            # Drop rows where we can't compare
            df = df.dropna(subset=['actual_val', 'forecast_val'])
            
            return df
            
        except Exception as e:
            print(f"Error loading economic calendar CSV: {e}")
            import traceback
            traceback.print_exc()
            return pd.DataFrame()
