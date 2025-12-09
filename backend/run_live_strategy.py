import time
import json
import argparse
import sys
from datetime import datetime, timedelta
from backend.engine.paper_trader import PaperTrader
from backend.engine.strategies.composite_strategy import CompositeStrategy
from backend.engine.data_loader import DataLoader
from backend.engine.live_data_loader import LiveDataLoader

def load_strategy_config(strategy_id):
    with open('backend/strategy_bank.json', 'r') as f:
        strategies = json.load(f)
        for s in strategies:
            if s['id'] == strategy_id:
                return s
    return None

def run_live(demo_mode=False):
    print(f"--- Starting Live Trading Simulation ({'DEMO REPLAY' if demo_mode else 'REAL-TIME'}) ---")
    
    # 1. Configuration
    symbol = "EURUSD=X"
    strategy_id = "London_Breakout_v3"
    interval = "15m"
    initial_capital = 10000.0
    
    config = load_strategy_config(strategy_id)
    if not config:
        print(f"Error: Strategy {strategy_id} not found.")
        return

    params = config['parameters']
    params['symbol'] = symbol
    
    # 2. Initialize Components
    spread = params.get('spread', 0.00015)
    broker = PaperTrader(initial_balance=initial_capital, spread=spread)
    
    # Historical Data Loader (for init)
    data_loader = DataLoader()
    
    # Fetch History for Initialization
    print("Fetching historical data for initialization...")
    end_date = datetime.now().strftime('%Y-%m-%d')
    start_date = (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d')
    
    history_data, _ = data_loader.fetch_ohlcv(symbol, start_date, end_date, interval=interval)
    
    if history_data is None or history_data.empty:
        print("Error: Could not fetch historical data. Exiting.")
        return

    # Initialize Strategy
    strategy = CompositeStrategy(data=history_data, parameters=params, broker=broker)
    
    print(f"Strategy: {strategy_id}")
    print(f"Symbol: {symbol}")
    print(f"Spread: {spread*10000:.1f} pips")
    print(f"Initial Balance: ${initial_capital:.2f}")
    
    # 3. Execution Loop
    if demo_mode:
        # --- DEMO MODE: Replay last 24 hours (96 candles) ---
        print("\n--- DEMO MODE: Replaying last 24 hours ---")
        replay_data = history_data.tail(96) 
        
        for timestamp, row in replay_data.iterrows():
            time.sleep(0.1) # Fast replay
            
            candle = {
                'Open': row['Open'], 'High': row['High'], 'Low': row['Low'], 
                'Close': row['Close'], 'Volume': row['Volume']
            }
            
            # Update & Run
            broker.update_price(symbol, candle['Close'])
            strategy.on_data(timestamp, candle)
            
            # Status
            _print_status(timestamp, candle['Close'], broker, initial_capital)
            
        print("\n--- Replay Complete ---")
        
    else:
        # --- REAL-TIME MODE ---
        print("\n--- LIVE MODE: Connecting to Yahoo Finance ---")
        live_loader = LiveDataLoader(symbol, interval=interval)
        
        try:
            while True:
                # 1. Fetch Latest Candle
                print("Fetching live data...", end="\r")
                candle = live_loader.fetch_latest_candle()
                
                if candle:
                    timestamp = candle['Date']
                    
                    # Update & Run
                    broker.update_price(symbol, candle['Close'])
                    strategy.on_data(timestamp, candle)
                    
                    # Status
                    _print_status(timestamp, candle['Close'], broker, initial_capital)
                
                # Wait for next update (e.g., 60 seconds)
                # For 15m candles, checking every minute is fine
                time.sleep(60)
                
        except KeyboardInterrupt:
            print("\nStopping Live Trading...")
        except Exception as e:
            print(f"\nError in Live Loop: {e}")

def _print_status(timestamp, price, broker, initial_capital):
    positions = broker.get_positions()
    equity = broker.get_equity()
    pnl = equity - initial_capital
    
    pos_str = "FLAT"
    color_code = ""
    reset_code = ""
    
    if "EURUSD=X" in positions:
        pos = positions["EURUSD=X"]
        side = "LONG" if pos['size'] > 0 else "SHORT"
        pos_str = f"{side} {abs(pos['size'])} @ {pos['avg_price']:.5f}"
        color_code = "\033[92m" # Green
        reset_code = "\033[0m"

    print(f"{color_code}[{timestamp}] Price: {price:.5f} | Pos: {pos_str} | Equity: ${equity:.2f} (PnL: ${pnl:.2f}){reset_code}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--demo', action='store_true', help='Run in Demo/Replay mode')
    args = parser.parse_args()
    
    run_live(demo_mode=args.demo)
