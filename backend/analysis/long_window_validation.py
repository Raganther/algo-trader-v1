"""Long-window validation of the position-management framework on real
metals/energy bear regimes (2009-2026 spot proxies via HistData).

For each symbol (XAUUSD / XAGUSD / WTIUSD) and each regime period, runs:
  1. Validated strategy
  2. Fully-random ablation (signal contribution control)
  3. Synthetic price inversion (regime-dependence control)
  4. Buy-and-hold (passive baseline)

Reads 15m bars from the price_data table (populated by
scripts/fetch_price_data_histdata.py).

Output: .claude/strategies/long-window-validation.md

Run:
    python3 -m backend.analysis.long_window_validation
"""

from __future__ import annotations

import sqlite3
import sys
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(ROOT))

from backend.engine.backtester import Backtester
from backend.strategies.trend_framework import TrendFrameworkStrategy

DB_PATH = Path(__file__).resolve().parent.parent / "research.db"
OUTPUT_PATH = ROOT / ".claude" / "strategies" / "long-window-validation.md"

VALIDATED_PARAMS = {
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
    "dynamic_adx": False,
}

REGIMES = {
    "XAUUSD": [
        ("2009 Mar – 2011 peak (bull run-up)", "2009-03-01", "2011-09-05"),
        ("2011 peak – 2012 transition", "2011-09-06", "2012-12-31"),
        ("2013 – 2015 bear", "2013-01-01", "2015-12-31"),
        ("2016 – 2019 chop / recovery", "2016-01-01", "2019-12-31"),
        ("2020 – 2026 bull (Alpaca overlap)", "2020-07-27", "2026-04-29"),
        ("Full window 2009 – 2026", "2009-03-01", "2026-04-29"),
    ],
    "XAGUSD": [
        ("2009 Sep – 2011 peak (bull run-up)", "2009-09-01", "2011-04-25"),
        ("2011 peak – 2012 collapse", "2011-04-26", "2012-12-31"),
        ("2013 – 2015 bear", "2013-01-01", "2015-12-31"),
        ("2016 – 2019 chop", "2016-01-01", "2019-12-31"),
        ("2020 – 2026 bull (Alpaca overlap)", "2020-07-27", "2026-04-29"),
        ("Full window 2009 – 2026", "2009-09-01", "2026-04-29"),
    ],
    "WTIUSD": [
        ("2010 Nov – 2014 stable / Brent rally", "2010-11-01", "2014-06-30"),
        ("2014 – 2016 oil collapse", "2014-07-01", "2016-12-31"),
        ("2017 – 2019 recovery / chop", "2017-01-01", "2019-12-31"),
        ("2020 COVID crash + recovery", "2020-01-01", "2021-12-31"),
        ("2022 – 2026 (modern)", "2022-01-01", "2026-04-29"),
        ("Full window 2010 – 2026", "2010-11-01", "2026-04-29"),
    ],
}

RANDOM_ABLATION_PARAMS = {**VALIDATED_PARAMS, "random_entry_prob": 0.15, "random_exit_prob": 0.10, "rng_seed": 42}


def load_15m(conn: sqlite3.Connection, symbol: str) -> pd.DataFrame:
    df = pd.read_sql_query(
        "SELECT timestamp, open, high, low, close, volume FROM price_data "
        "WHERE symbol=? ORDER BY timestamp",
        conn, params=(symbol,),
    )
    if df.empty:
        return df
    df.index = pd.to_datetime(df["timestamp"], unit="s", utc=True)
    df = df.drop(columns=["timestamp"])
    df.columns = ["Open", "High", "Low", "Close", "Volume"]
    return df


def slice_window(df: pd.DataFrame, start: str, end: str) -> pd.DataFrame:
    s = pd.Timestamp(start, tz="UTC")
    e = pd.Timestamp(end, tz="UTC")
    return df.loc[(df.index >= s) & (df.index <= e)].copy()


def invert_prices(df: pd.DataFrame) -> pd.DataFrame:
    """Reflect OHLC around close-mean pivot. Per runner.py:298-311."""
    if df.empty:
        return df
    pivot = df["Close"].mean()
    out = df.copy()
    out["Open"] = 2 * pivot - df["Open"]
    out["Close"] = 2 * pivot - df["Close"]
    out["High"] = 2 * pivot - df["Low"]
    out["Low"] = 2 * pivot - df["High"]
    return out


def run_strategy(data: pd.DataFrame, params: dict) -> dict:
    if len(data) < 100:
        return {"sharpe": None, "return_pct": None, "max_dd": None, "trades": 0, "win_rate": None}
    bt = Backtester(data, TrendFrameworkStrategy, parameters=params,
                    initial_capital=10000.0, spread=0.0003, execution_delay=0)
    r = bt.run()
    return {
        "sharpe": r.get("sharpe"),
        "return_pct": r.get("return_pct"),
        "max_dd": r.get("max_drawdown"),
        "trades": r.get("total_trades"),
        "win_rate": (r.get("win_rate") or 0) * 100,
    }


def buy_and_hold(data: pd.DataFrame) -> dict:
    if len(data) < 100:
        return {"sharpe": None, "return_pct": None, "max_dd": None}
    daily = data["Close"].resample("1D").last().dropna()
    if len(daily) < 2:
        return {"sharpe": None, "return_pct": None, "max_dd": None}
    daily_ret = daily.pct_change().dropna()
    sharpe = (daily_ret.mean() / daily_ret.std()) * (252 ** 0.5) if daily_ret.std() > 0 else 0.0
    cum = daily / daily.iloc[0]
    hwm = cum.cummax()
    dd = (hwm - cum) / hwm
    return {
        "sharpe": float(sharpe),
        "return_pct": float((daily.iloc[-1] / daily.iloc[0] - 1) * 100),
        "max_dd": float(dd.max() * 100),
    }


def fmt(v, fmt_str=":+.2f"):
    if v is None:
        return "—"
    return f"{v:{fmt_str.lstrip(':')}}"


def render_section(symbol: str, regime_results: list) -> str:
    lines = [f"## {symbol}", ""]
    lines.append("| Period | Validated Sharpe | Validated Ret | DD | Trades | WR | Random Sharpe | Inverted Sharpe | B&H Sharpe |")
    lines.append("|---|---|---|---|---|---|---|---|---|")
    for row in regime_results:
        v = row["validated"]
        rnd = row["random"]
        inv = row["inverted"]
        bh = row["buy_hold"]
        lines.append(
            f"| {row['period']} "
            f"| {fmt(v['sharpe'])} | {fmt(v['return_pct'])}% | {fmt(v['max_dd'], ':.2f')}% | {v['trades'] or 0} | {fmt(v['win_rate'], ':.0f')}% "
            f"| {fmt(rnd['sharpe'])} "
            f"| {fmt(inv['sharpe'])} "
            f"| {fmt(bh['sharpe'])} |"
        )
    lines.append("")
    return "\n".join(lines)


def interpret(all_results: dict) -> str:
    """Generate a short interpretation paragraph based on the numbers."""
    lines = ["## Interpretation", ""]
    for symbol, regime_results in all_results.items():
        bear = next((r for r in regime_results if "bear" in r["period"].lower() or "collapse" in r["period"].lower()), None)
        bull = next((r for r in regime_results if "bull" in r["period"].lower() and "alpaca" in r["period"].lower()), None)
        if bear and bull:
            bear_v = bear["validated"]["sharpe"]
            bear_inv = bear["inverted"]["sharpe"]
            bull_v = bull["validated"]["sharpe"]
            lines.append(
                f"**{symbol}**: bull-window Sharpe {fmt(bull_v)}, bear-window Sharpe {fmt(bear_v)}. "
                f"Bear-window inversion Sharpe {fmt(bear_inv)} (regime-dependence diagnostic — if bear inversion ≈ bear validated, "
                f"the framework is direction-agnostic in that regime; if very different, the framework's edge in the bear is still directional)."
            )
            lines.append("")
    return "\n".join(lines)


def main() -> None:
    conn = sqlite3.connect(DB_PATH)
    all_results = {}

    for symbol, regimes in REGIMES.items():
        full_df = load_15m(conn, symbol)
        if full_df.empty:
            print(f"[skip] {symbol}: no 15m data in price_data — run scripts/fetch_price_data_histdata.py first")
            continue
        print(f"\n=== {symbol}: {len(full_df)} bars from {full_df.index[0]} to {full_df.index[-1]} ===")

        regime_rows = []
        for label, start, end in regimes:
            slice_df = slice_window(full_df, start, end)
            if len(slice_df) < 200:
                print(f"  [skip] {label}: only {len(slice_df)} bars")
                continue
            print(f"  {label} ({len(slice_df)} bars)")
            row = {"period": label}
            row["validated"] = run_strategy(slice_df, VALIDATED_PARAMS)
            row["random"] = run_strategy(slice_df, RANDOM_ABLATION_PARAMS)
            row["inverted"] = run_strategy(invert_prices(slice_df), VALIDATED_PARAMS)
            row["buy_hold"] = buy_and_hold(slice_df)
            print(
                f"    validated S={fmt(row['validated']['sharpe'])}  "
                f"random S={fmt(row['random']['sharpe'])}  "
                f"inverted S={fmt(row['inverted']['sharpe'])}  "
                f"B&H S={fmt(row['buy_hold']['sharpe'])}"
            )
            regime_rows.append(row)
        all_results[symbol] = regime_rows

    conn.close()

    out = []
    out.append("Status: current | Epistemic: spot-proxy directional evidence | Last verified: 2026-04-29")
    out.append("")
    out.append("# Long-Window Validation — HistData Spot Proxies")
    out.append("")
    out.append("Validated 15m strategy applied to spot price proxies covering real bear regimes "
               "missing from the Alpaca window (2020-2026 only). HistData via philipperemy/FX-1-Minute-Data.")
    out.append("")
    out.append("**Caveats baked in:** spot prices ≠ ETF prices (no expense ratio drag, no tracking error, "
               "24h coverage filtered to RTH 13:30-20:00 UTC). Numbers are *directional/regime-shape evidence*, "
               "not exact P&L claims about live ETFs.")
    out.append("")
    out.append("**Sample sizing:** all backtests use 15m bars, validated recipe (rsi 7, stoch 14, OB 80, OS 15, "
               "ADX 20, sl_atr 2.0, trail_atr 2.0, trail_after 10 bars, min_hold 10 bars, skip Mon, dynamic_adx false), "
               "spread 0.0003, delay 0, initial capital $10k. Random ablation uses random_entry_prob=0.15, "
               "random_exit_prob=0.10, seed 42. Inversion reflects OHLC around close-mean pivot.")
    out.append("")
    for symbol in REGIMES:
        if symbol in all_results:
            out.append(render_section(symbol, all_results[symbol]))
    out.append(interpret(all_results))

    OUTPUT_PATH.write_text("\n".join(out))
    print(f"\nWrote {OUTPUT_PATH}")


if __name__ == "__main__":
    main()
