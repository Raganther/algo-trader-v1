import sqlite3
import json
import pandas as pd

def check_results():
    conn = sqlite3.connect('backend/research.db')
    cursor = conn.cursor()
    
    strategies = ['DonchianBreakout', 'DonchianTrend', 'StochRSIMeanReversion']
    
    timeframes = ['1h', '4h']
    
    print(f"{'Strategy':<25} {'Timeframe':<10} {'Return':<10} {'Max DD':<10} {'Win Rate':<10} {'Trades':<10}")
    print("-" * 75)
    
    for strat in strategies:
        for tf in timeframes:
            cursor.execute("SELECT return_pct, max_drawdown, win_rate, total_trades FROM test_runs WHERE strategy = ? AND symbol = 'BTC/USD' AND timeframe = ? AND start_date >= '2015-01-01'", (strat, tf))
            rows = cursor.fetchall()
            
            if not rows: continue
            
            max_dd = 0.0
            compound_mult = 1.0
            all_trades = 0
            all_wins = 0
            
            for row in rows:
                ret = row[0]
                dd = row[1]
                wr = row[2]
                trades = row[3]
                
                compound_mult *= (1 + ret/100)
                max_dd = max(max_dd, dd)
                
                # Normalize Win Rate
                if wr > 1.0:
                    wr = wr / 100.0
                
                wins = round(trades * wr) 
                
                all_trades += trades
                all_wins += wins
                
            final_return = (compound_mult - 1) * 100
            final_win_rate = (all_wins / all_trades * 100) if all_trades > 0 else 0
            
            print(f"{strat:<25} {tf:<10} {final_return:<10.2f} {max_dd:<10.2f} {final_win_rate:<10.2f} {all_trades:<10}")

    conn.close()

if __name__ == "__main__":
    check_results()
