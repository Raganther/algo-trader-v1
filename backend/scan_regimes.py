import argparse
import pandas as pd
from backend.engine.alpaca_loader import AlpacaDataLoader
from backend.analysis.regime_classifier import RegimeClassifier

def scan_regimes(symbol, start_date, end_date, timeframe='1d'):
    print(f"--- Scanning Regimes for {symbol} ({timeframe}) ---")
    
    # Load Data
    loader = AlpacaDataLoader()
    data = loader.fetch_data(symbol, timeframe, start_date, end_date)
    
    if data is None or data.empty:
        print("No data found.")
        return

    # Classify
    classifier = RegimeClassifier(data)
    results = classifier.classify()
    
    # Analyze Regimes
    regime_counts = results['regime'].value_counts(normalize=True) * 100
    print("\nRegime Distribution:")
    print(regime_counts)
    
    # Identify Segments
    results['group'] = (results['regime'] != results['regime'].shift()).cumsum()
    segments = results.groupby(['group', 'regime']).agg(
        start_date=('regime', lambda x: x.index[0]),
        end_date=('regime', lambda x: x.index[-1]),
        duration=('regime', 'count')
    ).reset_index()
    
    # Filter for significant segments (> 20 days/bars)
    significant_segments = segments[segments['duration'] > 20]
    
    print("\nSignificant Regime Segments (>20 bars):")
    for _, row in significant_segments.iterrows():
        print(f"{row['start_date'].date()} to {row['end_date'].date()}: {row['regime']} ({row['duration']} bars)")
        
if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--symbol", type=str, default="SPY")
    parser.add_argument("--start", type=str, default="2020-01-01")
    parser.add_argument("--end", type=str, default="2025-12-31")
    parser.add_argument("--timeframe", type=str, default="1d")
    args = parser.parse_args()
    
    scan_regimes(args.symbol, args.start, args.end, args.timeframe)
