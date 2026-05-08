"""Audit: how many trades does the ADX-filter early-return bug affect?

Bug: `stoch_rsi_mean_reversion.py:211-239` — when `current_adx > adx_threshold`
the strategy returns from `on_data` BEFORE reaching the stop-loss check, entry
block, or signal-exit blocks. Result: positions opened in low-ADX regime cannot
exit once ADX rises above threshold mid-trade.

This audit runs the long-window 7-bot backtest in two modes and compares:
    A: current behaviour (buggy — ADX gate blocks all logic)
    B: skip_adx_filter=True (no ADX filter at all)

B is NOT the proper fix — it lets entries fire in trending regimes too, which
will inflate trade count. But it's a clean upper bound on the exit-block bug:
any trade that closes earlier in B than in A is one the ADX gate was holding
captive in A.

Run:
    set -a && source .env && set +a
    python3 -m backend.analysis.audit_adx_filter_exit_block
"""
from __future__ import annotations

import json
from collections import defaultdict
from pathlib import Path

import pandas as pd

from backend.database import DatabaseManager
from backend.engine import correlation_sizing
from backend.engine.portfolio_runner import PortfolioRunner
from backend.strategies.stoch_rsi_mean_reversion import StochRSIMeanReversionStrategy

SYMBOLS = ["GLD", "IAU", "SLV", "GDX", "OIH", "XBI", "XOP"]
START = "2020-07-27"
END = "2026-04-27"
INITIAL = 94_000.0
SPREAD = 0.0003
PARAMS_BASE = {
    "rsi_period": 7,
    "stoch_period": 14,
    "overbought": 80,
    "oversold": 15,
    "adx_threshold": 20,
    "skip_adx_filter": False,
    "sl_atr": 2.0,
    "trailing_stop": True,
    "trail_atr": 2.0,
    "trail_after_bars": 10,
    "min_hold_bars": 10,
    "skip_days": [0],
}


def load_symbol_data() -> dict[str, pd.DataFrame]:
    db = DatabaseManager()
    db.initialize_db()
    start_ts = int(pd.Timestamp(START).tz_localize("UTC").timestamp())
    end_ts = int(pd.Timestamp(END).tz_localize("UTC").timestamp())
    out: dict[str, pd.DataFrame] = {}
    for sym in SYMBOLS:
        rows = db.get_price_bars(sym, start_ts=start_ts, end_ts=end_ts)
        if not rows:
            raise RuntimeError(f"no cached price_data rows for {sym} in window")
        df = pd.DataFrame(rows)
        df["timestamp"] = pd.to_datetime(df["timestamp"], unit="s", utc=True)
        df = df.set_index("timestamp").sort_index()
        df = df.rename(columns={"open": "Open", "high": "High", "low": "Low", "close": "Close", "volume": "Volume"})
        out[sym] = df
    return out


def run_one(symbol_data: dict[str, pd.DataFrame], skip_adx: bool) -> dict:
    correlation_sizing.DISCOUNT_ENABLED = True
    correlation_sizing.CLUSTER_CAP_ENABLED = False
    correlation_sizing.PORTFOLIO_CAP_ENABLED = True
    correlation_sizing.PORTFOLIO_CAP_FRAC = 1.0

    params = dict(PARAMS_BASE)
    params["skip_adx_filter"] = skip_adx

    pr = PortfolioRunner(
        symbol_data=symbol_data,
        strategy_class=StochRSIMeanReversionStrategy,
        parameters=params,
        initial_capital=INITIAL,
        spread=SPREAD,
    )
    return pr.run()


def compare_trades(buggy: list[dict], unfiltered: list[dict]) -> dict:
    """Compare trades from buggy run vs skip_adx_filter run."""
    def key(t: dict) -> tuple:
        et = t.get("entry_time") or "?"
        return (et, t.get("symbol"))

    by_buggy = {key(t): t for t in buggy}
    by_unfiltered = {key(t): t for t in unfiltered}

    common = set(by_buggy) & set(by_unfiltered)
    only_buggy = set(by_buggy) - set(by_unfiltered)
    only_unfiltered = set(by_unfiltered) - set(by_buggy)

    common_pnl_diff = 0.0
    common_exit_changed = 0
    for k in common:
        b, u = by_buggy[k], by_unfiltered[k]
        common_pnl_diff += float(u.get("pnl", 0)) - float(b.get("pnl", 0))
        if b.get("timestamp") != u.get("timestamp") or b.get("exit_reason") != u.get("exit_reason"):
            common_exit_changed += 1

    pnl_only_unfiltered = sum(float(by_unfiltered[k].get("pnl", 0)) for k in only_unfiltered)
    pnl_only_buggy = sum(float(by_buggy[k].get("pnl", 0)) for k in only_buggy)

    return {
        "n_buggy": len(by_buggy),
        "n_unfiltered": len(by_unfiltered),
        "common": len(common),
        "only_buggy": len(only_buggy),
        "only_unfiltered": len(only_unfiltered),
        "common_exit_changed": common_exit_changed,
        "common_pnl_diff_unfiltered_minus_buggy": round(common_pnl_diff, 2),
        "pnl_only_unfiltered": round(pnl_only_unfiltered, 2),
        "pnl_only_buggy": round(pnl_only_buggy, 2),
    }


def main() -> int:
    print(f"Loading 7-bot 15m data from research.db cache ({START} → {END})…")
    symbol_data = load_symbol_data()
    for sym, df in symbol_data.items():
        print(f"  {sym}: {len(df)} bars  {df.index[0]} → {df.index[-1]}")
    print()

    print("=== Run A: current behaviour (ADX gate blocks all logic when ADX > 20) ===")
    buggy = run_one(symbol_data, skip_adx=False)
    print(
        f"  return {buggy['return_pct']:.2f}%  Sharpe {buggy['sharpe']:.2f}  "
        f"DD {buggy['max_drawdown']:.2f}%  trades {buggy['total_trades']}"
    )
    print()

    print("=== Run B: skip_adx_filter=True (no ADX filter — upper bound on bug impact) ===")
    unfiltered = run_one(symbol_data, skip_adx=True)
    print(
        f"  return {unfiltered['return_pct']:.2f}%  Sharpe {unfiltered['sharpe']:.2f}  "
        f"DD {unfiltered['max_drawdown']:.2f}%  trades {unfiltered['total_trades']}"
    )
    print()

    print("=== Comparison ===")
    print(f"{'Metric':<24}{'A (buggy)':>14}{'B (no ADX)':>14}{'Δ':>14}")
    for metric, fmt in [
        ("return_pct", "%.2f%%"),
        ("sharpe", "%.2f"),
        ("max_drawdown", "%.2f%%"),
        ("total_trades", "%d"),
        ("max_concurrent", "%d"),
    ]:
        a, b = buggy[metric], unfiltered[metric]
        if metric == "total_trades" or metric == "max_concurrent":
            print(f"{metric:<24}{a:>14}{b:>14}{(b-a):>14}")
        else:
            print(f"{metric:<24}{a:>13.2f}{b:>13.2f}{(b-a):>13.2f}")
    print()

    attr = compare_trades(buggy.get("trade_history", []), unfiltered.get("trade_history", []))
    print("=== Trade-level attribution ===")
    for k, v in attr.items():
        print(f"  {k:<40} {v}")
    print()

    # B - A interpretation:
    # - only_buggy = 0 expected (everything in buggy should also be in unfiltered)
    # - only_unfiltered = trades the ADX gate prevented from entering in A (entry effect, NOT exit-block bug)
    # - common_exit_changed = same trade fired in both, but exited differently → THIS is the exit-block bug signal
    print("Interpretation:")
    print("  - 'common_exit_changed' counts trades where same entry but different exit timing/reason.")
    print("    THIS is the most direct signal of the exit-block bug (skip_adx_filter let exit fire).")
    print("  - 'only_unfiltered' counts entries the ADX gate blocked. Not the bug we're auditing —")
    print("    entries SHOULD be gated by ADX. This is the 'cost' of using skip_adx_filter as proxy.")
    print("  - 'common_pnl_diff_unfiltered_minus_buggy' is the aggregate P&L impact of the exit-block")
    print("    bug on the trades that fired in both runs. Positive means buggy version was leaving")
    print("    money on the table by holding too long; negative means buggy was over-stating profit.")

    out_dir = Path(__file__).resolve().parents[2] / ".claude" / "calibration"
    out_dir.mkdir(parents=True, exist_ok=True)
    summary = {
        "params": PARAMS_BASE,
        "window": {"start": START, "end": END, "initial": INITIAL, "spread": SPREAD},
        "run_a_buggy": {
            "return_pct": buggy["return_pct"],
            "sharpe": buggy["sharpe"],
            "max_drawdown": buggy["max_drawdown"],
            "total_trades": buggy["total_trades"],
        },
        "run_b_no_adx_filter": {
            "return_pct": unfiltered["return_pct"],
            "sharpe": unfiltered["sharpe"],
            "max_drawdown": unfiltered["max_drawdown"],
            "total_trades": unfiltered["total_trades"],
        },
        "attribution": attr,
    }
    out_path = out_dir / "audit-adx-filter-exit-block.json"
    out_path.write_text(json.dumps(summary, indent=2))
    print(f"\nWrote summary JSON → {out_path}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
