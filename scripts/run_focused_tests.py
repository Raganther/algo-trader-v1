"""Focused test runner — Feb 27 2026

Two test batches:

1. Precious metals thesis expansion
   Run StochRSI Enhanced params on SLV, IAU, GDX at 15m.
   Existing DB runs used baseline params (no trailing stop / min hold).
   This tests whether the enhancement transfers to correlated assets.

2. trail_atr sweep on GLD 15m
   Audit found trail_atr=1.5 showed +47.5% vs +43.0% baseline.
   Sweep 1.0 -> 2.5 in steps of 0.25 to find the true optimum.

Results saved to experiments table via ExperimentTracker.
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.strategies.stoch_rsi_mean_reversion import StochRSIMeanReversionStrategy as StochRSIMeanReversion
from backend.optimizer.sweep import SweepEngine
from backend.optimizer.experiment_tracker import ExperimentTracker

START = "2020-01-01"
END   = "2025-12-31"

# Validated enhanced params (GLD 15m baseline — these are the params we're testing on new assets)
ENHANCED_BASE = {
    "rsi_period":      [7],
    "stoch_period":    [14],
    "overbought":      [80],
    "oversold":        [15],
    "adx_threshold":   [20],
    "skip_adx_filter": [False],
    "sl_atr":          [2.0],
    "trailing_stop":   [True],
    "trail_atr":       [2.0],
    "trail_after_bars":[10],
    "min_hold_bars":   [10],
    "skip_days":       [[0]],
}


def run_precious_metals_expansion(engine):
    """Test enhanced params on SLV, IAU, GDX at 15m."""
    targets = ["SLV", "IAU", "GDX"]

    for symbol in targets:
        print(f"\n{'='*60}")
        print(f"PRECIOUS METALS EXPANSION: {symbol} 15m (enhanced params)")
        print(f"{'='*60}")
        results = engine.run_sweep(
            strategy_class=StochRSIMeanReversion,
            param_grid=ENHANCED_BASE,
            symbol=symbol,
            timeframe="15m",
            start=START,
            end=END,
            experiment_id=f"focused_enhanced_{symbol}_15m",
            skip_tested=True,
        )
        if results:
            r = results[0]
            print(f"\nResult: Return={r['return_pct']:.1f}%  "
                  f"Sharpe={r['sharpe']:.2f}  "
                  f"DD={r['max_drawdown']:.2f}%  "
                  f"Trades={r['total_trades']}")
        else:
            print("  (already tested or no data)")


def run_trail_atr_sweep(engine):
    """Sweep trail_atr from 1.0 to 2.5 on GLD 15m."""
    print(f"\n{'='*60}")
    print(f"TRAIL ATR SWEEP: GLD 15m (trail_atr 1.0 -> 2.5)")
    print(f"{'='*60}")

    sweep_grid = {**ENHANCED_BASE, "trail_atr": [1.0, 1.25, 1.5, 1.75, 2.0, 2.25, 2.5]}

    results = engine.run_sweep(
        strategy_class=StochRSIMeanReversion,
        param_grid=sweep_grid,
        symbol="GLD",
        timeframe="15m",
        start=START,
        end=END,
        experiment_id="focused_trail_atr_sweep_GLD_15m",
        skip_tested=False,  # Re-run even if some combos exist — fresh comparison
    )

    if results:
        print(f"\ntrail_atr results (sorted by Sharpe):")
        print(f"{'trail_atr':<12} {'Return%':<10} {'Sharpe':<10} {'DD%':<10} {'Trades':<8}")
        print("-" * 50)
        sorted_results = sorted(results, key=lambda x: x["params"].get("trail_atr", 0))
        for r in sorted_results:
            ta = r["params"].get("trail_atr", "?")
            print(f"{ta:<12} {r['return_pct']:<10.1f} {r['sharpe']:<10.2f} "
                  f"{r['max_drawdown']:<10.2f} {r['total_trades']:<8}")


if __name__ == "__main__":
    tracker = ExperimentTracker()
    engine = SweepEngine(tracker=tracker)

    print("=" * 60)
    print("FOCUSED TEST RUNNER")
    print("Batch 1: Precious metals expansion (SLV, IAU, GDX @ 15m)")
    print("Batch 2: trail_atr sweep (GLD 15m, 1.0 -> 2.5)")
    print("=" * 60)

    run_precious_metals_expansion(engine)
    run_trail_atr_sweep(engine)

    print(f"\n{'='*60}")
    print("All tests complete. Results saved to experiments DB.")
    print("Check dashboard or query: SELECT symbol, sharpe, return_pct FROM experiments")
    print(f"  WHERE experiment_id LIKE 'focused_%' ORDER BY sharpe DESC;")
    print(f"{'='*60}")
