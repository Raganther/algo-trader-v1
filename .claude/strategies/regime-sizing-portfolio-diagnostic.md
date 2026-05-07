Status: current | Epistemic: confirmed | Last verified: 2026-04-23 (results unaffected by Apr 28 edge-attribution finding)

# Regime Sizing Portfolio Diagnostic

> **May 7 2026 caveat.** All Sharpe figures in this file are close-anchored backtests with ~0.7 Sharpe optimism (1-bar polling delay artifact, see `.claude/calibration/live-vs-backtest-iau-diagnostic.md`). Live expectation = backtest Sharpe **− 0.7**. Per-regime/per-cell rankings are unaffected (the artifact is roughly uniform); absolute live numbers should be deflated.

> **Apr 28 2026 note:** This diagnostic asks whether broad regime multipliers improve drawdown-adjusted portfolio performance. The answer (no — baseline 4.27 daily Sharpe beats all regime variants) is a portfolio-level replay of validated trades; it does not depend on whether the StochRSI entry signal or the framework is the source of edge. Conclusion stands.

## Knowledge

Window: `2020-01-01` to `2025-12-31`. Source: validated StochRSI Enhanced trades for `GLD`, `IAU`, `SLV`, `GDX`, replayed on one realized-P&L timeline.

This is diagnostic-only. It scales closed-trade P&L by entry-regime multipliers; it does not change strategy logic, model intratrade cash constraints, or deploy live sizing.

Portfolio capital basis: `$40,000` (`$10,000` per symbol sleeve, matching the single-symbol backtests).

## Data Coverage

| Symbol | Intraday coverage used |
|--------|------------------------|
| GLD | 2020-07-27 to 2025-12-31 (34,910 bars) |
| IAU | 2020-07-27 to 2025-12-31 (30,753 bars) |
| SLV | 2020-07-27 to 2025-12-31 (35,481 bars) |
| GDX | 2020-07-27 to 2025-12-31 (36,267 bars) |

Closed trades replayed: **1,959**.

## Variants

| Variant | RANGING | TRENDING_UP | TRENDING_DOWN | HIGH_VOL |
|---------|---------|-------------|---------------|----------|
| baseline | 1.00x | 1.00x | 1.00x | 1.00x |
| conservative | 1.00x | 0.75x | 0.50x | 0.50x |
| aggressive_filter | 1.00x | 0.75x | 0.25x | 0.25x |
| high_vol_only | 1.00x | 1.00x | 1.00x | 0.50x |

## Portfolio Results

| Variant | P&L | Return | Max DD | Max DD % | Daily Sharpe | Worst day | Worst week | Affected trades | P&L vs base | DD vs base |
|---------|-----|--------|--------|----------|--------------|-----------|------------|-----------------|-------------|------------|
| baseline | $29,595.97 | 73.99% | $408.66 | 0.58% | 4.27 | $-103.11 | $-187.23 | 0 | $0.00 | $0.00 |
| conservative | $25,555.43 | 63.89% | $318.85 | 0.48% | 4.15 | $-103.11 | $-177.14 | 734 | $-4,040.54 | $-89.81 |
| aggressive_filter | $24,248.92 | 60.62% | $318.85 | 0.49% | 4.00 | $-103.11 | $-177.14 | 734 | $-5,347.05 | $-89.81 |
| high_vol_only | $28,104.51 | 70.26% | $408.66 | 0.60% | 4.19 | $-103.11 | $-187.23 | 137 | $-1,491.46 | $0.00 |

## Diagnostic Read

- Baseline remains strongest on raw P&L: $29,595.97.
- Best drawdown variant is `conservative` at $318.85 max DD.
- Best daily Sharpe variant is `baseline` at 4.27.
- `high_vol_only` changes 137 trades and gives $-1,491.46 P&L vs baseline with $0.00 DD change.

Decision implication: only promote regime sizing if a variant materially improves drawdown-adjusted returns. If reduced-risk variants mostly cut P&L without meaningful drawdown relief, keep regime as dashboard/context or a narrow high-vol caution signal.
