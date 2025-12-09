from backend.database import DatabaseManager
import sqlite3

db = DatabaseManager()
conn = sqlite3.connect(db.db_path)
cursor = conn.cursor()

# Check max return
cursor.execute("SELECT test_id, json_extract(metrics, '$.return_pct') as ret FROM test_runs WHERE strategy='StochRSIMeanReversion' ORDER BY ret DESC LIMIT 5")
rows = cursor.fetchall()
print("Top 5 StochRSI Runs:")
for r in rows:
    print(r)

conn.close()
