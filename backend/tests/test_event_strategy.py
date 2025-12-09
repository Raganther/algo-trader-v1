import pandas as pd
from backend.engine.backtester import Backtester
from backend.engine.strategies.composite_strategy import CompositeStrategy
from backend.engine.data_loader import DataLoader
import json

def test_event_strategy():
    # 1. Load Strategy Config
    with open('backend/strategy_bank.json', 'r') as f:
        bank = json.load(f)
    
    strategy_config = next(s for s in bank if s['id'] == 'News_Trader_v3')
    print(f"Testing Strategy: {strategy_config['id']}")
    
    # 2. Fetch Data (Use a period with known high impact events)
    # Testing daily data for 2024 with new backtester
    start_date = "2024-01-01"
    end_date = "2024-12-31"
    symbol = "EURUSD=X"
    
    loader = DataLoader()
    print(f"Fetching daily data for {symbol}...")
    data, metadata = loader.fetch_ohlcv(symbol, start_date, end_date, interval="1d")
    
    if data.empty:
        print("No price data found. Generating mock data for testing...")
        data = loader._generate_mock_data(start_date, end_date, interval="1d")
    
    # 3. Fetch Events
    events = loader.fetch_economic_events(start_date, end_date)
    print(f"Loaded {len(events)} events.")
    if not events.empty:
        print(events[['date', 'event', 'actual', 'forecast']].head())
    
    # 4. Run Backtest
    backtester = Backtester(
        data=data,
        strategy_class=CompositeStrategy,
        events=events,
        parameters=strategy_config['parameters'],
        interval="1d"
    )
    
    results = backtester.run()
    
    # 5. Analyze Results
    print("\n--- Results ---")
    print(f"Total Trades: {results['total_trades']}")
    print(f"Return: {results['return_pct']}%")
    print(f"Final Equity: {results['final_equity']}")
    
    print("\n--- Trade Log ---")
    for order in results['orders']:
        if order['status'] == 'filled':
            print(f"{order['fill_time']} {order['side'].upper()} @ {order['fill_price']}")

if __name__ == "__main__":
    test_event_strategy()
