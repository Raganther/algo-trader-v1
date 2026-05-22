Status: current | Epistemic: confirmed | Last verified: 2026-05-07

# Portfolio Runner — Per-Bot Cap Shrinking Experiment (Apr 30 2026 PM)

> **May 7 2026 caveat.** All Sharpe figures in this file are close-anchored backtests with ~0.7 Sharpe optimism baked in (1-bar polling delay artifact). Live expectation = backtest Sharpe **− 0.7**. ΔSharpe comparisons between configs in this file remain valid (the artifact is roughly uniform across runs). HWM trail anchor (May 7 finding) bypasses the artifact; cap-shrink and rotation experiments not yet re-run with HWM. See `.claude/calibration/live-vs-backtest-iau-diagnostic.md` and `.claude/strategies/trail-anchor-hwm.md`.

> **Headline:** Shrinking the per-bot notional cap from 25% → 12.5% **passes the decision rule** on both branches (cap-shrink alone +0.28 Sharpe / −1.54pp DD; cap-shrink + lineup expansion +0.45 Sharpe / −1.19pp DD). The 8-bot best-per-cluster lineup at 12.5% cap is the new highest-Sharpe configuration tested.
>
> **Status:** code shipped (`position_cap_frac` strategy param + `--position-cap-frac` CLI flag), default unchanged at 0.25 pending strategic decision on whether to flip the strategy default and reshuffle the live lineup.

## Setup

- Period: 2020-07-27 → 2026-04-27 (~5.75 years)
- Initial capital: $94,000 (matches live account)
- Spread 0.0003, source = alpaca via `--use-cache`, recipe params (StochRSI 7/14, OB/OS 80/15, ADX 20, SL 2 ATR, trailing 2 ATR after 10 bars, min hold 10, skip Mon)
- Portfolio total-notional cap: ON @ FRAC=1.0 (current default since `070e3dc`)
- Correlation discount: enabled
- Cluster cap: disabled (default)

## Code change

Added optional strategy param `position_cap_frac` to `TrendFrameworkStrategy` (default 0.25 — preserves byte-identical behaviour for single-symbol backtests + live deployment when omitted). Three sizing blocks (`trend_framework.py:268, 314, 369`) now read `equity * self.position_cap_frac` instead of the hardcoded `equity * 0.25`. New CLI flag `--position-cap-frac` on the `portfolio` subcommand (`runner.py`) injects the param into the parameters JSON before strategy instantiation.

Run 0 (no override) reproduces the `070e3dc` baseline byte-identical: +424.09% / 3.41% / 4.95 Sharpe / 4344 trades. Refactor is a no-op at default.

## Results

| Run | Universe | Cap | Return | DD | Sharpe | Trades | Max conc |
|---|---|---:|---:|---:|---:|---:|---:|
| 0 baseline | GLD,IAU,SLV,GDX,OIH,XBI,XOP | 25% | +424.09% | 3.41% | **4.95** | 4344 | 7 |
| 1 ablation | GLD,IAU,SLV,GDX,OIH,XBI,XOP | 12.5% | +236.86% | 1.87% | **5.23** (+0.28) | 4413 | 7 |
| 2 primary | GLD,SLV,OIH,XOP,IWM,SMH,XBI,IBB | 12.5% | +262.81% | 2.22% | **5.40** (+0.45) | 5004 | 8 |

Decision rule: ≥+0.30 Sharpe lift OR ≥−1pp DD with ≤0.10 Sharpe loss.

- **Run 1 vs Run 0** (pure cap-shrink, lineup unchanged): ΔSharpe +0.28, ΔDD −1.54pp. **Pass on the DD branch** (DD ≥−1pp with Sharpe a gain not a loss). The cap-shrink itself, with no other change, is a structural improvement.
- **Run 2 vs Run 0** (cap-shrink + best-per-cluster expansion): ΔSharpe +0.45, ΔDD −1.19pp. **Pass on both branches independently.** This is the strongest configuration tested.
- **Run 2 vs Run 1** (lineup-change isolated): ΔSharpe +0.17 from swapping IAU + GDX (redundant gold) for IWM + SMH + IBB (broad-index + biotech). Modest but positive — diversification dividend is real but smaller than the cap-shrink itself.

## Per-symbol contribution (Run 2)

| Symbol | Cluster | Trades | P&L ($) | Win rate |
|---|---|---:|---:|---:|
| OIH | energy | 589 | 43,835 | 42.4% |
| SLV | gold | 581 | 42,438 | 47.3% |
| SMH | broad/sector | 568 | 37,706 | 44.7% |
| XOP | energy | 628 | 30,396 | 42.0% |
| XBI | biotech | 601 | 29,524 | 43.4% |
| IBB | biotech | 637 | 21,730 | 43.3% |
| IWM | broad/sector | 672 | 21,322 | 45.5% |
| GLD | gold | 728 | 19,709 | 43.1% |

All 8 clear positive P&L. SMH (semis), IBB (biotech) and IWM (small-cap) — three symbols with no live deployment — collectively contribute $80.8k of the $247k aggregate, a meaningful share.

## Cluster co-occupancy

**Run 0 baseline (7 bots, 25% cap), gold cluster (GLD+IAU+SLV+GDX):**
- N=2: 26.9%, N=3: 15.7%, N=4: 3.5% — gold piles up frequently.

**Run 1 (7 bots, 12.5% cap), gold cluster:**
- N=2: 26.6%, N=3: 15.9%, N=4: 4.2% — distribution near-identical to baseline. Cap-shrink does **not** suppress gold pile-up; it just makes each pile-up smaller in dollar terms.

**Run 2 (8 bots, 12.5% cap), gold cluster (only GLD+SLV in lineup):**
- N=2: 15.9% max (no IAU/GDX). Reduces gold cluster exposure mechanically by lineup choice, not by cap behaviour.

## Why the return drops

Cap-shrink and return scale linearly. At 12.5% cap each position is half the dollar size of the 25% cap, so absolute P&L per trade halves. Sharpe is sizing-invariant by construction (mean and stdev both halve), so the apples-to-apples metric is Sharpe + DD%, not return. Run 1 has +0.28 Sharpe / −1.54pp DD with half the absolute return — a genuinely better risk-adjusted profile, just at lower notional throughput. Run 2 partially recovers throughput by adding more bots into the freed slots.

If the goal is to maximise *absolute return at a given account size*, the 25% baseline wins; if the goal is to maximise *risk-adjusted return* (or to have headroom to scale account size up without cap-stacking against the portfolio total), 12.5% wins.

## Recommendations

1. **Ship the param itself** ✓ already done. `position_cap_frac` is now a first-class strategy param + CLI flag. Future experiments (e.g. 5% × 20 bots, regime-conditional cap) are now one-line changes.
2. **Strategic decision pending** on whether to:
   - (a) Flip the default to `0.125` in `trend_framework.py` __init__, and
   - (b) Reshuffle the live lineup from 7 → 8 bots, swapping IAU + GDX out for IWM + SMH + IBB.
   This involves real-money implications (deploying 3 new bot types, retiring 2) and a deliberate trade-off (lower absolute return at current $94k account, higher Sharpe + DD-resilience). Decision belongs to the user.
3. **Untested next:** 20 bots × 5% cap on the full Run B universe — the cap-shrink curve may continue (theoretical √(20/4) = 2.24× Sharpe lift at perfect uncorrelation, much less in practice). Lower priority than acting on the Run 2 finding.

## Files

- `backend/strategies/trend_framework.py` — `position_cap_frac` param read in `__init__`, three sizing blocks updated.
- `backend/runner.py` — `--position-cap-frac` CLI flag on portfolio subcommand, injection into parameters JSON.
- `/tmp/cap_shrink/run{0,1,2}_*.md` — full snapshot output of each run.
