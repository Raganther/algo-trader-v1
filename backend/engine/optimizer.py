import itertools
import pandas as pd
from .backtester import Backtester

class Optimizer:
    def __init__(self, data, strategy_class, events=None):
        self.data = data
        self.strategy_class = strategy_class
        self.events = events

    def optimize(self, param_ranges: dict):
        """
        Run grid search optimization.
        param_ranges: dict of {param_name: range(start, stop, step)} or list of values
        """
        # Generate all combinations
        keys = param_ranges.keys()
        values = param_ranges.values()
        combinations = list(itertools.product(*values))
        
        results = []
        
        print(f"Starting optimization with {len(combinations)} combinations...")
        
        for i, combo in enumerate(combinations):
            params = dict(zip(keys, combo))
            
            # Run Backtest
            backtester = Backtester(self.data, self.strategy_class, events=self.events, parameters=params)
            run_result = backtester.run()
            
            # Store simplified result
            results.append({
                "parameters": params,
                "return_pct": run_result["return_pct"],
                "total_trades": run_result["total_trades"],
                "final_equity": run_result["final_equity"],
                "max_drawdown_pct": run_result.get("max_drawdown_pct", 0.0) # Ensure this exists in backtester later if not
            })
            
            if (i + 1) % 10 == 0:
                print(f"Processed {i + 1}/{len(combinations)}...")
                
        # Sort by Return % (Descending)
        sorted_results = sorted(results, key=lambda x: x["return_pct"], reverse=True)
        
        return sorted_results
