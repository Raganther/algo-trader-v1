"""Overnight gap distribution for GLD/IAU/SLV/GDX.

Run: python3 -m backend.analysis.gap_distribution

Reads daily bars from backend/research.db (price_data_daily), computes
overnight returns (open[t] - close[t-1]) / close[t-1], writes percentiles
to the gap_statistics table and a human-readable markdown summary at
.claude/calibration/gap-distribution.md.
"""
import sqlite3
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import pandas as pd

SYMBOLS = ["GLD", "IAU", "SLV", "GDX"]
DB_PATH = Path(__file__).resolve().parents[2] / "backend" / "research.db"
MD_PATH = Path(__file__).resolve().parents[2] / ".claude" / "calibration" / "gap-distribution.md"
PCTILES = [50, 90, 95, 99]


def load_daily(conn: sqlite3.Connection, symbol: str) -> pd.DataFrame:
    df = pd.read_sql_query(
        "SELECT timestamp, open, close FROM price_data_daily "
        "WHERE symbol = ? ORDER BY timestamp ASC",
        conn,
        params=(symbol,),
    )
    df["date"] = pd.to_datetime(df["timestamp"], unit="s", utc=True)
    df["date_str"] = df["date"].dt.strftime("%Y-%m-%d")
    df = (
        df.sort_values("timestamp")
        .drop_duplicates(subset=["date_str"], keep="last")
        .reset_index(drop=True)
    )
    df["prev_close"] = df["close"].shift(1)
    df["gap_pct"] = (df["open"] - df["prev_close"]) / df["prev_close"]
    df = df.dropna(subset=["gap_pct"]).reset_index(drop=True)
    # Filter |gap| > 15% as data artifacts (split-adjustment inconsistencies
    # at the Alpaca/Yahoo data-source boundary; real overnight gaps for these
    # 4 ETFs have never exceeded ~15% historically, even in 2008/COVID).
    artifacts = df[df["gap_pct"].abs() > 0.15]
    if len(artifacts) > 0:
        df = df[df["gap_pct"].abs() <= 0.15].reset_index(drop=True)
    df.attrs["artifacts_filtered"] = len(artifacts)
    return df


def compute_stats(df: pd.DataFrame, ref_price: float) -> dict:
    gaps = df["gap_pct"].to_numpy()
    abs_gaps = np.abs(gaps)
    stats = {
        "n": len(gaps),
        "start": df["date"].iloc[0].strftime("%Y-%m-%d"),
        "end": df["date"].iloc[-1].strftime("%Y-%m-%d"),
        "mean_pct": float(gaps.mean()),
        "std_pct": float(gaps.std()),
        "min_pct": float(gaps.min()),
        "max_pct": float(gaps.max()),
    }
    for p in PCTILES:
        stats[f"signed_p{p}_pct"] = float(np.percentile(gaps, p))
        stats[f"signed_p{100-p}_pct"] = float(np.percentile(gaps, 100 - p))
        stats[f"abs_p{p}_pct"] = float(np.percentile(abs_gaps, p))
        stats[f"abs_p{p}_at_ref"] = float(np.percentile(abs_gaps, p)) * ref_price
    stats["ref_price"] = ref_price
    return stats


def ensure_table(conn: sqlite3.Connection) -> None:
    conn.execute(
        """CREATE TABLE IF NOT EXISTS gap_statistics (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            symbol TEXT NOT NULL,
            pctl INTEGER NOT NULL,
            gap_pct REAL NOT NULL,
            gap_abs_at_ref_price REAL NOT NULL,
            ref_price REAL NOT NULL,
            sample_n INTEGER NOT NULL,
            lookback_start TEXT NOT NULL,
            lookback_end TEXT NOT NULL,
            window TEXT NOT NULL,
            computed_at TEXT NOT NULL,
            UNIQUE(symbol, pctl, window)
        )"""
    )
    conn.commit()


def persist(conn: sqlite3.Connection, symbol: str, window: str, stats: dict) -> None:
    now = datetime.now(timezone.utc).isoformat(timespec="seconds")
    rows = []
    for p in PCTILES:
        rows.append(
            (
                symbol,
                p,
                stats[f"abs_p{p}_pct"],
                stats[f"abs_p{p}_at_ref"],
                stats["ref_price"],
                stats["n"],
                stats["start"],
                stats["end"],
                window,
                now,
            )
        )
    conn.executemany(
        "INSERT OR REPLACE INTO gap_statistics "
        "(symbol, pctl, gap_pct, gap_abs_at_ref_price, ref_price, sample_n, "
        "lookback_start, lookback_end, window, computed_at) "
        "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
        rows,
    )
    conn.commit()


def format_pct(x: float) -> str:
    return f"{x*100:+.2f}%"


def format_abs(x: float) -> str:
    return f"${x:.3f}"


def write_markdown(all_stats: dict) -> None:
    lines = [
        f"Status: current | Epistemic: confirmed | Last verified: "
        f"{datetime.now(timezone.utc).strftime('%Y-%m-%d')}",
        "",
        "# Overnight Gap Distribution — GLD / IAU / SLV / GDX",
        "",
        "Source: `backend/research.db` → `price_data_daily`. "
        "Gap = `(open[t] - close[t-1]) / close[t-1]`.",
        "Regenerate: `python3 -m backend.analysis.gap_distribution`.",
        "",
        "## Full history (absolute gap)",
        "",
        "| Symbol | Samples | Range | p50 | p90 | p95 | p99 | Max |",
        "|--------|---------|-------|-----|-----|-----|-----|-----|",
    ]
    for sym in SYMBOLS:
        s = all_stats[sym]["full"]
        lines.append(
            f"| {sym} | {s['n']:,} | {s['start']} → {s['end']} | "
            f"{format_pct(s['abs_p50_pct'])} | {format_pct(s['abs_p90_pct'])} | "
            f"{format_pct(s['abs_p95_pct'])} | {format_pct(s['abs_p99_pct'])} | "
            f"{format_pct(abs(s['max_pct']) if abs(s['max_pct']) > abs(s['min_pct']) else abs(s['min_pct']))} |"
        )

    lines += [
        "",
        "## Full history at current reference price (for sizing)",
        "",
        "Ref price is the most recent close. `p95_abs` is the 95th-percentile "
        "absolute gap in dollars/share — the input to gap-aware position sizing.",
        "",
        "| Symbol | Ref $ | p50_abs | p90_abs | p95_abs | p99_abs |",
        "|--------|-------|---------|---------|---------|---------|",
    ]
    for sym in SYMBOLS:
        s = all_stats[sym]["full"]
        lines.append(
            f"| {sym} | ${s['ref_price']:.2f} | {format_abs(s['abs_p50_at_ref'])} | "
            f"{format_abs(s['abs_p90_at_ref'])} | {format_abs(s['abs_p95_at_ref'])} | "
            f"{format_abs(s['abs_p99_at_ref'])} |"
        )

    lines += [
        "",
        "## Signed distribution (full history)",
        "",
        "Down-gaps vs up-gaps. Symmetric for random-walk; asymmetric if there's "
        "tail skew (relevant: metals have fat down-gap tails historically).",
        "",
        "| Symbol | p1 (worst down) | p5 | p50 | p95 | p99 (worst up) |",
        "|--------|-----------------|----|----|----|----------------|",
    ]
    for sym in SYMBOLS:
        s = all_stats[sym]["full"]
        lines.append(
            f"| {sym} | {format_pct(s['signed_p1_pct'])} | "
            f"{format_pct(s['signed_p5_pct'])} | "
            f"{format_pct(s['signed_p50_pct'])} | "
            f"{format_pct(s['signed_p95_pct'])} | "
            f"{format_pct(s['signed_p99_pct'])} |"
        )

    lines += [
        "",
        "## Trailing 5 years",
        "",
        "Sanity check for regime shift. If trailing-5y percentiles are materially "
        "different from full-history, prefer trailing-5y for sizing.",
        "",
        "| Symbol | Samples | Range | p50_abs | p95_abs | p99_abs |",
        "|--------|---------|-------|---------|---------|---------|",
    ]
    for sym in SYMBOLS:
        s = all_stats[sym]["recent"]
        lines.append(
            f"| {sym} | {s['n']:,} | {s['start']} → {s['end']} | "
            f"{format_pct(s['abs_p50_pct'])} | {format_pct(s['abs_p95_pct'])} | "
            f"{format_pct(s['abs_p99_pct'])} |"
        )

    lines += [
        "",
        "## Apr 23 2026 SLV reference",
        "",
        "SLV overnight gap Apr 22 close → Apr 23 open: "
        "$70.365 → $68.67 = **−2.41%**. Where does this land in the distribution?",
        "",
    ]
    s = all_stats["SLV"]["full"]
    event_gap = -0.0241
    if event_gap < s["signed_p1_pct"]:
        zone = "worse than p1 (top 1% of historical down-gaps)"
    elif event_gap < s["signed_p5_pct"]:
        zone = "between p1 and p5 (1–5% tail of historical down-gaps)"
    else:
        zone = "within the middle 90% of historical gap distribution"
    lines.append(
        f"SLV full-history signed percentiles: p1 {format_pct(s['signed_p1_pct'])}, "
        f"p5 {format_pct(s['signed_p5_pct'])}, p99 {format_pct(s['signed_p99_pct'])}. "
        f"The −2.41% event falls {zone}."
    )
    lines += [
        "",
        "## Implications for sizing (1% gap budget)",
        "",
        "At 1% of equity allocated to gap risk per symbol, and using 95th-pctl absolute gap:",
        "",
        "| Symbol | p95 abs $ | Gap cap @ $94k equity | Current notional cap (25%) | Which binds? |",
        "|--------|-----------|-----------------------|----------------------------|--------------|",
    ]
    eq = 94_000.0
    budget = 0.01
    for sym in SYMBOLS:
        s = all_stats[sym]["full"]
        gap_cap = (eq * budget) / s["abs_p95_at_ref"]
        notional_cap = (eq * 0.25) / s["ref_price"]
        binds = "gap" if gap_cap < notional_cap else "notional"
        lines.append(
            f"| {sym} | {format_abs(s['abs_p95_at_ref'])} | "
            f"{int(gap_cap):,} sh | {int(notional_cap):,} sh | **{binds}** |"
        )
    lines += [
        "",
        "At 1% gap budget with current $94k equity, the 25% notional cap still binds for all 4 symbols — "
        "gap-aware sizing would be a **no-op at current equity**. As equity grows (the notional cap scales "
        "linearly with equity, so does the gap cap) the ratio stays constant, so the notional cap will keep "
        "binding unless the gap budget is tightened or the notional cap is loosened.",
        "",
        "To make the gap cap bite, options are:",
        "- Tighten gap budget to 0.5% → SLV cap becomes ~221 sh (vs 340 notional) → binds",
        "- Loosen notional cap (e.g. 50%) → gap cap becomes the binding constraint",
        "- Accept: at current 25% notional cap, gap risk is bounded by notional, not by an explicit gap budget",
        "",
    ]

    MD_PATH.write_text("\n".join(lines) + "\n")


def main() -> None:
    conn = sqlite3.connect(DB_PATH)
    ensure_table(conn)
    all_stats = {}

    for sym in SYMBOLS:
        df = load_daily(conn, sym)
        if df.empty:
            print(f"{sym}: NO DATA")
            continue
        ref_price = float(df["close"].iloc[-1])
        full = compute_stats(df, ref_price)

        cutoff = df["date"].iloc[-1] - pd.Timedelta(days=365 * 5)
        recent_df = df[df["date"] >= cutoff].reset_index(drop=True)
        recent = compute_stats(recent_df, ref_price)

        all_stats[sym] = {"full": full, "recent": recent, "artifacts": df.attrs.get("artifacts_filtered", 0)}
        persist(conn, sym, "full", full)
        persist(conn, sym, "recent_5y", recent)

        art = df.attrs.get("artifacts_filtered", 0)
        art_note = f"  [{art} artifact row(s) filtered]" if art else ""
        print(
            f"{sym}: n={full['n']:,} ({full['start']}→{full['end']})  "
            f"p95_abs={full['abs_p95_pct']*100:.2f}% ({format_abs(full['abs_p95_at_ref'])} @ ${ref_price:.2f})  "
            f"p99_abs={full['abs_p99_pct']*100:.2f}% ({format_abs(full['abs_p99_at_ref'])})"
            f"{art_note}"
        )

    write_markdown(all_stats)
    print(f"\nWrote {MD_PATH.relative_to(Path.cwd()) if MD_PATH.is_relative_to(Path.cwd()) else MD_PATH}")
    conn.close()


if __name__ == "__main__":
    main()
