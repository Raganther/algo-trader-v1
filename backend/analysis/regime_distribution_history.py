"""Rolling historical regime distribution across the universe.

Run: python3 -m backend.analysis.regime_distribution_history

For each asset in UNIVERSE, classify the full daily history with
`backend/indicators/regime.py:classify_regime`. ADX/SMA/ATR are causal
indicators — the label at date t only uses bars <= t — so a single
classification pass per asset is equivalent to re-running on each historical
slice. We then sample weekly snapshots and aggregate per-regime counts
across the universe.

Output:
- `.claude/strategies/regime-distribution-history.md` — markdown summary
  (percentile distribution of favourable-count, regime % over time,
   year-by-year averages, current-vs-history comparison).
- `backend/analysis/regime_distribution_history.csv` — long-form
  (date, n_assets, count_RANGING, count_TRENDING_UP, count_TRENDING_DOWN,
   count_HIGH_VOL, count_favourable) for plotting / further analysis.

Decision rule: if median favourable count across history is 8-15, rotation
has selection power. If it spikes to 25+ in bull-everything markets and
drops to <=3 in panic markets, rotation has structural blind spots.
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
from backend.analysis.regime_universe_scan import UNIVERSE


REGIMES = [RANGING, TRENDING_UP, TRENDING_DOWN, HIGH_VOL]
FAVOURABLE = {TRENDING_UP, TRENDING_DOWN}
MIN_BARS_FOR_CLASSIFICATION = 220   # 200 SMA + buffer
SAMPLE_FREQ = "W-FRI"               # weekly snapshots, Friday close
COVERAGE_FLOOR = 20                 # require >= this many assets at a snapshot

ROOT = Path(__file__).resolve().parents[2]
MD_PATH = ROOT / ".claude" / "strategies" / "regime-distribution-history.md"
CSV_PATH = ROOT / "backend" / "analysis" / "regime_distribution_history.csv"


def load_and_classify(db: DatabaseManager, symbol: str) -> pd.Series | None:
    """Return a Series of regime labels indexed by date, or None if insufficient data."""
    df = db.get_daily_bars(symbol)
    if df.empty or len(df) < MIN_BARS_FOR_CLASSIFICATION:
        return None
    regimes = classify_regime(df)
    # Drop the first MIN_BARS_FOR_CLASSIFICATION bars where indicators warm up;
    # they are labelled RANGING by the NaN-fallback, which would bias counts.
    regimes = regimes.iloc[MIN_BARS_FOR_CLASSIFICATION:]
    return regimes


def build_panel(asset_regimes: dict[str, pd.Series]) -> pd.DataFrame:
    """Build a wide DataFrame of regime labels — index = date, columns = symbols.
    Forward-fill within each asset (a non-trading day inherits the prior day's label)."""
    aligned = {}
    for sym, series in asset_regimes.items():
        # normalise to date (drop intraday tz)
        s = series.copy()
        s.index = s.index.tz_convert("UTC").normalize() if s.index.tz is not None else pd.to_datetime(s.index).normalize()
        s = s[~s.index.duplicated(keep="last")]
        aligned[sym] = s
    panel = pd.DataFrame(aligned).sort_index()
    panel = panel.ffill()  # weekend / holiday carryover
    return panel


def aggregate_counts(panel: pd.DataFrame) -> pd.DataFrame:
    """For each row of the panel, count assets in each regime."""
    rows = []
    for date, row in panel.iterrows():
        valid = row.dropna()
        if len(valid) < COVERAGE_FLOOR:
            continue
        counts = {f"count_{r}": int((valid == r).sum()) for r in REGIMES}
        counts["date"] = date
        counts["n_assets"] = len(valid)
        counts["count_favourable"] = sum(counts[f"count_{r}"] for r in FAVOURABLE)
        rows.append(counts)
    out = pd.DataFrame(rows)
    cols = ["date", "n_assets"] + [f"count_{r}" for r in REGIMES] + ["count_favourable"]
    return out[cols]


def sample_weekly(daily: pd.DataFrame) -> pd.DataFrame:
    """Resample the daily aggregate to weekly Friday snapshots."""
    daily = daily.set_index("date")
    weekly = daily.resample(SAMPLE_FREQ).last().dropna(how="all").reset_index()
    return weekly


def percentile_summary(series: pd.Series) -> dict:
    return {
        "min": int(series.min()),
        "p10": int(series.quantile(0.10)),
        "p25": int(series.quantile(0.25)),
        "median": int(series.median()),
        "mean": float(series.mean()),
        "p75": int(series.quantile(0.75)),
        "p90": int(series.quantile(0.90)),
        "max": int(series.max()),
    }


def yearly_breakdown(weekly: pd.DataFrame) -> pd.DataFrame:
    df = weekly.copy()
    df["year"] = pd.to_datetime(df["date"]).dt.year
    g = df.groupby("year").agg(
        snapshots=("date", "count"),
        avg_n=("n_assets", "mean"),
        avg_ranging=("count_RANGING", "mean"),
        avg_tup=("count_TRENDING_UP", "mean"),
        avg_tdown=("count_TRENDING_DOWN", "mean"),
        avg_hv=("count_HIGH_VOL", "mean"),
        avg_fav=("count_favourable", "mean"),
        max_fav=("count_favourable", "max"),
        min_fav=("count_favourable", "min"),
    ).round(1)
    return g.reset_index()


def build_markdown(weekly: pd.DataFrame, today_fav: int | None, today_n: int | None) -> str:
    today_str = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    n_snapshots = len(weekly)
    start = pd.to_datetime(weekly["date"].iloc[0]).strftime("%Y-%m-%d")
    end = pd.to_datetime(weekly["date"].iloc[-1]).strftime("%Y-%m-%d")

    fav_stats = percentile_summary(weekly["count_favourable"])
    rang_stats = percentile_summary(weekly["count_RANGING"])
    tup_stats = percentile_summary(weekly["count_TRENDING_UP"])
    tdown_stats = percentile_summary(weekly["count_TRENDING_DOWN"])
    hv_stats = percentile_summary(weekly["count_HIGH_VOL"])
    n_assets_stats = percentile_summary(weekly["n_assets"])

    median_fav = fav_stats["median"]
    p10_fav, p90_fav = fav_stats["p10"], fav_stats["p90"]

    if 8 <= median_fav <= 15:
        verdict = (
            f"**Verdict: ROTATION HAS SELECTION POWER.** Median favourable count over "
            f"{n_snapshots} weekly snapshots is **{median_fav}**, inside the 8-15 selective "
            "band. The universe regularly presents a tradeable subset of trending assets — "
            "rotation backtest is justified."
        )
    elif median_fav < 8:
        verdict = (
            f"**Verdict: NARROW UNIVERSE OR STRICT DETECTOR.** Median favourable count is "
            f"**{median_fav}** (below 8). Either (a) the 33-asset universe is too narrow "
            "for the framework's preferred regime, (b) the regime detector's ADX 25 "
            "threshold is too strict, or (c) sustained trends are genuinely rare. Consider "
            "widening the universe and/or relaxing the detector before committing to a "
            "rotation backtest."
        )
    else:
        verdict = (
            f"**Verdict: SATURATED.** Median favourable count is **{median_fav}** (above 15) "
            "— most of the universe is trending most of the time. Rotation has limited "
            "selection lift; the lineup choice would be dominated by which-trending-asset, "
            "not whether-to-rotate."
        )

    today_line = ""
    if today_fav is not None and today_n is not None:
        if today_fav <= p10_fav:
            today_pct = "low (≤ p10 historically)"
        elif today_fav >= p90_fav:
            today_pct = "high (≥ p90 historically)"
        else:
            today_pct = f"typical (between p10={p10_fav} and p90={p90_fav})"
        today_line = (
            f"\n**Today's reading ({today_str}): {today_fav}/{today_n} favourable** — "
            f"{today_pct}.\n"
        )

    yearly = yearly_breakdown(weekly)

    lines = []
    lines.append(f"Status: current | Epistemic: confirmed | Last verified: {today_str}")
    lines.append("")
    lines.append("# Regime Distribution History")
    lines.append("")
    lines.append(
        "Rolling weekly snapshot of how many assets in the universe sit in each regime, "
        "across the available daily-bar history. Tells us whether the favourable-count "
        "(TRENDING_UP + TRENDING_DOWN) distribution supports a rotation strategy."
    )
    lines.append("")
    lines.append("## Inputs")
    lines.append("")
    lines.append(f"- Universe: {len(UNIVERSE)} ETFs (same list as `regime_universe_scan.py`).")
    lines.append(f"- Sample frequency: weekly (Friday snapshot). Total snapshots: **{n_snapshots}**.")
    lines.append(f"- Window: **{start} → {end}**.")
    lines.append(f"- Coverage floor: ignore weeks with < {COVERAGE_FLOOR} assets having ≥{MIN_BARS_FOR_CLASSIFICATION} bars.")
    lines.append(
        "- Indicators are causal (ADX 14, SMA 200, ATR 14 — all rolling/EMA, no look-ahead), "
        "so we classify each asset's full series once and sample at each snapshot date."
    )
    lines.append("")

    lines.append("## Headline distributions")
    lines.append("")
    lines.append("| Metric | min | p10 | p25 | median | mean | p75 | p90 | max |")
    lines.append("|---|---:|---:|---:|---:|---:|---:|---:|---:|")
    for label, stats in [
        ("Favourable (TUP+TDOWN)", fav_stats),
        ("RANGING", rang_stats),
        ("TRENDING_UP", tup_stats),
        ("TRENDING_DOWN", tdown_stats),
        ("HIGH_VOL", hv_stats),
        ("N assets covered", n_assets_stats),
    ]:
        lines.append(
            f"| {label} | {stats['min']} | {stats['p10']} | {stats['p25']} | "
            f"{stats['median']} | {stats['mean']:.1f} | {stats['p75']} | "
            f"{stats['p90']} | {stats['max']} |"
        )
    lines.append("")
    lines.append(verdict)
    lines.append(today_line)

    lines.append("## Year-by-year averages")
    lines.append("")
    lines.append("| Year | snaps | avg N | avg RANGING | avg TUP | avg TDOWN | avg HV | avg FAV | min FAV | max FAV |")
    lines.append("|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|")
    for _, row in yearly.iterrows():
        lines.append(
            f"| {int(row['year'])} | {int(row['snapshots'])} | {row['avg_n']} | "
            f"{row['avg_ranging']} | {row['avg_tup']} | {row['avg_tdown']} | "
            f"{row['avg_hv']} | {row['avg_fav']} | {int(row['min_fav'])} | "
            f"{int(row['max_fav'])} |"
        )
    lines.append("")

    lines.append("## Decision rule")
    lines.append("")
    lines.append(
        "- Median favourable in 8-15 → rotation has meaningful selection power; build the "
        "rotation backtest (gated on shared-timeline runner).\n"
        "- Median favourable < 8 → either widen the universe (more sectors / international / "
        "single-name liquid stocks) or relax the detector (lower ADX threshold, shorter SMA) "
        "before investing in rotation engineering.\n"
        "- Median favourable > 15 → almost everything trends most of the time; the rotation "
        "thesis loses its premise. Stay with fixed-lineup + correlation-aware sizing."
    )
    lines.append("")

    lines.append("## Notable extremes")
    lines.append("")
    top_fav = weekly.nlargest(5, "count_favourable")[["date", "n_assets", "count_favourable", "count_RANGING", "count_HIGH_VOL"]]
    bot_fav = weekly.nsmallest(5, "count_favourable")[["date", "n_assets", "count_favourable", "count_RANGING", "count_HIGH_VOL"]]
    top_hv = weekly.nlargest(5, "count_HIGH_VOL")[["date", "n_assets", "count_favourable", "count_RANGING", "count_HIGH_VOL"]]

    def fmt_block(title: str, df: pd.DataFrame) -> list[str]:
        out = [f"### {title}", "", "| Date | N | Favourable | RANGING | HIGH_VOL |", "|---|---:|---:|---:|---:|"]
        for _, row in df.iterrows():
            out.append(
                f"| {pd.to_datetime(row['date']).strftime('%Y-%m-%d')} | "
                f"{int(row['n_assets'])} | {int(row['count_favourable'])} | "
                f"{int(row['count_RANGING'])} | {int(row['count_HIGH_VOL'])} |"
            )
        out.append("")
        return out

    lines.extend(fmt_block("Most-trending weeks (top 5 by favourable count)", top_fav))
    lines.extend(fmt_block("Least-trending weeks (bottom 5 by favourable count)", bot_fav))
    lines.extend(fmt_block("Highest HIGH_VOL weeks (top 5)", top_hv))

    lines.append("## Output files")
    lines.append("")
    lines.append(f"- This file: `{MD_PATH.relative_to(ROOT)}`")
    lines.append(f"- Long-form CSV (for plotting): `{CSV_PATH.relative_to(ROOT)}`")
    lines.append("")

    return "\n".join(lines) + "\n"


def main() -> None:
    db = DatabaseManager()
    db.initialize_db()

    print(f"Loading + classifying {len(UNIVERSE)} assets...")
    asset_regimes = {}
    skipped = []
    for sym in UNIVERSE:
        regimes = load_and_classify(db, sym)
        if regimes is None:
            skipped.append(sym)
            print(f"  SKIP {sym}: insufficient bars")
            continue
        asset_regimes[sym] = regimes
        print(f"  OK   {sym}: {len(regimes)} classified bars ({regimes.index[0].date()} → {regimes.index[-1].date()})")

    if not asset_regimes:
        print("No usable assets. Aborting.")
        return

    print(f"\nBuilding aligned panel ({len(asset_regimes)} assets, {len(skipped)} skipped)...")
    panel = build_panel(asset_regimes)
    print(f"Panel shape: {panel.shape}")

    print("Aggregating per-day counts...")
    daily = aggregate_counts(panel)
    print(f"Days passing coverage floor (>= {COVERAGE_FLOOR} assets): {len(daily)}")

    print(f"Resampling to weekly ({SAMPLE_FREQ})...")
    weekly = sample_weekly(daily)
    print(f"Weekly snapshots: {len(weekly)}")

    weekly.to_csv(CSV_PATH, index=False)
    print(f"Wrote {CSV_PATH}")

    # Today's reading from the live row of the panel (last row)
    today_fav = today_n = None
    if not panel.empty:
        last = panel.iloc[-1].dropna()
        if len(last) >= COVERAGE_FLOOR:
            today_n = len(last)
            today_fav = int(((last == TRENDING_UP) | (last == TRENDING_DOWN)).sum())

    md = build_markdown(weekly, today_fav, today_n)
    MD_PATH.parent.mkdir(parents=True, exist_ok=True)
    MD_PATH.write_text(md)
    print(f"Wrote {MD_PATH}")

    fav = weekly["count_favourable"]
    print(f"\nFavourable-count distribution across {len(weekly)} weekly snapshots:")
    print(f"  min={int(fav.min())}  p10={int(fav.quantile(0.10))}  median={int(fav.median())}  "
          f"p90={int(fav.quantile(0.90))}  max={int(fav.max())}  mean={fav.mean():.1f}")
    if today_fav is not None:
        print(f"\nToday's reading: {today_fav}/{today_n} favourable.")


if __name__ == "__main__":
    main()
