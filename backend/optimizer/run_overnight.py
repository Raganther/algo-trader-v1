"""Overnight Strategy Discovery Orchestrator.

Chains all discovery phases (sweep -> filter -> validate -> expand) into a
single unattended run. Designed to run overnight (~10 hours).

Usage:
    python -m backend.optimizer.run_overnight
    python -m backend.optimizer.run_overnight --quick
    python -m backend.optimizer.run_overnight --max-hours 10
    python -m backend.optimizer.run_overnight --skip-composable
"""

import argparse
import json
import sqlite3
import time
from datetime import datetime

from backend.optimizer.sweep import SweepEngine
from backend.optimizer.run_sweep import PARAM_GRIDS, STRATEGY_MAP
from backend.optimizer.pipeline import validate_candidate, STRATEGY_CLASS_MAP
from backend.optimizer.run_composable import run_composable_sweep
from backend.optimizer.validate_composable import rebuild_params
from backend.optimizer.composable_strategy import ComposableStrategy
from backend.optimizer.experiment_tracker import ExperimentTracker
from backend.optimizer.validation import get_related_symbols


# ---------------------------------------------------------------------------
# Time budget
# ---------------------------------------------------------------------------

class TimeBudget:
    """Track elapsed time against a global budget."""

    def __init__(self, max_hours):
        self.max_seconds = max_hours * 3600
        self.start_time = time.time()
        self.pass_times = {}  # name -> elapsed seconds (after end_pass)

    def elapsed(self):
        return time.time() - self.start_time

    def remaining(self):
        return max(0, self.max_seconds - self.elapsed())

    def is_expired(self):
        return self.elapsed() >= self.max_seconds

    def start_pass(self, name):
        self.pass_times[name] = time.time()

    def end_pass(self, name):
        if name in self.pass_times:
            self.pass_times[name] = time.time() - self.pass_times[name]

    def fmt_elapsed(self):
        e = self.elapsed()
        return f"{int(e // 3600)}h {int((e % 3600) // 60)}m"

    def fmt_remaining(self):
        r = self.remaining()
        return f"{int(r // 3600)}h {int((r % 3600) // 60)}m"


# ---------------------------------------------------------------------------
# Sweep targets (priority-ordered)
# ---------------------------------------------------------------------------

SWEEP_TARGETS = [
    # Tier 1: GLD untested timeframes (strongest known edge)
    ("GLD", "15m"), ("GLD", "4h"), ("GLD", "1d"),
    # Tier 2: Gold-correlated on 1h
    ("SLV", "1h"), ("IAU", "1h"), ("GDX", "1h"),
    # Tier 3: XLE untested timeframes
    ("XLE", "15m"), ("XLE", "4h"), ("XLE", "1d"),
    # Tier 4: XBI, TLT additional timeframes
    ("XBI", "15m"), ("XBI", "4h"), ("TLT", "15m"), ("TLT", "4h"),
    # Tier 5: Broad market
    ("SPY", "1h"), ("SPY", "4h"), ("QQQ", "1h"), ("QQQ", "4h"),
    ("IWM", "1h"), ("IWM", "4h"),
    # Tier 6: DIA
    ("DIA", "1h"), ("DIA", "4h"),
]

COMPOSABLE_TARGETS = [
    ("GLD", "15m"), ("GLD", "4h"),
    ("SLV", "1h"), ("IAU", "1h"), ("GDX", "1h"),
]

ADJACENT_TF = {
    "5m":  ["15m"],
    "15m": ["5m", "1h"],
    "1h":  ["15m", "4h"],
    "4h":  ["1h", "1d"],
    "1d":  ["4h"],
}

SWEEP_STRATEGIES = ["StochRSIMeanReversion", "DonchianBreakout", "MACDBollinger"]

# Quick mode: reduced grids for smoke testing
QUICK_GRIDS = {
    "StochRSIMeanReversion": {
        "rsi_period": [14, 21],
        "stoch_period": [7, 14],
        "overbought": [75, 80],
        "oversold": [20, 25],
        "sl_atr": [2.0, 3.0],
        "skip_adx_filter": [False],
        "adx_threshold": [25],
    },
    "DonchianBreakout": {
        "entry_period": [20, 55],
        "exit_period": [10],
        "stop_loss_atr": [2.0],
        "atr_period": [14],
    },
    "MACDBollinger": {
        "macd_fast": [12],
        "macd_slow": [26],
        "macd_signal": [9],
        "bb_period": [20],
        "bb_std": [2.0],
        "sl_atr": [2.0],
    },
}

# Medium mode: covers edge cases without exhaustive search
# StochRSI: 3*3*3*3*3*2*2 = 972 combos (vs 3,456 full, 32 quick)
# Donchian: 4*2*2*2 = 32 combos
# MACD: 2*2*2*2*2*2 = 64 combos
MEDIUM_GRIDS = {
    "StochRSIMeanReversion": {
        "rsi_period": [7, 14, 21],
        "stoch_period": [7, 14, 21],
        "overbought": [70, 80, 85],
        "oversold": [15, 20, 30],
        "sl_atr": [1.5, 2.0, 3.0],
        "skip_adx_filter": [True, False],
        "adx_threshold": [20, 25],
    },
    "DonchianBreakout": {
        "entry_period": [10, 20, 30, 55],
        "exit_period": [5, 10],
        "stop_loss_atr": [1.5, 3.0],
        "atr_period": [14, 20],
    },
    "MACDBollinger": {
        "macd_fast": [8, 12],
        "macd_slow": [21, 26],
        "macd_signal": [9, 12],
        "bb_period": [15, 20],
        "bb_std": [1.5, 2.0],
        "sl_atr": [1.5, 2.0],
    },
}

# Scan mode: coarse sweep to detect edges quickly (~8 combos per strategy)
# Just enough to answer "does this asset/timeframe have any edge at all?"
# StochRSI: 2*1*2*2*1*1*1 = 8 combos
# Donchian: 2*1*1*1 = 2 combos
# MACD: 1*1*1*1*1*1 = 1 combo
# Total per target: 11 combos (~5 seconds)
SCAN_GRIDS = {
    "StochRSIMeanReversion": {
        "rsi_period": [14, 21],
        "stoch_period": [14],
        "overbought": [75, 80],
        "oversold": [20, 25],
        "sl_atr": [2.0],
        "skip_adx_filter": [False],
        "adx_threshold": [25],
    },
    "DonchianBreakout": {
        "entry_period": [20, 55],
        "exit_period": [10],
        "stop_loss_atr": [2.0],
        "atr_period": [14],
    },
    "MACDBollinger": {
        "macd_fast": [12],
        "macd_slow": [26],
        "macd_signal": [9],
        "bb_period": [20],
        "bb_std": [2.0],
        "sl_atr": [2.0],
    },
}

START_DATE = "2020-01-01"
END_DATE = "2025-12-31"


# ---------------------------------------------------------------------------
# Pass 1: Broad Sweep
# ---------------------------------------------------------------------------

def pass1_broad_sweep(engine, budget, targets, strategies, grids,
                      quick=False, skip_composable=False):
    """Run param sweeps across priority-ordered targets."""
    budget.start_pass("sweep")

    total_sweeps = 0
    total_results = 0

    print(f"\n{'='*60}")
    print("PASS 1: BROAD SWEEP")
    print(f"{'='*60}")
    print(f"Targets: {len(targets)} symbol/timeframe combos")
    print(f"Strategies: {strategies}")
    print(f"Time remaining: {budget.fmt_remaining()}")

    for symbol, tf in targets:
        if budget.is_expired():
            print("\n*** Time budget expired — stopping sweeps ***")
            break

        for strat_name in strategies:
            if budget.is_expired():
                break

            strategy_class = STRATEGY_MAP.get(strat_name)
            grid = grids.get(strat_name)
            if not strategy_class or not grid:
                continue

            try:
                results = engine.run_sweep(
                    strategy_class=strategy_class,
                    param_grid=grid,
                    symbol=symbol,
                    timeframe=tf,
                    start=START_DATE,
                    end=END_DATE,
                    skip_tested=True,
                    verbose=True,
                )
                total_sweeps += 1
                total_results += len(results)

            except Exception as e:
                print(f"  ERROR {strat_name} {symbol} {tf}: {e}")

    # Composable sweeps
    if not skip_composable and not budget.is_expired():
        comp_targets = COMPOSABLE_TARGETS[:2] if quick else COMPOSABLE_TARGETS
        print(f"\n--- Composable sweeps ({len(comp_targets)} targets) ---")
        for symbol, tf in comp_targets:
            if budget.is_expired():
                print("\n*** Time budget expired — stopping composable sweeps ***")
                break

            try:
                print(f"  Composable {symbol} {tf}...")
                run_composable_sweep(
                    symbol=symbol,
                    timeframe=tf,
                    quick=quick,
                )
                total_sweeps += 1
            except Exception as e:
                print(f"  ERROR composable {symbol} {tf}: {e}")

    budget.end_pass("sweep")
    print(f"\nPass 1 complete: {total_sweeps} sweeps, {total_results} new param results "
          f"({budget.fmt_elapsed()} elapsed)")
    return total_results


# ---------------------------------------------------------------------------
# Pass 2: Filter Candidates
# ---------------------------------------------------------------------------

def pass2_filter(budget):
    """Query DB for promising unvalidated candidates."""
    budget.start_pass("filter")

    print(f"\n{'='*60}")
    print("PASS 2: FILTER CANDIDATES")
    print(f"{'='*60}")

    conn = sqlite3.connect("backend/research.db")
    conn.row_factory = sqlite3.Row

    existing_rows = conn.execute('''
        SELECT id, strategy, symbol, timeframe, parameters,
               return_pct, sharpe, total_trades, max_drawdown,
               strategy_source
        FROM experiments
        WHERE sharpe > 0.5
          AND total_trades >= 30
          AND validation_status = 'pending'
          AND strategy_source != 'composable'
        ORDER BY sharpe DESC
        LIMIT 50
    ''').fetchall()

    composable_rows = conn.execute('''
        SELECT id, strategy, symbol, timeframe, parameters,
               return_pct, sharpe, total_trades, max_drawdown,
               strategy_source
        FROM experiments
        WHERE sharpe > 0.5
          AND total_trades >= 30
          AND validation_status = 'pending'
          AND strategy_source = 'composable'
        ORDER BY sharpe DESC
        LIMIT 20
    ''').fetchall()

    conn.close()

    existing = [dict(r) for r in existing_rows]
    composable = [dict(r) for r in composable_rows]

    for c in existing + composable:
        if isinstance(c["parameters"], str):
            c["parameters"] = json.loads(c["parameters"])

    print(f"  Existing candidates:   {len(existing)}")
    print(f"  Composable candidates: {len(composable)}")

    budget.end_pass("filter")
    return existing, composable


# ---------------------------------------------------------------------------
# Pass 3: Validate
# ---------------------------------------------------------------------------

def pass3_validate(existing, composable, tracker, budget):
    """Run full validation pipeline on filtered candidates."""
    budget.start_pass("validate")

    print(f"\n{'='*60}")
    print("PASS 3: VALIDATE CANDIDATES")
    print(f"{'='*60}")
    print(f"Candidates: {len(existing)} existing + {len(composable)} composable")
    print(f"Time remaining: {budget.fmt_remaining()}")

    results = {"passed": [], "marginal": [], "rejected": []}

    # --- Existing strategies ---
    for i, exp in enumerate(existing):
        if budget.is_expired():
            print("\n*** Time budget expired — stopping validation ***")
            break

        strategy_name = exp["strategy"]
        strategy_class = STRATEGY_CLASS_MAP.get(strategy_name)
        if not strategy_class:
            print(f"  [{i+1}/{len(existing)}] Skip (unknown class): {strategy_name}")
            continue

        params = exp["parameters"]
        symbol = exp["symbol"]
        tf = exp["timeframe"]

        print(f"  [{i+1}/{len(existing)}] {strategy_name} {symbol} {tf} "
              f"(Sharpe {exp['sharpe']:.3f})...", end=" ", flush=True)

        try:
            validation = validate_candidate(
                strategy_class, params, symbol, tf, verbose=False
            )
            status = validation["status"]
            _save_validation(tracker, exp["id"], validation)
            results[status.lower()].append(_winner_entry(
                strategy_name, symbol, tf, exp["sharpe"], validation
            ))
            print(f"-> {status}")

        except Exception as e:
            print(f"-> ERROR: {e}")

    # --- Composable strategies ---
    for i, exp in enumerate(composable):
        if budget.is_expired():
            print("\n*** Time budget expired — stopping composable validation ***")
            break

        params = exp["parameters"]
        symbol = exp["symbol"]
        tf = exp["timeframe"]
        label = f"{params.get('entry', '?')} + {params.get('exit', '?')}"

        print(f"  [C{i+1}/{len(composable)}] {label} {symbol} {tf} "
              f"(Sharpe {exp['sharpe']:.3f})...", end=" ", flush=True)

        try:
            full_params = rebuild_params(params, symbol)
            if not full_params:
                print("-> Skip (can't rebuild)")
                continue

            validation = validate_candidate(
                ComposableStrategy, full_params, symbol, tf, verbose=False
            )
            status = validation["status"]
            _save_validation(tracker, exp["id"], validation)
            results[status.lower()].append(_winner_entry(
                "ComposableStrategy", symbol, tf, exp["sharpe"], validation,
                label=label,
            ))
            print(f"-> {status}")

        except Exception as e:
            print(f"-> ERROR: {e}")

    budget.end_pass("validate")

    p, m, r = len(results["passed"]), len(results["marginal"]), len(results["rejected"])
    print(f"\nPass 3 complete: {p} passed, {m} marginal, {r} rejected "
          f"({budget.fmt_elapsed()} elapsed)")
    return results


def _save_validation(tracker, row_id, validation):
    """Persist validation result to DB."""
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
        row_id=row_id,
        validation_status=validation["status"].lower(),
        test_return_pct=test_return,
        validation_details=details,
    )


def _winner_entry(strategy, symbol, tf, sharpe, validation, label=None):
    return {
        "strategy": strategy,
        "symbol": symbol,
        "timeframe": tf,
        "sharpe": sharpe,
        "label": label or strategy,
        "validation": validation,
    }


# ---------------------------------------------------------------------------
# Pass 4: Expand Winners
# ---------------------------------------------------------------------------

def pass4_expand(validation_results, engine, budget, grids, skip_composable=False):
    """Expand winners to adjacent timeframes and related assets."""
    budget.start_pass("expand")

    winners = validation_results["passed"] + validation_results["marginal"]

    print(f"\n{'='*60}")
    print("PASS 4: EXPAND WINNERS")
    print(f"{'='*60}")
    print(f"Winners to expand: {len(winners)}")
    print(f"Time remaining: {budget.fmt_remaining()}")

    if not winners:
        print("  No winners to expand.")
        budget.end_pass("expand")
        return 0

    total_new = 0

    for w in winners:
        if budget.is_expired():
            print("\n*** Time budget expired — stopping expansion ***")
            break

        symbol = w["symbol"]
        tf = w["timeframe"]
        strategy_name = w["strategy"]

        adj_tfs = ADJACENT_TF.get(tf, [])
        related = [s for s in get_related_symbols(symbol) if s != symbol]

        targets = [(symbol, new_tf) for new_tf in adj_tfs]
        targets += [(new_sym, tf) for new_sym in related]

        if not targets:
            continue

        print(f"\n  Expanding {w['label']} {symbol} {tf} -> {len(targets)} targets")

        for new_sym, new_tf in targets:
            if budget.is_expired():
                break

            if strategy_name == "ComposableStrategy":
                if skip_composable:
                    continue
                try:
                    print(f"    Composable {new_sym} {new_tf}...", end=" ", flush=True)
                    run_composable_sweep(
                        symbol=new_sym, timeframe=new_tf, quick=True,
                    )
                    print("done")
                except Exception as e:
                    print(f"ERROR: {e}")
            else:
                # Map full class name -> short name for grid lookup
                short_name = _class_to_short(strategy_name)
                if not short_name:
                    continue

                grid = grids.get(short_name)
                strategy_class = STRATEGY_MAP.get(short_name)
                if not grid or not strategy_class:
                    continue

                try:
                    results = engine.run_sweep(
                        strategy_class=strategy_class,
                        param_grid=grid,
                        symbol=new_sym,
                        timeframe=new_tf,
                        start=START_DATE,
                        end=END_DATE,
                        skip_tested=True,
                        verbose=False,
                    )
                    total_new += len(results)
                    if results:
                        best = results[0]
                        print(f"    {short_name} {new_sym} {new_tf}: "
                              f"{len(results)} new | "
                              f"best Sharpe {best['sharpe']:.3f}")
                    else:
                        print(f"    {short_name} {new_sym} {new_tf}: all skipped")
                except Exception as e:
                    print(f"    ERROR {short_name} {new_sym} {new_tf}: {e}")

    budget.end_pass("expand")
    print(f"\nPass 4 complete: {total_new} new results from expansion "
          f"({budget.fmt_elapsed()} elapsed)")
    return total_new


def _class_to_short(class_name):
    """Map a full strategy class name to the short key used in STRATEGY_MAP."""
    for short, cls in STRATEGY_MAP.items():
        if cls.__name__ == class_name:
            return short
    return None


# ---------------------------------------------------------------------------
# Summary report
# ---------------------------------------------------------------------------

def print_summary(budget, tracker, count_before, validation_results):
    """Print final summary report."""
    count_after = tracker.count()

    print(f"\n{'='*60}")
    print("OVERNIGHT DISCOVERY — FINAL REPORT")
    print(f"{'='*60}")

    # Timing
    print(f"\nRuntime: {budget.fmt_elapsed()}")
    for name, duration in budget.pass_times.items():
        if isinstance(duration, (int, float)):
            print(f"  {name}: {duration/60:.1f}m")

    # Experiment counts
    new = count_after - count_before
    print(f"\nExperiments: {count_before} -> {count_after} (+{new} new)")

    # Validation breakdown
    if validation_results:
        p = len(validation_results.get("passed", []))
        m = len(validation_results.get("marginal", []))
        r = len(validation_results.get("rejected", []))
        print(f"\nValidation: {p} passed, {m} marginal, {r} rejected")

        for w in validation_results.get("passed", []) + validation_results.get("marginal", []):
            v = w["validation"]
            holdout = v.get("holdout", {})
            wf = v.get("walk_forward", {})
            print(f"  [{v['status']}] {w['label']} on {w['symbol']} {w['timeframe']}")
            if holdout:
                print(f"    Holdout: test {holdout.get('test_return', 0):.1f}%, "
                      f"degradation {holdout.get('degradation', 0):.1f}%")
            if wf:
                print(f"    Walk-forward: {wf.get('pass_rate', 0)*100:.0f}% pass rate")

    # Top 10 all-time
    print(f"\nTop 10 all-time (by score):")
    top = tracker.get_top_candidates(n=10, min_trades=30)
    for i, exp in enumerate(top, 1):
        vs = exp.get("validation_status", "pending")
        tag = f" [{vs}]" if vs != "pending" else ""
        print(f"  {i}. {exp['strategy']} {exp['symbol']} {exp['timeframe']}: "
              f"Sharpe {exp.get('sharpe', 0):.3f}, "
              f"{exp.get('return_pct', 0):.1f}%, "
              f"{exp.get('total_trades', 0)} trades{tag}")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(
        description="Overnight Strategy Discovery Orchestrator"
    )
    parser.add_argument("--quick", action="store_true",
                        help="Smoke test with reduced grids (< 1 hour)")
    parser.add_argument("--max-hours", type=float, default=10,
                        help="Time limit in hours (default: 10)")
    parser.add_argument("--scan", action="store_true",
                        help="Coarse scan (~11 combos per target, detect edges fast)")
    parser.add_argument("--medium", action="store_true",
                        help="Medium grids (~1,000 combos, balanced coverage)")
    parser.add_argument("--skip-composable", action="store_true",
                        help="Skip composable strategy sweeps")
    parser.add_argument("--skip-sweep", action="store_true",
                        help="Skip Pass 1 (broad sweep)")
    parser.add_argument("--skip-validation", action="store_true",
                        help="Skip Pass 3 (validation)")
    parser.add_argument("--symbols", type=str, default=None,
                        help="Comma-separated symbols to target (e.g. GLD,IAU,SLV)")
    parser.add_argument("--timeframes", type=str, default=None,
                        help="Comma-separated timeframes to target (e.g. 15m,1h,4h)")
    args = parser.parse_args()

    if args.quick and args.max_hours == 10:  # only cap if user didn't specify
        args.max_hours = 1.0

    budget = TimeBudget(args.max_hours)
    tracker = ExperimentTracker()
    engine = SweepEngine(tracker=tracker)
    count_before = tracker.count()

    print(f"{'='*60}")
    print("OVERNIGHT STRATEGY DISCOVERY")
    print(f"{'='*60}")
    print(f"Started:          {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Time budget:      {args.max_hours}h")
    grid_mode = "scan" if args.scan else "quick" if args.quick else "medium" if args.medium else "full"
    print(f"Grid mode:        {grid_mode}")
    print(f"Skip composable:  {args.skip_composable}")
    print(f"Skip sweep:       {args.skip_sweep}")
    print(f"Skip validation:  {args.skip_validation}")
    print(f"Experiments in DB: {count_before}")

    if args.scan:
        grids = SCAN_GRIDS
        targets = SWEEP_TARGETS
    elif args.quick:
        grids = QUICK_GRIDS
        targets = SWEEP_TARGETS[:6]
    elif args.medium:
        grids = MEDIUM_GRIDS
        targets = SWEEP_TARGETS
    else:
        grids = PARAM_GRIDS
        targets = SWEEP_TARGETS

    # Filter targets by --symbols and --timeframes if specified
    if args.symbols:
        allowed_symbols = [s.strip().upper() for s in args.symbols.split(",")]
        targets = [(s, tf) for s, tf in targets if s in allowed_symbols]
    if args.timeframes:
        allowed_tfs = [t.strip() for t in args.timeframes.split(",")]
        targets = [(s, tf) for s, tf in targets if tf in allowed_tfs]

    # Pass 1: Broad sweep
    if not args.skip_sweep:
        pass1_broad_sweep(
            engine, budget, targets, SWEEP_STRATEGIES, grids,
            quick=args.quick, skip_composable=args.skip_composable,
        )
    else:
        print(f"\n*** Skipping Pass 1 (sweep) ***")

    # Pass 2 & 3: Filter and validate
    validation_results = {"passed": [], "marginal": [], "rejected": []}
    if not args.skip_validation:
        existing, composable = pass2_filter(budget)
        validation_results = pass3_validate(existing, composable, tracker, budget)
    else:
        print(f"\n*** Skipping Pass 2-3 (filter/validation) ***")

    # Pass 4: Expand winners — pull from DB if no winners from this run
    winners_from_run = validation_results["passed"] + validation_results["marginal"]
    if not winners_from_run:
        # Load already-passed strategies from DB for expansion
        db_winners = tracker.get_top_candidates(n=30, min_trades=30,
                                                 validation_status="passed")
        for exp in db_winners:
            validation_results["passed"].append(_winner_entry(
                exp["strategy"], exp["symbol"], exp["timeframe"],
                exp.get("sharpe", 0), {"status": "PASSED"},
            ))
        print(f"\n  Loaded {len(db_winners)} passed strategies from DB for expansion")

    pass4_expand(
        validation_results, engine, budget, grids,
        skip_composable=args.skip_composable,
    )

    # Final report
    print_summary(budget, tracker, count_before, validation_results)
    print(f"\nFinished: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")


if __name__ == "__main__":
    main()
