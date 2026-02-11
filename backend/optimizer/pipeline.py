"""Full validation pipeline.

Chains: disqualification → holdout → walk-forward → multi-asset.
Updates the experiments table with validation results.
"""

import json

from backend.optimizer.disqualify import passes_disqualification
from backend.optimizer.validation import validate_holdout, walk_forward, multi_asset_check
from backend.optimizer.experiment_tracker import ExperimentTracker

# Strategy class lookup
from backend.strategies.stoch_rsi_mean_reversion import StochRSIMeanReversionStrategy
from backend.strategies.donchian_breakout import DonchianBreakoutStrategy
from backend.strategies.macd_bollinger import MACDBollingerStrategy
from backend.strategies.regime_gated_stoch import RegimeGatedStoch
from backend.strategies.swing_breakout import SwingBreakoutStrategy

STRATEGY_CLASS_MAP = {
    "StochRSIMeanReversionStrategy": StochRSIMeanReversionStrategy,
    "DonchianBreakoutStrategy": DonchianBreakoutStrategy,
    "MACDBollingerStrategy": MACDBollingerStrategy,
    "RegimeGatedStoch": RegimeGatedStoch,
    "SwingBreakoutStrategy": SwingBreakoutStrategy,
}


def validate_candidate(strategy_class, params, symbol, timeframe, verbose=True):
    """Full validation pipeline for a single candidate.

    Steps:
        1. Disqualification (hard filters)
        2. Train/test holdout (2020-2023 train, 2024-2025 test)
        3. Walk-forward (rolling 2-year train, 1-year test)
        4. Multi-asset consistency (related assets)

    Returns:
        dict with status, details, and all sub-results
    """
    label = f"{strategy_class.__name__} on {symbol} {timeframe}"

    if verbose:
        print(f"\nValidating: {label}")
        print(f"  Params: {params}")

    # Step 1: Disqualification — run full-period backtest
    if verbose:
        print("  Step 1: Disqualification check...")

    from backend.engine.data_utils import load_backtest_data
    from backend.engine.backtester import Backtester
    from backend.optimizer.scoring import calc_sharpe
    import sys, os
    from contextlib import contextmanager

    @contextmanager
    def _suppress():
        old = sys.stdout
        sys.stdout = open(os.devnull, "w")
        try:
            yield
        finally:
            sys.stdout.close()
            sys.stdout = old

    full_params = {**params, "symbol": symbol}
    full_data = load_backtest_data(symbol, timeframe, "2020-01-01", "2025-12-31")
    if full_data.empty:
        return {"status": "REJECTED", "reason": "no_data"}

    with _suppress():
        bt = Backtester(full_data, strategy_class, full_params,
                        10000.0, 0.0003, execution_delay=0, interval=timeframe)
        full_result = bt.run()

    passes, reason = passes_disqualification(full_result, years=5)
    if not passes:
        if verbose:
            print(f"  REJECTED: {reason}")
        return {"status": "REJECTED", "reason": reason}

    if verbose:
        print(f"  Passed. {full_result['total_trades']} trades, "
              f"{full_result['return_pct']:.2f}% return, "
              f"{full_result['max_drawdown']:.1f}% dd")

    # Step 2: Train/test holdout
    if verbose:
        print("  Step 2: Holdout test (train 2020-2023, test 2024-2025)...")

    holdout = validate_holdout(strategy_class, params, symbol, timeframe)
    if "error" in holdout:
        return {"status": "REJECTED", "reason": f"holdout_error: {holdout['error']}"}

    if verbose:
        print(f"  Train: {holdout['train_return']:.2f}% (Sharpe {holdout['train_sharpe']:.3f})")
        print(f"  Test:  {holdout['test_return']:.2f}% (Sharpe {holdout['test_sharpe']:.3f})")
        print(f"  Degradation: {holdout['degradation']:.2f}%")

    if holdout["test_return"] < 0:
        if verbose:
            print("  REJECTED: negative out-of-sample return")
        return {
            "status": "REJECTED",
            "reason": "negative_out_of_sample",
            "holdout": holdout,
        }

    # Step 3: Walk-forward
    if verbose:
        print("  Step 3: Walk-forward validation...")

    wf = walk_forward(strategy_class, params, symbol, timeframe)

    if verbose:
        for w in wf["windows"]:
            status = "+" if w["test_return"] > 0 else "-"
            print(f"    {w['test_period']}: {w['test_return']:+.2f}% "
                  f"(Sharpe {w['test_sharpe']:.3f}) {status}")
        print(f"  Pass rate: {wf['pass_count']}/{wf['total_windows']} "
              f"({wf['pass_rate']*100:.0f}%)")

    if wf["pass_rate"] < 0.5:
        if verbose:
            print("  REJECTED: walk-forward pass rate < 50%")
        return {
            "status": "REJECTED",
            "reason": "walk_forward_failure",
            "holdout": holdout,
            "walk_forward": wf,
        }

    # Step 4: Multi-asset consistency
    if verbose:
        print("  Step 4: Multi-asset consistency...")

    ma = multi_asset_check(strategy_class, params, symbol, timeframe)

    if verbose:
        for sym, res in ma["results"].items():
            if "error" in res:
                print(f"    {sym}: no data")
            else:
                status = "+" if res["return_pct"] > 0 else "-"
                print(f"    {sym}: {res['return_pct']:+.2f}% "
                      f"(Sharpe {res['sharpe']:.3f}) {status}")
        print(f"  Positive: {ma['positive_count']}/{ma['total_assets']} "
              f"({ma['positive_rate']*100:.0f}%)")

    # Final status
    if ma["passes"] and wf["pass_rate"] >= 0.75:
        status = "PASSED"
    elif ma["passes"] or wf["pass_rate"] >= 0.5:
        status = "MARGINAL"
    else:
        status = "REJECTED"

    if verbose:
        print(f"\n  RESULT: {status}")

    return {
        "status": status,
        "full_result": {
            "return_pct": full_result["return_pct"],
            "sharpe": calc_sharpe(full_result.get("equity_curve", [])),
            "total_trades": full_result["total_trades"],
            "max_drawdown": full_result["max_drawdown"],
        },
        "holdout": holdout,
        "walk_forward": wf,
        "multi_asset": ma,
    }


def validate_top_candidates(tracker=None, n=20, verbose=True):
    """Pull top N experiments and run full validation on each.

    Updates the experiments table with validation results.

    Returns:
        list of (experiment_row, validation_result) tuples
    """
    tracker = tracker or ExperimentTracker()

    # Get top candidates that haven't been validated yet
    top = tracker.get_top_candidates(n=n, min_trades=30)

    results = []

    for experiment in top:
        # Skip already validated
        if experiment.get("validation_status") not in (None, "pending"):
            if verbose:
                print(f"\nSkipping (already {experiment['validation_status']}): "
                      f"{experiment['strategy']} on {experiment['symbol']}")
            continue

        strategy_name = experiment["strategy"]
        strategy_class = STRATEGY_CLASS_MAP.get(strategy_name)
        if not strategy_class:
            if verbose:
                print(f"\nSkipping (unknown strategy class): {strategy_name}")
            continue

        params = experiment["parameters"]
        symbol = experiment["symbol"]
        timeframe = experiment["timeframe"]

        validation = validate_candidate(
            strategy_class, params, symbol, timeframe, verbose=verbose
        )

        # Update experiments table
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
            row_id=experiment["id"],
            validation_status=validation["status"].lower(),
            test_return_pct=test_return,
            validation_details=details,
        )

        results.append((experiment, validation))

    # Summary
    if verbose:
        print(f"\n{'='*60}")
        print("VALIDATION SUMMARY")
        print(f"{'='*60}")
        passed = sum(1 for _, v in results if v["status"] == "PASSED")
        marginal = sum(1 for _, v in results if v["status"] == "MARGINAL")
        rejected = sum(1 for _, v in results if v["status"] == "REJECTED")
        print(f"Passed: {passed}  Marginal: {marginal}  Rejected: {rejected}")

        if passed + marginal > 0:
            print(f"\nValidated candidates:")
            for exp, val in results:
                if val["status"] in ("PASSED", "MARGINAL"):
                    holdout = val.get("holdout", {})
                    print(f"  [{val['status']}] {exp['symbol']} {exp['timeframe']}: "
                          f"test return {holdout.get('test_return', 'N/A')}%, "
                          f"WF pass rate {val.get('walk_forward', {}).get('pass_rate', 0)*100:.0f}%")

    return results
