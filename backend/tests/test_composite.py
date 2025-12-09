from engine.backtester import Backtester
from engine.strategies.composite_strategy import CompositeStrategy
from engine.data_loader import DataLoader
import pandas as pd

def test_composite():
    print("Testing Composite Strategy...")
    
    # 1. Load Data
    loader = DataLoader()
    data, _ = loader.fetch_ohlcv("EURUSD=X", "2023-01-01", "2023-06-01")
    
    # 2. Define Configuration
    # Strategy: 
    # Buy if RSI(14) < 30
    # Sell if RSI(14) > 70
    # Stop Loss: 1%
    config = {
        "signals": [
            {
                "type": "RSI",
                "id": "rsi_1",
                "params": {"rsi_period": 14}
            }
        ],
        "conditions": [
            {
                "signal_id": "rsi_1",
                "operator": "<",
                "value": 30
            }
        ],
        "exit_conditions": [
            {
                "signal_id": "rsi_1",
                "operator": ">",
                "value": 70
            }
        ],
        "stop_loss": 0.01, # 1%
        "take_profit": 0.05 # 5%
    }
    
    # 3. Run Backtest
    backtester = Backtester(data, CompositeStrategy, parameters=config)
    results = backtester.run()
    
    print(f"Initial Capital: {results['initial_capital']}")
    print(f"Final Equity: {results['final_equity']}")
    print(f"Total Trades: {results['total_trades']}")
    print(f"Return: {results['return_pct']}%")
    
    if results['total_trades'] > 0:
        print("SUCCESS: Trades executed.")
    else:
        print("WARNING: No trades executed (might be valid if RSI never < 30, but unlikely for 6 months).")

if __name__ == "__main__":
    test_composite()
