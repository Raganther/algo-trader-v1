Status: current | Epistemic: distribution confirmed; rotation-implication FALSIFIED Apr 30 PM | Last verified: 2026-04-30

# Regime Distribution History

Rolling weekly snapshot of how many assets in the universe sit in each regime, across the available daily-bar history. Tells us whether the favourable-count (TRENDING_UP + TRENDING_DOWN) distribution supports a rotation strategy.

> **Apr 30 PM update — rotation backtest run, both rules failed.** The "rotation has selection power" + "rotation backtest is justified" verdicts below were inputs to the Apr 30 PM rotation V1+V2 study. The universe-distribution evidence here is real (median favourable = 8 is genuinely inside the selective band), **but the actual backtest still failed**: V1 TRENDING_UP rule ΔSharpe −1.65, V2 RANGING rule ΔSharpe −0.37. The selection power exists; what's missing is *a strategy class that doesn't already self-select regime via its own entry filter*. StochRSI mean-reversion has an ADX<20 filter that makes external rotation redundant or destructive. The distribution evidence remains valid for future strategy classes (breakouts, momentum, donchian-trend); the "rotation backtest is justified" conclusion below is closed for the deployed strategy. See `.claude/strategies/portfolio-runner-rotation-v1.md`.

## Inputs

- Universe: 33 ETFs (same list as `regime_universe_scan.py`).
- Sample frequency: weekly (Friday snapshot). Total snapshots: **807**.
- Window: **2010-11-19 → 2026-05-01**.
- Coverage floor: ignore weeks with < 20 assets having ≥220 bars.
- Indicators are causal (ADX 14, SMA 200, ATR 14 — all rolling/EMA, no look-ahead), so we classify each asset's full series once and sample at each snapshot date.

## Headline distributions

| Metric | min | p10 | p25 | median | mean | p75 | p90 | max |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| Favourable (TUP+TDOWN) | 0 | 3 | 5 | 8 | 9.1 | 12 | 16 | 26 |
| RANGING | 0 | 13 | 18 | 22 | 21.3 | 26 | 28 | 33 |
| TRENDING_UP | 0 | 1 | 2 | 5 | 6.2 | 9 | 12 | 24 |
| TRENDING_DOWN | 0 | 0 | 1 | 2 | 3.0 | 4 | 8 | 23 |
| HIGH_VOL | 0 | 0 | 0 | 0 | 1.4 | 1 | 3 | 33 |
| N assets covered | 30 | 30 | 30 | 32 | 31.8 | 33 | 33 | 33 |

**Verdict: ROTATION HAS SELECTION POWER.** Median favourable count over 807 weekly snapshots is **8**, inside the 8-15 selective band. The universe regularly presents a tradeable subset of trending assets — rotation backtest is justified.

**Today's reading (2026-04-29): 7/33 favourable** — typical (between p10=3 and p90=16).

## Year-by-year averages

| Year | snaps | avg N | avg RANGING | avg TUP | avg TDOWN | avg HV | avg FAV | min FAV | max FAV |
|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 2010 | 7 | 30.0 | 18.7 | 9.7 | 0.9 | 0.7 | 10.6 | 6 | 17 |
| 2011 | 52 | 30.0 | 21.6 | 3.8 | 2.4 | 2.2 | 6.2 | 0 | 21 |
| 2012 | 52 | 30.0 | 21.2 | 6.3 | 2.3 | 0.1 | 8.7 | 1 | 26 |
| 2013 | 52 | 30.0 | 19.5 | 7.3 | 2.8 | 0.3 | 10.2 | 4 | 19 |
| 2014 | 52 | 30.0 | 18.8 | 7.3 | 2.3 | 1.5 | 9.7 | 3 | 18 |
| 2015 | 52 | 30.3 | 22.6 | 2.0 | 4.5 | 1.2 | 6.5 | 1 | 18 |
| 2016 | 53 | 31.8 | 21.5 | 5.7 | 3.4 | 1.2 | 9.1 | 1 | 22 |
| 2017 | 52 | 32.0 | 21.1 | 7.9 | 2.1 | 0.8 | 10.1 | 5 | 18 |
| 2018 | 52 | 32.1 | 20.3 | 4.3 | 4.8 | 2.6 | 9.1 | 3 | 25 |
| 2019 | 52 | 33.0 | 22.6 | 6.7 | 2.6 | 1.1 | 9.3 | 1 | 23 |
| 2020 | 52 | 33.0 | 20.1 | 6.4 | 2.5 | 4.0 | 8.9 | 0 | 25 |
| 2021 | 53 | 33.0 | 23.7 | 6.5 | 1.8 | 0.9 | 8.4 | 2 | 19 |
| 2022 | 52 | 33.0 | 21.6 | 4.0 | 6.9 | 0.5 | 10.9 | 0 | 23 |
| 2023 | 52 | 33.0 | 22.3 | 7.2 | 3.1 | 0.4 | 10.3 | 3 | 25 |
| 2024 | 52 | 33.0 | 22.2 | 8.5 | 1.0 | 1.3 | 9.5 | 4 | 22 |
| 2025 | 52 | 33.0 | 22.4 | 6.3 | 2.1 | 2.2 | 8.4 | 1 | 19 |
| 2026 | 18 | 33.0 | 18.3 | 9.9 | 3.1 | 1.7 | 12.9 | 5 | 25 |

## Decision rule

- Median favourable in 8-15 → rotation has meaningful selection power; build the rotation backtest (gated on shared-timeline runner).
- Median favourable < 8 → either widen the universe (more sectors / international / single-name liquid stocks) or relax the detector (lower ADX threshold, shorter SMA) before investing in rotation engineering.
- Median favourable > 15 → almost everything trends most of the time; the rotation thesis loses its premise. Stay with fixed-lineup + correlation-aware sizing.

## Notable extremes

### Most-trending weeks (top 5 by favourable count)

| Date | N | Favourable | RANGING | HIGH_VOL |
|---|---:|---:|---:|---:|
| 2012-06-01 | 30 | 26 | 4 | 0 |
| 2018-01-26 | 32 | 25 | 7 | 0 |
| 2018-12-28 | 33 | 25 | 8 | 0 |
| 2020-01-03 | 33 | 25 | 8 | 0 |
| 2023-12-29 | 33 | 25 | 8 | 0 |

### Least-trending weeks (bottom 5 by favourable count)

| Date | N | Favourable | RANGING | HIGH_VOL |
|---|---:|---:|---:|---:|
| 2011-08-12 | 30 | 0 | 3 | 27 |
| 2011-11-04 | 30 | 0 | 30 | 0 |
| 2020-03-13 | 33 | 0 | 0 | 33 |
| 2020-03-20 | 33 | 0 | 0 | 33 |
| 2020-06-19 | 33 | 0 | 33 | 0 |

### Highest HIGH_VOL weeks (top 5)

| Date | N | Favourable | RANGING | HIGH_VOL |
|---|---:|---:|---:|---:|
| 2020-03-13 | 33 | 0 | 0 | 33 |
| 2020-03-20 | 33 | 0 | 0 | 33 |
| 2020-03-06 | 33 | 1 | 1 | 31 |
| 2020-03-27 | 33 | 2 | 1 | 30 |
| 2025-04-11 | 33 | 1 | 2 | 30 |

## Output files

- This file: `.claude/strategies/regime-distribution-history.md`
- Long-form CSV (for plotting): `backend/analysis/regime_distribution_history.csv`

