import sqlite3
import pandas as pd

conn = sqlite3.connect('backend/research.db')
query = """
SELECT start_date, end_date, return_pct 
FROM test_runs 
WHERE strategy = 'StochRSIMeanReversion' 
AND symbol = 'SPY' 
AND timeframe = '5m'
"""
try:
    df = pd.read_sql_query(query, conn)
    if not df.empty:
        print(df)
    else:
        print("No records found.")
except Exception as e:
    print(e)
finally:
    conn.close()
