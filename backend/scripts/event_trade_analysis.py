"""
Event Trade Analysis — Diagnostic script to determine if economic event blackouts help.

Tags each trade from the GLD 15m StochRSI Enhanced backtest as:
  - "event" = entry occurred within N hours of a high-impact USD event
  - "clean" = no nearby event

Compares performance (win rate, avg PnL, total PnL) for event vs clean trades
across multiple buffer windows (1h, 2h, 4h).

Usage:
    python -m backend.scripts.event_trade_analysis
"""

import pandas as pd
import numpy as np
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from backend.engine.data_loader import DataLoader
from backend.engine.alpaca_loader import AlpacaDataLoader
from backend.engine.backtester import Backtester
from backend.strategies.stoch_rsi_mean_reversion import StochRSIMeanReversionStrategy


def run_analysis():
    # --- Config ---
    symbol = 'GLD'
    timeframe = '15m'
    start = '2020-01-01'
    end = '2025-12-31'
    buffer_hours_list = [1, 2, 4, 6]

    # Enhanced params (validated best edge — Sharpe 2.42)
    params = {
        'symbol': symbol,
        'rsi_period': 7,
        'stoch_period': 14,
        'overbought': 80,
        'oversold': 15,
        'adx_threshold': 20,
        'sl_atr': 2.0,
        'trailing_stop': True,
        'trail_atr': 2.0,
        'trail_after_bars': 10,
        'min_hold_bars': 10,
        'skip_days': [0],  # Skip Monday
    }

    # --- Load Data ---
    print("Loading GLD 15m data from Alpaca...")
    alpaca_loader = AlpacaDataLoader()
    # Alpaca doesn't support 15m directly — fetch 1m and resample
    raw_data = alpaca_loader.fetch_data(symbol, '1m', start, end)
    if raw_data is None or raw_data.empty:
        print("ERROR: No data returned from Alpaca")
        return
    ohlc_dict = {'Open': 'first', 'High': 'max', 'Low': 'min', 'Close': 'last', 'Volume': 'sum'}
    data = raw_data.resample('15min').agg(ohlc_dict).dropna()
    print(f"  Loaded {len(data)} bars ({data.index[0]} to {data.index[-1]})")
    loader = DataLoader()  # for event loading

    # --- Load Events ---
    print("Loading high-impact USD event times...")
    event_times = loader.get_event_blackout_times(start, end, currency='USD')
    event_times_sorted = sorted(event_times)
    print(f"  {len(event_times_sorted)} events found")

    # Show sample events
    if event_times_sorted:
        print(f"  Sample: {event_times_sorted[:5]}")

    # --- Run Backtest (suppress per-bar output) ---
    print("\nRunning backtest...")
    import io, contextlib
    backtester = Backtester(
        data,
        StochRSIMeanReversionStrategy,
        parameters=params,
        initial_capital=10000.0,
        spread=0.0003,
        execution_delay=0,
    )
    with contextlib.redirect_stdout(io.StringIO()):
        results = backtester.run()
    trades = results.get('trade_history', [])
    print(f"  {len(trades)} trades completed")
    print(f"  Return: {results['return_pct']}%, Max DD: {results['max_drawdown']}%")

    if not trades:
        print("No trades to analyse.")
        return

    # --- Resolve trade timestamps to datetimes (all tz-naive for comparison) ---
    trade_datetimes = []
    for trade in trades:
        ts = trade.get('timestamp')
        if ts is not None:
            if isinstance(ts, int) and 0 <= ts < len(data):
                dt = data.index[ts]
                trade_datetimes.append(dt.tz_localize(None) if dt.tzinfo else dt)
            elif isinstance(ts, str):
                dt = pd.Timestamp(ts)
                trade_datetimes.append(dt.tz_localize(None) if dt.tzinfo else dt)
            elif isinstance(ts, pd.Timestamp):
                trade_datetimes.append(ts.tz_localize(None) if ts.tzinfo else ts)
            else:
                trade_datetimes.append(None)
        else:
            trade_datetimes.append(None)

    # --- Analyse by buffer window ---
    # Event times are already tz-naive from get_event_blackout_times
    event_times_list = sorted(event_times)

    print("\n" + "=" * 80)
    print("EVENT TRADE ANALYSIS — GLD 15m StochRSI Enhanced")
    print("=" * 80)

    for buffer_hours in buffer_hours_list:
        buffer_td = pd.Timedelta(hours=buffer_hours)

        event_trades = []
        clean_trades = []

        for trade, dt in zip(trades, trade_datetimes):
            if dt is None:
                continue

            # Check if this trade's entry is within buffer_hours of any event
            near_event = False
            if event_times_list:
                # Binary search for closest event
                import bisect
                idx = bisect.bisect_left(event_times_list, dt)
                for check_idx in [idx - 1, idx]:
                    if 0 <= check_idx < len(event_times_list):
                        diff = abs(dt - event_times_list[check_idx])
                        if diff <= buffer_td:
                            near_event = True
                            break

            if near_event:
                event_trades.append(trade)
            else:
                clean_trades.append(trade)

        # --- Calculate stats ---
        def calc_stats(trade_list, label):
            if not trade_list:
                return {'label': label, 'count': 0, 'total_pnl': 0, 'avg_pnl': 0,
                        'win_rate': 0, 'avg_win': 0, 'avg_loss': 0}

            pnls = [t['pnl'] for t in trade_list]
            wins = [p for p in pnls if p > 0]
            losses = [p for p in pnls if p <= 0]

            return {
                'label': label,
                'count': len(pnls),
                'total_pnl': round(sum(pnls), 2),
                'avg_pnl': round(np.mean(pnls), 2),
                'win_rate': round(len(wins) / len(pnls) * 100, 1),
                'avg_win': round(np.mean(wins), 2) if wins else 0,
                'avg_loss': round(np.mean(losses), 2) if losses else 0,
            }

        event_stats = calc_stats(event_trades, f"Event (±{buffer_hours}h)")
        clean_stats = calc_stats(clean_trades, "Clean")

        print(f"\n--- Buffer: ±{buffer_hours} hours ---")
        print(f"{'Metric':<20} {'Event trades':<20} {'Clean trades':<20} {'Diff':<15}")
        print("-" * 75)

        for metric in ['count', 'total_pnl', 'avg_pnl', 'win_rate', 'avg_win', 'avg_loss']:
            ev = event_stats[metric]
            cl = clean_stats[metric]
            diff = cl - ev if isinstance(ev, (int, float)) else ''
            unit = '%' if metric == 'win_rate' else ''
            prefix = '$' if metric in ['total_pnl', 'avg_pnl', 'avg_win', 'avg_loss'] else ''
            print(f"  {metric:<18} {prefix}{ev}{unit:<18} {prefix}{cl}{unit:<18} {prefix}{diff}{unit}")

    # --- Summary recommendation ---
    print("\n" + "=" * 80)
    print("RECOMMENDATION")
    print("=" * 80)
    print("If event trades show significantly worse avg PnL or win rate,")
    print("implement event_blackout_hours in the strategy.")
    print("If similar or better, the blackout filter is not needed.\n")


if __name__ == '__main__':
    run_analysis()
