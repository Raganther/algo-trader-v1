Status: current | Epistemic: confirmed | Last verified: 2026-04-23

# Overnight Gap Distribution — GLD / IAU / SLV / GDX

Source: `backend/research.db` → `price_data_daily`. Gap = `(open[t] - close[t-1]) / close[t-1]`.
Regenerate: `python3 -m backend.analysis.gap_distribution`.

## Full history (absolute gap)

| Symbol | Samples | Range | p50 | p90 | p95 | p99 | Max |
|--------|---------|-------|-----|-----|-----|-----|-----|
| GLD | 5,380 | 2004-11-19 → 2026-04-10 | +0.41% | +1.25% | +1.64% | +2.74% | +5.97% |
| IAU | 5,330 | 2005-01-31 → 2026-04-10 | +0.41% | +1.27% | +1.69% | +2.74% | +5.96% |
| SLV | 5,017 | 2006-05-01 → 2026-04-10 | +0.72% | +2.30% | +3.08% | +5.25% | +13.87% |
| GDX | 5,002 | 2006-05-23 → 2026-04-10 | +0.79% | +2.26% | +2.88% | +4.79% | +13.68% |

## Full history at current reference price (for sizing)

Ref price is the most recent close. `p95_abs` is the 95th-percentile absolute gap in dollars/share — the input to gap-aware position sizing.

| Symbol | Ref $ | p50_abs | p90_abs | p95_abs | p99_abs |
|--------|-------|---------|---------|---------|---------|
| GLD | $437.13 | $1.791 | $5.482 | $7.170 | $11.963 |
| IAU | $89.56 | $0.371 | $1.142 | $1.513 | $2.458 |
| SLV | $69.08 | $0.495 | $1.591 | $2.128 | $3.625 |
| GDX | $99.39 | $0.790 | $2.250 | $2.867 | $4.765 |

## Signed distribution (full history)

Down-gaps vs up-gaps. Symmetric for random-walk; asymmetric if there's tail skew (relevant: metals have fat down-gap tails historically).

| Symbol | p1 (worst down) | p5 | p50 | p95 | p99 (worst up) |
|--------|-----------------|----|----|----|----------------|
| GLD | -2.34% | -1.25% | +0.05% | +1.26% | +2.19% |
| IAU | -2.33% | -1.26% | +0.07% | +1.28% | +2.24% |
| SLV | -4.22% | -2.22% | +0.09% | +2.36% | +4.01% |
| GDX | -3.90% | -2.20% | +0.10% | +2.31% | +3.97% |

## Trailing 5 years

Sanity check for regime shift. If trailing-5y percentiles are materially different from full-history, prefer trailing-5y for sizing.

| Symbol | Samples | Range | p50_abs | p95_abs | p99_abs |
|--------|---------|-------|---------|---------|---------|
| GLD | 1,256 | 2021-04-12 → 2026-04-10 | +0.41% | +1.85% | +2.80% |
| IAU | 1,255 | 2021-04-12 → 2026-04-10 | +0.42% | +1.83% | +2.86% |
| SLV | 1,255 | 2021-04-12 → 2026-04-10 | +0.78% | +3.39% | +5.63% |
| GDX | 1,256 | 2021-04-12 → 2026-04-10 | +0.81% | +2.97% | +4.80% |

## Apr 23 2026 SLV reference

SLV overnight gap Apr 22 close → Apr 23 open: $70.365 → $68.67 = **−2.41%**. Where does this land in the distribution?

SLV full-history signed percentiles: p1 -4.22%, p5 -2.22%, p99 +4.01%. The −2.41% event falls between p1 and p5 (1–5% tail of historical down-gaps).

## Implications for sizing (1% gap budget)

At 1% of equity allocated to gap risk per symbol, and using 95th-pctl absolute gap:

| Symbol | p95 abs $ | Gap cap @ $94k equity | Current notional cap (25%) | Which binds? |
|--------|-----------|-----------------------|----------------------------|--------------|
| GLD | $7.170 | 131 sh | 53 sh | **notional** |
| IAU | $1.513 | 621 sh | 262 sh | **notional** |
| SLV | $2.128 | 441 sh | 340 sh | **notional** |
| GDX | $2.867 | 327 sh | 236 sh | **notional** |

At 1% gap budget with current $94k equity, the 25% notional cap still binds for all 4 symbols — gap-aware sizing would be a **no-op at current equity**. As equity grows (the notional cap scales linearly with equity, so does the gap cap) the ratio stays constant, so the notional cap will keep binding unless the gap budget is tightened or the notional cap is loosened.

To make the gap cap bite, options are:
- Tighten gap budget to 0.5% → SLV cap becomes ~221 sh (vs 340 notional) → binds
- Loosen notional cap (e.g. 50%) → gap cap becomes the binding constraint
- Accept: at current 25% notional cap, gap risk is bounded by notional, not by an explicit gap budget

