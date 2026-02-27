"""Validation runner — Feb 27 2026

Runs holdout + walk-forward validation on:
1. SLV 15m enhanced params
2. GDX 15m enhanced params
3. trail_atr comparison: 1.5 vs 2.0 (current) on GLD 15m

Updates experiments table with validation_status = 'passed' or 'failed'.
"""

import sys
import os
import sqlite3
import json
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.strategies.stoch_rsi_mean_reversion import StochRSIMeanReversionStrategy
from backend.optimizer.validation import validate_holdout, walk_forward
from backend.optimizer.experiment_tracker import ExperimentTracker

DB_FILE = "backend/research.db"

# Validated enhanced params
ENHANCED_PARAMS = {
    "rsi_period": 7, "stoch_period": 14, "overbought": 80, "oversold": 15,
    "adx_threshold": 20, "skip_adx_filter": False, "sl_atr": 2.0,
    "trailing_stop": True, "trail_atr": 2.0, "trail_after_bars": 10,
    "min_hold_bars": 10, "skip_days": [0],
}


def get_experiment_id(symbol, timeframe, experiment_id_prefix):
    """Get the DB row id for a focused test run."""
    conn = sqlite3.connect(DB_FILE)
    cur = conn.cursor()
    cur.execute("""
        SELECT id, parameters, sharpe, return_pct FROM experiments
        WHERE symbol=? AND timeframe=? AND experiment_id LIKE ?
        ORDER BY sharpe DESC LIMIT 1
    """, (symbol, timeframe, f"{experiment_id_prefix}%"))
    row = cur.fetchone()
    conn.close()
    return row


def print_holdout(label, result):
    print(f"\n  Holdout ({label}):")
    print(f"    Train (2020-2023): {result['train_return']:.1f}%  Sharpe {result['train_sharpe']:.2f}  Trades {result['train_trades']}")
    print(f"    Test  (2024-2025): {result['test_return']:.1f}%  Sharpe {result['test_sharpe']:.2f}  Trades {result['test_trades']}")


def print_walkforward(result):
    print(f"\n  Walk-forward: {result['pass_count']}/{result['total_windows']} windows positive")
    for w in result["windows"]:
        status = "✓" if w["test_return"] > 0 else "✗"
        print(f"    {status} Test {w['test_period']}: {w['test_return']:.1f}%  Sharpe {w['test_sharpe']:.2f}  Trades {w['test_trades']}")


def validate_asset(symbol, timeframe, params, tracker):
    print(f"\n{'='*60}")
    print(f"VALIDATING: {symbol} {timeframe}")
    print(f"{'='*60}")

    holdout = validate_holdout(StochRSIMeanReversionStrategy, params, symbol, timeframe)
    wf = walk_forward(StochRSIMeanReversionStrategy, params, symbol, timeframe)

    print_holdout(symbol, holdout)
    print_walkforward(wf)

    # Pass criteria: test period positive + walk-forward >= 3/4 windows positive
    holdout_pass = holdout["test_return"] > 0
    wf_pass = wf["pass_count"] >= 3

    passed = holdout_pass and wf_pass
    status = "passed" if passed else "failed"
    verdict = "PASSED ✓" if passed else "FAILED ✗"

    print(f"\n  Verdict: {verdict}")
    print(f"    Holdout test positive: {'Yes' if holdout_pass else 'No'}")
    print(f"    Walk-forward >= 3/4:   {'Yes' if wf_pass else 'No'}")

    # Update DB
    row = get_experiment_id(symbol, timeframe, "focused_enhanced")
    if row:
        tracker.update_validation(
            row_id=row[0],
            validation_status=status,
            test_return_pct=holdout["test_return"],
            validation_details={
                "holdout": holdout,
                "walk_forward": {"pass_count": wf["pass_count"], "total": wf["total_windows"],
                                 "avg_test_return": wf["avg_test_return"]},
            }
        )
        print(f"  DB updated: row {row[0]} → {status}")
    else:
        print("  Warning: no matching DB row found to update")

    return passed, holdout, wf


def validate_trail_atr_comparison(tracker):
    """Compare trail_atr=1.5 vs 2.0 on holdout period only."""
    print(f"\n{'='*60}")
    print(f"TRAIL ATR COMPARISON: GLD 15m — 1.5 vs 2.0 on holdout (2024-2025)")
    print(f"{'='*60}")

    for trail_val in [1.5, 2.0]:
        params = {**ENHANCED_PARAMS, "trail_atr": trail_val}
        result = validate_holdout(StochRSIMeanReversionStrategy, params, "GLD", "15m")
        print(f"\n  trail_atr={trail_val}:")
        print(f"    Train (2020-2023): {result['train_return']:.1f}%  Sharpe {result['train_sharpe']:.2f}")
        print(f"    Test  (2024-2025): {result['test_return']:.1f}%  Sharpe {result['test_sharpe']:.2f}")

    # Update the best trail_atr=1.5 row to passed if it beats 2.0 on test
    params_15 = {**ENHANCED_PARAMS, "trail_atr": 1.5}
    params_20 = {**ENHANCED_PARAMS, "trail_atr": 2.0}

    r15 = validate_holdout(StochRSIMeanReversionStrategy, params_15, "GLD", "15m")
    r20 = validate_holdout(StochRSIMeanReversionStrategy, params_20, "GLD", "15m")

    if r15["test_return"] > r20["test_return"]:
        print(f"\n  trail_atr=1.5 wins on holdout ({r15['test_return']:.1f}% vs {r20['test_return']:.1f}%)")
        print(f"  Recommendation: update validated params to trail_atr=1.5")
    else:
        print(f"\n  trail_atr=2.0 holds on holdout ({r20['test_return']:.1f}% vs {r15['test_return']:.1f}%)")
        print(f"  Recommendation: keep validated params at trail_atr=2.0")


if __name__ == "__main__":
    tracker = ExperimentTracker()

    print("=" * 60)
    print("VALIDATION RUNNER")
    print("Checking SLV 15m, GDX 15m, and trail_atr comparison")
    print("=" * 60)

    # 1. Validate precious metals expansion
    slv_passed, slv_holdout, slv_wf = validate_asset("SLV", "15m", ENHANCED_PARAMS, tracker)
    gdx_passed, gdx_holdout, gdx_wf = validate_asset("GDX", "15m", ENHANCED_PARAMS, tracker)

    # 2. trail_atr comparison
    validate_trail_atr_comparison(tracker)

    # Final summary
    print(f"\n{'='*60}")
    print("SUMMARY")
    print(f"{'='*60}")
    print(f"  SLV 15m: {'PASSED ✓' if slv_passed else 'FAILED ✗'}")
    print(f"  GDX 15m: {'PASSED ✓' if gdx_passed else 'FAILED ✗'}")
    print(f"{'='*60}")
