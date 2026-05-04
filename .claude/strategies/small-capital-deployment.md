Status: current | Epistemic: backtest-validated, not live-tested | Last verified: 2026-05-04

# Small-Capital Deployment Plan ($1k start)

> Practical deployment shape if real-money pilot starts at **$1k** rather than the original $5–10k threshold. Documents what changes and why, with the empirical $1k backtest as the anchor.

## Why this exists

Original framing in CLAUDE.md was "need $5–10k to deploy real money." User asked Apr 30 PM whether $1k could work as a slow-compounding starting point. The answer is **yes with structural modifications** — the strategy survives at $1k but is not the same product as the $94k system. This file is the spec for that smaller variant.

## The structural problem at $1k

**Whole-share sizing + GTC stops** (post-Apr 17 architecture) means each entry must be ≥1 share. At 25% per-bot notional cap, $1k equity = $250 per position:

| Symbol | Price (May 2026) | $250 cap / price | Tradable? |
|---|---:|---:|---|
| SLV | ~$25 | 10 shares | ✓ clean (granular sizing) |
| IAU | ~$45 | 5 shares | ✓ ok |
| GDX | ~$45 | 5 shares | ✓ ok |
| XBI | ~$130 | 1 share | rounding tax |
| GLD | ~$200 | 1 share | rounding tax |
| XOP | ~$200 | 1 share | rounding tax |
| **OIH** | **~$440** | **0 shares** | **❌ priced out** |
| SMH | ~$240 | 1 share | rounding tax |
| IWM | ~$220 | 1 share | rounding tax |

Two structural problems:
1. **Symbol exclusion** — OIH literally cannot trade. SMH/IWM/IBB marginal.
2. **Sizing-rule override by quantisation** — at $94k the 2% risk rule binds at the share level (121.3 → 121 shares = 0.25% error). At $1k it binds at "1 share or 0 shares" — the risk-amount calculation is essentially decorative.

Sharpe is sizing-invariant **only when sizing is continuous**. Discrete shares break that property. The tax scales as ~1/√equity.

## Recommended $1k configuration

```
Lineup:        SLV + IAU + GDX + XBI                  [4 bots, 3 economic bets compressed to 2]
Per-bot cap:   50% (vs default 25%)                   [doubles slot size, halves bot count to 2 active]
Portfolio cap: 100%                                    [unchanged — keeps total exposure bounded]
Stops:         GTC + whole-share                       [unchanged — don't break what works]
Risk per trade: 2%                                     [unchanged — overridden by share rounding anyway]
Min hold:      10 bars                                 [unchanged]
Skip days:     Monday                                  [unchanged]
```

**Why 50% per-bot cap, not 25%.**
At 25% × $1k = $250, you cannot buy 1 share of GLD without exceeding the cap. At 50% × $1k = $500, you can hold 2 shares of GLD (and have a sizing gradient on cheaper symbols). The portfolio-level 100% cap still binds total exposure, so the change is "2 slots × 50%" instead of "4 slots × 25%". Less diversification per moment, but the alternative is structural unfillability.

**Why these 4 symbols.**
- All sub-$130 → tradable with whole-share sizing
- SLV + IAU + GDX cover the gold cluster (3 of 4)
- XBI is the only biotech in the validated set
- Energy cluster (OIH/XOP) is dropped — XOP at $200 marginal, OIH at $440 impossible
- This collapses the "3 independent economic bets" structure into "2" (gold + biotech)

## Empirical validation — $1k backtest

Run on 2026-05-04 with `--initial 1000 --position-cap-frac 0.50 --symbols SLV,IAU,GDX,XBI` over 2020-07-27 → 2026-04-27:

| Metric | $1k 4-bot @ 50% | $94k 7-bot @ 25% (Run 0) | Δ |
|---|---:|---:|---:|
| Final equity | **$5,118.32** | $493,220 | – |
| Return | **+411.83%** | +424.09% | −12pp (≈ same) |
| Sharpe (daily) | **3.83** | 4.95 | **−1.12** |
| Max DD | **4.67%** | 3.41% | +1.26pp |
| Trades | 2,335 | 4,344 | half (4 sym vs 7) |
| Max concurrent | 4 | 7 | – |

**Per-symbol contribution ($1k run):**
- SLV: 569 trades, $1,423 PnL, 48.5% WR
- GDX: 557 trades, $1,189 PnL, 44.7% WR
- XBI: 547 trades, $1,072 PnL, 45.7% WR
- IAU: 662 trades, $434 PnL, 40.8% WR

**Cluster co-occupancy ($1k run):**
- gold (GDX/IAU/SLV, no GLD): N=2 26.9%, N=3 4.0%, N=4 0% (no GLD = no possibility)
- energy: N=0 100% (no symbols deployed in this cluster)
- biotech (XBI): N=1 33.2%

## Interpretation

**Returns hold; Sharpe drops 1.12; DD widens 1.26pp.**

- **Returns hold (411% vs 424%)** — the compounding mechanism works as expected. ~33% annualised at $1k matches the $94k figure.
- **Sharpe drops from 4.95 → 3.83** — the rounding tax + reduced lineup costs ~1.1 points of risk-adjusted return. Still > 2.0 quality bar, but materially below the headline backtest. Realistic expectation at this size.
- **DD widens 4.67% vs 3.41%** — discrete-share sizing produces lumpier exposure on adverse days. Worst-case dollar drawdown ~$47 on $1k; same percentage as $3,200 on $94k. Psychologically survivable but watch for over-sizing.
- **Energy cluster is 100% absent** — confirms OIH/XOP/XLE drop out cleanly. No "partial fill" — you simply don't have the bet.

## Compounding path

At ~33% annualised, $1k → $5,118 in 5.75 years. With a more conservative 25% annualised expectation (Sharpe shading + slippage drag at small size):

```
Year 0:  $1,000
Year 1:  $1,250
Year 2:  $1,563   ← around here you can re-add GLD with proper granularity
Year 3:  $1,953
Year 4:  $2,441   ← around here OIH becomes tradable (>$1,800 needed)
Year 5:  $3,052
Year 6:  $3,815
Year 7:  $4,768
Year 8:  $5,960   ← back to original 7-bot lineup viability
```

**Faster path: monthly contributions.** $200/month + 25% annualised gets to $5k threshold in ~18–24 months. Contributions dominate compounding at this size.

## Lineup expansion thresholds (re-add as equity grows)

| Equity | Cap | Slot size | Symbols unlockable |
|---:|---:|---:|---|
| $1,000 | 50% | $500 | SLV, IAU, GDX, XBI (current) |
| $1,500 | 50% | $750 | + GLD (clean), XOP (clean) |
| $2,000 | 25% | $500 | back to default cap; full metals + XBI |
| $2,800 | 25% | $700 | + XOP (clean) |
| $5,300 | 25% | $1,325 | + OIH (clean) — full 7-bot lineup viable |

**Above ~$5k**, the rounding tax becomes negligible and the deployment is structurally identical to the $94k system, just smaller.

## Risks specific to small-capital deployment

1. **Behavioural risk: dollar amounts feel meaningless.** A 4.67% DD on $1k = $47. Tempting to deviate from system because "it's only $50". Discipline cost > capital cost at this size.
2. **Spread + commission ratio.** Alpaca paper has no commissions; real-money commission depends on broker tier. At $200 position with $0.06 spread = 0.03% — same %. Spread cost is scale-invariant, but if real broker has per-share fees the small positions amplify the drag.
3. **Energy gap.** With no OIH/XOP/XLE deployed, a sustained metals chop while energy rallies (the kind of regime where the $94k lineup makes money on the energy cluster) is dead time at $1k. The lineup is more concentrated than the validated 7-bot setup.
4. **No Sharpe headroom for cap-shrink.** The Apr 30 PM cap-shrink experiment (8 bots × 12.5%) requires symbols sized cleanly at 12.5% of equity. At $1k that's $125/position — only SLV (5 shares × $25) survives. Cap-shrink is unavailable until ~$5k.

## Decision rule for graduating

Re-evaluate the lineup at any of these triggers:
- Equity crosses $1,500 → re-add GLD/XOP, return to 25% cap, run as 5–6 bot
- Equity crosses $2,000 → portfolio cap binds at 4×25% again, return to default lineup
- Equity crosses $5,000 → re-add OIH, full 7-bot lineup, original system
- Live Sharpe in the small-cap config < 2.0 over 6 months → strategy doesn't scale down; pause and reassess
- Live Sharpe ≥ 3.0 → tax is tolerable, strategy works as designed at this size

## What's not solved here

- **Live execution validation at $1k.** The backtest is computed on the same Alpaca 15m bars as the $94k validation. Whole-share rounding behaves the same in backtest and live, so the figures should translate — but real-money fills at small share counts (1 share orders) may have different microstructure than the $94k 121-share fills. Not validated until paper-traded at the small size.
- **Real-money commissions modelling.** If user's real broker is not Alpaca paper, commission structure may shift the result. Not modelled here.
- **Tax drag.** Backtest is pre-tax. At ~750 trades/year with mostly intraday holds, all P&L is short-term gains. Effective annualised return after tax ≈ pre-tax × (1 - marginal_rate).

## Files referenced

- Empirical run command: see "Empirical validation" section above for full CLI invocation
- Snapshot output: `.claude/strategies/portfolio-runner-baseline.md` was overwritten with the $1k run on 2026-05-04, then restored to the canonical V2 baseline. Re-run the canonical command to regenerate if needed.
- Per-bot cap mechanism: `backend/strategies/stoch_rsi_mean_reversion.py` `position_cap_frac` parameter
- Portfolio cap mechanism: `backend/engine/correlation_sizing.py` `portfolio_cap_max_size` helper, default ON
