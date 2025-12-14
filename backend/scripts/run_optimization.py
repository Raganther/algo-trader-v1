import subprocess
import json
import sys

adx_values = [30, 35, 40]
rsi_values = [7, 14, 21]

print("Starting Parameter Sweep (ADX vs RSI)...")

for adx in adx_values:
    for rsi in rsi_values:
        # We also need to set stoch_period to match rsi_period usually, or keep it independent.
        # Let's keep stoch_period matched for simplicity as per common practice.
        params = json.dumps({
            "adx_threshold": adx, 
            "rsi_period": rsi,
            "stoch_period": rsi 
        })
        tag = f"ADX{adx}_RSI{rsi}"
        cmd = [
            "python3", "-m", "backend.runner", "backtest",
            "--strategy", "HybridRegime",
            "--symbol", "GBPJPY=X",
            "--timeframe", "1h",
            "--start", "2020-01-01",
            "--end", "2024-12-31",
            "--parameters", params,
            "--tag", tag
        ]
        print(f"Running {tag}...")
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode != 0:
            print(f"Error running {tag}: {result.stderr}")
        else:
            # Extract Return from output
            ret = "N/A"
            dd = "N/A"
            for line in result.stdout.split('\n'):
                if "Return:" in line:
                    ret = line.strip()
                if "Max DD:" in line:
                    dd = line.strip()
            print(f"  {ret}, {dd}")

print("Sweep Complete.")
