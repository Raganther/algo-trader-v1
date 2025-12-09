import subprocess
import json
import re

years = [2016, 2017, 2019, 2020, 2023, 2024, 2025]

print("=== Batch Adaptive Backtest ===")

results = {}

for year in years:
    print(f"\n--- Running for {year} ---")
    
    end_date = f"{year}-12-31"
    if year == 2025:
        end_date = "2025-11-30"
        
    cmd = [
        "python3", "-m", "backend.runner", "backtest",
        "--strategy", "StochRSIMeanReversion",
        "--symbol", "SPY",
        "--timeframe", "5m",
        "--start", f"{year}-01-01",
        "--end", end_date,
        "--source", "alpaca",
        "--parameters", '{"rsi_period": 7, "stoch_period": 7}' # Uses default adaptive logic
    ]
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True)
        output = result.stdout
        
        # Extract Return
        ret = "N/A"
        for line in output.split('\n'):
            if "Return:" in line:
                ret = line.split("Return:")[1].strip()
                break
        
        results[year] = ret
        print(f"Year {year}: {ret}")
        
    except Exception as e:
        print(f"Error: {e}")

print("\n=== Summary ===")
print(json.dumps(results, indent=2))
