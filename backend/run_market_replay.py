import time
import json
import pandas as pd
from datetime import datetime, timedelta
from backend.engine.paper_trader import PaperTrader
from backend.engine.strategies.composite_strategy import CompositeStrategy
from backend.engine.data_loader import DataLoader

def load_strategy_config(strategy_id):
    with open('backend/strategy_bank.json', 'r') as f:
        strategies = json.load(f)
        for s in strategies:
            if s['id'] == strategy_id:
                return s
    return None

def run_replay():
    print("--- Market Replay: London Breakout v3 ---")
    
    # 1. Configuration
    symbol = "EURUSD=X"
    strategy_id = "London_Breakout_v3"
    interval = "15m"
    initial_capital = 10000.0
    
    # Pick a specific date range where we know a trade happened
    # Based on previous analysis, let's pick a recent active period or a known winning day.
    # Let's try to find a day in 2024.
    start_date = "2024-06-10"
    end_date = "2024-06-15"
    
    config = load_strategy_config(strategy_id)
    if not config:
        print(f"Error: Strategy {strategy_id} not found.")
        return

    params = config['parameters']
    params['symbol'] = symbol
    
    # 2. Initialize Components
    spread = params.get('spread', 0.00015)
    broker = PaperTrader(initial_balance=initial_capital, spread=spread)
    data_loader = DataLoader()
    
    # 3. Load Data
    print(f"Loading data for {symbol} ({start_date} to {end_date})...")
    data, _ = data_loader.fetch_ohlcv(symbol, start_date, end_date, interval)
    
    if data is None or data.empty:
        print("Error: No data found for replay.")
        return
        
    # Split into "History" (for init) and "Replay" (for loop)
    # We need some history to initialize indicators (e.g. 1 day)
    # Let's say the first 24 hours is history, the rest is replay.
    split_idx = 24 * 4 # 24 hours * 4 candles/hour (15m)
    
    if len(data) < split_idx + 10:
        print("Error: Not enough data for replay.")
        return
        
    history_data = data.iloc[:split_idx]
    replay_data = data.iloc[split_idx:]
    
    print(f"Initializing Strategy with {len(history_data)} candles of history...")
    strategy = CompositeStrategy(data=history_data, parameters=params, broker=broker)
    
    print(f"Starting Replay of {len(replay_data)} candles...")
    print("Watching for 08:00 London Breakout...")
    
    # 4. Replay Loop
    try:
        for timestamp, row in replay_data.iterrows():
            # Simulate "Waiting" (Fast forward: 0.5s per candle)
            time.sleep(0.5)
            
            # Format candle
            candle = {
                'Open': row['Open'],
                'High': row['High'],
                'Low': row['Low'],
                'Close': row['Close'],
                'Volume': row['Volume']
            }
            
            # Update Broker
            current_price = candle['Close']
            broker.update_price(symbol, current_price)
            
            # Run Strategy
            # We print the time to see the "Live" progression
            time_str = timestamp.strftime('%Y-%m-%d %H:%M')
            print(f"[{time_str}] Price: {current_price:.5f} | ", end="")
            
            strategy.on_data(timestamp, candle)
            
            # Print Status
            positions = broker.get_positions()
            equity = broker.get_equity()
            pnl = equity - initial_capital
            
            pos_str = "FLAT"
            if symbol in positions:
                pos = positions[symbol]
                side = "LONG" if pos['size'] > 0 else "SHORT"
                pos_str = f"{side} {abs(pos['size'])} @ {pos['avg_price']:.5f}"
                
                # Highlight active trade
                print(f"\033[92mPos: {pos_str} | PnL: ${pnl:.2f}\033[0m") # Green text
            else:
                print(f"Pos: {pos_str} | PnL: ${pnl:.2f}")
                
    except KeyboardInterrupt:
        print("\nStopping Replay...")

if __name__ == "__main__":
    run_replay()
