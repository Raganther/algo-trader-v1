from backend.engine.optimizer import Optimizer
from backend.strategies.donchian_breakout import DonchianBreakoutStrategy
import pandas as pd
import numpy as np

def test_optimizer():
    print("Testing Optimizer with DonchianBreakoutStrategy...")
    
    # 1. Mock Data (instead of fetching)
    dates = pd.date_range(start="2023-01-01", periods=100, freq="D")
    prices = np.linspace(100, 200, 100) + np.random.normal(0, 1, 100)
    
    data = pd.DataFrame({
        "Open": prices,
        "High": prices + 2,
        "Low": prices - 2,
        "Close": prices,
        "Volume": [1000] * 100
    }, index=dates)
    
    print("Mock Data Created.")
    
    # 2. Define Ranges
    # Entry Period: 20, 30, 40
    # Exit Period: 10, 15, 20
    # Total combinations: 3 * 3 = 9
    ranges = {
        "entry_period": range(20, 41, 10),
        "exit_period": range(10, 21, 5)
    }
    
    # 3. Run Optimizer
    # Note: Optimizer needs to pass 'symbol' in parameters if strategy requires it.
    # The Optimizer class usually merges fixed parameters with optimized ones.
    # Let's check if we can pass fixed parameters to Optimizer or if it handles it.
    # Assuming Optimizer just passes the kwargs to strategy.
    
    optimizer = Optimizer(data, DonchianBreakoutStrategy)
    
    # We might need to inject fixed parameters like 'symbol' if the strategy strictly requires them.
    # DonchianBreakoutStrategy defaults symbol to 'Unknown' if not present, so it should be fine.
    
    results = optimizer.optimize(ranges)
    
    # 4. Verify Results
    print(f"\nOptimization Complete. Found {len(results)} results.")
    print("Top 3 Results:")
    for i, res in enumerate(results[:3]):
        print(f"{i+1}. Params: {res['parameters']}, Return: {res['return_pct']}%")
        
    if len(results) == 9:
        print("\nSUCCESS: Generated correct number of combinations.")
    else:
        print(f"\nFAILURE: Expected 9 combinations, got {len(results)}.")

if __name__ == "__main__":
    test_optimizer()
