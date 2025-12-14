import subprocess
import json

years = [2018, 2024]
adx_values = [20, 25, 30, 35, 40, 45, 50]

print("=== ADX Optimization Sweep ===")

for year in years:
    print(f"\n--- Optimizing for {year} ---")
    for adx in adx_values:
        params = json.dumps({"adx_threshold": adx, "rsi_period": 7, "stoch_period": 7})
        tag = f"ADX{adx}"
        
        cmd = [
            "python3", "-m", "backend.runner", "backtest",
            "--strategy", "StochRSIMeanReversion",
            "--symbol", "SPY",
            "--timeframe", "5m",
            "--start", f"{year}-01-01",
            "--end", f"{year}-12-31",
            "--source", "alpaca",
            "--parameters", params,
            "--tag", tag
        ]
        
        try:
            result = subprocess.run(cmd, capture_output=True, text=True)
            output = result.stdout
            
            # Extract Return and Max DD
            ret = "N/A"
            dd = "N/A"
            for line in output.split('\n'):
                if "Return:" in line:
                    ret = line.split("Return:")[1].strip()
                if "Max DD:" in line:
                    dd = line.split("Max DD:")[1].strip()
            
            print(f"ADX {adx}: Return {ret}, Max DD {dd}")
            
        except Exception as e:
            print(f"Error: {e}")
