"""CLI entry point for running parameter sweeps.

Usage:
    python -m backend.optimizer.run_sweep
    python -m backend.optimizer.run_sweep --strategy StochRSIMeanReversion --symbol SPY --timeframe 5m
    python -m backend.optimizer.run_sweep --quick   # Small test sweep
"""

import argparse
import sys

from backend.optimizer.sweep import SweepEngine
from backend.optimizer.experiment_tracker import ExperimentTracker

# Import strategies from runner.py's STRATEGY_MAP
from backend.strategies.stoch_rsi_mean_reversion import StochRSIMeanReversionStrategy
from backend.strategies.donchian_breakout import DonchianBreakoutStrategy
from backend.strategies.macd_bollinger import MACDBollingerStrategy
from backend.strategies.regime_gated_stoch import RegimeGatedStoch
from backend.strategies.swing_breakout import SwingBreakoutStrategy

STRATEGY_MAP = {
    "StochRSIMeanReversion": StochRSIMeanReversionStrategy,
    "DonchianBreakout": DonchianBreakoutStrategy,
    "MACDBollinger": MACDBollingerStrategy,
    "RegimeGatedStoch": RegimeGatedStoch,
    "SwingBreakout": SwingBreakoutStrategy,
}

# Default param grids per strategy
PARAM_GRIDS = {
    "StochRSIMeanReversion": {
        "rsi_period": [7, 14, 21],
        "stoch_period": [7, 14, 21],
        "overbought": [70, 75, 80, 85],
        "oversold": [15, 20, 25, 30],
        "sl_atr": [1.5, 2.0, 2.5, 3.0],
        "skip_adx_filter": [True, False],
        "adx_threshold": [20, 25, 30],
    },
    "DonchianBreakout": {
        "entry_period": [10, 20, 30, 55],
        "exit_period": [5, 10, 20],
        "stop_loss_atr": [1.5, 2.0, 3.0],
        "atr_period": [14, 20],
    },
    "MACDBollinger": {
        "macd_fast": [8, 12, 16],
        "macd_slow": [21, 26, 30],
        "macd_signal": [7, 9, 12],
        "bb_period": [15, 20, 25],
        "bb_std": [1.5, 2.0, 2.5],
        "sl_atr": [1.5, 2.0, 3.0],
    },
}

# Quick test: small grid for smoke testing
QUICK_GRID = {
    "StochRSIMeanReversion": {
        "rsi_period": [14],
        "stoch_period": [14],
        "overbought": [75, 80],
        "oversold": [20, 25],
        "sl_atr": [2.0],
        "skip_adx_filter": [True],
    },
}

DEFAULT_SYMBOLS = ["SPY", "QQQ", "IWM", "XLE", "XBI", "EEM", "GLD", "TLT"]
DEFAULT_TIMEFRAMES = ["5m", "15m", "1h"]


def main():
    parser = argparse.ArgumentParser(description="Run parameter sweeps")
    parser.add_argument("--strategy", type=str, help="Strategy name")
    parser.add_argument("--symbol", type=str, help="Single symbol to sweep")
    parser.add_argument("--timeframe", type=str, help="Single timeframe to sweep")
    parser.add_argument("--start", type=str, default="2020-01-01")
    parser.add_argument("--end", type=str, default="2025-12-31")
    parser.add_argument("--quick", action="store_true", help="Quick smoke test")
    parser.add_argument("--experiment-id", type=str, help="Custom experiment group ID")
    parser.add_argument("--no-skip", action="store_true",
                        help="Don't skip already-tested combinations")

    args = parser.parse_args()

    tracker = ExperimentTracker()
    engine = SweepEngine(tracker=tracker)

    if args.quick:
        # Quick smoke test: 1 strategy, 1 symbol, small grid
        strategy_name = args.strategy or "StochRSIMeanReversion"
        symbol = args.symbol or "SPY"
        tf = args.timeframe or "1h"
        grid = QUICK_GRID.get(strategy_name, list(QUICK_GRID.values())[0])

        print(f"\n*** QUICK TEST: {strategy_name} on {symbol} {tf} ***\n")
        results = engine.run_sweep(
            strategy_class=STRATEGY_MAP[strategy_name],
            param_grid=grid,
            symbol=symbol,
            timeframe=tf,
            start=args.start,
            end=args.end,
            experiment_id=args.experiment_id or f"quick_{strategy_name}",
            skip_tested=not args.no_skip,
        )
        _print_summary(results, tracker)
        return

    if args.strategy:
        # Single strategy sweep
        strategy_name = args.strategy
        if strategy_name not in STRATEGY_MAP:
            print(f"Unknown strategy: {strategy_name}")
            print(f"Available: {list(STRATEGY_MAP.keys())}")
            sys.exit(1)

        symbols = [args.symbol] if args.symbol else DEFAULT_SYMBOLS
        timeframes = [args.timeframe] if args.timeframe else DEFAULT_TIMEFRAMES
        grid = PARAM_GRIDS.get(strategy_name, {})

        if not grid:
            print(f"No default param grid for {strategy_name}. "
                  f"Add one to PARAM_GRIDS or use --quick.")
            sys.exit(1)

        for symbol in symbols:
            for tf in timeframes:
                engine.run_sweep(
                    strategy_class=STRATEGY_MAP[strategy_name],
                    param_grid=grid,
                    symbol=symbol,
                    timeframe=tf,
                    start=args.start,
                    end=args.end,
                    experiment_id=args.experiment_id or f"sweep_{strategy_name}",
                    skip_tested=not args.no_skip,
                )

        _print_summary(engine.results, tracker)
    else:
        print("Specify --strategy or --quick. Use --help for options.")
        sys.exit(1)


def _print_summary(results, tracker):
    """Print sweep results summary."""
    if not results:
        print("\nNo results.")
        return

    print(f"\n{'='*60}")
    print(f"SWEEP SUMMARY")
    print(f"{'='*60}")
    print(f"Total runs: {len(results)}")
    print(f"Total experiments in DB: {tracker.count()}")

    top = [r for r in results if r["score"] > -999]
    if top:
        print(f"\nTop 10 by score:")
        for i, r in enumerate(top[:10], 1):
            print(f"  {i}. {r['strategy']} {r['symbol']} {r['timeframe']}: "
                  f"score={r['score']:.4f}, "
                  f"return={r['return_pct']:.2f}%, "
                  f"sharpe={r['sharpe']:.4f}, "
                  f"trades={r['total_trades']}, "
                  f"dd={r['max_drawdown']:.1f}%")

    disqualified = [r for r in results if r["score"] == -999]
    if disqualified:
        print(f"\nDisqualified (< 10 trades): {len(disqualified)}")


if __name__ == "__main__":
    main()
