from engine.backtester import Backtester
from engine.strategies.composite_strategy import CompositeStrategy
from engine.data_loader import DataLoader
import pandas as pd

def test_price_action():
    print("Testing Advanced Price Action Signals...")
    
    # 1. Load Data
    loader = DataLoader()
    data, _ = loader.fetch_ohlcv("EURUSD=X", "2023-01-01", "2023-12-31")
    
    # 2. Define Configuration
    # Strategy: 
    # - Trend: Uptrend (ADX > 25 AND Fast > Slow)
    # - Support: Price near Support Level
    # - Entry: Trend == 1.0 AND Support == 1.0
    # - Exit: Trend == -1.0 (Trend Reversal) OR Support == -1.0 (Resistance)
    
    config = {
        "signals": [
            {
                "type": "Trend",
                "id": "trend_1",
                "params": {"fast_period": 20, "slow_period": 50, "adx_threshold": 20}
            },
            {
                "type": "SupportResistance",
                "id": "sr_1",
                "params": {"window": 10, "tolerance": 0.01} # 1% tolerance
            }
        ],
        "conditions": [
            {
                "signal_id": "trend_1",
                "operator": "==",
                "value": 1.0 # Uptrend
            },
            {
                "signal_id": "sr_1",
                "operator": "==",
                "value": 1.0 # Near Support
            }
        ],
        "exit_conditions": [
            {
                "signal_id": "trend_1",
                "operator": "==",
                "value": -1.0 # Downtrend
            }
        ],
        "stop_loss": 0.01,
        "take_profit": 0.03
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
        for trade in results['orders'][:5]:
            print(f"Trade: {trade['side']} at {trade['price']} on {trade['timestamp']}")
    else:
        print("WARNING: No trades executed. (This might happen if Trend + Support alignment is rare)")

if __name__ == "__main__":
    test_price_action()
