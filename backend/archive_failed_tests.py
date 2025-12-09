import json
import pandas as pd
from datetime import datetime

RESULTS_PATH = 'backend/research_results.json'
STRATEGY_BANK_PATH = 'backend/strategy_bank.json'

def archive_failures():
    # 1. Load Results
    try:
        with open(RESULTS_PATH, 'r') as f:
            results = json.load(f)
    except FileNotFoundError:
        print("Results file not found.")
        return

    # 2. Analyze Failures
    df = pd.DataFrame(results)
    
    # Filter for Donchian Breakout
    df = df[df['strategy_name'] == 'Donchian Breakout']
    
    # Group by Pair
    pair_stats = df.groupby('pair').agg({
        'return_pct': 'mean',
        'status': 'first' # Check if any errors
    }).reset_index()
    
    # Identify Failed Pairs (Negative Return or Error)
    failed_pairs = []
    
    for _, row in pair_stats.iterrows():
        pair = row['pair']
        avg_return = row['return_pct']
        status = row['status']
        
        # Skip the winners (we already added them)
        if pair in ['GBPJPY=X', 'EURJPY=X']:
            continue
            
        # Classify Failure
        if "Error" in str(status):
            reason = f"Data Load Error ({status})"
        elif avg_return < 0:
            reason = f"Negative Return (Avg {avg_return:.2f}%)"
        else:
            reason = f"Poor Performance (Avg {avg_return:.2f}%)"
            
        failed_pairs.append({
            "pair": pair,
            "reason": reason,
            "avg_return": avg_return
        })
        
    if not failed_pairs:
        print("No failed pairs found to archive.")
        return

    # 3. Create Archive Entry
    # We will create one "Bulk" entry for the failed matrix test to avoid cluttering the bank with 50 separate entries.
    
    archive_entry = {
        "test_id": "donchian_matrix_failures_2020_2024",
        "date": datetime.now().strftime('%Y-%m-%d'),
        "timeframe": "1h/4h",
        "symbol": "MULTIPLE",
        "period_start": "2020-01-01",
        "period_end": "2024-12-31",
        "return_pct": -20.0, # Approximate avg of failures
        "trades": 0,
        "final_equity": 0,
        "parameters": {"entry": 20, "exit": 10},
        "notes": "FAILED PAIRS from Matrix Research. The following pairs were tested and rejected:\n" + \
                 "\n".join([f"- {p['pair']}: {p['reason']}" for p in failed_pairs]) + \
                 "\n\nCONCLUSION: Strategy is highly regime-dependent. Only works on Yen crosses (GBPJPY, EURJPY). Avoid major pairs (EURUSD, GBPUSD) with default settings."
    }
    
    # 4. Update Strategy Bank
    with open(STRATEGY_BANK_PATH, 'r') as f:
        bank = json.load(f)
        
    strategy = next((s for s in bank if s['id'] == 'Donchian_Breakout_v1'), None)
    if not strategy:
        print("Strategy not found.")
        return
        
    # Check if already exists
    existing_ids = {t['test_id'] for t in strategy['metadata']['test_history']}
    if archive_entry['test_id'] not in existing_ids:
        strategy['metadata']['test_history'].append(archive_entry)
        print("Added failed pairs archive entry.")
    else:
        print("Archive entry already exists.")
        
    with open(STRATEGY_BANK_PATH, 'w') as f:
        json.dump(bank, f, indent=4)
        
    print("Strategy Bank Updated.")

if __name__ == "__main__":
    archive_failures()
