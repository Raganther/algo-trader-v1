from backend.engine.alpaca_loader import AlpacaDataLoader
from alpaca.data.enums import DataFeed
from alpaca.data.requests import StockBarsRequest
from alpaca.data.timeframe import TimeFrame, TimeFrameUnit
import pandas as pd
import numpy as np

# Strategy Returns (from our research)
strategy_returns = {
    2016: 4.98,
    2017: 11.14,
    2018: -3.31,
    2019: 2.69,
    2020: 14.23,
    2021: 14.28,
    2022: 24.74,
    2023: 11.02,
    2024: 5.30,
    2025: 12.86
}

def get_annual_volatility():
    try:
        loader = AlpacaDataLoader()
        print("Fetching SPY Daily Data (2016-2025)...")
        
        # Fetch long history
        request_params = StockBarsRequest(
            symbol_or_symbols=["SPY"],
            timeframe=TimeFrame.Day,
            start="2016-01-01",
            end="2025-11-30",
            feed=DataFeed.SIP
        )
        bars = loader.stock_client.get_stock_bars(request_params)
        df = bars.df.reset_index()
        
        # Calculate Daily Returns
        # Calculate Daily Returns
        df['return'] = df['close'].pct_change()
        df['year'] = df['timestamp'].dt.year
        
        # Calculate ADX
        # We need High, Low, Close
        # Simple ADX implementation or import? Let's import from backend
        from backend.indicators.adx import adx
        
        df['adx'] = adx(df['high'], df['low'], df['close'], 14)
        
        stats = []
        for year, group in df.groupby('year'):
            # Annualized Volatility
            vol = group['return'].std() * np.sqrt(252) * 100
            
            # Average ADX
            avg_adx = group['adx'].mean()
            
            strat_ret = strategy_returns.get(year, 0)
            
            stats.append({
                "Year": year,
                "Market_Vol": round(vol, 2),
                "Avg_ADX": round(avg_adx, 2),
                "Strategy_Ret": strat_ret
            })
            
        results = pd.DataFrame(stats)
        print("\n=== Market Regime Analysis ===")
        print(results.to_string(index=False))
        
        # Correlation
        corr_vol = results['Market_Vol'].corr(results['Strategy_Ret'])
        corr_adx = results['Avg_ADX'].corr(results['Strategy_Ret'])
        
        print(f"\nCorrelation (Volatility vs Return): {corr_vol:.2f}")
        print(f"Correlation (ADX vs Return): {corr_adx:.2f}")
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    get_annual_volatility()
