
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from .engine.data_loader import DataLoader
from .engine.backtester import Backtester
from .engine.strategies.composite_strategy import CompositeStrategy
from .engine.history_manager import HistoryManager
import pandas as pd

app = FastAPI(title="Forex Backtester API")

# Initialize History Manager
history_manager = HistoryManager()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Strategy Registry
STRATEGIES = {
    "Composite": CompositeStrategy
}

class BacktestRequest(BaseModel):
    symbol: str = "EURUSD=X"
    start_date: str = "2023-01-01"
    end_date: str = "2023-12-31"
    interval: str = "1d"
    strategy: str = "SMA"
    parameters: dict = {}

@app.get("/")
def read_root():
    return {"status": "active", "service": "Forex Backtester Backend"}

@app.get("/health")
def health_check():
    return {"status": "ok"}

@app.post("/run_backtest")
def run_backtest(request: BacktestRequest):
    try:
        loader = DataLoader()
        data, metadata = loader.fetch_ohlcv(request.symbol, request.start_date, request.end_date, request.interval)
        
        # Fetch events (mock for now)
        events = loader.fetch_economic_events(request.start_date, request.end_date)
        
        strategy_class = STRATEGIES.get(request.strategy)
        if not strategy_class:
            raise HTTPException(status_code=400, detail=f"Unknown strategy: {request.strategy}")
            
        # Inject events into the strategy instance
        # For MVP, let's modify Backtester to accept events or pass them to strategy init
        backtester = Backtester(data, strategy_class, events=events, parameters=request.parameters, interval=request.interval)
        results = backtester.run()
        
        # Add Metadata
        results['metadata'] = metadata
        
        # Save to History
        history_manager.save_run(request.strategy, request.parameters, results)
        
        # Convert results to JSON-friendly format
        # Pandas timestamps need conversion
        results['orders'] = [
            {**o, 'timestamp': o['timestamp'].isoformat() if pd.notnull(o.get('timestamp')) else None,
             'fill_time': o['fill_time'].isoformat() if pd.notnull(o.get('fill_time')) else None} 
            for o in results['orders']
        ]
        
        return results
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/history")
def get_history():
    return history_manager.get_history()

# --- New Research API Endpoints ---

from .database import DatabaseManager
db = DatabaseManager()

@app.get("/api/edges")
def get_edges():
    """Returns aggregated stats to identify proven edges."""
    try:
        conn = db.get_connection()
        # First get the best timeframe for each strategy/symbol combo
        # (the one with highest return)
        query = """
        WITH BestTimeframes AS (
            SELECT 
                strategy,
                symbol,
                timeframe,
                AVG(return_pct) as avg_return,
                ROW_NUMBER() OVER (PARTITION BY strategy, symbol ORDER BY AVG(return_pct) DESC) as rn
            FROM test_runs
            GROUP BY strategy, symbol, timeframe
        )
        SELECT 
            t.strategy,
            t.symbol,
            bt.timeframe,
            COUNT(*) as years_tested,
            AVG(t.return_pct) as avg_annual_return,
            AVG(t.win_rate) as avg_win_rate,
            SUM(CASE WHEN t.return_pct > 0 THEN 1 ELSE 0 END) as profitable_years
        FROM test_runs t
        JOIN BestTimeframes bt ON t.strategy = bt.strategy AND t.symbol = bt.symbol AND bt.rn = 1
        WHERE t.timeframe = bt.timeframe
        GROUP BY t.strategy, t.symbol, bt.timeframe
        HAVING avg_annual_return > 0
        ORDER BY avg_annual_return DESC
        """
        import pandas as pd
        df = pd.read_sql_query(query, conn)
        return df.to_dict(orient='records')
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/runs")
def get_runs():
    """Returns all test runs (metrics only)."""
    return db.get_all_test_runs()

@app.get("/api/runs/{test_id:path}")
def get_run_details(test_id: str):
    """Returns full details for a specific test run, including equity curve."""
    try:
        # Decode URL-encoded ID if needed, but 'path' usually gives raw string?
        # Actually, FastAPI 'path' parameter gives the string.
        # If the client sends %2F, Starlette might decode it.
        # Let's verify.
        
        run = db.get_test_run(test_id)
        if not run:
            raise HTTPException(status_code=404, detail=f"Test run not found: {test_id}")
            
        curve = db.get_equity_curve(test_id)
        
        # Downsample large equity curves to prevent browser crashes
        # Target ~2000 points for Recharts performance
        if curve and len(curve) > 2000:
            step = len(curve) // 2000
            curve = curve[::step]
        
        run['equity_curve'] = curve if curve else []
        
        return run
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/results/composite")
def get_composite_details(strategy: str, symbol: str, timeframe: str = "1h"):
    """Returns stitched equity curve for a strategy/symbol combo."""
    curve = db.get_composite_equity_curve(strategy, symbol, timeframe)
    
    # Calculate aggregate stats
    if not curve:
        raise HTTPException(status_code=404, detail="No data found for this combination")
        
    start_equity = curve[0]['equity']
    end_equity = curve[-1]['equity']
    total_return = ((end_equity - start_equity) / start_equity) * 100
    
    # Simple Max Drawdown on composite
    import pandas as pd
    df = pd.DataFrame(curve)
    df['equity'] = pd.to_numeric(df['equity'])
    hwm = df['equity'].cummax()
    dd = (hwm - df['equity']) / hwm
    max_dd = dd.max() * 100
    
    # Downsample for frontend performance (Recharts crashes with >10k points)
    # Target ~2000 points
    total_points = len(curve)
    if total_points > 2000:
        step = total_points // 2000
        curve = curve[::step]

    return {
        "strategy": strategy,
        "symbol": symbol,
        "timeframe": timeframe,
        "return_pct": total_return,
        "max_drawdown": max_dd,
        "equity_curve": curve
    }
