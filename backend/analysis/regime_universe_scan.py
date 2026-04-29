"""30-asset regime universe scan.

Run: python3 -m backend.analysis.regime_universe_scan

For each asset in UNIVERSE, ensure daily bars exist in price_data_daily
(auto-fetch via yfinance if missing or stale by >5 days), classify the regime
on each bar, then report the current regime, duration in current regime, and
60-day persistence. Writes a snapshot to .claude/strategies/regime-universe-snapshot.md.

Decision rule: if 8-15 of N assets are in a "favourable" regime (TRENDING_UP
or sustained TRENDING_DOWN), rotation has selection power. <=3 or >=25 means
the universe lacks discriminating signal on this date.
"""
from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path

import pandas as pd

from backend.database import DatabaseManager
from backend.indicators.regime import (
    classify_regime,
    RANGING,
    TRENDING_UP,
    TRENDING_DOWN,
    HIGH_VOL,
)


UNIVERSE = [
    # Gold cluster
    "GLD", "IAU", "SLV", "GDX",
    # Energy
    "XLE", "OIH", "XOP",
    # Sector SPDRs
    "XLF", "XLK", "XLI", "XLV", "XLY", "XLP", "XLU", "XLB",
    # Biotech / health
    "XBI", "IBB",
    # Broad indices
    "SPY", "QQQ", "IWM", "DIA",
    # Niche / diversifiers
    "KRE", "SMH", "ITA", "ARKK",
    "EFA", "EEM", "EWZ",
    "GBTC", "TLT", "UUP", "VXX", "DBA",
]

REGIMES = [RANGING, TRENDING_UP, TRENDING_DOWN, HIGH_VOL]
FAVOURABLE = {TRENDING_UP, TRENDING_DOWN}  # sustained directional moves
PERSISTENCE_LOOKBACK = 60
STALE_DAYS = 5
DEFAULT_FETCH_START = "2010-01-01"

ROOT = Path(__file__).resolve().parents[2]
MD_PATH = ROOT / ".claude" / "strategies" / "regime-universe-snapshot.md"


def ensure_data(db: DatabaseManager, symbol: str) -> str | None:
    """Ensure symbol has reasonably fresh daily bars. Returns status string for logging."""
    min_ts, max_ts, count = db.get_daily_bars_range(symbol)
    today_ts = int(datetime.now(timezone.utc).replace(hour=0, minute=0, second=0, microsecond=0).timestamp())
    needs_fetch = (count == 0) or (max_ts is None) or ((today_ts - max_ts) > STALE_DAYS * 86400)

    if not needs_fetch:
        return f"{symbol}: db hit ({count} bars)"

    try:
        import yfinance as yf
    except ImportError:
        return f"{symbol}: SKIP — yfinance not installed and DB has {count} bars"

    start = DEFAULT_FETCH_START
    if max_ts:
        start = datetime.fromtimestamp(max_ts, tz=timezone.utc).strftime("%Y-%m-%d")
    end = datetime.now(timezone.utc).strftime("%Y-%m-%d")

    try:
        raw = yf.download(symbol, start=start, end=end, interval="1d",
                          auto_adjust=True, progress=False)
    except Exception as e:
        return f"{symbol}: FETCH ERROR — {e}"

    if raw is None or raw.empty:
        return f"{symbol}: no yfinance data"

    if isinstance(raw.columns, pd.MultiIndex):
        raw.columns = raw.columns.get_level_values(0)

    df = raw[["Open", "High", "Low", "Close", "Volume"]].copy()
    df.index = pd.to_datetime(df.index).tz_localize("UTC").normalize()
    df = df.dropna()
    saved = db.save_daily_bars(symbol, df)
    _, max_ts2, count2 = db.get_daily_bars_range(symbol)
    last = datetime.fromtimestamp(max_ts2, tz=timezone.utc).strftime("%Y-%m-%d") if max_ts2 else "?"
    return f"{symbol}: fetched +{saved} → {count2} bars (last {last})"


def current_regime_duration(regimes: pd.Series) -> int:
    """Count bars at the tail that share the last bar's label."""
    if regimes.empty:
        return 0
    last = regimes.iloc[-1]
    n = 0
    for label in reversed(regimes.tolist()):
        if label == last:
            n += 1
        else:
            break
    return n


def regime_persistence(regimes: pd.Series, lookback: int = PERSISTENCE_LOOKBACK) -> float:
    """Fraction of last `lookback` bars matching the current regime."""
    if regimes.empty:
        return 0.0
    tail = regimes.iloc[-lookback:]
    last = regimes.iloc[-1]
    return float((tail == last).sum()) / float(len(tail))


def scan_symbol(db: DatabaseManager, symbol: str) -> dict | None:
    df = db.get_daily_bars(symbol)
    if df.empty or len(df) < 220:  # need >200 for SMA
        return None
    regimes = classify_regime(df)
    last_idx = df.index[-1]
    return {
        "symbol": symbol,
        "regime": regimes.iloc[-1],
        "duration_bars": current_regime_duration(regimes),
        "persistence_60d": regime_persistence(regimes),
        "last_bar": last_idx.strftime("%Y-%m-%d"),
        "n_bars": len(df),
    }


def build_markdown(rows: list[dict], fetch_log: list[str]) -> str:
    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    n_total = len(rows)

    counts = {r: 0 for r in REGIMES}
    for row in rows:
        counts[row["regime"]] = counts.get(row["regime"], 0) + 1

    favourable = sum(counts[r] for r in FAVOURABLE)

    if favourable <= 3:
        verdict = (
            f"**Verdict: NARROW** — only {favourable}/{n_total} assets in a favourable "
            "(TRENDING) regime today. Universe may be too narrow or the day is "
            "broadly chop/HIGH_VOL. Rotation lift today would be limited."
        )
    elif favourable >= 25:
        verdict = (
            f"**Verdict: SATURATED** — {favourable}/{n_total} favourable. Almost everything "
            "is trending; rotation has little selection power on a day like this."
        )
    elif 8 <= favourable <= 15:
        verdict = (
            f"**Verdict: SELECTIVE** — {favourable}/{n_total} favourable. This is the regime "
            "where rotation has meaningful lift: enough assets to pick from, not so many "
            "that picking is irrelevant."
        )
    else:
        verdict = (
            f"**Verdict: BORDERLINE** — {favourable}/{n_total} favourable. Outside the 8–15 "
            "selective band but not extreme. Repeat the scan over a week to characterise."
        )

    lines = []
    lines.append(f"Status: current | Epistemic: confirmed | Last verified: {today}")
    lines.append("")
    lines.append("# Regime Universe Snapshot")
    lines.append("")
    lines.append(
        "Daily-bar regime classification across a ~30-asset ETF universe. "
        "First step in the Apr 29 strategic direction (Regime-Aware Asset Rotation, "
        "see `research-roadmap.md`). Tells us whether the universe has selection "
        "power — i.e. whether on a typical day there is a useful subset of assets "
        "in a strong regime worth rotating capital toward."
    )
    lines.append("")
    lines.append(f"- Universe size: {n_total} (target ~30)")
    lines.append(f"- Classifier: `backend/indicators/regime.py:classify_regime` (defaults: ADX 14 / SMA 200 / ATR 14, ADX threshold 25, ATR vol multiplier 1.5x)")
    lines.append(f"- Persistence window: last {PERSISTENCE_LOOKBACK} bars")
    lines.append(f"- Source: `price_data_daily` (yfinance, auto-fetched if stale > {STALE_DAYS} days)")
    lines.append("")

    lines.append("## Today's regime distribution")
    lines.append("")
    lines.append("| Regime | Count | % of universe |")
    lines.append("|---|---:|---:|")
    for r in REGIMES:
        c = counts.get(r, 0)
        lines.append(f"| {r} | {c} | {c / n_total * 100:.1f}% |")
    lines.append(f"| **Favourable (TRENDING)** | **{favourable}** | **{favourable / n_total * 100:.1f}%** |")
    lines.append("")
    lines.append(verdict)
    lines.append("")

    lines.append("## Per-asset detail")
    lines.append("")
    lines.append("| Symbol | Regime | Days in regime | 60d persistence | Last bar | Bars |")
    lines.append("|---|---|---:|---:|---|---:|")
    rows_sorted = sorted(rows, key=lambda r: (REGIMES.index(r["regime"]) if r["regime"] in REGIMES else 99, r["symbol"]))
    for row in rows_sorted:
        lines.append(
            f"| {row['symbol']} | {row['regime']} | {row['duration_bars']} "
            f"| {row['persistence_60d'] * 100:.0f}% | {row['last_bar']} | {row['n_bars']} |"
        )
    lines.append("")

    lines.append("## Decision rule")
    lines.append("")
    lines.append(
        "Rotation has selection power if 8–15 of the universe are in a favourable "
        "(TRENDING_UP or sustained TRENDING_DOWN) regime on a typical day. "
        "Persistent <=3 means the universe is too narrow or the regime detector is "
        "too strict; persistent >=25 means rotation just always picks 'everything', "
        "i.e. no selection lift. Single-day reading is noisy — re-run weekly and "
        "compute the rolling distribution before making any architectural call."
    )
    lines.append("")

    lines.append("## Fetch log")
    lines.append("")
    lines.append("```")
    for entry in fetch_log:
        lines.append(entry)
    lines.append("```")
    lines.append("")

    return "\n".join(lines) + "\n"


def main() -> None:
    db = DatabaseManager()
    db.initialize_db()

    fetch_log: list[str] = []
    rows: list[dict] = []
    skipped: list[str] = []

    for symbol in UNIVERSE:
        status = ensure_data(db, symbol)
        if status:
            fetch_log.append(status)
        result = scan_symbol(db, symbol)
        if result is None:
            skipped.append(symbol)
            fetch_log.append(f"{symbol}: SKIP — insufficient bars (<220)")
            continue
        rows.append(result)

    if not rows:
        print("No assets had sufficient data. Aborting.")
        return

    print(f"\nScanned {len(rows)} assets ({len(skipped)} skipped: {skipped})\n")
    counts = {r: 0 for r in REGIMES}
    for row in rows:
        counts[row["regime"]] = counts.get(row["regime"], 0) + 1
    for r in REGIMES:
        print(f"  {r:14s} {counts.get(r, 0):3d}")
    favourable = sum(counts[r] for r in FAVOURABLE)
    print(f"  {'FAVOURABLE':14s} {favourable:3d} / {len(rows)}")

    md = build_markdown(rows, fetch_log)
    MD_PATH.parent.mkdir(parents=True, exist_ok=True)
    MD_PATH.write_text(md)
    print(f"\nWrote {MD_PATH}")


if __name__ == "__main__":
    main()
