import sqlite3
import json
import pandas as pd
from datetime import datetime

DB_FILE = "backend/research.db"

class DatabaseManager:
    def __init__(self, db_file=DB_FILE):
        self.db_file = db_file

    def get_connection(self):
        return sqlite3.connect(self.db_file)

    def initialize_db(self):
        """Creates the necessary tables if they don't exist."""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # 1. Test Runs Table (Metrics & Metadata)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS test_runs (
                test_id TEXT PRIMARY KEY,
                strategy TEXT,
                symbol TEXT,
                timeframe TEXT,
                start_date TEXT,
                end_date TEXT,
                return_pct REAL,
                max_drawdown REAL,
                win_rate REAL,
                total_trades INTEGER,
                parameters TEXT, -- JSON string
                timestamp TEXT,
                iteration_index INTEGER DEFAULT 0
            )
        ''')
        
        # Migration: Add column if missing
        try:
            cursor.execute('ALTER TABLE test_runs ADD COLUMN iteration_index INTEGER DEFAULT 0')
        except sqlite3.OperationalError:
            pass # Column likely exists
        
        # 2. Equity Curves Table (Heavy Data)
        # Linked by test_id
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS equity_curves (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                test_id TEXT,
                data TEXT, -- JSON string of the equity curve/chart data
                FOREIGN KEY(test_id) REFERENCES test_runs(test_id)
            )
        ''')

        # 3. Insights Table (Anomalies & Findings)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS insights (
                insight_id TEXT PRIMARY KEY,
                type TEXT,
                description TEXT,
                confidence REAL,
                scope TEXT, -- JSON list
                parameters TEXT, -- JSON dict
                expiration TEXT,
                status TEXT,
                created_at TEXT,
                last_updated TEXT
            )
        ''')

        # 4. Live Trade Log (Verification & Slippage)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS live_trade_log (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id TEXT,
                timestamp TEXT,
                symbol TEXT,
                strategy TEXT,
                side TEXT,
                qty REAL,
                signal_price REAL,
                fill_price REAL,
                slippage REAL,
                spread REAL,
                pnl REAL
            )
        ''')
        
        conn.commit()
        conn.close()
        print("Database initialized.")

    def get_next_iteration_index(self, strategy, symbol):
        """Calculates the next iteration index for a strategy/symbol pair."""
        conn = self.get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute('''
                SELECT MAX(iteration_index) FROM test_runs 
                WHERE strategy = ? AND symbol = ?
            ''', (strategy, symbol))
            result = cursor.fetchone()
            current_max = result[0] if result and result[0] is not None else 0
            return current_max + 1
        except Exception as e:
            print(f"Error getting iteration index: {e}")
            return 1
        finally:
            conn.close()

    def save_test_run(self, data):
        """Saves a test run dictionary (as produced by runner.py) to the DB."""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        metrics = data['metrics']
        
        # Extract parameters safely
        params = json.dumps(data.get('parameters', {}))
        
        # Insert into test_runs
        # Handle missing start/end dates
        start_date = data.get('start')
        if not start_date:
            year = data.get('year', '2023')
            start_date = f"{year}-01-01"
            
        end_date = data.get('end')
        if not end_date:
            year = data.get('year', '2023')
            end_date = f"{year}-12-31"

            end_date = f"{year}-12-31"

        try:
            cursor.execute('''
                INSERT OR REPLACE INTO test_runs (
                    test_id, strategy, symbol, timeframe, start_date, end_date,
                    return_pct, max_drawdown, win_rate, total_trades, parameters, timestamp, iteration_index
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                data['test_id'],
                data['strategy'],
                data['symbol'],
                data['timeframe'],
                start_date,
                end_date,
                metrics.get('return_pct', 0.0),
                metrics.get('max_drawdown', 0.0),
                metrics.get('win_rate', 0.0),
                metrics.get('total_trades', 0),
                params,
                datetime.now().isoformat(),
                data.get('iteration_index', 0)
            ))
            
            # Insert into equity_curves
            # We store the equity_curve list (which now contains detailed {time, equity}) as a JSON string
            # Previously it was 'chart_data' (OHLC), now we want the actual equity curve
            equity_data = metrics.get('equity_curve', [])
            
            # If equity_curve is empty or old format (list of floats), fallback?
            # The new backtester produces list of dicts.
            
            chart_data = json.dumps(equity_data)
            
            # First delete existing curve if replacing
            cursor.execute('DELETE FROM equity_curves WHERE test_id = ?', (data['test_id'],))
            
            cursor.execute('''
                INSERT INTO equity_curves (test_id, data) VALUES (?, ?)
            ''', (data['test_id'], chart_data))
            
            conn.commit()
            # print(f"Saved test {data['test_id']} to DB.")
            
        except Exception as e:
            print(f"Error saving to DB: {e}")
        finally:
            conn.close()

    def get_all_test_runs(self):
        """Retrieves all test runs (metrics only) for analysis."""
        conn = self.get_connection()
        conn.row_factory = sqlite3.Row # Access by column name
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM test_runs')
        rows = cursor.fetchall()
        
        results = []
        for row in rows:
            # Convert Row to dict
            d = dict(row)
            # Parse parameters JSON back to dict
            if d['parameters']:
                d['parameters'] = json.loads(d['parameters'])
            results.append(d)
            
        conn.close()
        return results

    def get_test_run(self, test_id):
        """Retrieves a single test run with metrics."""
        conn = self.get_connection()
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM test_runs WHERE test_id = ?', (test_id,))
        row = cursor.fetchone()
        conn.close()
        
        if row:
            d = dict(row)
            if d['parameters']:
                d['parameters'] = json.loads(d['parameters'])
            return d
        return None

    def get_equity_curve(self, test_id):
        """Retrieves the chart data for a specific test."""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('SELECT data FROM equity_curves WHERE test_id = ?', (test_id,))
        row = cursor.fetchone()
        conn.close()
        
        if row:
            return json.loads(row[0])
        return None

    def get_composite_equity_curve(self, strategy, symbol, timeframe):
        """Stitches together equity curves from multiple yearly runs."""
        conn = self.get_connection()
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        # 1. Fetch all runs for this combo
        cursor.execute('''
            SELECT test_id, start_date 
            FROM test_runs 
            WHERE strategy = ? AND symbol = ? AND timeframe = ?
            ORDER BY start_date ASC
        ''', (strategy, symbol, timeframe))
        
        runs = cursor.fetchall()
        
        composite_curve = []
        
        last_equity = None
        
        for run in runs:
            # Fetch curve for this run
            cursor.execute('SELECT data FROM equity_curves WHERE test_id = ?', (run['test_id'],))
            curve_row = cursor.fetchone()
            if curve_row and curve_row[0]:
                curve_data = json.loads(curve_row[0])
                
                if not curve_data:
                    continue
                    
                # Normalize equity to stitch curves smoothly
                current_start_equity = curve_data[0]['equity']
                
                if last_equity is not None and current_start_equity > 0:
                    adjustment_factor = last_equity / current_start_equity
                    for point in curve_data:
                        point['equity'] = point['equity'] * adjustment_factor
                
                # Append to composite
                composite_curve.extend(curve_data)
                last_equity = composite_curve[-1]['equity']
                
        conn.close()
        return composite_curve

    def save_insight(self, insight):
        """Saves a single insight to the DB."""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                INSERT OR REPLACE INTO insights (
                    insight_id, type, description, confidence, scope, 
                    parameters, expiration, status, created_at, last_updated
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                insight['insight_id'],
                insight['type'],
                insight['description'],
                insight['confidence'],
                json.dumps(insight['scope']),
                json.dumps(insight.get('parameters', {})),
                insight.get('expiration'),
                insight.get('status', 'active'),
                insight.get('created_at', datetime.now().isoformat()),
                insight.get('last_updated', datetime.now().isoformat())
            ))
            conn.commit()
        except Exception as e:
            print(f"Error saving insight: {e}")
        finally:
            conn.close()

    def get_all_insights(self):
        """Retrieves all insights."""
        conn = self.get_connection()
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        # Ensure table exists (for migration safety)
        try:
            cursor.execute('SELECT * FROM insights')
            rows = cursor.fetchall()
        except sqlite3.OperationalError:
            return []
            
        results = []
        for row in rows:
            d = dict(row)
            d['scope'] = json.loads(d['scope']) if d['scope'] else []
            d['parameters'] = json.loads(d['parameters']) if d['parameters'] else {}
            results.append(d)
            
        conn.close()
        return results

    def save_live_trade(self, trade_data):
        """Saves a live trade log entry."""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                INSERT INTO live_trade_log (
                    session_id, timestamp, symbol, strategy, side, qty, 
                    signal_price, fill_price, slippage, spread, pnl
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                trade_data['session_id'],
                trade_data['timestamp'],
                trade_data['symbol'],
                trade_data['strategy'],
                trade_data['side'],
                trade_data['qty'],
                trade_data['signal_price'],
                trade_data['fill_price'],
                trade_data['slippage'],
                trade_data['spread'],
                trade_data.get('pnl', 0.0)
            ))
            conn.commit()
            # print(f"Logged trade for {trade_data['symbol']}")
        except Exception as e:
            print(f"Error saving live trade log: {e}")
        finally:
            conn.close()
    def get_live_trades(self):
        """Retrieves all live trade logs."""
        conn = self.get_connection()
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        try:
            cursor.execute('SELECT * FROM live_trade_log ORDER BY timestamp ASC')
            rows = cursor.fetchall()
            results = [dict(row) for row in rows]
            return results
        except Exception as e:
            print(f"Error fetching live trades: {e}")
            return []
        finally:
            conn.close()
