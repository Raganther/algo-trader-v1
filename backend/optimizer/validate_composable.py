"""Validate top composable strategy candidates through Phase 2 pipeline.

Maps stored block names back to callables and runs:
1. Disqualification (hard filters)
2. Train/test holdout (2020-2023 train, 2024-2025 test)
3. Walk-forward (rolling 2-year train, 1-year test)
4. Multi-asset consistency (related assets)

Usage:
    python -m backend.optimizer.validate_composable
    python -m backend.optimizer.validate_composable --top 10
"""

import argparse
import sqlite3
import json

from backend.optimizer.composable_strategy import ComposableStrategy
from backend.optimizer.pipeline import validate_candidate
from backend.optimizer.experiment_tracker import ExperimentTracker
from backend.optimizer import building_blocks as bb


# Map stored block names back to callables
ENTRY_MAP = {
    "stochrsi_cross(os=20,ob=80)": bb.stochrsi_cross(oversold=20, overbought=80),
    "stochrsi_cross(os=15,ob=85)": bb.stochrsi_cross(oversold=15, overbought=85),
    "macd_cross": bb.macd_cross(),
    "bollinger_bounce": bb.bollinger_bounce(),
    "donchian_breakout": bb.donchian_breakout(),
    "rsi_extreme(os=30,ob=70)": bb.rsi_extreme(oversold=30, overbought=70),
    "sma_cross(50/200)": bb.sma_cross(),
}

EXIT_MAP = {
    "opposite_zone(os=20,ob=80)": bb.opposite_zone(oversold=20, overbought=80),
    "atr_stop(2.0x)": bb.atr_stop(multiplier=2.0),
    "atr_stop(3.0x)": bb.atr_stop(multiplier=3.0),
    "bollinger_exit": bb.bollinger_exit(),
    "donchian_exit": bb.donchian_exit(),
    "trailing_atr(2.0x)": bb.trailing_atr(multiplier=2.0),
    "trailing_atr(3.0x)": bb.trailing_atr(multiplier=3.0),
}

FILTER_MAP = {
    "no_filter": bb.no_filter(),
    "adx_ranging(<25)": bb.adx_ranging(threshold=25),
    "adx_trending(>25)": bb.adx_trending(threshold=25),
    "chop_trending(<38.2)": bb.chop_trending(),
    "chop_ranging(>61.8)": bb.chop_ranging(),
    "sma_uptrend": bb.sma_uptrend(),
}

SIZER_MAP = {
    "fixed_pct(25%)": bb.fixed_pct(0.25),
    "risk_atr(2%,2.0x)": bb.risk_atr(risk_pct=0.02, atr_mult=2.0),
    "risk_atr(2%,3.0x)": bb.risk_atr(risk_pct=0.02, atr_mult=3.0),
}


def rebuild_params(stored_params, symbol):
    """Reconstruct callable params from stored string names."""
    entry_fn = ENTRY_MAP.get(stored_params["entry"])
    exit_fn = EXIT_MAP.get(stored_params["exit"])
    filter_fn = FILTER_MAP.get(stored_params["filter"])
    sizer_fn = SIZER_MAP.get(stored_params.get("sizer", "fixed_pct(25%)"))

    if not entry_fn or not exit_fn:
        return None

    return {
        "symbol": symbol,
        "entry_fn": entry_fn,
        "exit_fn": exit_fn,
        "filter_fn": filter_fn,
        "sizer_fn": sizer_fn,
        "_entry_name": stored_params["entry"],
        "_exit_name": stored_params["exit"],
        "_filter_name": stored_params["filter"],
        "_sizer_name": stored_params.get("sizer", "fixed_pct(25%)"),
    }


def get_top_composable(n=10, min_trades=10):
    """Get top unique composable combos from DB (deduped by entry+exit+filter)."""
    conn = sqlite3.connect("backend/research.db")
    conn.row_factory = sqlite3.Row
    rows = conn.execute('''
        SELECT id, parameters, symbol, timeframe, return_pct, sharpe,
               total_trades, max_drawdown, validation_status
        FROM experiments
        WHERE strategy_source = 'composable'
          AND sharpe > 0
          AND total_trades >= ?
        ORDER BY sharpe DESC
    ''', (min_trades,)).fetchall()
    conn.close()

    # Deduplicate by entry+exit+filter (sizer doesn't affect results)
    seen = set()
    unique = []
    for row in rows:
        params = json.loads(row["parameters"])
        key = f"{params['entry']}|{params['exit']}|{params['filter']}"
        if key in seen:
            continue
        seen.add(key)
        unique.append(dict(row))
        if len(unique) >= n:
            break

    return unique


def run_validation(n=10, min_trades=10):
    """Validate top composable candidates."""
    tracker = ExperimentTracker()
    candidates = get_top_composable(n=n, min_trades=min_trades)

    print(f"Found {len(candidates)} unique composable candidates to validate\n")

    results = []

    for i, exp in enumerate(candidates):
        params = json.loads(exp["parameters"])
        symbol = exp["symbol"]
        timeframe = exp["timeframe"]
        label = f"{params['entry']} + {params['exit']} + {params['filter']}"

        # Skip already validated
        if exp.get("validation_status") not in (None, "", "pending"):
            print(f"[{i+1}/{len(candidates)}] Skipping (already {exp['validation_status']}): {label}")
            continue

        print(f"[{i+1}/{len(candidates)}] Validating: {label}")
        print(f"  Sweep: Sharpe {exp['sharpe']:.3f}, {exp['return_pct']:+.1f}%, "
              f"{exp['total_trades']} trades, DD {exp['max_drawdown']:.1f}%")

        # Rebuild callable params
        full_params = rebuild_params(params, symbol)
        if not full_params:
            print(f"  SKIP: could not rebuild params")
            continue

        # Run validation
        validation = validate_candidate(
            ComposableStrategy, full_params, symbol, timeframe, verbose=True
        )

        # Update DB
        test_return = None
        if "holdout" in validation and "test_return" in validation["holdout"]:
            test_return = validation["holdout"]["test_return"]

        details = {}
        if "holdout" in validation:
            details["holdout_degradation"] = validation["holdout"].get("degradation")
        if "walk_forward" in validation:
            details["walk_forward_pass_rate"] = validation["walk_forward"].get("pass_rate")
            details["avg_test_return"] = validation["walk_forward"].get("avg_test_return")
        if "multi_asset" in validation:
            details["multi_asset_positive_rate"] = validation["multi_asset"].get("positive_rate")
        if "reason" in validation:
            details["rejection_reason"] = validation["reason"]

        tracker.update_validation(
            row_id=exp["id"],
            validation_status=validation["status"].lower(),
            test_return_pct=test_return,
            validation_details=details,
        )

        results.append((exp, validation))
        print()

    # Summary
    print(f"\n{'='*60}")
    print("COMPOSABLE VALIDATION SUMMARY")
    print(f"{'='*60}")
    passed = sum(1 for _, v in results if v["status"] == "PASSED")
    marginal = sum(1 for _, v in results if v["status"] == "MARGINAL")
    rejected = sum(1 for _, v in results if v["status"] == "REJECTED")
    print(f"Passed: {passed}  Marginal: {marginal}  Rejected: {rejected}")

    for exp, val in results:
        params = json.loads(exp["parameters"])
        label = f"{params['entry']} + {params['exit']} + {params['filter']}"
        holdout = val.get("holdout", {})
        wf = val.get("walk_forward", {})
        print(f"  [{val['status']}] {label}")
        if holdout:
            print(f"    Holdout: train {holdout.get('train_return', 'N/A'):.1f}%, "
                  f"test {holdout.get('test_return', 'N/A'):.1f}%")
        if wf:
            print(f"    Walk-forward: {wf.get('pass_rate', 0)*100:.0f}% pass rate")

    return results


def main():
    parser = argparse.ArgumentParser(description="Validate top composable strategies")
    parser.add_argument("--top", type=int, default=10, help="Number of unique combos to validate")
    parser.add_argument("--min-trades", type=int, default=10, help="Min trades filter")
    args = parser.parse_args()

    run_validation(n=args.top, min_trades=args.min_trades)


if __name__ == "__main__":
    main()
