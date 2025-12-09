import subprocess
import json
import os

class ToolBox:
    def __init__(self, runner_path="backend.runner"):
        self.runner_path = runner_path

    def run_backtest(self, strategy: str, symbol: str, timeframe: str = "1h", source: str = "alpaca", params: dict = None):
        """
        Executes a backtest using the runner.py CLI.
        Returns the output as a string (or JSON if we parse it).
        """
        # Auto-detect source for Forex
        if "USD" in symbol or "EUR" in symbol or "JPY" in symbol or "GBP" in symbol or "=" in symbol:
            source = "csv"

        cmd = [
            "python3", "-m", self.runner_path,
            "backtest",
            "--strategy", strategy,
            "--symbol", symbol,
            "--timeframe", timeframe,
            "--source", source
        ]

        if params:
            cmd.extend(["--parameters", json.dumps(params)])

        print(f"ToolBox Executing: {' '.join(cmd)}")
        
        try:
            result = subprocess.run(
                cmd, 
                capture_output=True, 
                text=True, 
                cwd=os.getcwd()
            )
            
            if result.returncode != 0:
                return f"Error: {result.stderr}"
                
            return result.stdout
            
        except Exception as e:
            return f"Exception executing tool: {str(e)}"

    def get_strategies(self):
        """List available strategies."""
        # This could parse the backend/strategies directory or call runner --help
        # For now, hardcoded or simple scan
        return ["StochRSIMeanReversion", "DonchianTrend", "StochRSIQuant"]
