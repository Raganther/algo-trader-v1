from engine.backtester import Backtester
from engine.strategies.composite_strategy import CompositeStrategy
from engine.data_loader import DataLoader
import pandas as pd

def test_custom_strategy():
    print("Testing Complex Composite Strategy (Dip Buy in Uptrend)...")
    
    # 1. Load Data
    loader = DataLoader()
    data, _ = loader.fetch_ohlcv("EURUSD=X", "2023-01-01", "2023-12-31")
    
    # 2. Define Configuration
    # Strategy: 
    # - Signal 1: RSI(14)
    # - Signal 2: SMA(50)
    # - Entry: RSI < 30 AND Price > SMA(50) (Buying a pullback in an uptrend)
    # - Exit: RSI > 70
    # - Stop Loss: 0.5%
    
    config = {
        "signals": [
            {
                "type": "RSI",
                "id": "rsi_14",
                "params": {"rsi_period": 14}
            },
            {
                "type": "SMA",
                "id": "sma_50",
                "params": {"period": 50} # Note: SMASignal uses 'period' or 'fast_period'? Let's check SMASignal.
                # SMASignal uses 'fast_period' and 'slow_period' usually for crossover. 
                # But if we want just one SMA value, we might need to check how SMASignal.generate works.
                # Let's assume for now we treat it as a single line or use the 'fast' one.
                # Actually, SMASignal returns 1.0 (Buy), -1.0 (Sell) based on Crossover.
                # Wait, CompositeStrategy reads the raw value? 
                # In CompositeStrategy.on_data: "val = instance.generate(index, row)"
                # SMASignal.generate returns the SIGNAL (-1, 0, 1), not the SMA value itself.
                
                # CRITICAL FINDING: Our SMASignal returns a signal (-1/1), not the raw SMA value.
                # If we want "Price > SMA", we can't use SMASignal as is if it only returns crossover signals.
                # However, SMASignal logic is: fast > slow = 1.0.
                # So if we want "Price > SMA(50)", we can define:
                # Fast = 1 (Price is effectively SMA 1), Slow = 50.
                # Then SMASignal.generate will return 1.0 if Price > SMA(50).
            }
        ],
        "conditions": [
            {
                "signal_id": "rsi_14",
                "operator": "<",
                "value": 30
            },
            {
                "signal_id": "sma_50", # This is actually a Crossover Signal instance
                "operator": "==", 
                "value": 1.0 # 1.0 means Fast(Price) > Slow(SMA50)
            }
        ],
        "exit_conditions": [
            {
                "signal_id": "rsi_14",
                "operator": ">",
                "value": 70
            }
        ],
        "stop_loss": 0.005, # 0.5%
        "take_profit": 0.02 # 2%
    }
    
    # Adjusting SMASignal params to act as Price > SMA
    # SMASignal uses 'fast_period' and 'slow_period'.
    # If we set fast_period=1, it's basically Price.
    config['signals'][1]['params'] = {"fast_period": 1, "slow_period": 50}

    # 3. Run Backtest
    backtester = Backtester(data, CompositeStrategy, parameters=config)
    results = backtester.run()
    
    print(f"Initial Capital: {results['initial_capital']}")
    print(f"Final Equity: {results['final_equity']}")
    print(f"Total Trades: {results['total_trades']}")
    print(f"Return: {results['return_pct']}%")
    
    if results['total_trades'] > 0:
        print("SUCCESS: Trades executed.")
        for trade in results['orders'][:5]:
            print(f"Trade: {trade['side']} at {trade['price']} on {trade['timestamp']}")
    else:
        print("WARNING: No trades executed.")

if __name__ == "__main__":
    test_custom_strategy()
