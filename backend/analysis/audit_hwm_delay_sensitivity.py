"""Audit: is HWM trail anchor structurally insensitive to a 1-bar phase shift?

Falsification test for the May 7 mechanism claim in `trail-anchor-hwm.md`:
"HWM is structurally insensitive to the 1-bar phase shift that close-anchor suffers from."

Approach: data-shift preprocessing (Option B from the audit plan). We can't fix the
broken `--delay 1` plumbing without a multi-day refactor, so instead we pre-shift
the OHLCV by one 15m bar and run the same backtest at delay=0. Strategy code is
untouched; only the input data is phase-shifted.

Decision rule:
    Δsharpe(anchor) := Sharpe(anchor, shift=0) − Sharpe(anchor, shift=1)
    H₀ (claim) predicts Δsharpe(close) ≈ 0.7 (large), Δsharpe(hwm) ≈ 0 (small).
    Falsified if Δsharpe(hwm) ≥ 0.5 × Δsharpe(close).

Run:
    set -a && source .env && set +a
    python3 -m backend.analysis.audit_hwm_delay_sensitivity
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


def shift_ohlcv(symbol_data: dict[str, pd.DataFrame], n: int) -> dict[str, pd.DataFrame]:
    """Shift each symbol's OHLCV by `n` bars. The strategy at row i now "sees"
    what was true at row i-n — simulating live's polling delay where the
    strategy reacts ~1 bar late.

    The index is preserved so downstream timestamp logic (skip-Mon, weekly
    rotation, equity time-series) is unchanged. Only the OHLCV values are
    aligned to a stale bar.
    """
    if n == 0:
        return symbol_data
    out: dict[str, pd.DataFrame] = {}
    for sym, df in symbol_data.items():
        shifted = df.shift(n).dropna()
        out[sym] = shifted
    return out


def run_one(symbol_data: dict[str, pd.DataFrame], anchor: str, shift: int) -> dict:
    """Run a single portfolio backtest cell. Returns the standard results dict."""
    correlation_sizing.DISCOUNT_ENABLED = True
    correlation_sizing.CLUSTER_CAP_ENABLED = False
    correlation_sizing.PORTFOLIO_CAP_ENABLED = True
    correlation_sizing.PORTFOLIO_CAP_FRAC = 1.0

    params = dict(PARAMS_BASE)
    params["trail_anchor"] = anchor

    data = shift_ohlcv(symbol_data, shift)
    pr = PortfolioRunner(
        symbol_data=data,
        strategy_class=StochRSIMeanReversionStrategy,
        parameters=params,
        initial_capital=INITIAL,
        spread=SPREAD,
    )
    return pr.run()


def attribute_trades(close_trades: list[dict], hwm_trades: list[dict]) -> dict:
    """Classify the difference between close-anchored and HWM-anchored trades
    at shift=0. Trades match on (entry_time, symbol).
    """
    def key(t: dict) -> tuple:
        et = t.get("entry_time") or t.get("entry_timestamp") or t.get("entry_idx")
        return (et, t.get("symbol"))

    by_close = {key(t): t for t in close_trades}
    by_hwm = {key(t): t for t in hwm_trades}

    close_keys = set(by_close)
    hwm_keys = set(by_hwm)

    only_close = close_keys - hwm_keys
    only_hwm = hwm_keys - close_keys
    common = close_keys & hwm_keys

    bar_aligned = 0
    held_longer = 0
    held_shorter = 0
    pnl_diff_common = 0.0
    for k in common:
        c, h = by_close[k], by_hwm[k]
        c_pnl = float(c.get("pnl", 0.0))
        h_pnl = float(h.get("pnl", 0.0))
        pnl_diff_common += h_pnl - c_pnl
        c_exit = c.get("timestamp")
        h_exit = h.get("timestamp")
        if c_exit == h_exit and c.get("exit_reason") == h.get("exit_reason"):
            bar_aligned += 1
        elif h_exit is not None and c_exit is not None and h_exit > c_exit:
            held_longer += 1
        else:
            held_shorter += 1

    pnl_only_close = sum(float(by_close[k].get("pnl", 0.0)) for k in only_close)
    pnl_only_hwm = sum(float(by_hwm[k].get("pnl", 0.0)) for k in only_hwm)

    return {
        "n_close_trades": len(close_keys),
        "n_hwm_trades": len(hwm_keys),
        "common": len(common),
        "only_close": len(only_close),
        "only_hwm": len(only_hwm),
        "common_bar_aligned": bar_aligned,
        "common_hwm_held_longer": held_longer,
        "common_hwm_held_shorter": held_shorter,
        "pnl_diff_common": round(pnl_diff_common, 2),
        "pnl_only_close": round(pnl_only_close, 2),
        "pnl_only_hwm": round(pnl_only_hwm, 2),
    }


def main() -> int:
    print(f"Loading 7-bot 15m data from research.db cache ({START} → {END})…")
    symbol_data = load_symbol_data()
    for sym, df in symbol_data.items():
        print(f"  {sym}: {len(df)} bars  {df.index[0]} → {df.index[-1]}")
    print()

    cells: dict[tuple[str, int], dict] = {}
    for shift in (0, 1):
        for anchor in ("close", "hwm"):
            print(f"=== Running anchor={anchor}  shift={shift} ===")
            res = run_one(symbol_data, anchor, shift)
            cells[(anchor, shift)] = res
            print(
                f"  return {res['return_pct']:.2f}%  Sharpe {res['sharpe']:.2f}  "
                f"DD {res['max_drawdown']:.2f}%  trades {res['total_trades']}"
            )
            print()

    # 2x2 table
    print("\n=== 2×2 Sharpe matrix ===")
    print(f"{'':<12}{'shift=0':>14}{'shift=1':>14}{'Δsharpe':>14}")
    for anchor in ("close", "hwm"):
        s0 = cells[(anchor, 0)]["sharpe"]
        s1 = cells[(anchor, 1)]["sharpe"]
        print(f"{anchor:<12}{s0:>14.2f}{s1:>14.2f}{(s0-s1):>14.2f}")

    print("\n=== 2×2 Return matrix ===")
    print(f"{'':<12}{'shift=0':>14}{'shift=1':>14}")
    for anchor in ("close", "hwm"):
        r0 = cells[(anchor, 0)]["return_pct"]
        r1 = cells[(anchor, 1)]["return_pct"]
        print(f"{anchor:<12}{r0:>13.2f}%{r1:>13.2f}%")

    print("\n=== 2×2 Max DD matrix ===")
    print(f"{'':<12}{'shift=0':>14}{'shift=1':>14}")
    for anchor in ("close", "hwm"):
        d0 = cells[(anchor, 0)]["max_drawdown"]
        d1 = cells[(anchor, 1)]["max_drawdown"]
        print(f"{anchor:<12}{d0:>13.2f}%{d1:>13.2f}%")

    delta_close = cells[("close", 0)]["sharpe"] - cells[("close", 1)]["sharpe"]
    delta_hwm = cells[("hwm", 0)]["sharpe"] - cells[("hwm", 1)]["sharpe"]
    print()
    print(f"Δsharpe(close) = {delta_close:+.2f}")
    print(f"Δsharpe(hwm)   = {delta_hwm:+.2f}")
    print()
    threshold = 0.5 * abs(delta_close)
    if abs(delta_hwm) >= threshold:
        verdict = "FALSIFIED"
        explain = (
            f"|Δsharpe(hwm)|={abs(delta_hwm):.2f} ≥ 0.5×|Δsharpe(close)|={threshold:.2f} — "
            f"HWM is similarly sensitive to the phase shift. The +0.78 backtest lift "
            f"likely comes from better signal extraction (intra-trade extremes), not "
            f"delay-immunity. Live HWM should still be discounted by ~0.7 Sharpe."
        )
    else:
        verdict = "SUPPORTED"
        explain = (
            f"|Δsharpe(hwm)|={abs(delta_hwm):.2f} < 0.5×|Δsharpe(close)|={threshold:.2f} — "
            f"HWM resists the phase shift while close-anchored does not. Mechanism "
            f"claim consistent with data. Live HWM tripwires at 5.73 are reasonable."
        )
    print(f"=== VERDICT: {verdict} ===")
    print(explain)

    # Per-trade attribution at shift=0
    attr = attribute_trades(
        cells[("close", 0)].get("trade_history", []),
        cells[("hwm", 0)].get("trade_history", []),
    )
    print("\n=== Per-trade attribution (shift=0, close vs hwm) ===")
    for k, v in attr.items():
        print(f"  {k:<28} {v}")

    # Persist a JSON record alongside the writeup for future reference
    out_dir = Path(__file__).resolve().parents[2] / ".claude" / "calibration"
    out_dir.mkdir(parents=True, exist_ok=True)
    summary = {
        "params": PARAMS_BASE,
        "window": {"start": START, "end": END, "initial": INITIAL, "spread": SPREAD},
        "cells": {
            f"{a}_shift{s}": {
                "return_pct": cells[(a, s)]["return_pct"],
                "sharpe": cells[(a, s)]["sharpe"],
                "max_drawdown": cells[(a, s)]["max_drawdown"],
                "total_trades": cells[(a, s)]["total_trades"],
            }
            for a in ("close", "hwm")
            for s in (0, 1)
        },
        "delta_sharpe_close": round(delta_close, 4),
        "delta_sharpe_hwm": round(delta_hwm, 4),
        "verdict": verdict,
        "attribution": attr,
    }
    out_path = out_dir / "audit-hwm-delay-mechanism.json"
    out_path.write_text(json.dumps(summary, indent=2))
    print(f"\nWrote summary JSON → {out_path}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
