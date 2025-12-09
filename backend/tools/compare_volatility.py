import pandas as pd
import numpy as np

def calculate_atr(df, period=14):
    high = df['high']
    low = df['low']
    close = df['close']
    
    tr1 = high - low
    tr2 = (high - close.shift()).abs()
    tr3 = (low - close.shift()).abs()
    
    tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
    atr = tr.rolling(window=period).mean()
    return atr

def load_and_calc_atr(filepath, symbol):
    try:
        # Load only 2024 data for recent context
        df = pd.read_csv(filepath, index_col=0, parse_dates=True)
        df = df.loc['2024-01-01':'2024-12-31']
        
        if df.empty:
            print(f"{symbol}: No data for 2024")
            return 0
            
        # Normalize columns
        df.columns = [c.lower() for c in df.columns]
        
        # Calculate ATR manually
        df['atr'] = calculate_atr(df, 14)
        
        avg_atr = df['atr'].mean()
        
        if "JPY" in symbol:
            avg_pips = avg_atr * 100
        else:
            avg_pips = avg_atr * 10000
            
        return avg_pips
    except Exception as e:
        print(f"Error processing {symbol}: {e}")
        return 0

def main():
    files = [
        ("USDJPY", "backend/data/USDJPY=X_2000-01-01_2025-11-25_15m.csv"),
        ("EURUSD", "backend/data/EURUSD=X_2014-01-01_2025-12-31_15m.csv"),
        ("GBPUSD", "backend/data/GBPUSD=X_2000-01-01_2025-11-25_15m.csv")
    ]
    
    print("--- 2024 Average Volatility (ATR-14 on 15m) ---")
    print(f"{'Pair':<10} | {'Avg Pips':<10} | {'Strategy Return':<15}")
    print("-" * 45)
    
    returns = {
        "USDJPY": "+18.28%",
        "EURUSD": "+1.09%",
        "GBPUSD": "-0.16%"
    }
    
    for symbol, path in files:
        pips = load_and_calc_atr(path, symbol)
        ret = returns.get(symbol, "N/A")
        print(f"{symbol:<10} | {pips:<10.2f} | {ret:<15}")

if __name__ == "__main__":
    main()
