import argparse
import pandas as pd
import json
import os
from backend.engine.data_loader import DataLoader
from backend.engine.alpaca_loader import AlpacaDataLoader # New
from backend.engine.backtester import Backtester
from backend.database import DatabaseManager
from backend.strategies.donchian_breakout import DonchianBreakoutStrategy
from backend.strategies.bollinger_breakout import BollingerBreakoutStrategy
from backend.strategies.nfp_breakout import NFPBreakoutStrategy
from backend.strategies.macd_bollinger import MACDBollingerStrategy # New
from backend.strategies.stoch_rsi_mean_reversion import StochRSIMeanReversionStrategy
from backend.strategies.stoch_rsi_next_open import StochRSINextOpen
from backend.strategies.stoch_rsi_limit import StochRSILimit
from backend.strategies.hybrid_regime import HybridRegimeStrategy # New
from backend.strategies.hybrid_regime import HybridRegimeStrategy # New
from backend.strategies.donchian_trend import DonchianTrendStrategy # New
from backend.strategies.simple_sma import SimpleSMAStrategy
from backend.strategies.stoch_rsi_quant import StochRSIQuantStrategy # New
from backend.strategies.gamma_scalping import GammaScalping
from backend.strategies.rapid_fire_test import RapidFireTestStrategy # New
from backend.strategies.a_golden_cross import AGoldenCrossStrategy

# Strategy Mapping
STRATEGY_MAP = {
    "DonchianBreakout": DonchianBreakoutStrategy,
    "BollingerBreakout": BollingerBreakoutStrategy,
    "NFPBreakout": NFPBreakoutStrategy,
    "MACDBollinger": MACDBollingerStrategy,
    "StochRSIMeanReversion": StochRSIMeanReversionStrategy,
    "StochRSINextOpen": StochRSINextOpen,
    "StochRSILimit": StochRSILimit,
    "HybridRegime": HybridRegimeStrategy,
    "HybridRegime (Realistic_1x)": HybridRegimeStrategy, # Alias for user request
    "DonchianTrend": DonchianTrendStrategy,
    "SimpleSMA": SimpleSMAStrategy,
    "StochRSIQuant": StochRSIQuantStrategy,
    "GammaScalping": GammaScalping,
    "RapidFireTest": RapidFireTestStrategy,
    "AGoldenCross": AGoldenCrossStrategy,
}

def run_backtest(args):
    print(f"--- Starting Backtest: {args.strategy} on {args.symbol} ({args.timeframe}) ---")
    
    # 1. Load Data
    # 1. Load Data
    if args.source == 'alpaca':
        print("Using Alpaca Data Source...")
        loader = AlpacaDataLoader()
        
        # Handle Resampling for unsupported timeframes (e.g. 5m, 15m, 4h)
        target_tf = args.timeframe
        fetch_tf = target_tf
        
        if target_tf == '4h':
            fetch_tf = '1h'
        elif target_tf in ['5m', '15m']:
            fetch_tf = '1m'
        
        # Fetch Data
        data = loader.fetch_data(args.symbol, fetch_tf, args.start, args.end)
        
        # -----------------------------------------------
        
        # Fetch VIXY (Volatility Proxy) for Hybrid Strategy
        if args.strategy in ['HybridRegime', 'StochRSIQuant', 'HybridRegime (Realistic_1x)']:
            print("Fetching VIXY data for Volatility Filter...")
            try:
                vix_data = loader.fetch_data("VIXY", "1d", args.start, args.end) # VIX is daily usually
                if not vix_data.empty:
                    # Resample VIX to match target timeframe (forward fill)
                    # First, ensure VIX has a 'Close'
                    vix_close = vix_data[['Close']].rename(columns={'Close': 'vix_close'})
                    
                    # Merge with main data
                    # Use reindex with ffill to broadcast daily VIX to intraday timestamps
                    # Ensure indices are timezone-aware and matching
                    if data.index.tz is None and vix_close.index.tz is not None:
                        vix_close.index = vix_close.index.tz_localize(None)
                    elif data.index.tz is not None and vix_close.index.tz is None:
                        vix_close.index = vix_close.index.tz_localize('UTC')
                        
                    data['vix_close'] = vix_close.reindex(data.index, method='ffill')['vix_close']
                    print("VIXY data merged successfully.")
                else:
                    print("Warning: VIXY data empty.")
            except Exception as e:
                print(f"Warning: Failed to fetch VIXY: {e}")
        
        # Resample if needed
        if data is not None and not data.empty and target_tf != fetch_tf:
            print(f"Resampling {fetch_tf} to {target_tf}...")
            ohlc_dict = {'Open': 'first', 'High': 'max', 'Low': 'min', 'Close': 'last', 'Volume': 'sum'}
            
            # Map timeframe to pandas alias
            resample_tf = target_tf
            if target_tf == '5m': resample_tf = '5min'
            if target_tf == '15m': resample_tf = '15min'
            
            # Add VIX to aggregation if present
            if 'vix_close' in data.columns:
                ohlc_dict['vix_close'] = 'last'
                
            # Add Sector TICK to aggregation if present

            
            data = data.resample(resample_tf).agg(ohlc_dict).dropna()
            
    else:
        # Default CSV/Oanda Loader
        loader = DataLoader()
        try:
            # Try fetching target timeframe directly first
            data, _ = loader.fetch_ohlcv(args.symbol, args.start, args.end, interval=args.timeframe)
        except Exception:
            data = None
        
    if data is None or data.empty:
        if args.source == 'csv': # Only try fallback for CSV
            print(f"Direct data missing for {args.timeframe}. Attempting 1m resample...")
            data_1m, _ = loader.fetch_ohlcv(args.symbol, args.start, args.end, interval="1m")
            if data_1m is not None and not data_1m.empty:
                ohlc_dict = {'Open': 'first', 'High': 'max', 'Low': 'min', 'Close': 'last', 'Volume': 'sum'}
                data = data_1m.resample(args.timeframe).agg(ohlc_dict).dropna()
            else:
                print("Error: No data found.")
                return
        else:
            print("Error: No data found from Alpaca.")
            return

    # 2. Initialize Strategy
    # Import Sniper Strategy
    try:
        from backend.strategies.stoch_rsi_sniper import StochRSISniperStrategy
        STRATEGY_MAP['StochRSISniper'] = StochRSISniperStrategy
    except ImportError:
        pass # File might not exist yet
        
    strategy_class = STRATEGY_MAP.get(args.strategy)
    if not strategy_class:
        print(f"Error: Strategy '{args.strategy}' not found in map.")
        return
        
    # Default Params (can be overridden by args later)
    # 2. Configure Parameters
    if args.strategy == "MACDBollinger":
        params = {
            "symbol": args.symbol,
            "bb_period": 20,
            "bb_std": 2.0,
            "macd_fast": 12,
            "macd_slow": 26,
            "macd_signal": 9,
            "sl_atr": 2.0,
            "atr_period": 14,
            # Refinement Options (Optimized for GBPJPY)
            "use_trailing_stop": True,
            "trailing_atr_dist": 3.0,
            "use_adx_filter": False,
            "adx_threshold": 25
        }
    elif args.strategy == "DonchianBreakout":
        params = {
            "symbol": args.symbol,
            "entry_period": 20,
            "exit_period": 10,
            "stop_loss_atr": 2.0,
            "atr_period": 20
        }
    elif args.strategy in ["HybridRegime", "HybridRegime (Realistic_1x)"]:
        params = {
            "symbol": args.symbol,
            "adx_period": 14,
            "adx_threshold": 25,
            # StochRSI Params
            "rsi_period": 14,
            "stoch_period": 14,
            "k_period": 3,
            "d_period": 3,
            "overbought": 80,
            "oversold": 20,
            # Donchian Params
            "entry_period": 20,
            "exit_period": 10,
            "stop_loss_atr": 2.0,
            "atr_period": 20
        }
    elif args.strategy == "DonchianTrend":
        params = {
            "symbol": args.symbol,
            "entry_period": 20,
            "exit_period": 10,
            "stop_loss_atr": 2.0,
            "atr_period": 20,
            "adx_period": 14,
            "adx_threshold": 25,
            "sma_period": 200
        }
    else:
        params = {
            "symbol": args.symbol
        }
        
    # Override with CLI parameters if provided
    if args.parameters:
        try:
            cli_params = json.loads(args.parameters)
            params.update(cli_params)
            print(f"Overridden Parameters: {cli_params}")
        except json.JSONDecodeError:
            print("Error: Invalid JSON in --parameters")
            return
    
    # 3. Run Backtest
    # Initialize Backtester
    print(f"DEBUG: Data Shape: {data.shape}")
    if len(data) > 1:
        print(f"DEBUG: Data Frequency: {data.index[1] - data.index[0]}")

    backtester = Backtester(
        data, 
        strategy_class, 
        parameters=params, 
        initial_capital=10000.0,
        spread=args.spread,
        execution_delay=args.delay
    )
    results = backtester.run()
    
    # 4. Report
    print("\n=== RESULTS ===")
    print(f"Return: {results['return_pct']}%")
    print(f"Max DD: {results['max_drawdown']}%")
    print(f"Trades: {results['total_trades']}")
    print(f"Win Rate: {results['win_rate'] * 100:.2f}%")
    
    # 5. Save Results (Direct to SQLite)
    # Extract years from date range
    start_year = int(args.start.split('-')[0])
    end_year = int(args.end.split('-')[0])
    
    db = DatabaseManager()
    db.initialize_db()
    
    # If multi-year, split into yearly segments
    if end_year > start_year:
        print(f"\nSplitting into yearly segments ({start_year}-{end_year})...")
        
        # Convert equity curve to DataFrame
        equity_curve = results['equity_curve']
        if equity_curve:
            df_eq = pd.DataFrame(equity_curve)
            if isinstance(df_eq.iloc[0]['time'], int):
                df_eq['datetime'] = pd.to_datetime(df_eq['time'], unit='s')
            else:
                df_eq['datetime'] = pd.to_datetime(df_eq['time'])
            df_eq.set_index('datetime', inplace=True)
            
            trade_history = results.get('trade_history', [])
            
            for year in range(start_year, end_year + 1):
                year_start = f"{year}-01-01"
                year_end = f"{year}-12-31"
                
                year_data = df_eq.loc[year_start:year_end]
                if year_data.empty:
                    continue
                
                # Calculate Year Metrics
                start_equity = year_data.iloc[0]['equity']
                end_equity = year_data.iloc[-1]['equity']
                year_return_pct = ((end_equity - start_equity) / start_equity) * 100
                
                # Year Max Drawdown
                slice_equity = year_data['equity']
                slice_hwm = slice_equity.cummax()
                slice_dd = (slice_hwm - slice_equity) / slice_hwm
                year_max_dd = slice_dd.max() * 100
                
                # Filter trades for this year
                year_win = 0
                year_loss = 0
                for trade in trade_history:
                    ts_val = trade.get('timestamp')
                    if ts_val is not None:
                        try:
                            if isinstance(ts_val, int):
                                if 0 <= ts_val < len(data):
                                    ts_dt = data.index[ts_val]
                                    if ts_dt.year == year:
                                        if trade['pnl'] > 0: year_win += 1
                                        else: year_loss += 1
                            elif isinstance(ts_val, str):
                                trade_year = int(ts_val.split('-')[0])
                                if trade_year == year:
                                    if trade['pnl'] > 0: year_win += 1
                                    else: year_loss += 1
                        except:
                            pass
                
                total_trades = year_win + year_loss
                win_rate = (year_win / total_trades) if total_trades > 0 else 0.0
                
                # Slice equity curve
                slice_curve = []
                for ts, row in year_data.iterrows():
                    slice_curve.append({
                        "time": int(ts.timestamp()) if isinstance(ts, pd.Timestamp) else str(ts),
                        "equity": row['equity']
                    })
                
                # Build test_id
                test_id = f"{args.strategy}_{args.symbol}_{args.timeframe}_{year}"
                strategy_name = args.strategy
                if args.tag:
                    test_id += f"_{args.tag}"
                    strategy_name += f" ({args.tag})"
                
                output = {
                    "test_id": test_id,
                    "strategy": strategy_name,
                    "symbol": args.symbol,
                    "timeframe": args.timeframe,
                    "start": year_start,
                    "end": year_end,
                    "metrics": {
                        "return_pct": round(year_return_pct, 2),
                        "max_drawdown": round(year_max_dd, 2),
                        "total_trades": total_trades,
                        "win_rate": round(win_rate, 2),
                        "equity_curve": slice_curve
                    },
                    "parameters": params
                }
                db.save_test_run(output)
                print(f"  {year}: {year_return_pct:.2f}% Return, {year_max_dd:.2f}% DD, {total_trades} Trades")
        
        print(f"Saved {end_year - start_year + 1} yearly records to database.")
    else:
        # Single year - save as before
        test_id = f"{args.strategy}_{args.symbol}_{args.timeframe}_{start_year}"
        strategy_name = args.strategy
        
        if args.tag:
            test_id += f"_{args.tag}"
            strategy_name += f" ({args.tag})"
        
        output = {
            "test_id": test_id,
            "strategy": strategy_name,
            "symbol": args.symbol,
            "timeframe": args.timeframe,
            "start": args.start,
            "end": args.end,
            "metrics": results,
            "parameters": params
        }
        db.save_test_run(output)
        print(f"Results saved to SQLite Database.")
    
    # Auto-Analysis removed to decouple execution from analysis.

def main():
    parser = argparse.ArgumentParser(description="Gemini Trading Research Engine")
    subparsers = parser.add_subparsers(dest='command', help='Command to run')
    
    # Backtest Command
    bt_parser = subparsers.add_parser('backtest', help='Run a single backtest')
    bt_parser.add_argument('--strategy', type=str, required=True, help='Strategy Name (e.g., Donchian)')
    bt_parser.add_argument('--symbol', type=str, required=True, help='Symbol (e.g., GBPJPY=X)')
    bt_parser.add_argument('--timeframe', type=str, default='1h', help='Timeframe (e.g., 1h, 4h)')
    bt_parser.add_argument('--start', type=str, default='2020-01-01', help='Start Date')
    bt_parser.add_argument('--end', type=str, default='2024-12-31', help='End Date')
    bt_parser.add_argument("--spread", type=float, default=0.0, help="Spread in price units (default 0.0)")
    bt_parser.add_argument("--delay", type=int, default=0, help="Execution Delay (0=Instant, 1=Next Bar)")
    bt_parser.add_argument("--source", type=str, default="csv", choices=["csv", "alpaca"], help="Data Source (csv or alpaca)")
    bt_parser.add_argument("--parameters", type=str, help="JSON string of parameters to override defaults")
    bt_parser.add_argument("--tag", type=str, help="Optional tag to identify this run variation")
    
    # Matrix Command
    matrix_parser = subparsers.add_parser('matrix', help='Run matrix research')
    matrix_parser.add_argument('--strategy', type=str, required=True, help='Strategy Name')
    matrix_parser.add_argument('--pairs', type=str, default='all', help='Comma-separated pairs or "all"')
    matrix_parser.add_argument('--years', type=str, default='2020-2024', help='Year range (e.g. 2020-2024)')
    matrix_parser.add_argument("--spread", type=float, default=0.0, help="Spread in price units (default 0.0)")
    matrix_parser.add_argument("--delay", type=int, default=0, help="Execution Delay (0=Instant, 1=Next Bar)")
    matrix_parser.add_argument("--timeframes", type=str, default="1h,4h", help="Comma-separated timeframes (default 1h,4h)")
    matrix_parser.add_argument("--source", type=str, default="csv", choices=["csv", "alpaca"], help="Data Source (csv or alpaca)")
    matrix_parser.add_argument("--tag", type=str, help="Optional tag to identify this run variation")
    
    # Trade Command (Paper/Live)
    trade_parser = subparsers.add_parser('trade', help='Run live/paper trading')
    trade_parser.add_argument('--strategy', type=str, required=True, help='Strategy Name')
    trade_parser.add_argument('--symbol', type=str, required=True, help='Symbol')
    trade_parser.add_argument('--timeframe', type=str, default='5m', help='Timeframe')
    trade_parser.add_argument('--paper', action='store_true', default=True, help='Use Paper Trading (Default: True)')
    trade_parser.add_argument('--live', action='store_false', dest='paper', help='Use Live Trading')
    trade_parser.add_argument("--parameters", type=str, help="JSON string of parameters")
    
    args = parser.parse_args()
    
    if args.command == 'backtest':
        run_backtest(args)
    elif args.command == 'matrix':
        run_matrix(args)
    elif args.command == 'trade':
        run_live_trading(args)
    else:
        parser.print_help()

def run_live_trading(args):
    import time
    from datetime import datetime
    from backend.engine.alpaca_trader import AlpacaTrader
    from backend.engine.alpaca_loader import AlpacaDataLoader
    
    print(f"--- Starting Live Trading: {args.strategy} on {args.symbol} ({args.timeframe}) ---")
    print(f"Mode: {'PAPER' if args.paper else 'LIVE'}")
    
    # 1. Initialize Components
    broker = AlpacaTrader(paper=args.paper)
    loader = AlpacaDataLoader()
    
    # 2. Configure Strategy
    strategy_class = STRATEGY_MAP.get(args.strategy)
    if not strategy_class:
        print(f"Error: Strategy '{args.strategy}' not found.")
        return
        
    params = {"symbol": args.symbol}
    if args.parameters:
        try:
            params.update(json.loads(args.parameters))
        except:
            print("Error parsing parameters JSON")
            return
            
    # Initialize Strategy (with empty data first)
    # We need a dummy dataframe to init the strategy? 
    # Or we can init with None and feed data later?
    # The strategy __init__ usually expects data.
    # Let's fetch initial history to warm up indicators.
    
    print("Warming up indicators...")
    # Fetch enough data for indicators (e.g. 100 bars)
    # We need to calculate start date based on timeframe
    # Simple approximation: 5 days ago
    start_date = (datetime.now() - pd.Timedelta(days=5)).strftime('%Y-%m-%d')
    end_date = datetime.now().strftime('%Y-%m-%d')
    
    # Handle Timeframe mapping
    fetch_tf = args.timeframe
    if args.timeframe == '5m': fetch_tf = '1m' # We resample
    
    initial_data = loader.fetch_data(args.symbol, fetch_tf, start_date, end_date)
    
    if initial_data is None or initial_data.empty:
        print("Error: Could not fetch warmup data.")
        return
        
    # Resample if needed
    if args.timeframe == '5m':
        ohlc_dict = {'Open': 'first', 'High': 'max', 'Low': 'min', 'Close': 'last', 'Volume': 'sum'}
        initial_data = initial_data.resample('5min').agg(ohlc_dict).dropna()
        
    print(f"Warmup Data: {len(initial_data)} bars")
    
    # Initialize Strategy
    strategy = strategy_class(initial_data, None, params, 100000, broker)
    
    # 3. Live Loop
    print("Entering Live Loop... (Press Ctrl+C to stop)")
    
    last_bar_time = initial_data.index[-1]
    
    try:
        while True:
            # Sleep logic (simple polling)
            # For 5m bars, we can poll every 1 minute to check if a new bar is ready?
            # Or just sleep 60s.
            time.sleep(60)
            
            # Fetch latest data (small window)
            # We fetch last 2 days to be safe and ensure continuity
            now = datetime.now()
            start_fetch = (now - pd.Timedelta(days=2)).strftime('%Y-%m-%d')
            end_fetch = (now + pd.Timedelta(days=1)).strftime('%Y-%m-%d') # Future to get today
            
            latest_data = loader.fetch_data(args.symbol, fetch_tf, start_fetch, end_fetch)
            
            if latest_data is not None and not latest_data.empty:
                # Resample
                if args.timeframe == '5m':
                    ohlc_dict = {'Open': 'first', 'High': 'max', 'Low': 'min', 'Close': 'last', 'Volume': 'sum'}
                    latest_data = latest_data.resample('5min').agg(ohlc_dict).dropna()
                
                # Check for new bar
                current_last_bar_time = latest_data.index[-1]
                
                if current_last_bar_time > last_bar_time:
                    print(f"[{now.strftime('%H:%M:%S')}] New Bar Detected: {current_last_bar_time}")
                    
                    # Get the new bar row
                    new_bar = latest_data.iloc[-1]
                    
                    # Update Strategy Data (Append new bar)
                    # Strategy usually keeps its own data copy or we update it?
                    # Our Strategy class doesn't have an 'update_data' method standard.
                    # But on_bar passes the row.
                    # However, indicators need the full series usually.
                    # We should update strategy.data
                    
                    # Hack: Re-init strategy or append?
                    # Appending to dataframe is slow.
                    # But for 5m bars it's fine.
                    
                    # Better: Pass the FULL latest_data to on_bar?
                    # The strategy.on_bar(row, i, df) takes the dataframe.
                    # So we should update strategy.data first.
                    
                    strategy.data = latest_data
                    
                    # CRITICAL: Re-calculate indicators for the new data
                    # The strategy expects 'k', 'd', 'adx' etc. in the row
                    strategy.generate_signals(strategy.data)
                    
                    # Get the new bar row (now with indicators)
                    new_bar = strategy.data.iloc[-1]
                    
                    # Run Strategy Logic
                    # We use len(latest_data)-1 as the index
                    strategy.on_bar(new_bar, len(latest_data)-1, strategy.data)
                    
                    last_bar_time = current_last_bar_time
                    
                else:
                    # No new bar
                    pass
            
    except KeyboardInterrupt:
        print("\nStopping Live Trading...")

def run_matrix(args):
    import multiprocessing
    from multiprocessing import Pool, cpu_count
    
    print(f"--- Starting Matrix Research: {args.strategy} ---")
    
    # Configuration
    PAIRS = ["GBPJPY=X", "EURJPY=X", "USDJPY=X", "GBPUSD=X", "EURUSD=X", "AUDUSD=X", "USDCAD=X", "USDCHF=X", "NZDUSD=X", "EURGBP=X", "GBPCHF=X"]
    YEARS = range(2020, 2025)
    TIMEFRAMES = args.timeframes.split(',')
    
    # Filter if args provided (simple comma-separated support)
    if args.pairs and args.pairs != 'all':
        PAIRS = args.pairs.split(',')
    if args.years:
        start_y, end_y = map(int, args.years.split('-'))
        YEARS = range(start_y, end_y + 1)
        
    tasks = []
    # Create one task per Pair/Timeframe (covering ALL years)
    from datetime import datetime, timedelta
    
    # Create one task per Pair/Timeframe (covering ALL years)
    for pair in PAIRS:
        for tf in TIMEFRAMES:
            start_year = min(YEARS)
            end_year = max(YEARS)
            
            end_date = f"{end_year}-12-31"
            if end_year == datetime.now().year:
                end_date = (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d')
            
            tasks.append({
                "strategy": args.strategy,
                "symbol": pair,
                "timeframe": tf,
                "start": f"{start_year}-01-01",
                "end": end_date,
                "years_range": list(YEARS),
                "years_range": list(YEARS),
                "spread": args.spread,
                "delay": args.delay,
                "source": args.source
            })
                
    print(f"Total Tasks (Continuous Runs): {len(tasks)}")
    
    # Batch Processing (Memory Safe)
    BATCH_SIZE = 4
    results_buffer = []

    # Resume Logic: Filter out existing tasks
    # Note: With continuous runs, it's harder to check "partial" completion.
    # For now, we'll just run them. If we wanted to be smart, we'd check if ALL years for a pair exist.
    
    if not tasks:
        print("All tasks completed.")
        return
    
    # Run in batches
    for i in range(0, len(tasks), BATCH_SIZE):
        batch = tasks[i:i+BATCH_SIZE]
        print(f"Processing Batch {i//BATCH_SIZE + 1}/{(len(tasks)-1)//BATCH_SIZE + 1}...")
        
        with Pool(processes=min(len(batch), cpu_count())) as pool:
            batch_results_lists = pool.map(worker_task, batch)
            
        # worker_task now returns a LIST of yearly results (or None)
        # Flatten the list of lists
        valid_results = []
        for res_list in batch_results_lists:
            if res_list:
                valid_results.extend(res_list)
        
        results_buffer.extend(valid_results)
        
        # Save Intermediate
        save_results_db(valid_results)
        
    print("Matrix Research Complete.")

def worker_task(task_config):
    try:
        if task_config.get('source') == 'alpaca':
            # Lazy import to avoid circular dep issues in multiprocessing if any
            from backend.engine.alpaca_loader import AlpacaDataLoader
            loader = AlpacaDataLoader()
            # Alpaca fetch_data returns dataframe directly
            # Handle Resampling for unsupported timeframes (e.g. 4h)
            target_tf = task_config['timeframe']
            fetch_tf = target_tf
            
            if target_tf == '4h':
                fetch_tf = '1h'
            elif target_tf in ['5m', '15m']:
                fetch_tf = '1m'
            
            data = loader.fetch_data(task_config['symbol'], fetch_tf, task_config['start'], task_config['end'])
            
            if data is not None and not data.empty and target_tf != fetch_tf:
                ohlc_dict = {'Open': 'first', 'High': 'max', 'Low': 'min', 'Close': 'last', 'Volume': 'sum'}
                # Map timeframe to pandas alias
                resample_tf = target_tf
                if target_tf == '5m': resample_tf = '5min'
                if target_tf == '15m': resample_tf = '15min'
                
                data = data.resample(resample_tf).agg(ohlc_dict).dropna()
        else:
            loader = DataLoader()
            data = None
            
            # Try Target Timeframe
            try:
                data, _ = loader.fetch_ohlcv(task_config['symbol'], task_config['start'], task_config['end'], interval=task_config['timeframe'])
            except Exception:
                pass # Fallback to 1m
        
        if data is None or data.empty:
            # Fallback to 1m
            try:
                data_1m, _ = loader.fetch_ohlcv(task_config['symbol'], task_config['start'], task_config['end'], interval="1m")
                if data_1m is not None and not data_1m.empty:
                    ohlc_dict = {'Open': 'first', 'High': 'max', 'Low': 'min', 'Close': 'last', 'Volume': 'sum'}
                    resample_tf = task_config['timeframe']
                    if resample_tf == '5m': resample_tf = '5min'
                    if resample_tf == '15m': resample_tf = '15min'
                    data = data_1m.resample(resample_tf).agg(ohlc_dict).dropna()
            except Exception:
                pass # Both failed
                
        if data is None or data.empty:
            return None

        # Strategy
        strategy_class = STRATEGY_MAP.get(task_config['strategy'])
        if not strategy_class: return None
        
        # Configure Parameters based on Strategy
        strategy_name = task_config['strategy']
        symbol = task_config['symbol']
        
        if strategy_name == "MACDBollinger":
            params = {
                "symbol": symbol,
                "bb_period": 20,
                "bb_std": 2.0,
                "macd_fast": 12,
                "macd_slow": 26,
                "macd_signal": 9,
                "sl_atr": 2.0,
                "atr_period": 14,
                # Refinement Options (Optimized for GBPJPY)
                "use_trailing_stop": True,
                "trailing_atr_dist": 3.0,
                "use_adx_filter": False,
                "adx_threshold": 25
            }
        elif strategy_name == "DonchianBreakout":
            params = {
                "symbol": symbol,
                "entry_period": 20,
                "exit_period": 10,
                "stop_loss_atr": 2.0,
                "atr_period": 20
            }
        elif strategy_name == "HybridRegime":
            params = {
                "symbol": symbol,
                "adx_period": 14,
                "adx_threshold": 25,
                # StochRSI Params
                "rsi_period": 14,
                "stoch_period": 14,
                "k_period": 3,
                "d_period": 3,
                "overbought": 80,
                "oversold": 20,
                # Donchian Params
                "entry_period": 20,
                "exit_period": 10,
                "stop_loss_atr": 2.0,
                "atr_period": 20
            }
        else:
            params = {
                "symbol": symbol,
                "entry_period": 20,
                "exit_period": 10,
                "stop_loss_atr": 2.0,
                "atr_period": 20
            }
        
        # Run Continuous Backtest
        print(f"DEBUG: Data Shape: {data.shape}")
        if len(data) > 1:
            print(f"DEBUG: Data Frequency: {data.index[1] - data.index[0]}")
            
        backtester = Backtester(
            data, 
            strategy_class, 
            parameters=params, 
            initial_capital=10000.0,
            spread=task_config.get('spread', 0.0),
            execution_delay=task_config.get('delay', 0)
        )
        full_results = backtester.run()
        
        # Post-Process: Split into Yearly Segments
        yearly_outputs = []
        
        # Convert equity curve to DataFrame for easy resampling
        equity_curve = full_results['equity_curve']
        if not equity_curve:
            return None
            
        df_eq = pd.DataFrame(equity_curve)
        # Handle timestamp conversion
        if isinstance(df_eq.iloc[0]['time'], int):
            df_eq['datetime'] = pd.to_datetime(df_eq['time'], unit='s')
        else:
            df_eq['datetime'] = pd.to_datetime(df_eq['time'])
            
        df_eq.set_index('datetime', inplace=True)
        
        # Iterate through requested years
        for year in task_config['years_range']:
            year_start = f"{year}-01-01"
            year_end = f"{year}-12-31"
            
            # Slice the equity curve for this year
            # We include the last point of previous year as "start" if possible for continuity,
            # but for simple stats, just taking the year's data is fine.
            # Actually, to calculate return correctly: (End Equity / Start Equity) - 1
            # Start Equity = Equity at first timestamp of the year (or last of prev year)
            
            year_data = df_eq.loc[year_start:year_end]
            
            if year_data.empty:
                continue
                
            start_equity = year_data.iloc[0]['equity']
            end_equity = year_data.iloc[-1]['equity']
            
            # Calculate Year Return
            year_return_pct = ((end_equity - start_equity) / start_equity) * 100
            
            # Calculate Year Max Drawdown
            # We need to recalculate HWM relative to this year's start?
            # Or just take the drawdown relative to the year's peak?
            # Standard practice: Max DD *within* the period.
            # So we treat year_data as a fresh series.
            
            # Re-calculate DD for this slice
            slice_equity = year_data['equity']
            slice_hwm = slice_equity.cummax()
            slice_dd = (slice_hwm - slice_equity) / slice_hwm
            year_max_dd = slice_dd.max() * 100
            
            # Prepare Metrics
            # Note: win_rate, total_trades etc. would need trade list filtering.
            # For now, we might just estimate or leave them 0 if not critical for Heatmap.
            # The Heatmap primarily uses Return and MaxDD.
            
            # Filter trades for this year
            year_trades = []
            trade_history = full_results.get('trade_history', [])
            
            # Convert trade timestamps to datetime for filtering
            # Assuming trade['timestamp'] is an index or timestamp compatible with our year_start/end
            # The backtester returns 'trade_history' which has 'timestamp' (index)
            # We need to map this index to the datetime index of our data?
            # Or if 'timestamp' is already a datetime/timestamp from the data?
            
            # In our engine, 'timestamp' passed to place_order is usually the index (datetime)
            
            year_win = 0
            year_loss = 0
            
            for trade in trade_history:
                ts_val = trade.get('timestamp')
                # print(f"DEBUG: Trade TS: {ts_val} Type: {type(ts_val)}")
                if ts_val is not None:
                    try:
                        # Case A: Integer Index (Intraday)
                        if isinstance(ts_val, int):
                            idx = int(ts_val)
                            if 0 <= idx < len(backtester.data):
                                ts_dt = backtester.data.index[idx]
                                if str(ts_dt.year) == str(year):
                                    year_trades.append(trade)
                                    if trade['pnl'] > 0: year_win += 1
                                    else: year_loss += 1
                        
                        # Case B: String Date (Daily)
                        elif isinstance(ts_val, str):
                            # ts_val is 'YYYY-MM-DD'
                            trade_year = ts_val.split('-')[0]
                            if str(trade_year) == str(year):
                                year_trades.append(trade)
                                if trade['pnl'] > 0: year_win += 1
                                else: year_loss += 1
                                
                    except Exception as e:
                        pass
            
            total_trades = len(year_trades)
            win_rate = (year_win / total_trades) if total_trades > 0 else 0.0

            # Create the output object
            # Re-convert slice to list of dicts
            slice_curve = []
            for ts, row in year_data.iterrows():
                slice_curve.append({
                    "time": int(ts.timestamp()) if isinstance(ts, pd.Timestamp) else str(ts),
                    "equity": row['equity']
                })

            yearly_outputs.append({
                "test_id": f"{task_config['strategy']}_{task_config['symbol']}_{task_config['timeframe']}_{year}",
                "strategy": task_config['strategy'],
                "symbol": task_config['symbol'],
                "timeframe": task_config['timeframe'],
                "start": year_start,
                "end": year_end,
                "year": year,
                "metrics": {
                    "return_pct": round(year_return_pct, 2),
                    "max_drawdown": round(year_max_dd, 2),
                    "total_trades": total_trades,
                    "win_rate": round(win_rate, 2),
                    "equity_curve": slice_curve
                },
                "parameters": backtester.parameters
            })
            
        return yearly_outputs

    except Exception as e:
        print(f"Task Failed {task_config['symbol']}: {e}")
        import traceback
        traceback.print_exc()
        return None

def save_results_db(new_results):
    db = DatabaseManager()
    # db.initialize_db() # Assumed initialized in main
    
    for res in new_results:
        db.save_test_run(res)
    print(f"Batch saved to DB.")

if __name__ == "__main__":
    main()
