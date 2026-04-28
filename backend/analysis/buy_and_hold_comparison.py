"""Buy-and-hold comparison for the validated/boundary asset universe.

Run:
    python3 -m backend.analysis.buy_and_hold_comparison

Loads 15m close prices from research.db for each symbol, resamples to daily,
computes B&H return, max drawdown, and annualised Sharpe (daily × sqrt(252)) —
same convention as backend/engine/backtester.py.

Output: comparison table written to stdout in markdown form, ready to paste
into research-log.md alongside the strategy Sharpes from CLAUDE.md.
"""

from __future__ import annotations

import sqlite3
from pathlib import Path

import pandas as pd

DB_PATH = Path(__file__).resolve().parent.parent / "research.db"

SYMBOLS = [
    "GLD", "SLV", "GDX", "IAU", "XLE", "OIH", "XBI", "XOP",
    "SPY", "QQQ", "IWM", "DIA",
]

# Strategy Sharpes verified Apr 28 (full-strategy, 2020 → Apr 27 2026, validated recipe).
STRATEGY_SHARPE = {
    "GLD": 2.48, "SLV": 2.46, "GDX": 2.46, "IAU": 1.95,
    "XLE": 2.30, "OIH": 2.33, "XBI": 2.18, "XOP": 1.98,
    "SPY": 1.36, "QQQ": 1.45, "IWM": 2.30, "DIA": 1.83,
}
STRATEGY_RETURN = {
    "GLD": 45.13, "SLV": 131.04, "GDX": 133.27, "IAU": 39.34,
    "XLE": 85.70, "OIH": 146.06, "XBI": 84.87, "XOP": 91.65,
    "SPY": 21.94, "QQQ": 27.17, "IWM": 57.42, "DIA": 27.32,
}
STRATEGY_DD = {
    "GLD": 1.22, "SLV": 2.00, "GDX": 2.01, "IAU": 1.32,
    "XLE": 3.27, "OIH": 2.96, "XBI": 2.44, "XOP": 3.29,
    "SPY": 2.02, "QQQ": 2.19, "IWM": 1.43, "DIA": 2.56,
}


def load_daily_close(conn: sqlite3.Connection, symbol: str) -> pd.Series:
    df = pd.read_sql_query(
        "SELECT timestamp, close FROM price_data WHERE symbol=? ORDER BY timestamp",
        conn, params=(symbol,),
    )
    df["ts"] = pd.to_datetime(df["timestamp"], unit="s")
    df = df.set_index("ts").sort_index()
    daily = df["close"].resample("1D").last().dropna()
    return daily


def bh_metrics(daily: pd.Series) -> dict:
    if len(daily) < 2:
        return {"return_pct": 0.0, "max_dd_pct": 0.0, "sharpe": 0.0,
                "start": None, "end": None, "n_days": 0}
    daily_ret = daily.pct_change().dropna()
    sharpe = 0.0
    if daily_ret.std() > 0:
        sharpe = (daily_ret.mean() / daily_ret.std()) * (252 ** 0.5)
    cum = daily / daily.iloc[0]
    hwm = cum.cummax()
    dd = (hwm - cum) / hwm
    return {
        "return_pct": (daily.iloc[-1] / daily.iloc[0] - 1) * 100,
        "max_dd_pct": dd.max() * 100,
        "sharpe": float(sharpe),
        "start": daily.index[0].strftime("%Y-%m-%d"),
        "end": daily.index[-1].strftime("%Y-%m-%d"),
        "n_days": len(daily),
    }


def main() -> None:
    conn = sqlite3.connect(DB_PATH)
    rows = []
    for sym in SYMBOLS:
        daily = load_daily_close(conn, sym)
        if daily.empty:
            print(f"[skip] {sym}: no 15m data in price_data")
            continue
        m = bh_metrics(daily)
        rows.append({
            "symbol": sym,
            "bh_return": m["return_pct"],
            "bh_dd": m["max_dd_pct"],
            "bh_sharpe": m["sharpe"],
            "start": m["start"],
            "end": m["end"],
            "strat_return": STRATEGY_RETURN.get(sym),
            "strat_dd": STRATEGY_DD.get(sym),
            "strat_sharpe": STRATEGY_SHARPE.get(sym),
        })
    conn.close()

    print()
    print("# Buy-and-Hold vs Strategy — Apr 28 2026")
    print()
    print(f"Window: 15m data resampled to daily close. First-bar -> last-bar return on each symbol.")
    print()
    print("| Symbol | B&H Return | B&H DD | B&H Sharpe | Strat Return | Strat DD | Strat Sharpe | Δ Sharpe | Δ DD |")
    print("|---|---|---|---|---|---|---|---|---|")
    for r in rows:
        ds = r["strat_sharpe"] - r["bh_sharpe"] if r["strat_sharpe"] is not None else None
        dd_ratio = r["bh_dd"] / r["strat_dd"] if r["strat_dd"] else 0
        print(
            f"| {r['symbol']} | {r['bh_return']:+.2f}% | {r['bh_dd']:.2f}% | {r['bh_sharpe']:.2f} "
            f"| {r['strat_return']:+.2f}% | {r['strat_dd']:.2f}% | {r['strat_sharpe']:.2f} "
            f"| {ds:+.2f} | {dd_ratio:.1f}× |"
        )
    print()
    print("Δ Sharpe = strategy Sharpe − B&H Sharpe (positive = strategy adds risk-adjusted value)")
    print("Δ DD = ratio B&H DD / strategy DD (higher = strategy provides more drawdown protection)")
    print()


if __name__ == "__main__":
    main()
