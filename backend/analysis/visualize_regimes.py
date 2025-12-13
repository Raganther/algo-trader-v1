import argparse
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime, timedelta
import os

from backend.engine.alpaca_loader import AlpacaDataLoader
from backend.analysis.regime_quantifier import RegimeQuantifier

def visualize_regimes(symbol, start_date, end_date, timeframe='1d'):
    """
    Generates an interactive HTML chart with Market Regimes highlighted.
    """
    print(f"--- Visualizing Regimes for {symbol} ({start_date} to {end_date}) ---")
    
    # 1. Fetch Data
    loader = AlpacaDataLoader()
    try:
        data = loader.fetch_data(symbol, timeframe, start_date, end_date)
    except Exception as e:
        print(f"Error fetching data: {e}")
        return

    if data is None or data.empty:
        print("No data found.")
        return
        
    print(f"Loaded {len(data)} bars.")
    
    # 2. Quantify Regimes
    quantifier = RegimeQuantifier(data)
    # Using default parameters for now
    df = quantifier.quantify()
    
    # 3. Prepare Plot
    fig = go.Figure()
    
    # Add Candlestick
    fig.add_trace(go.Candlestick(
        x=df.index,
        open=df['Open'] if 'Open' in df.columns else data['Open'],
        high=df['High'] if 'High' in df.columns else data['High'],
        low=df['Low'] if 'Low' in df.columns else data['Low'],
        close=df['Close'],
        name='Price'
    ))
    
    # Add SMAs
    fig.add_trace(go.Scatter(x=df.index, y=df['sma_fast'], line=dict(color='orange', width=1), name='SMA Fast'))
    fig.add_trace(go.Scatter(x=df.index, y=df['sma_slow'], line=dict(color='blue', width=1), name='SMA Slow'))
    
    # 4. Add Regime Backgrounds
    # We need to find contiguous blocks of the same regime
    
    # Define Colors
    colors = {
        RegimeQuantifier.BULL_TREND: 'rgba(0, 255, 0, 0.1)',   # Green
        RegimeQuantifier.BEAR_TREND: 'rgba(255, 0, 0, 0.1)',   # Red
        RegimeQuantifier.VOLATILE:   'rgba(128, 0, 128, 0.2)', # Purple
        RegimeQuantifier.RANGING:    'rgba(128, 128, 128, 0.1)' # Grey
    }
    
    # Helper to add shape
    def add_shape(start, end, regime):
        color = colors.get(regime, 'rgba(0,0,0,0)')
        fig.add_vrect(
            x0=start, x1=end,
            fillcolor=color, opacity=1, layer="below", line_width=0,
            annotation_text=regime if (end - start).days > 10 else "", # Only label big blocks
            annotation_position="top left"
        )

    # Iterate to find blocks
    current_regime = None
    start_idx = None
    
    # Ensure index is datetime
    df.index = pd.to_datetime(df.index)
    
    for i in range(len(df)):
        date = df.index[i]
        regime = df['regime'].iloc[i]
        
        if regime != current_regime:
            if current_regime is not None:
                # End of previous block
                end_date = df.index[i] # Use current date as end of previous block (approx)
                add_shape(start_idx, end_date, current_regime)
            
            # Start new block
            current_regime = regime
            start_idx = date
            
    # Add last block
    if current_regime is not None:
        add_shape(start_idx, df.index[-1], current_regime)

    # Layout
    fig.update_layout(
        title=f"Market Regimes: {symbol} ({timeframe})",
        yaxis_title="Price",
        xaxis_title="Date",
        template="plotly_dark",
        height=800
    )
    
    # 5. Save
    output_dir = ".agent/analysis"
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
        
    filename = f"{output_dir}/regime_chart_{symbol}_{timeframe}.html"
    fig.write_html(filename)
    print(f"✅ Chart saved to: {filename}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("symbol", type=str, help="Symbol to analyze (e.g., SPY)")
    parser.add_argument("--start", type=str, default="2020-01-01", help="Start Date (YYYY-MM-DD)")
    parser.add_argument("--end", type=str, default=datetime.now().strftime("%Y-%m-%d"), help="End Date")
    parser.add_argument("--tf", type=str, default="1d", help="Timeframe (1d, 1h, 15m)")
    
    args = parser.parse_args()
    visualize_regimes(args.symbol, args.start, args.end, args.tf)
