"""Portfolio replay for regime-aware sizing variants.

Run:
    python3 -m backend.analysis.regime_sizing_portfolio

Diagnostic-only. Reuses validated StochRSI Enhanced trades for GLD/IAU/SLV/GDX,
then replays realized P&L on a shared portfolio timeline with simple regime
multipliers. This does not change live strategy code.
"""

from __future__ import annotations

import argparse
import sqlite3
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import pandas as pd

from backend.analysis.stochrsi_regime_performance import (
    DB_PATH,
    HIGH_VOL,
    RANGING,
    SYMBOLS,
    TRENDING_DOWN,
    TRENDING_UP,
    build_trade_frame,
    fmt_money,
    fmt_pct,
    fmt_sharpe,
)


ROOT = Path(__file__).resolve().parents[2]
MD_PATH = ROOT / ".claude" / "strategies" / "regime-sizing-portfolio-diagnostic.md"
PORTFOLIO_CAPITAL = 40000.0

VARIANTS = {
    "baseline": {
        RANGING: 1.0,
        TRENDING_UP: 1.0,
        TRENDING_DOWN: 1.0,
        HIGH_VOL: 1.0,
    },
    "conservative": {
        RANGING: 1.0,
        TRENDING_UP: 0.75,
        TRENDING_DOWN: 0.5,
        HIGH_VOL: 0.5,
    },
    "aggressive_filter": {
        RANGING: 1.0,
        TRENDING_UP: 0.75,
        TRENDING_DOWN: 0.25,
        HIGH_VOL: 0.25,
    },
    "high_vol_only": {
        RANGING: 1.0,
        TRENDING_UP: 1.0,
        TRENDING_DOWN: 1.0,
        HIGH_VOL: 0.5,
    },
}


def max_drawdown(equity: pd.Series) -> tuple[float, float]:
    if equity.empty:
        return 0.0, 0.0
    peaks = equity.cummax()
    drawdown = peaks - equity
    dd_dollars = float(drawdown.max())
    dd_pct = float((drawdown / peaks).max() * 100)
    return dd_dollars, dd_pct


def variant_replay(trades: pd.DataFrame, name: str, multipliers: dict[str, float], start: str, end: str) -> dict:
    replay = trades.copy()
    replay["multiplier"] = replay["regime"].map(multipliers).fillna(1.0)
    replay["scaled_pnl"] = replay["pnl"] * replay["multiplier"]
    replay["realized_time"] = replay["exit_time"].fillna(replay["entry_time"])
    replay = replay.sort_values(["realized_time", "symbol", "entry_time"]).reset_index(drop=True)

    equity = PORTFOLIO_CAPITAL + replay["scaled_pnl"].cumsum()
    dd_dollars, dd_pct = max_drawdown(equity)

    daily_index = pd.date_range(start=start, end=end, freq="D", tz="UTC")
    daily_pnl = (
        replay.assign(day=replay["realized_time"].dt.normalize())
        .groupby("day")["scaled_pnl"]
        .sum()
        .reindex(daily_index, fill_value=0.0)
    )
    trading_daily_pnl = daily_pnl[daily_pnl.index.dayofweek < 5]
    daily_std = float(trading_daily_pnl.std(ddof=1))
    daily_sharpe = (
        float((trading_daily_pnl.mean() / daily_std) * np.sqrt(252))
        if daily_std > 0
        else 0.0
    )

    weekly_pnl = daily_pnl.resample("W-FRI").sum()
    affected = replay[replay["multiplier"] != 1.0]
    return {
        "variant": name,
        "total_pnl": float(replay["scaled_pnl"].sum()),
        "return_pct": float(replay["scaled_pnl"].sum() / PORTFOLIO_CAPITAL * 100),
        "max_dd": dd_dollars,
        "max_dd_pct": dd_pct,
        "daily_sharpe": daily_sharpe,
        "worst_day": float(daily_pnl.min()),
        "worst_week": float(weekly_pnl.min()),
        "trades": int(len(replay)),
        "affected_trades": int(len(affected)),
        "avg_multiplier": float(replay["multiplier"].mean()),
    }


def build_results(trades: pd.DataFrame, start: str, end: str) -> pd.DataFrame:
    rows = [variant_replay(trades, name, mults, start, end) for name, mults in VARIANTS.items()]
    results = pd.DataFrame(rows)
    baseline = results.loc[results["variant"] == "baseline"].iloc[0]
    results["pnl_vs_baseline"] = results["total_pnl"] - baseline["total_pnl"]
    results["dd_vs_baseline"] = results["max_dd"] - baseline["max_dd"]
    return results


def print_console(results: pd.DataFrame, coverage: dict[str, str], trade_count: int) -> None:
    print("Data coverage:")
    for symbol in SYMBOLS:
        print(f"  {symbol}: {coverage.get(symbol, 'missing')}")
    print(f"\nClosed trades replayed: {trade_count}")
    display = results.copy()
    for col in ["total_pnl", "max_dd", "worst_day", "worst_week", "pnl_vs_baseline", "dd_vs_baseline"]:
        display[col] = display[col].map(fmt_money)
    display["return_pct"] = display["return_pct"].map(lambda x: f"{x:.2f}%")
    display["max_dd_pct"] = display["max_dd_pct"].map(lambda x: f"{x:.2f}%")
    display["daily_sharpe"] = display["daily_sharpe"].map(fmt_sharpe)
    display["avg_multiplier"] = display["avg_multiplier"].map(lambda x: f"{x:.2f}x")
    print()
    print(display.to_string(index=False))


def write_markdown(results: pd.DataFrame, coverage: dict[str, str], trade_count: int, start: str, end: str) -> None:
    now = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    lines = [
        f"Status: current | Epistemic: confirmed | Last verified: {now}",
        "",
        "# Regime Sizing Portfolio Diagnostic",
        "",
        "## Knowledge",
        "",
        f"Window: `{start}` to `{end}`. Source: validated StochRSI Enhanced trades "
        "for `GLD`, `IAU`, `SLV`, `GDX`, replayed on one realized-P&L timeline.",
        "",
        "This is diagnostic-only. It scales closed-trade P&L by entry-regime multipliers; "
        "it does not change strategy logic, model intratrade cash constraints, or deploy live sizing.",
        "",
        "Portfolio capital basis: `$40,000` (`$10,000` per symbol sleeve, matching the "
        "single-symbol backtests).",
        "",
        "## Data Coverage",
        "",
        "| Symbol | Intraday coverage used |",
        "|--------|------------------------|",
    ]
    for symbol in SYMBOLS:
        lines.append(f"| {symbol} | {coverage.get(symbol, 'missing')} |")

    lines += [
        "",
        f"Closed trades replayed: **{trade_count:,}**.",
        "",
        "## Variants",
        "",
        "| Variant | RANGING | TRENDING_UP | TRENDING_DOWN | HIGH_VOL |",
        "|---------|---------|-------------|---------------|----------|",
    ]
    for name, mults in VARIANTS.items():
        lines.append(
            f"| {name} | {mults[RANGING]:.2f}x | {mults[TRENDING_UP]:.2f}x | "
            f"{mults[TRENDING_DOWN]:.2f}x | {mults[HIGH_VOL]:.2f}x |"
        )

    lines += [
        "",
        "## Portfolio Results",
        "",
        "| Variant | P&L | Return | Max DD | Max DD % | Daily Sharpe | Worst day | Worst week | Affected trades | P&L vs base | DD vs base |",
        "|---------|-----|--------|--------|----------|--------------|-----------|------------|-----------------|-------------|------------|",
    ]
    for _, row in results.iterrows():
        lines.append(
            f"| {row['variant']} | {fmt_money(row['total_pnl'])} | {row['return_pct']:.2f}% | "
            f"{fmt_money(row['max_dd'])} | {row['max_dd_pct']:.2f}% | {fmt_sharpe(row['daily_sharpe'])} | "
            f"{fmt_money(row['worst_day'])} | {fmt_money(row['worst_week'])} | "
            f"{int(row['affected_trades'])} | {fmt_money(row['pnl_vs_baseline'])} | "
            f"{fmt_money(row['dd_vs_baseline'])} |"
        )

    lines += [
        "",
        "## Diagnostic Read",
        "",
    ]
    baseline = results.loc[results["variant"] == "baseline"].iloc[0]
    best_dd = results.sort_values("max_dd").iloc[0]
    best_sharpe = results.sort_values("daily_sharpe", ascending=False).iloc[0]
    high_vol = results.loc[results["variant"] == "high_vol_only"].iloc[0]
    lines += [
        f"- Baseline remains strongest on raw P&L: {fmt_money(baseline['total_pnl'])}.",
        f"- Best drawdown variant is `{best_dd['variant']}` at {fmt_money(best_dd['max_dd'])} max DD.",
        f"- Best daily Sharpe variant is `{best_sharpe['variant']}` at {fmt_sharpe(best_sharpe['daily_sharpe'])}.",
        f"- `high_vol_only` changes {int(high_vol['affected_trades'])} trades and gives "
        f"{fmt_money(high_vol['pnl_vs_baseline'])} P&L vs baseline with "
        f"{fmt_money(high_vol['dd_vs_baseline'])} DD change.",
        "",
        "Decision implication: only promote regime sizing if a variant materially improves "
        "drawdown-adjusted returns. If reduced-risk variants mostly cut P&L without meaningful "
        "drawdown relief, keep regime as dashboard/context or a narrow high-vol caution signal.",
    ]
    MD_PATH.write_text("\n".join(lines).rstrip() + "\n")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--symbols", default=",".join(SYMBOLS))
    parser.add_argument("--start", default="2020-01-01")
    parser.add_argument("--end", default="2025-12-31")
    parser.add_argument("--no-markdown", action="store_true")
    args = parser.parse_args()

    symbols = [s.strip().upper() for s in args.symbols.split(",") if s.strip()]
    with sqlite3.connect(DB_PATH) as conn:
        trades, coverage = build_trade_frame(conn, symbols, args.start, args.end)
    results = build_results(trades, args.start, args.end)
    print_console(results, coverage, len(trades))
    if not args.no_markdown:
        write_markdown(results, coverage, len(trades), args.start, args.end)
        print(f"\nWrote {MD_PATH}")


if __name__ == "__main__":
    main()
