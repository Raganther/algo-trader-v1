from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from backend.database import DatabaseManager
import json

app = FastAPI()

# Allow CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify the frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

db = DatabaseManager()

@app.get("/api/runs")
def get_runs():
    """Returns a list of all test runs."""
    try:
        runs = db.get_all_test_runs()
        # Convert row objects to dicts if needed (DatabaseManager already does this)
        return runs
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/edges")
def get_edges():
    """Returns aggregated stats to identify proven edges."""
    try:
        conn = db.get_connection()
        query = """
        SELECT 
            strategy,
            symbol,
            COUNT(*) as years_tested,
            AVG(return_pct) as avg_annual_return,
            AVG(win_rate) as avg_win_rate,
            SUM(CASE WHEN return_pct > 0 THEN 1 ELSE 0 END) as profitable_years
        FROM test_runs 
        GROUP BY strategy, symbol
        HAVING avg_annual_return > 0
        ORDER BY avg_annual_return DESC
        """
        import pandas as pd
        df = pd.read_sql_query(query, conn)
        return df.to_dict(orient='records')
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/runs/{test_id}")
def get_run_details(test_id: str):
    """Returns full details for a specific test run, including equity curve."""
    try:
        run = db.get_test_run(test_id)
        if not run:
            raise HTTPException(status_code=404, detail="Test run not found")
            
        curve = db.get_equity_curve(test_id)
        run['equity_curve'] = curve if curve else []
        
        return run
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/analysis/drawdown")
def get_drawdown_analysis(strategy: str, symbol: str, timeframe: str):
    """Returns continuous drawdown analysis for a strategy/symbol pair."""
    try:
        from backend.analytics import DrawdownAnalyzer
        analyzer = DrawdownAnalyzer()
        result = analyzer.analyze(strategy, symbol, timeframe)
        if result is None:
            raise HTTPException(status_code=404, detail="No data found for this combination")
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
