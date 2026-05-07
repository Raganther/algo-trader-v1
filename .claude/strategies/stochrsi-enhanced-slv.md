Status: current | Epistemic: headline confirmed; framework IS the edge (signal decorative); metals direction-dependent (regime risk) | Last verified: 2026-04-28

# StochRSI Enhanced — SLV 15m

> **May 7 2026 caveat.** Sharpe figures below are **close-anchored backtests with ~0.7 Sharpe optimism** (1-bar polling delay artifact, see `.claude/calibration/live-vs-backtest-iau-diagnostic.md`). Live expectation = backtest Sharpe **− 0.7**. HWM trail anchor (`.claude/strategies/trail-anchor-hwm.md`, opt-in via `trail_anchor: 'hwm'`) lifts long-window 7-bot Sharpe by +0.78 and is structurally insensitive to the artifact; per-asset HWM Sharpes not yet re-run.

> **Strategy file:** `backend/strategies/stoch_rsi_mean_reversion.py`

> **Apr 28 2026 status update — framework attribution finding.**
>
> Verified Sharpe (Apr 28): **2.46** full-strategy / **2.47** long-only — *long-only Sharpe ≈ full-strategy on SLV; shorts add return but cost roughly equivalent DD-adjusted noise.* Headline returns/DD on this card remain accurate.
>
> Random-entry control (tested directly on SLV): replacing the StochRSI entry trigger with random Bernoulli draws (p=0.15, seed=42), keeping all other logic identical, produces Sharpe **2.04** vs validated **2.46**. The StochRSI entry contributes ~0.42 Sharpe — real but a minority of the total edge. The bulk of the Sharpe comes from the position-management framework (2.0 ATR stop, trailing stop after 10 bars, ADX ranging filter, 2% fixed-risk sizing, 25% notional cap, K-cross exit, 10-bar min-hold).
>
> What this means: the metrics below are correct as a record of *what the validated recipe produces on SLV*. The interpretation "StochRSI mean-reversion is the edge on SLV" is **partially correct** — the entry signal contributes meaningfully but is not the primary effect. See `research-log.md` → "Random-Entry Control — Apr 28 2026" for full data.

## Knowledge

### Validated Parameters

Same params as GLD 15m — no tuning needed, transferred directly.

| Param | Code name | Value |
|---|---|---|
| RSI period | `rsi_period` | 7 |
| Stoch period | `stoch_period` | 14 |
| Overbought | `overbought` | 80 |
| Oversold | `oversold` | 15 |
| ADX threshold | `adx_threshold` | 20 |
| ADX filter ON | `skip_adx_filter` | false |
| ATR stop | `sl_atr` | 2.0 |
| Trailing stop | `trailing_stop` | true |
| Trail ATR mult | `trail_atr` | 2.0 |
| Trail after bars | `trail_after_bars` | 10 |
| Min hold | `min_hold_bars` | 10 |
| Skip days | `skip_days` | [0] (Monday) |

#### Backtest command:
```bash
python3 -m backend.runner backtest --strategy StochRSIMeanReversion --symbol SLV --timeframe 15m \
  --start 2020-01-01 --end 2025-12-31 --source alpaca --spread 0.0003 --delay 0 \
  --parameters '{"rsi_period":7,"stoch_period":14,"overbought":80,"oversold":15,"adx_threshold":20,"skip_adx_filter":false,"sl_atr":2.0,"trailing_stop":true,"trail_atr":2.0,"trail_after_bars":10,"min_hold_bars":10,"skip_days":[0]}'
```

### Performance Summary (verified Apr 27 2026)

- **Full-period return (2020 → Apr 27 2026):** **+144.26%**, **Max drawdown:** 2.00%, **Trades:** 581, **Win rate:** 47%
- **Comparable 2020–2025 sub-window:** ~+108% (compounded from yearly), 544 trades
- **Sharpe:** *needs recompute* — previous +2.41 figure is suspect from same Apr 4 transcription pattern as GLD
- **Holdout test (2024–2025):** +29.9%, Sharpe 2.30 — pre-fix, directionally valid

> **Apr 27 2026 correction:** Today's verified rerun shows **dramatically higher return** than the Apr 4 transcription claimed — ~+108% on the 2020–2025 sub-window vs the card's claimed +97.96%. The trade count is closer (544 vs claimed 485) but still ~12% higher than transcribed. **SLV is the asset most affected by the transcription errors.** The pre-Apr-4 SLV figure was +105.3% / 544 trades, which exactly matches today's 2020–2025 sub-window — meaning the Apr 4 stop-check fix produced effectively no change for SLV either, and the "post-fix" 485 / +97.96% was a clear transcription error. Engine itself healthy (see GLD card for full investigation). **Pre-Apr-4:** +105.3% / 2.00% DD / 544 trades. **Apr 4 transcription (suspect):** +97.96% / 2.00% DD / 485 trades. **Apr 27 verified:** ~+108% / 2.00% DD / 544 trades on 2020–2025; +144.26% / 2.00% DD / 581 trades on extended window.

### Year-by-Year (verified Apr 27 2026)

| Year | Return | DD | Trades |
|---|---|---|---|
| 2020 | +2.84% | 2.84% | 44 *(partial — starts Jul)* |
| 2021 | +12.27% | 2.03% | 101 |
| 2022 | +23.94% | 1.27% | 83 |
| 2023 | +10.30% | 1.72% | 110 |
| 2024 | +17.84% | 3.62% | 104 |
| 2025 | +11.84% | 1.94% | 102 |
| 2026 (YTD to Apr 27) | +16.98% | 6.77% | 37 |

2022 was strongest (+23.94%) — silver rally year. 2026 YTD already +16.98% on 37 trades but with the highest single-year DD (6.77%) — reflects the Apr 22 metals selloff.

### Key Findings

**Why it works:** Silver shares the same mean-reversion structure as GLD within a precious metals trend. Same macro drivers (CPI, USD, rates) produce the same short-term oscillations. Params transferred without any tuning.

**Higher absolute return than GLD** (+97.96% vs +39.22%) because silver is more volatile — larger moves per trade. This comes with higher drawdown (2.00% vs 0.73%) — still excellent, but 2.7× GLD's DD.

**Baseline (unenhanced) was already Sharpe 1.31.** Enhancement (trailing stop + min hold + skip Monday) improved it to 2.41 — same structural improvement seen on GLD.

### Thesis Validation

This result confirms the **precious metals thesis**: the StochRSI Enhanced edge is not GLD-specific. It is a structural property of precious metals mean-reverting at 15m within a longer-term trend.

### Long-Only Baseline (verified Apr 28 2026)

Live bots run both long and short since Apr 13. This long-only figure is the **practical floor**.

| Metric | Full Strategy | Long-Only |
|--------|--------------|-----------|
| Return (2020 → Apr 27 2026) | +144.26% | **+94.53%** |
| Max Drawdown | 2.00% | **1.14%** (notably smoother) |
| Trades | 581 | **359** (~38% fewer) |
| Win Rate | 47% | **49%** (slightly higher) |
| Sharpe | *recompute* | *recompute* (prior estimate ~3.10 — likely highest of the four, unverified) |

**Return drop:** −34%. **DD improvement:** −0.86% (much lower). SLV long-only is **strongly profitable on its own** — +94.53% over ~6 years on just the long side. Drawdown half of full-strategy.

**Year-by-year long-only (verified Apr 28 2026):**

| Year | Return | DD | Trades |
|---|---|---|---|
| 2020 | +5.56% | 2.10% | 28 *(partial)* |
| 2021 | +8.50% | 2.02% | 62 |
| 2022 | +8.42% | 2.37% | 49 |
| 2023 | +8.16% | 2.20% | 72 |
| 2024 | +12.75% | 2.06% | 63 |
| 2025 | +11.70% | 1.36% | 62 |
| 2026 (YTD to Apr 27) | +13.88% | 2.27% | 23 |

Most consistent year-by-year of all four metals — every year between +5.56% and +13.88%. 2026 YTD strongest start (+13.88% in <4 months). Old estimate (~+65%) was too pessimistic by ~30 percentage points — the **biggest underestimate of the four assets**, matching the same SLV-pessimism pattern seen in the full-strategy correction.

**Implication:** SLV long-only is viable as a standalone strategy. If shorts ever stopped working, SLV would still produce ~+15%/year compounded. Combined with full-strategy's +144%, SLV is the strongest asset in the bot lineup by a wide margin.

### Forward Testing

slv-test bot running on cloud with aggressive params (OB 60/OS 40, 3-bar hold/trail after 1 bar, 0.5 ATR). All 4 exit mechanics confirmed — see `CLAUDE.md` and `.claude/calibration/calibration-notes.md`.

Backtest prediction for test params (Dec 2025 – Mar 2026): +14.25%, 44 trades, 57% WR — strongest of the 4 symbols under test params.

### Overnight Gap Risk (Apr 23 2026)

SLV is the most gap-prone of the 4 symbols (full-history p95 abs gap 3.08%, p99 5.25%, max 13.87% — silver's intraday and overnight volatility runs ~2× gold). First materially-painful live overnight gap: Apr 23 — entry $70.48 Apr 22, GTC stop $70.15 triggered at open Apr 23 and filled at $68.74 (−$1.74/share = −$605 on 347 sh = −0.64% equity). Clean fill vs open print, not slippage; pure gap risk. The −2.41% event falls between p5 and p1 of the historical down-gap distribution. Current 25% notional cap already bounds worst-case p99 loss to ~1.3% equity per symbol — no SLV-specific sizing change needed. See `.claude/calibration/gap-distribution.md` for full distribution tables.
