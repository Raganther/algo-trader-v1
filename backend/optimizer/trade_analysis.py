"""Phase 2: Diagnostic trade analysis for edge enhancement.

Runs a single backtest with enriched trade records, then slices
the data by time-of-day, day-of-week, volatility regime, exit reason,
and trade duration to find where the edge leaks.

Usage:
    python -m backend.optimizer.trade_analysis
"""

import pandas as pd
from backend.engine.backtester import Backtester
from backend.engine.data_utils import load_backtest_data
from backend.strategies.stoch_rsi_mean_reversion import StochRSIMeanReversionStrategy

# GLD 15m validated params (Sharpe 1.66)
PARAMS = {
    'symbol': 'GLD',
    'rsi_period': 7,
    'stoch_period': 14,
    'overbought': 80,
    'oversold': 15,
    'adx_threshold': 20,
    'skip_adx_filter': False,
    'sl_atr': 2.0,
    'dynamic_adx': False,
}


def run_diagnostic():
    print("Loading GLD 15m data...")
    data = load_backtest_data('GLD', '15m', '2020-01-01', '2025-06-01')
    print(f"  Bars: {len(data)}")

    print("Running backtest with enriched trade records...")
    bt = Backtester(
        data=data,
        strategy_class=StochRSIMeanReversionStrategy,
        parameters=PARAMS,
        initial_capital=10000.0,
        spread=0.0003,
        execution_delay=0,
        interval='15m',
    )
    results = bt.run()

    trades = results['trade_history']
    print(f"  Total trades: {len(trades)}")
    print(f"  Return: {results['return_pct']:.2f}%")
    print(f"  Win rate: {results['win_rate']:.2f}")
    print(f"  Max DD: {results['max_drawdown']:.2f}%")

    if not trades:
        print("No trades — check parameters.")
        return

    df = pd.DataFrame(trades)

    # Calculate duration in bars
    if 'entry_bar' in df.columns and 'timestamp' in df.columns:
        df['duration_bars'] = df['timestamp'] - df['entry_bar']

    print(f"\n{'='*60}")
    print("TRADE ANALYSIS — GLD 15m StochRSI (Sharpe 1.66 baseline)")
    print(f"{'='*60}")

    # --- 1. Exit Reason ---
    print(f"\n--- EXIT REASON ---")
    if 'exit_reason' in df.columns:
        for reason in df['exit_reason'].unique():
            subset = df[df['exit_reason'] == reason]
            wins = len(subset[subset['pnl'] > 0])
            total = len(subset)
            avg_pnl = subset['pnl'].mean()
            total_pnl = subset['pnl'].sum()
            print(f"  {reason:8s}: {total:4d} trades, win rate {wins/total*100:.1f}%, "
                  f"avg PnL ${avg_pnl:.2f}, total PnL ${total_pnl:.2f}")
    else:
        print("  exit_reason not available")

    # --- 2. Time of Day ---
    print(f"\n--- TIME OF DAY (ET) ---")
    if 'entry_hour' in df.columns:
        df['entry_hour'] = df['entry_hour'].astype(float).astype(int)
        hour_groups = df.groupby('entry_hour')
        print(f"  {'Hour':>4s} | {'Trades':>6s} | {'Win%':>5s} | {'Avg PnL':>8s} | {'Total PnL':>10s}")
        print(f"  {'-'*4} | {'-'*6} | {'-'*5} | {'-'*8} | {'-'*10}")
        for hour, group in sorted(hour_groups):
            wins = len(group[group['pnl'] > 0])
            total = len(group)
            avg_pnl = group['pnl'].mean()
            total_pnl = group['pnl'].sum()
            marker = " ***" if avg_pnl < 0 else " +++" if total >= 20 and wins/total > 0.5 else ""
            print(f"  {int(hour):4d} | {total:6d} | {wins/total*100:5.1f} | ${avg_pnl:8.2f} | ${total_pnl:10.2f}{marker}")
    else:
        print("  entry_hour not available")

    # --- 3. Day of Week ---
    print(f"\n--- DAY OF WEEK ---")
    dow_names = {0: 'Mon', 1: 'Tue', 2: 'Wed', 3: 'Thu', 4: 'Fri'}
    if 'entry_dow' in df.columns:
        df['entry_dow'] = df['entry_dow'].astype(float).astype(int)
        dow_groups = df.groupby('entry_dow')
        print(f"  {'Day':>4s} | {'Trades':>6s} | {'Win%':>5s} | {'Avg PnL':>8s} | {'Total PnL':>10s}")
        print(f"  {'-'*4} | {'-'*6} | {'-'*5} | {'-'*8} | {'-'*10}")
        for dow, group in sorted(dow_groups):
            wins = len(group[group['pnl'] > 0])
            total = len(group)
            avg_pnl = group['pnl'].mean()
            total_pnl = group['pnl'].sum()
            name = dow_names.get(int(dow), str(int(dow)))
            marker = " ***" if avg_pnl < 0 else ""
            print(f"  {name:>4s} | {total:6d} | {wins/total*100:5.1f} | ${avg_pnl:8.2f} | ${total_pnl:10.2f}{marker}")
    else:
        print("  entry_dow not available")

    # --- 4. Volatility Regime (ATR terciles) ---
    print(f"\n--- VOLATILITY REGIME (ATR at entry) ---")
    if 'atr_at_entry' in df.columns:
        df['atr_tercile'] = pd.qcut(df['atr_at_entry'], 3, labels=['Low', 'Medium', 'High'])
        print(f"  {'Regime':>8s} | {'Trades':>6s} | {'Win%':>5s} | {'Avg PnL':>8s} | {'Total PnL':>10s} | {'ATR range':>14s}")
        print(f"  {'-'*8} | {'-'*6} | {'-'*5} | {'-'*8} | {'-'*10} | {'-'*14}")
        for regime in ['Low', 'Medium', 'High']:
            group = df[df['atr_tercile'] == regime]
            if len(group) == 0:
                continue
            wins = len(group[group['pnl'] > 0])
            total = len(group)
            avg_pnl = group['pnl'].mean()
            total_pnl = group['pnl'].sum()
            atr_range = f"${group['atr_at_entry'].min():.2f}-${group['atr_at_entry'].max():.2f}"
            marker = " ***" if avg_pnl < 0 else ""
            print(f"  {regime:>8s} | {total:6d} | {wins/total*100:5.1f} | ${avg_pnl:8.2f} | ${total_pnl:10.2f} | {atr_range:>14s}{marker}")
    else:
        print("  atr_at_entry not available")

    # --- 5. Trade Duration ---
    print(f"\n--- TRADE DURATION (bars) ---")
    if 'duration_bars' in df.columns:
        winners = df[df['pnl'] > 0]
        losers = df[df['pnl'] <= 0]
        print(f"  Winners: avg {winners['duration_bars'].mean():.1f} bars, "
              f"median {winners['duration_bars'].median():.0f}")
        print(f"  Losers:  avg {losers['duration_bars'].mean():.1f} bars, "
              f"median {losers['duration_bars'].median():.0f}")

        # Duration buckets
        bins = [0, 5, 10, 20, 50, 100, float('inf')]
        labels = ['1-5', '6-10', '11-20', '21-50', '51-100', '100+']
        df['duration_bucket'] = pd.cut(df['duration_bars'], bins=bins, labels=labels)
        print(f"\n  {'Bars':>8s} | {'Trades':>6s} | {'Win%':>5s} | {'Avg PnL':>8s} | {'Total PnL':>10s}")
        print(f"  {'-'*8} | {'-'*6} | {'-'*5} | {'-'*8} | {'-'*10}")
        for bucket in labels:
            group = df[df['duration_bucket'] == bucket]
            if len(group) == 0:
                continue
            wins = len(group[group['pnl'] > 0])
            total = len(group)
            avg_pnl = group['pnl'].mean()
            total_pnl = group['pnl'].sum()
            marker = " ***" if avg_pnl < 0 else ""
            print(f"  {bucket:>8s} | {total:6d} | {wins/total*100:5.1f} | ${avg_pnl:8.2f} | ${total_pnl:10.2f}{marker}")
    else:
        print("  duration data not available")

    # --- 6. Direction ---
    print(f"\n--- DIRECTION ---")
    if 'direction' in df.columns:
        for direction in ['long', 'short']:
            group = df[df['direction'] == direction]
            if len(group) == 0:
                continue
            wins = len(group[group['pnl'] > 0])
            total = len(group)
            avg_pnl = group['pnl'].mean()
            total_pnl = group['pnl'].sum()
            print(f"  {direction:>6s}: {total:4d} trades, win rate {wins/total*100:.1f}%, "
                  f"avg PnL ${avg_pnl:.2f}, total PnL ${total_pnl:.2f}")

    # --- Summary ---
    print(f"\n{'='*60}")
    print("FINDINGS SUMMARY")
    print(f"{'='*60}")
    print("Look for:")
    print("  *** = Negative avg PnL (potential dead zone to filter out)")
    print("  +++ = High win rate with decent sample size (golden zone)")
    print("\nDecisions:")
    print("  - Filter out hours/days with *** if sample is large enough (>30 trades)")
    print("  - If stop exits dominate losses, consider trailing stop")
    print("  - If losers last much longer than winners, add time-based exit")
    print("  - If low-vol regime is clearly better, add vol scaling")


if __name__ == '__main__':
    run_diagnostic()
