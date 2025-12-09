import os
import pandas as pd
import requests
from alpaca.data.historical import StockHistoricalDataClient, CryptoHistoricalDataClient
from alpaca.data.requests import StockBarsRequest, CryptoBarsRequest
from alpaca.data.timeframe import TimeFrame, TimeFrameUnit
from datetime import datetime
from dotenv import load_dotenv
from alpaca.data.enums import DataFeed

load_dotenv()

class AlpacaDataLoader:
    def __init__(self):
        self.api_key = os.getenv('ALPACA_API_KEY')
        self.secret_key = os.getenv('ALPACA_SECRET_KEY')
        self.endpoint = os.getenv('ALPACA_ENDPOINT', 'https://paper-api.alpaca.markets')
        
        if not self.api_key or not self.secret_key:
            raise ValueError("Alpaca API keys not found in .env")
            
        self.stock_client = StockHistoricalDataClient(self.api_key, self.secret_key)
        self.crypto_client = CryptoHistoricalDataClient(self.api_key, self.secret_key)

    def fetch_data(self, symbol, timeframe, start_date, end_date):
        """
        Fetch historical data from Alpaca.
        symbol: e.g. 'AAPL', 'BTC/USD', 'GBP/USD'
        timeframe: '1h', '1d', '15m'
        start_date: datetime object or string
        end_date: datetime object or string
        """
        
        # Determine asset class
        # Standard Forex Currencies
        forex_currencies = ['USD', 'EUR', 'GBP', 'JPY', 'AUD', 'CAD', 'CHF', 'NZD']
        
        # Check if both parts are forex currencies
        parts = symbol.split('/')
        if len(parts) == 2 and parts[0] in forex_currencies and parts[1] in forex_currencies:
            is_forex = True
            is_crypto = False
        else:
            is_forex = False
            is_crypto = symbol in ['BTC/USD', 'ETH/USD', 'LTC/USD', 'BCH/USD', 'SOL/USD'] or ('/' in symbol and 'USD' in symbol and not is_forex)
        
        # Clean symbol for Forex API (e.g. GBP/USD -> GBPUSD)
        # Actually, let's check what the API expects.
        # Docs say: "currency_pairs"
        
        # Map timeframe string to Alpaca TimeFrame
        tf_map = {
            '1m': TimeFrame.Minute,
            '5m': TimeFrame(5, TimeFrameUnit.Minute),
            '15m': TimeFrame(15, TimeFrameUnit.Minute),
            '30m': TimeFrame(30, TimeFrameUnit.Minute),
            '1h': TimeFrame.Hour,
            '4h': TimeFrame(4, TimeFrameUnit.Hour),
            '1d': TimeFrame.Day
        }
        alpaca_tf = tf_map.get(timeframe, TimeFrame.Hour)

        try:
            if is_forex and not is_crypto:
                return self._fetch_forex(symbol, timeframe, start_date, end_date)
            elif is_crypto:
                request_params = CryptoBarsRequest(
                    symbol_or_symbols=[symbol],
                    timeframe=alpaca_tf,
                    start=start_date,
                    end=end_date
                )
                bars = self.crypto_client.get_crypto_bars(request_params)
                df = bars.df
            else:
                # Stock
                request_params = StockBarsRequest(
                    symbol_or_symbols=[symbol],
                    timeframe=alpaca_tf,
                    start=start_date,
                    end=end_date,
                    feed=DataFeed.SIP # Use SIP for historical data
                )
                bars = self.stock_client.get_stock_bars(request_params)
                df = bars.df
            
            # Reset index to get 'timestamp' as a column if it's in index
            if 'timestamp' not in df.columns:
                df = df.reset_index()
            
            # Filter for the specific symbol
            if 'symbol' in df.columns:
                df = df[df['symbol'] == symbol]
            
            return self._process_df(df)
            
        except Exception as e:
            print(f"Error fetching Alpaca data for {symbol}: {e}")
            return pd.DataFrame()

    def _fetch_forex(self, symbol, timeframe, start_date, end_date):
        # Direct API call for Forex
        # Endpoint: https://data.alpaca.markets/v1beta1/forex/rates
        # Note: This endpoint might require different permissions or base URL.
        # Data API URL is usually https://data.alpaca.markets
        
        base_url = "https://data.alpaca.markets/v1beta1/forex/rates"
        
        headers = {
            "APCA-API-KEY-ID": self.api_key,
            "APCA-API-SECRET-KEY": self.secret_key
        }
        
        # Convert timeframe to API format
        # 1Min, 5Min, 15Min, 1H, 1D
        tf_api_map = {
            '1m': '1Min',
            '15m': '15Min',
            '1h': '1H',
            '1d': '1D'
        }
        tf_str = tf_api_map.get(timeframe, '1H')
        
        # Ensure dates are ISO strings
        if isinstance(start_date, datetime):
            start_str = start_date.isoformat()
        else:
            start_str = start_date
            
        if isinstance(end_date, datetime):
            end_str = end_date.isoformat()
        else:
            end_str = end_date

        params = {
            "currency_pairs": symbol, # e.g. GBP/USD
            "timeframe": tf_str,
            "start": start_str,
            "end": end_str,
            "limit": 10000 # Max limit
        }
        
        print(f"Fetching Forex Data: {symbol} {timeframe} from {base_url}")
        response = requests.get(base_url, headers=headers, params=params)
        print(f"DEBUG: Response Status: {response.status_code}")
        print(f"DEBUG: Response Text: {response.text[:200]}...") # Print first 200 chars
        
        if response.status_code != 200:
            print(f"Forex API Error: {response.status_code} {response.text}")
            return pd.DataFrame()
            
        data = response.json()
        # Structure: {'rates': {'GBP/USD': [{'t': ..., 'o': ..., 'h': ..., 'l': ..., 'c': ..., 'v': ...}]}}
        
        if symbol not in data.get('rates', {}):
            print("No data found in response")
            return pd.DataFrame()
            
        rates = data['rates'][symbol]
        df = pd.DataFrame(rates)
        
        # Rename columns
        # Alpaca Forex returns: t (time), o, h, l, c, v (volume - maybe?)
        df = df.rename(columns={
            't': 'Date',
            'o': 'Open',
            'h': 'High',
            'l': 'Low',
            'c': 'Close',
            'v': 'Volume' # Check if volume exists
        })
        
        # Ensure Date is datetime
        df['Date'] = pd.to_datetime(df['Date'])
        
        # Set Date as index
        df.set_index('Date', inplace=True)
        
        # Ensure numeric
        cols = ['Open', 'High', 'Low', 'Close']
        if 'Volume' in df.columns:
            cols.append('Volume')
        else:
            df['Volume'] = 0
            cols.append('Volume')
            
        df[cols] = df[cols].apply(pd.to_numeric)
        
        return df[['Open', 'High', 'Low', 'Close', 'Volume']]

    def _process_df(self, df):
        # Rename columns to match our engine's expected format
        # Handle case variations (Alpaca returns lowercase)
        rename_map = {
            'open': 'Open',
            'high': 'High',
            'low': 'Low',
            'close': 'Close',
            'volume': 'Volume',
            'timestamp': 'Date',
            'vwap': 'VWAP',
            'trade_count': 'TradeCount'
        }
        df = df.rename(columns=rename_map)
        
        # Ensure Date is datetime
        if 'Date' in df.columns:
            df['Date'] = pd.to_datetime(df['Date'])
            df.set_index('Date', inplace=True)
        
        # Ensure all required columns exist
        required_cols = ['Open', 'High', 'Low', 'Close', 'Volume']
        for col in required_cols:
            if col not in df.columns:
                df[col] = 0.0
        
        # Keep only required columns
        return df[required_cols]

    def get_data(self, symbol, timeframe, limit=200):
        """Convenience method to get last N candles."""
        from datetime import timedelta
        
        now = datetime.now()
        
        # Calculate rough start date with buffer for weekends/holidays
        if timeframe == '5m':
            delta = timedelta(minutes=5 * limit * 3) 
        elif timeframe == '15m':
            delta = timedelta(minutes=15 * limit * 3)
        elif timeframe == '1h':
            delta = timedelta(hours=limit * 3)
        elif timeframe == '4h':
            delta = timedelta(hours=4 * limit * 3)
        else:
            delta = timedelta(days=limit * 2)
            
        start = now - delta
        end = now
        
        df = self.fetch_data(symbol, timeframe, start, end)
        
        # Slice to exact limit
        if not df.empty:
            df = df.tail(limit)
            
        return df
