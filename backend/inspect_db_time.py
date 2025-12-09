from backend.database import DatabaseManager
import json

db = DatabaseManager()
conn = db.get_connection()
cursor = conn.cursor()

# Get the first few test IDs
cursor.execute("""
    SELECT test_id FROM test_runs 
    WHERE strategy = 'StochRSIMeanReversion' AND symbol = 'GBPJPY=X'
    ORDER BY start_date ASC
    LIMIT 3
""")
test_ids = [r[0] for r in cursor.fetchall()]

print(f"Inspecting Test IDs: {test_ids}")

for tid in test_ids:
    print(f"\n--- Test ID: {tid} ---")
    cursor.execute('SELECT data FROM equity_curves WHERE test_id = ?', (tid,))
    row = cursor.fetchone()
    if row:
        data = json.loads(row[0])
        if data:
            print(f"First 3 points:")
            for p in data[:3]:
                print(p)
            print(f"Last 3 points:")
            for p in data[-3:]:
                print(p)
        else:
            print("Empty data")
    else:
        print("No equity curve found")

conn.close()
