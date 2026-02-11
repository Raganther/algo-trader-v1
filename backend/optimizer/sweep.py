"""Sweep Engine — parameter optimisation across strategies and assets.

Fetches data once per symbol/timeframe, runs Backtester N times with
different parameter combinations, scores results, and saves to the
experiments table via ExperimentTracker.
"""

import os
import sys
import time
from contextlib import contextmanager
from itertools import product

from backend.engine.backtester import Backtester
from backend.engine.data_utils import load_backtest_data
from backend.optimizer.scoring import calc_sharpe, score_result
from backend.optimizer.experiment_tracker import ExperimentTracker


@contextmanager
def suppress_stdout():
    """Suppress stdout during backtests (strategies print on every bar)."""
    old_stdout = sys.stdout
    sys.stdout = open(os.devnull, "w")
    try:
        yield
    finally:
        sys.stdout.close()
        sys.stdout = old_stdout


# Hardcoded — validated against live execution. No exceptions.
SPREAD = 0.0003
EXECUTION_DELAY = 0
INITIAL_CAPITAL = 10000.0


class SweepEngine:
    """Run parameter sweeps for a strategy across symbols and timeframes."""

    def __init__(self, tracker=None, spread=SPREAD, initial_capital=INITIAL_CAPITAL):
        self.spread = spread
        self.initial_capital = initial_capital
        self.tracker = tracker or ExperimentTracker()
        self.results = []

    def run_sweep(self, strategy_class, param_grid, symbol, timeframe,
                  start, end, experiment_id=None, strategy_source="existing",
                  skip_tested=True, verbose=True):
        """Run backtests for all parameter combinations.

        Fetches data once, runs Backtester for each param combo.

        Args:
            strategy_class: Strategy class reference
            param_grid: dict of param_name -> list of values
            symbol: e.g. "SPY"
            timeframe: e.g. "5m"
            start: start date string
            end: end date string
            experiment_id: group label for this sweep run
            strategy_source: "existing", "composable", "llm_generated"
            skip_tested: skip param combos already in experiments table
            verbose: print progress

        Returns:
            list of result dicts, sorted by score descending
        """
        strategy_name = strategy_class.__name__

        if experiment_id is None:
            experiment_id = f"sweep_{strategy_name}_{symbol}_{timeframe}"

        # 1. Load data once
        if verbose:
            print(f"\n{'='*60}")
            print(f"Sweep: {strategy_name} on {symbol} {timeframe}")
            print(f"Period: {start} to {end}")
            print(f"{'='*60}")
            print("Loading data...")

        data = load_backtest_data(symbol, timeframe, start, end)
        if data.empty:
            print(f"ERROR: No data for {symbol} {timeframe}")
            return []

        if verbose:
            print(f"Data loaded: {len(data)} bars")

        # 2. Generate parameter combinations
        combos = self._expand_grid(param_grid)
        if verbose:
            print(f"Parameter combinations: {len(combos)}")

        # 3. Run each combination
        sweep_results = []
        skipped = 0
        errors = 0
        t0 = time.time()

        for i, params in enumerate(combos):
            # Always include symbol in params (strategies expect it)
            params["symbol"] = symbol

            # Skip if already tested
            if skip_tested and self.tracker.has_been_tested(
                strategy_name, symbol, timeframe, params
            ):
                skipped += 1
                continue

            try:
                bt = Backtester(
                    data=data,
                    strategy_class=strategy_class,
                    parameters=params,
                    initial_capital=self.initial_capital,
                    spread=self.spread,
                    execution_delay=EXECUTION_DELAY,
                    interval=timeframe,
                )
                # Suppress strategy per-bar debug prints
                with suppress_stdout():
                    result = bt.run()

                # Score
                equity_curve = result.get("equity_curve", [])
                sharpe = calc_sharpe(equity_curve)
                score = score_result(result, equity_curve)

                result["sharpe"] = sharpe
                result["score"] = score
                result["params"] = params
                result["symbol"] = symbol
                result["timeframe"] = timeframe
                result["strategy"] = strategy_name

                sweep_results.append(result)

                # Save to experiments table
                self.tracker.save(
                    experiment_id=experiment_id,
                    strategy=strategy_name,
                    symbol=symbol,
                    timeframe=timeframe,
                    params=params,
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
                    strategy_source=strategy_source,
                )

            except Exception as e:
                errors += 1
                if verbose:
                    print(f"  ERROR combo {i+1}: {e}")

            # Progress update
            if verbose and (i + 1) % 50 == 0:
                elapsed = time.time() - t0
                rate = (i + 1 - skipped) / elapsed if elapsed > 0 else 0
                print(f"  Progress: {i+1}/{len(combos)} "
                      f"({skipped} skipped, {errors} errors, "
                      f"{rate:.1f} runs/sec)")

        # 4. Sort by score
        sweep_results.sort(key=lambda r: r["score"], reverse=True)
        self.results.extend(sweep_results)

        elapsed = time.time() - t0
        if verbose:
            print(f"\nComplete: {len(sweep_results)} results "
                  f"({skipped} skipped, {errors} errors) "
                  f"in {elapsed:.1f}s")
            if sweep_results:
                best = sweep_results[0]
                print(f"Best: score={best['score']:.4f}, "
                      f"return={best['return_pct']:.2f}%, "
                      f"sharpe={best['sharpe']:.4f}, "
                      f"trades={best['total_trades']}")

        return sweep_results

    def run_multi_sweep(self, sweep_configs, start, end, experiment_id=None):
        """Run sweeps across multiple strategy/symbol/timeframe combinations.

        Args:
            sweep_configs: list of dicts with keys:
                strategy: strategy class
                symbols: list of symbols
                timeframes: list of timeframes
                param_grid: dict of param_name -> list of values
            start: start date string
            end: end date string
            experiment_id: shared experiment group label

        Returns:
            list of all results, sorted by score
        """
        all_results = []

        for config in sweep_configs:
            strategy_class = config["strategy"]
            symbols = config["symbols"]
            timeframes = config["timeframes"]
            param_grid = config["param_grid"]
            source = config.get("strategy_source", "existing")

            for symbol in symbols:
                for tf in timeframes:
                    results = self.run_sweep(
                        strategy_class=strategy_class,
                        param_grid=param_grid,
                        symbol=symbol,
                        timeframe=tf,
                        start=start,
                        end=end,
                        experiment_id=experiment_id,
                        strategy_source=source,
                    )
                    all_results.extend(results)

        # Sort all results by score
        all_results.sort(key=lambda r: r["score"], reverse=True)
        return all_results

    @staticmethod
    def _expand_grid(param_grid):
        """Cartesian product of all parameter values."""
        if not param_grid:
            return [{}]
        keys = list(param_grid.keys())
        values = list(param_grid.values())
        return [dict(zip(keys, combo)) for combo in product(*values)]
