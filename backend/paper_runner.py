import time
import pandas as pd
from datetime import datetime
from backend.engine.alpaca_loader import AlpacaDataLoader
from backend.engine.live_broker import LiveBroker
from backend.strategies.stoch_rsi_mean_reversion import StochRSIMeanReversionStrategy

def run_paper_trading():
    SYMBOL = "SPY"
    TIMEFRAME = "5m"
    
    print(f"--- Starting Paper Trading for {SYMBOL} ({TIMEFRAME}) ---")
    
    # 1. Initialize Components
    loader = AlpacaDataLoader()
    broker = LiveBroker(symbol=SYMBOL, paper=True)
    
    # Initialize DB Logger
    from backend.database import DatabaseManager
    import uuid
    db = DatabaseManager()
    session_id = str(uuid.uuid4())
    print(f"Session ID: {session_id}")
    
    # Initial Data Fetch (to initialize strategy)
    print("Fetching initial data...")
    data = loader.get_data(SYMBOL, TIMEFRAME, limit=200) # Fetch last 200 candles
    
    if data.empty:
        print("Error: No data fetched. Exiting.")
        return

    
    # Initialize Strategy
    # We pass dummy events/params, mostly need the logic
    params = {
        'symbol': SYMBOL,
        'rsi_period': 14,
        'stoch_period': 14,
        'k_period': 3,
        'd_period': 3,
        'adx_threshold': 25,
        'sl_atr': 3.0,
        'position_size': 100000.0 # Not used by LiveBroker (it uses dynamic sizing if we implemented it, or fixed)
        # Wait, Strategy calculates size based on risk.
        # LiveBroker.buy(size) receives that calculated size.
    }
    
    strategy = StochRSIMeanReversionStrategy(data, None, params, initial_cash=100000.0, broker=broker)
    
    print("Strategy Initialized. Waiting for next candle...")
    
    while True:
        # Sleep logic: Wait for next 5m mark
        # e.g. if now is 10:02, wait until 10:05:05 (give 5s buffer for data to arrive)
        now = datetime.now()
        next_minute = 5 - (now.minute % 5)
        seconds_to_wait = (next_minute * 60) - now.second + 5
        
        if seconds_to_wait <= 0:
            seconds_to_wait += 300 # Add 5 mins if we are exactly on the mark
            
        print(f"Sleeping for {seconds_to_wait} seconds...")
        time.sleep(seconds_to_wait)
        
        print(f"Wake up! Fetching latest data for {SYMBOL}...")
        
        try:
            # 1. Fetch Updated Data
            new_data = loader.get_data(SYMBOL, TIMEFRAME, limit=200)
            
            if new_data.empty:
                print("Warning: No new data fetched. Skipping...")
                continue
            
            # 2. Update Strategy Data
            strategy.data = new_data
            
            # 3. Recalculate Indicators
            strategy.generate_signals(new_data)
            
            # 4. Run Logic for the LAST Closed Candle
            # The last row in 'new_data' is the candle that just closed (Alpaca returns closed candles usually)
            # Let's verify: Alpaca get_bars returns historical data.
            # If we ask at 10:05:05, we should get the 10:00-10:05 candle as the last one.
            
            last_index = len(new_data) - 1
            last_row = new_data.iloc[-1]
            
            print(f"Processing Candle: {last_row.name} | Close: {last_row['Close']}")
            
            # Update Broker State (Equity, Positions)
            broker.refresh()
            
            # Run Strategy Logic
            strategy.on_bar(last_row, last_index, new_data)
            
            # 5. Log New Trades
            new_trades = broker.get_new_trades()
            if new_trades:
                print(f"Logging {len(new_trades)} new trades to DB...")
                for trade in new_trades:
                    trade['session_id'] = session_id
                    trade['strategy'] = "StochRSIMeanReversion" # Hardcoded for now
                    db.save_live_trade(trade)
            
        except Exception as e:
            print(f"Error in trading loop: {e}")
            time.sleep(60) # Retry in 1 min

if __name__ == "__main__":
    run_paper_trading()
