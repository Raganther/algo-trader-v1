from backend.engine.backtester import Backtester
from backend.strategies.donchian_breakout import DonchianBreakoutStrategy
import pandas as pd
import numpy as np

def test_engine():
    print("Testing Backtesting Engine with DonchianBreakoutStrategy...")
    
    # Mock Data
    dates = pd.date_range(start="2023-01-01", periods=100, freq="D")
    
    # Create a trend for Donchian Breakout to catch
    # Linear trend from 100 to 200
    prices = np.linspace(100, 200, 100)
    
    # Add some noise
    noise = np.random.normal(0, 1, 100)
    prices = prices + noise
    
    data = pd.DataFrame({
        "Open": prices,
        "High": prices + 2,
        "Low": prices - 2,
        "Close": prices,
        "Volume": [1000] * 100
    }, index=dates)

    print("Mock Data Created.")
    
    # Run Backtest
    # Parameters for Donchian: entry_period=20, exit_period=10
    parameters = {
        'symbol': 'TEST',
        'entry_period': 20,
        'exit_period': 10,
        'stop_loss_atr': 2.0,
        'atr_period': 14
    }
    
    backtester = Backtester(data, DonchianBreakoutStrategy, parameters=parameters)
    results = backtester.run()
    
    print("Backtest Complete.")
    print(f"Total Trades: {results['total_trades']}")
    print(f"Final Equity: {results['final_equity']}")
    print(f"Return: {results['return_pct']}%")
    
    for order in results['orders']:
        print(f"Order: {order['side']} at {order['price']} on {order['timestamp']}")

if __name__ == "__main__":
    test_engine()
