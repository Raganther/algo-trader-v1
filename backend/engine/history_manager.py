import json
import os
from datetime import datetime

class HistoryManager:
    def __init__(self, filepath="history.json"):
        self.filepath = filepath
        self._ensure_file_exists()

    def _ensure_file_exists(self):
        if not os.path.exists(self.filepath):
            with open(self.filepath, 'w') as f:
                json.dump([], f)

    def save_run(self, strategy, parameters, results):
        """
        Save a backtest run to history.
        """
        run_data = {
            "timestamp": datetime.now().isoformat(),
            "strategy": strategy,
            "parameters": parameters,
            "initial_capital": results.get("initial_capital"),
            "final_equity": results.get("final_equity"),
            "total_trades": results.get("total_trades"),
            # Calculate simple return
            "return_pct": round(((results.get("final_equity") - results.get("initial_capital")) / results.get("initial_capital")) * 100, 2)
            # Explicitly exclude chart_data and debug_history to prevent bloat
        }

        with open(self.filepath, 'r') as f:
            history = json.load(f)
        
        history.append(run_data)
        
        with open(self.filepath, 'w') as f:
            json.dump(history, f, indent=4)
            
        return run_data

    def get_history(self):
        """
        Get all past runs.
        """
        with open(self.filepath, 'r') as f:
            return json.load(f)
