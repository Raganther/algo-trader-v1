import sqlite3
import os

DB_PATH = 'backend/research.db'

def cleanup_rapidfire():
    if not os.path.exists(DB_PATH):
        print(f"Database not found at {DB_PATH}")
        return

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    print("--- Cleaning up RapidFireTest Data ---")
    
    # 1. Count records before
    cursor.execute("SELECT COUNT(*) FROM test_runs WHERE strategy = 'RapidFireTest'")
    total_runs = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM live_trade_log WHERE strategy = 'RapidFireTest'")
    total_trades = cursor.fetchone()[0]
    
    print(f"Before: {total_runs} Test Runs, {total_trades} Live Trades")
    
    # 2. Delete Test Runs (Keep Iteration 2)
    # Note: Iteration 2 was logged with iteration_index = 2.
    
    cursor.execute("DELETE FROM test_runs WHERE strategy = 'RapidFireTest' AND iteration_index != 2")
    deleted_runs = cursor.rowcount
    print(f"Deleted {deleted_runs} Test Runs (Non-Iteration 2)")
    
    # 3. Delete Live Trades (Keep Iteration 2)
    cursor.execute("DELETE FROM live_trade_log WHERE strategy = 'RapidFireTest' AND iteration_index != 2")
    deleted_trades = cursor.rowcount
    print(f"Deleted {deleted_trades} Live Trades (Non-Iteration 2)")
    
    conn.commit()
    conn.close()
    print("--- Cleanup Complete ---")

if __name__ == "__main__":
    cleanup_rapidfire()
