Status: current | Epistemic: backtest-validated under bug-fixed calibration | Last verified: 2026-05-10

# Portfolio-Lineup Selection — Tighter Hand-Picked Lineups Don't Beat 7-Bot Baseline

> Direct test of the May 9 question: given that only GLD and SLV clear the 2.0 Sharpe quality bar at the per-asset level under `adx_filter_mode='entry_only'`, would a tighter hand-picked lineup beat the current 7-bot portfolio Sharpe (4.17)? **Answer: no.** Sharpe is monotonic with bot count across the tested range; diversification dominates per-asset quality.

## Setup

All four runs use identical strategy params, window, capital, and infrastructure. Only `--symbols` varies.

- Window: 2020-07-27 → 2026-04-27, $94k initial
- Params: validated set + `trail_anchor:'hwm'` + `adx_filter_mode:'entry_only'`
- Per-bot cap: 25% (`position_cap_frac=0.25`)
- Portfolio total-notional cap: ON at FRAC=1.0
- Correlation discount: ON (default; structurally inactive but logged)
- Source: alpaca, spread 0.0003, delay 0

## Results

| Run | Lineup | N | Return | Max DD | Sharpe | Trades | Max conc | Δ Sharpe vs 0 |
|---|---|---:|---:|---:|---:|---:|---:|---:|
| 0 (baseline) | GLD,IAU,SLV,GDX,OIH,XBI,XOP | 7 | +230.73% | 2.58% | **4.17** | 4639 | 6 | — |
| C | drop GDX | 6 | +202.47% | 2.99% | **4.01** | 4031 | 5 | −0.16 |
| B | drop GDX+XOP | 5 | +172.55% | 2.80% | **3.87** | 3366 | 5 | −0.30 |
| A | best-per-cluster (GLD,SLV,OIH,XBI) | 4 | +151.56% | 2.45% | **3.79** | 2624 | 4 | −0.38 |

## Decision rule (from `portfolio-runner-cap-shrink.md` precedent)

Keep change if **ΔSharpe ≥ +0.30 vs baseline** OR **ΔDD ≤ −1pp with ΔSharpe ≥ −0.10**.

- **Sharpe branch:** All three lineups *lose* Sharpe (−0.16 / −0.30 / −0.38). FAILS.
- **DD branch:** Biggest DD improvement is Run A at 2.58% → 2.45% = −0.13pp. Nowhere near the 1pp bar. FAILS.

**Verdict: keep the current 7-bot lineup. No live action.**

## The structural finding — Sharpe is monotonic with bot count

| N bots | Sharpe |
|---:|---:|
| 4 | 3.79 |
| 5 | 3.87 |
| 6 | 4.01 |
| 7 | 4.17 |

Each additional bot adds roughly **+0.10–0.15 Sharpe** across the tested range. This is the textbook diversification lift in action: at low cross-correlation, portfolio Sharpe scales approximately as `√N × asset_Sharpe`. Adding √8/√7 ≈ 1.069 multiplier to a 4.17 Sharpe ≈ 4.46 if a perfectly-correlation-zero 8th bot existed.

**Implication:** the lever isn't *trimming the weak bots* — it's *adding more uncorrelated bots*, which in turn requires per-bot cap shrinking so they fit within the 100% notional ceiling.

## Why the May 9 per-asset table was the wrong question

The May 9 close-anchored entry_only per-asset run showed only GLD (2.28) and SLV (2.19) clear Sharpe 2.0 standalone. The naive read was "the lineup is mostly junk; trim to GLD+SLV+OIH+XBI." This experiment shows that read is wrong:

- **GDX standalone Sharpe 1.46 → still adds +0.16 Sharpe at the portfolio level** (Run 0 vs Run C)
- **XOP standalone Sharpe 1.32 → still adds +0.14 Sharpe at the portfolio level** (Run C vs Run B)
- **IAU standalone Sharpe 1.88 → adds +0.08 Sharpe at the portfolio level** (Run B vs Run A)

Even bots well below the standalone quality bar are pulling their weight via diversification. The 2.0 Sharpe per-asset bar is a *quality screen for candidate addition*, not a *prune threshold for existing lineups*.

## Per-symbol contributions (Run 0, control)

From `portfolio-runner-baseline.md` and today's leg B output:

| Symbol | Trades | P&L | Win % |
|---|---:|---:|---:|
| GDX | 608 | $29,821 | 43.4% |
| GLD | 770 | $24,716 | 41.4% |
| IAU | 740 | $19,591 | 42.3% |
| OIH | 611 | $50,576 | 44.7% |
| SLV | 612 | $43,064 | 45.1% |
| XBI | 631 | $21,189 | 43.9% |
| XOP | 667 | $27,966 | 42.4% |

OIH is the single biggest contributor; even GDX (heaviest May 9 bug-beneficiary) is mid-pack on dollar P&L. The bug correction changed the *Sharpe attribution story* (GDX's standalone risk-adjusted return wasn't real); it didn't change the *cash contribution* story enough to make GDX prunable.

## Cluster co-occupancy (Run 0, control)

- gold (GDX/GLD/IAU/SLV): N≥2 = 18.3% of bars, N≥3 = 5.6%, N=4 = 0.8%
- energy (OIH/XLE/XOP): N≥2 = 4.8% of bars (no XLE in lineup)
- biotech (XBI): N=1 = 15.0% of bars

Trimmed lineups (A/B) reduce gold-cluster co-occupancy (Run A: gold N≥2 = 4.5%) but also reduce *opportunity for diversification within the cluster* — Sharpe drops correspondingly.

## Outstanding follow-ups

1. **Per-bot cap shrink under entry_only — next experiment.** Apr 30 PM Run 2 showed 8 bots × 12.5% lifted Sharpe +0.45 under buggy mode (4.95 → 5.40). Does that lift survive bug correction? If yes, this is the only candidate change with a credible path past Sharpe 4.17.
2. **Universe expansion under entry_only.** Apr 30 PM Run B showed expansion is a DD-reducer not Sharpe-lifter at our scale under buggy mode (Sharpe 4.86 → 4.76, DD 3.58% → 2.45%). Worth re-checking under bug fix if cap-shrink lands well.
3. **Standalone-bot pruning has no further runway here** — closed by this experiment.

## Reproduce

```bash
# Baseline (Run 0) — already in calibration-journal.md as the HWM+entry_only leg B:
python3 -m backend.runner portfolio --strategy StochRSIMeanReversion \
  --symbols GLD,IAU,SLV,GDX,OIH,XBI,XOP \
  --timeframe 15m --start 2020-07-27 --end 2026-04-27 \
  --source alpaca --spread 0.0003 --initial 94000 \
  --parameters '{"rsi_period":7,"stoch_period":14,"overbought":80,"oversold":15,"adx_threshold":20,"skip_adx_filter":false,"sl_atr":2.0,"trailing_stop":true,"trail_atr":2.0,"trail_after_bars":10,"min_hold_bars":10,"skip_days":[0],"trail_anchor":"hwm","adx_filter_mode":"entry_only"}'

# Runs A / B / C — change only --symbols:
#   A: GLD,SLV,OIH,XBI
#   B: GLD,IAU,SLV,OIH,XBI
#   C: GLD,IAU,SLV,OIH,XOP,XBI
```

The portfolio runner overwrites `portfolio-runner-baseline.md` on each run — restore from git after each comparison run.
