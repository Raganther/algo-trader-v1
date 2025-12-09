import pandas as pd
from backend.database import DatabaseManager

class DrawdownAnalyzer:
    def __init__(self):
        self.db = DatabaseManager()

    def analyze(self, strategy: str, symbol: str, timeframe: str):
        conn = self.db.get_connection()
        try:
            # 1. Fetch all yearly runs
            query = """
            SELECT test_id, start_date, return_pct, max_drawdown, total_trades, win_rate
            FROM test_runs 
            WHERE strategy = ? 
              AND symbol = ? 
              AND timeframe = ?
            ORDER BY start_date ASC
            """
            cursor = conn.cursor()
            cursor.execute(query, (strategy, symbol, timeframe))
            runs = cursor.fetchall()
            
            if not runs:
                return None

            # Store yearly stats for cross-referencing
            yearly_stats = []
            for r in runs:
                yearly_stats.append({
                    "year": r[1].split('-')[0],
                    "return_pct": r[2],
                    "max_drawdown": r[3],
                    "total_trades": r[4] if r[4] is not None else 0,
                    "win_rate": r[5] if r[5] is not None else 0.0
                })

            # 2. Stitch Equity Curve
            full_curve = []
            last_equity = 10000.0
            
            for run in runs:
                test_id = run[0]
                
                curve_data = self.db.get_equity_curve(test_id)
                
                if curve_data and isinstance(curve_data, list) and len(curve_data) > 0:
                    if isinstance(curve_data[0], dict) and 'equity' in curve_data[0]:
                         current_year_start = curve_data[0]['equity']
                         # Avoid division by zero
                         if current_year_start == 0:
                             scale_factor = 0
                         else:
                             scale_factor = last_equity / current_year_start
                         
                         for point in curve_data:
                             normalized_point = point.copy()
                             normalized_point['equity'] = point['equity'] * scale_factor
                             
                             # Normalize time to datetime object immediately
                             t = point['time']
                             if isinstance(t, (int, float)):
                                 # Assume Unix timestamp (seconds)
                                 normalized_point['time'] = pd.to_datetime(t, unit='s')
                             else:
                                 # Assume string date
                                 normalized_point['time'] = pd.to_datetime(t)
                                 
                             full_curve.append(normalized_point)
                             
                         last_equity = full_curve[-1]['equity']

            if not full_curve:
                return {
                    "equity_curve": [],
                    "drawdown_periods": [],
                    "yearly_stats": yearly_stats,
                    "metrics": {}
                }
                
            # 3. Calculate Drawdown
            df = pd.DataFrame(full_curve)
            # Time is already normalized to datetime objects in the loop above
            df = df.sort_values('time').drop_duplicates(subset='time').reset_index(drop=True)
            
            df['hwm'] = df['equity'].cummax()
            df['dd'] = (df['hwm'] - df['equity']) / df['hwm']
            
            # 4. Identify Drawdown Periods
            periods = []
            in_drawdown = False
            start_date = None
            max_dd = 0.0
            bottom_date = None
            
            for i, row in df.iterrows():
                if row['dd'] > 0:
                    if not in_drawdown:
                        in_drawdown = True
                        start_date = row['time']
                        max_dd = 0.0
                        bottom_date = row['time']
                    
                    if row['dd'] > max_dd:
                        max_dd = row['dd']
                        bottom_date = row['time']
                else:
                    if in_drawdown:
                        in_drawdown = False
                        end_date = row['time']
                        duration = (end_date - start_date).days
                        
                        if max_dd > 0.05: # Filter small noise
                            periods.append({
                                "Start": start_date.strftime('%Y-%m-%d'),
                                "Bottom": bottom_date.strftime('%Y-%m-%d'),
                                "End": end_date.strftime('%Y-%m-%d'),
                                "Depth": max_dd, # Keep as float for frontend formatting
                                "Duration": duration
                            })
            
            # Check active drawdown
            if in_drawdown:
                 duration = (df.iloc[-1]['time'] - start_date).days
                 if max_dd > 0.05:
                    periods.append({
                        "Start": start_date.strftime('%Y-%m-%d'),
                        "Bottom": bottom_date.strftime('%Y-%m-%d'),
                        "End": "Active",
                        "Depth": max_dd,
                        "Duration": duration
                    })

            # Sort periods by depth
            periods.sort(key=lambda x: x['Depth'], reverse=True)

            # 5. Prepare Response
            # Downsample curve for frontend performance if needed (e.g., take every Nth point)
            # For now, return full curve but convert timestamps to string
            
            # Optimization: Return only necessary fields
            final_curve = []
            for i, row in df.iterrows():
                final_curve.append({
                    "time": row['time'].strftime('%Y-%m-%d'),
                    "equity": row['equity'],
                    "drawdown": row['dd']
                })

            metrics = {
                "total_return": (df.iloc[-1]['equity'] - df.iloc[0]['equity']) / df.iloc[0]['equity'],
                "max_drawdown": df['dd'].max(),
                "current_drawdown": df.iloc[-1]['dd']
            }

            return {
                "equity_curve": final_curve,
                "drawdown_periods": periods,
                "yearly_stats": yearly_stats,
                "metrics": metrics
            }
        finally:
            conn.close()
