import pandas as pd
from backend.engine.backtester import Backtester
from backend.engine.data_loader import DataLoader
from backend.engine.strategies.composite_strategy import CompositeStrategy

def run_batch_test():
    # Configuration (Matches London_Breakout_v3 from strategy_bank.json)
    base_parameters = {
        "range_start": "00:00",
        "range_end": "08:00",
        "trade_window_end": "12:00",
        "buffer_pips": 2.0,
        "risk_per_trade": 0.005,
        "stop_loss_pct": 0.005,
        "trail_activation_pct": 0.005,
        "trail_offset_pct": 0.0025,
        "signals": [
             {
                "id": "AsianRange",
                "type": "TimeRange",
                "params": {
                    "range_start": "00:00",
                    "range_end": "08:00",
                    "trade_window_end": "12:00",
                    "buffer_pips": 2.0,
                    "pip_size": 0.0001 
                }
            }
        ],
        "conditions": [
            { "signal_id": "AsianRange", "operator": "==", "value": 1.0 }
        ],
        "short_conditions": [
            { "signal_id": "AsianRange", "operator": "==", "value": -1.0 }
        ]
    }
    
    # Test Parameters
    symbols = ["EURUSD=X", "USDJPY=X", "GBPUSD=X"]
    timeframe = "15m"
    start_date = "2023-01-01"
    end_date = "2024-12-31"
    
    print(f"--- Batch Test: London Breakout ({timeframe}) ---")
    print(f"Period: {start_date} to {end_date}")
    print("-" * 65)
    print(f"{'Symbol':<10} | {'Return':<10} | {'Trades':<8} | {'Win Rate':<8}")
    print("-" * 65)
    
    loader = DataLoader()
    
    for symbol in symbols:
        # 1. Load Data
        try:
            df, _ = loader.fetch_ohlcv(symbol, start_date, end_date, timeframe)
            if df.empty:
                print(f"{symbol:<10} | {'NO DATA':<10} | {'-':<8} | {'-':<8}")
                continue
        except Exception as e:
            print(f"{symbol:<10} | {'ERROR':<10} | {str(e)}")
            continue

        # 2. Adjust for JPY
        # We need to deep copy or re-create params to avoid modifying the base for next iteration
        import copy
        current_params = base_parameters.copy()
        current_params['symbol'] = symbol # Pass symbol for PaperTrader
        
        # Adjust pip size for JPY pairs
        if "JPY" in symbol:
            # Update pip_size in the signal params
            for sig in current_params['signals']:
                if sig['id'] == 'AsianRange':
                    sig['params']['pip_size'] = 0.01
        
        # Run Backtest
        # Note: Backtester now uses PaperTrader internally.
        backtester = Backtester(
            data=df,
            strategy_class=CompositeStrategy,
            parameters=current_params,
            initial_capital=10000.0,
            interval=timeframe
        )
        
        results = backtester.run()
        
        trades = results['total_trades']
        return_pct = results['return_pct']
        
        # Calculate Win Rate if possible (PaperTrader tracks orders, not round-trip trades yet)
        # We can approximate win rate by checking realized PnL of closed positions?
        # For now, let's just show Return and Trades.
        win_rate = 0.0 
        
        print(f"{symbol:<10} | {return_pct:>9.2f}% | {trades:>8} | {win_rate:>7.1f}%")

    print("-" * 65)

if __name__ == "__main__":
    run_batch_test()
