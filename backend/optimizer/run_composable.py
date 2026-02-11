"""Run composable strategy sweep.

Usage:
    python -m backend.optimizer.run_composable --symbol GLD --timeframe 1h
    python -m backend.optimizer.run_composable --symbol GLD --timeframe 1h --quick
    python -m backend.optimizer.run_composable --describe
"""

import argparse
import sys
import os
import time
import uuid
from contextlib import contextmanager

from backend.optimizer.combination_generator import (
    generate_combinations,
    describe,
)
from backend.optimizer.composable_strategy import ComposableStrategy
from backend.optimizer.experiment_tracker import ExperimentTracker
from backend.optimizer.scoring import calc_sharpe, score_result
from backend.engine.data_utils import load_backtest_data
from backend.engine.backtester import Backtester


SPREAD = 0.0003
EXECUTION_DELAY = 0
INITIAL_CAPITAL = 10000.0


@contextmanager
def suppress_stdout():
    old = sys.stdout
    sys.stdout = open(os.devnull, "w")
    try:
        yield
    finally:
        sys.stdout.close()
        sys.stdout = old


def run_composable_sweep(
    symbol="GLD",
    timeframe="1h",
    start="2020-01-01",
    end="2025-12-31",
    quick=False,
):
    """Run all composable combinations on a single symbol/timeframe."""
    tracker = ExperimentTracker()

    print(f"Loading data: {symbol} {timeframe} ({start} to {end})...")
    data = load_backtest_data(symbol, timeframe, start, end)
    if data.empty:
        print(f"No data for {symbol} {timeframe}")
        return

    print(f"Loaded {len(data)} bars")

    # Generate combinations
    combos = generate_combinations(symbol=symbol, timeframe=timeframe)
    total = len(combos)
    print(f"Generated {total} compatible combinations")

    if quick:
        combos = combos[:10]
        total = len(combos)
        print(f"Quick mode: testing first {total} only")

    # Track results
    passed = 0
    failed = 0
    best_sharpe = -999
    best_label = ""

    start_time = time.time()

    for idx, (params, label) in enumerate(combos):
        # Check if already tested (use label as dedup key)
        hash_params = {
            "entry": params["_entry_name"],
            "exit": params["_exit_name"],
            "filter": params["_filter_name"],
            "sizer": params["_sizer_name"],
        }
        if tracker.has_been_tested("ComposableStrategy", symbol, timeframe, hash_params):
            continue

        try:
            with suppress_stdout():
                bt = Backtester(
                    data=data.copy(),
                    strategy_class=ComposableStrategy,
                    parameters=params,
                    initial_capital=INITIAL_CAPITAL,
                    spread=SPREAD,
                    execution_delay=EXECUTION_DELAY,
                    interval=timeframe,
                )
                result = bt.run()

            equity_curve = result.get("equity_curve", [])
            sharpe = calc_sharpe(equity_curve)
            score = score_result(result, equity_curve)

            # Save to experiments DB
            experiment_id = str(uuid.uuid4())[:8]
            tracker.save(
                experiment_id=experiment_id,
                strategy="ComposableStrategy",
                strategy_source="composable",
                symbol=symbol,
                timeframe=timeframe,
                params=hash_params,
                results={
                    "return_pct": result["return_pct"],
                    "max_drawdown": result["max_drawdown"],
                    "total_trades": result["total_trades"],
                    "win_rate": result["win_rate"],
                    "profit_factor": result["profit_factor"],
                    "sharpe": sharpe,
                    "equity_curve": equity_curve,
                },
                score=score,
                train_period=f"{start} to {end}",
            )

            if sharpe > best_sharpe:
                best_sharpe = sharpe
                best_label = label

            if result.get("return_pct", 0) > 0:
                passed += 1
            else:
                failed += 1

        except Exception as e:
            failed += 1
            if idx < 5:
                print(f"  Error on combo {idx}: {e}")

        # Progress
        done = idx + 1
        if done % 25 == 0 or done == total:
            elapsed = time.time() - start_time
            rate = done / elapsed if elapsed > 0 else 0
            remaining = (total - done) / rate if rate > 0 else 0
            print(
                f"  [{done}/{total}] "
                f"{passed} positive, {failed} negative | "
                f"Best Sharpe: {best_sharpe:.3f} | "
                f"ETA: {remaining/60:.1f}m"
            )

    elapsed = time.time() - start_time
    print(f"\nDone in {elapsed/60:.1f} minutes")
    print(f"Results: {passed} positive, {failed} negative out of {passed+failed} tested")
    print(f"Best Sharpe: {best_sharpe:.3f}")
    print(f"Best combo: {best_label}")
    print(f"Total experiments in DB: {tracker.count()}")


def main():
    parser = argparse.ArgumentParser(description="Run composable strategy sweep")
    parser.add_argument("--symbol", type=str, default="GLD", help="Symbol to test")
    parser.add_argument("--timeframe", type=str, default="1h", help="Timeframe")
    parser.add_argument("--start", type=str, default="2020-01-01")
    parser.add_argument("--end", type=str, default="2025-12-31")
    parser.add_argument("--quick", action="store_true", help="Test first 10 combos only")
    parser.add_argument("--describe", action="store_true", help="Show available blocks")
    args = parser.parse_args()

    if args.describe:
        describe()
        return

    run_composable_sweep(
        symbol=args.symbol,
        timeframe=args.timeframe,
        start=args.start,
        end=args.end,
        quick=args.quick,
    )


if __name__ == "__main__":
    main()
