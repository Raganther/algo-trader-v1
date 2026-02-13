"""Phase 4: A/B sweep of edge enhancements vs baseline.

Tests each enhancement independently against the GLD 15m Sharpe 1.66 baseline,
then tests the best combinations.

Usage:
    python -m backend.optimizer.enhancement_sweep
"""

import sys
import os
import io
from contextlib import contextmanager
from backend.engine.backtester import Backtester
from backend.engine.data_utils import load_backtest_data
from backend.strategies.stoch_rsi_mean_reversion import StochRSIMeanReversionStrategy
from backend.optimizer.scoring import calc_sharpe

# GLD 15m validated baseline params
BASELINE = {
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


@contextmanager
def suppress_stdout():
    """Suppress print output during backtests."""
    old_stdout = sys.stdout
    sys.stdout = io.StringIO()
    try:
        yield
    finally:
        sys.stdout = old_stdout


def run_backtest(data, params):
    """Run single backtest with suppressed output, return results + Sharpe."""
    with suppress_stdout():
        bt = Backtester(
            data=data,
            strategy_class=StochRSIMeanReversionStrategy,
            parameters=params,
            initial_capital=10000.0,
            spread=0.0003,
            execution_delay=0,
            interval='15m',
        )
        results = bt.run()

    # Calculate Sharpe from equity curve
    equity_curve = results.get('equity_curve', [])
    sharpe = calc_sharpe(equity_curve) if equity_curve else 0.0

    return {
        'return_pct': results['return_pct'],
        'sharpe': sharpe,
        'total_trades': results['total_trades'],
        'win_rate': results['win_rate'],
        'max_drawdown': results['max_drawdown'],
        'profit_factor': results['profit_factor'],
    }


def print_result(label, r, baseline_sharpe=None):
    """Print a single result row."""
    delta = ""
    if baseline_sharpe is not None:
        diff = r['sharpe'] - baseline_sharpe
        delta = f"  ({'+' if diff >= 0 else ''}{diff:.3f})"
    print(f"  {label:<45s} Sharpe {r['sharpe']:.3f}{delta}  "
          f"Ret {r['return_pct']:6.1f}%  Trades {r['total_trades']:4d}  "
          f"WR {r['win_rate']*100:5.1f}%  DD {r['max_drawdown']:5.2f}%  "
          f"PF {r['profit_factor']:.2f}")


def main():
    print("Loading GLD 15m data...")
    data = load_backtest_data('GLD', '15m', '2020-01-01', '2025-06-01')
    print(f"  Bars: {len(data)}")

    # --- Baseline ---
    print("\nRunning baseline...")
    baseline = run_backtest(data, BASELINE)
    bs = baseline['sharpe']
    print(f"\n{'='*110}")
    print(f"BASELINE")
    print(f"{'='*110}")
    print_result("GLD 15m StochRSI (validated)", baseline)

    # --- Enhancement 1: Monday Filter ---
    print(f"\n{'='*110}")
    print("ENHANCEMENT 1: DAY-OF-WEEK FILTER")
    print(f"{'='*110}")
    day_variants = [
        ("Skip Monday", {'skip_days': [0]}),
        ("Skip Friday", {'skip_days': [4]}),
        ("Skip Mon+Fri", {'skip_days': [0, 4]}),
    ]
    for label, overrides in day_variants:
        params = {**BASELINE, **overrides}
        r = run_backtest(data, params)
        print_result(label, r, bs)

    # --- Enhancement 2: Trailing Stop ---
    print(f"\n{'='*110}")
    print("ENHANCEMENT 2: TRAILING STOP")
    print(f"{'='*110}")
    trail_variants = [
        ("Trail 2x ATR after 3 bars", {'trailing_stop': True, 'trail_after_bars': 3, 'trail_atr': 2.0}),
        ("Trail 2x ATR after 5 bars", {'trailing_stop': True, 'trail_after_bars': 5, 'trail_atr': 2.0}),
        ("Trail 2x ATR after 10 bars", {'trailing_stop': True, 'trail_after_bars': 10, 'trail_atr': 2.0}),
        ("Trail 1.5x ATR after 5 bars", {'trailing_stop': True, 'trail_after_bars': 5, 'trail_atr': 1.5}),
        ("Trail 3x ATR after 5 bars", {'trailing_stop': True, 'trail_after_bars': 5, 'trail_atr': 3.0}),
        ("Trail 2x ATR after 20 bars", {'trailing_stop': True, 'trail_after_bars': 20, 'trail_atr': 2.0}),
    ]
    for label, overrides in trail_variants:
        params = {**BASELINE, **overrides}
        r = run_backtest(data, params)
        print_result(label, r, bs)

    # --- Enhancement 3: Minimum Hold Period ---
    print(f"\n{'='*110}")
    print("ENHANCEMENT 3: MINIMUM HOLD BARS")
    print(f"{'='*110}")
    hold_variants = [
        ("Min hold 3 bars", {'min_hold_bars': 3}),
        ("Min hold 5 bars", {'min_hold_bars': 5}),
        ("Min hold 10 bars", {'min_hold_bars': 10}),
        ("Min hold 20 bars", {'min_hold_bars': 20}),
    ]
    for label, overrides in hold_variants:
        params = {**BASELINE, **overrides}
        r = run_backtest(data, params)
        print_result(label, r, bs)

    # --- Combinations of winners ---
    print(f"\n{'='*110}")
    print("COMBINATIONS (best from each category)")
    print(f"{'='*110}")
    combo_variants = [
        ("Skip Mon + Trail 2x/5bar", {
            'skip_days': [0], 'trailing_stop': True, 'trail_after_bars': 5, 'trail_atr': 2.0}),
        ("Skip Mon + Min hold 5", {
            'skip_days': [0], 'min_hold_bars': 5}),
        ("Trail 2x/5bar + Min hold 5", {
            'trailing_stop': True, 'trail_after_bars': 5, 'trail_atr': 2.0, 'min_hold_bars': 5}),
        ("All three: Skip Mon + Trail 2x/5bar + Hold 5", {
            'skip_days': [0], 'trailing_stop': True, 'trail_after_bars': 5, 'trail_atr': 2.0, 'min_hold_bars': 5}),
        ("Skip Mon + Trail 2x/10bar + Hold 10", {
            'skip_days': [0], 'trailing_stop': True, 'trail_after_bars': 10, 'trail_atr': 2.0, 'min_hold_bars': 10}),
    ]
    for label, overrides in combo_variants:
        params = {**BASELINE, **overrides}
        r = run_backtest(data, params)
        print_result(label, r, bs)

    print(f"\n{'='*110}")
    print("DONE — Compare Sharpe deltas to baseline. Positive = improvement.")
    print(f"{'='*110}")


if __name__ == '__main__':
    main()
