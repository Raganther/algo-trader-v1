import sqlite3
import json
from backend.database import DatabaseManager

def debug_equity():
    db = DatabaseManager()
    conn = db.get_connection()
    cursor = conn.cursor()
    
    # Get a recent test ID
    # cursor.execute("SELECT test_id FROM test_runs WHERE strategy='StochRSIMeanReversion' AND symbol='GBPJPY=X' AND timeframe='1h' ORDER BY start_date DESC LIMIT 1")
    
    # Check a specific Matrix ID
    test_id = "StochRSIMeanReversion_EURJPY=X_1h_2024"
    print(f"Inspecting Test ID: {test_id}")
    
    # Get equity curve data
    cursor.execute("SELECT data FROM equity_curves WHERE test_id = ?", (test_id,))
    row = cursor.fetchone()
    
    if not row:
        print("No equity curve entry found.")
        return
        
    data_str = row[0]
    print(f"Data Length: {len(data_str)}")
    
    try:
        data = json.loads(data_str)
        print(f"Parsed JSON Type: {type(data)}")
        if isinstance(data, list) and len(data) > 0:
            print(f"First Item: {data[0]}")
        else:
            print("Data is empty list or not a list.")
    except Exception as e:
        print(f"JSON Parse Error: {e}")

if __name__ == "__main__":
    debug_equity()
