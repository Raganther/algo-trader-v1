Status: current | Epistemic: confirmed | Last verified: 2026-04-08

# Calibration Notes — Algo Trader V1

Confirmed methodology for validating the backtest engine against live results.

## Plan

### Active
- [ ] **Run Apr 20 calibration comparison** — backtest with identical params over Mar 20–Apr 20 window. Compare trade counts (Layer 1), entry/exit prices (Layer 2), stop slippage (Layer 3), aggregate P&L (Layer 4). Commands in Knowledge section. Stop if a layer fails before proceeding to next.
- [ ] **Apply calibration corrections post-Apr-20** — if spread or slippage models are off, adjust backtest params accordingly before switching to validated params.

### Research
- [ ] **Post-calibration research loop (three phases):** Research (backtest, filter Sharpe > 2 / DD < 3% / WF pass) → Validate (4–8 week forward test, goal is prediction accuracy not profit) → Deploy (real money). Execution layer corrections from Apr 20 apply universally; signal layer needs its own forward test per new strategy.

## Knowledge

### What calibration is

The test params (OB 60/OS 40, ADX 50, 3-bar hold, 0.5 ATR trail) are not a trading strategy — they're a calibration instrument. By running the same params in backtest and live simultaneously, we verify whether the backtest engine faithfully models reality.

**Clean window: Mar 20 – Apr 20, 2026.** Mar 20 = first fully confirmed clean day with all fixes deployed (race condition fix Mar 19, 18/18 Alpaca orders matched). Target: ~80–100 trades per symbol across the window.

### How to run the comparison (run on Apr 20)

```bash
# Full window + lead-in (for indicator warmup)
python3 -m backend.runner backtest --strategy StochRSIMeanReversion --symbol GLD \
  --timeframe 15m --start 2026-01-01 --end 2026-04-20 --source alpaca \
  --spread 0.0003 --delay 0 \
  --parameters '{"rsi_period":7,"stoch_period":14,"overbought":60,"oversold":40,"adx_threshold":50,"skip_adx_filter":false,"sl_atr":2.0,"dynamic_adx":false,"trailing_stop":true,"trail_atr":0.5,"trail_after_bars":1,"min_hold_bars":3,"skip_days":[],"trading_hours":[13.5,20],"long_only":true}'

# Pre-window baseline (subtract to isolate Mar 20 – Apr 20)
# Same command with --end 2026-03-20
```

**REQUIRED: always include `"trading_hours":[13.5,20]`** — the live bot only processes bars during 13:30–20:00 UTC (market hours gate in runner.py). Without this param, the backtest processes pre/post-market bars and inflates trade counts. The value `13.5` = 13:30 exactly matches the live gate. Fractional hour support added Apr 3 — strategy now computes `hour + minute/60` before comparing.

**REQUIRED: always include `"long_only":true`** — the live bots never execute short trades. Short signals fire in the strategy code but are blocked by the fractional share guard in `live_broker.py`. The backtest has no such guard, so without `long_only:true` it executes both long and short trades — roughly doubling the trade count and producing a fundamentally mismatched comparison. The strategy param `long_only` is not set on live bots, but the *executed behaviour* is long-only regardless of where the block happens. Confirmed Apr 3: without `long_only` ratio was 1.79x; with `long_only` ratio is 0.90x (43 backtest vs ~48 live).

Run both for all 4 symbols. Subtract pre-window baseline to isolate the clean live window.

**Why the lead-in matters:** backtest needs ~50 bars of warmup before indicators are valid. Starting from Jan 1 ensures warmup completes before the comparison window opens.

### Layered comparison framework

| What you compare | What it confirms |
|---|---|
| Trade count | Signal generation faithful — indicators, bar timing, entry/exit logic match |
| Entry/exit prices (trade by trade) | Whether the 0.03% spread assumption reflects reality |
| Stop fill prices vs backtest | How accurately backtest models intrabar server-side stop execution |
| Aggregate P&L | Overall model accuracy |

Stop if a layer fails before proceeding to the next.

**Caveats:**
- Paper fills ≠ real-money fills — Alpaca paper simulates at market price
- Calibration is a snapshot — valid for the market conditions during the test window only
- Need ~80–100 trades for P&L comparison to be statistically meaningful

### Market regime during calibration window

The Mar 20 – Apr 20 calibration window coincides with an extreme and historically unusual market regime for precious metals.

**Background:** A US-Israeli military operation against Iran (Operation Epic Fury) launched February 28, 2026 triggered one of the most volatile periods in precious metals history. Gold hit an all-time high of ~$5,600 in late January, then crashed ~25% to ~$4,100 by mid-March — its worst weekly performance since 1983. Silver had its single worst day since 1980. Counterintuitively, safe-haven flows went into the US dollar rather than metals, because $120 oil locked the Fed into high rates, making non-yielding assets expensive to hold.

**GLD during our window:** ~$400–430 (gold spot ~$4,000–4,300) — the post-crash partial recovery phase.

**Key dates confirmed via news (Apr 1):**
- **Mar 19:** Flash crash trigger — Middle East energy infrastructure attacks + hawkish Fed (Warsh). Gold -6.9%, Silver -12.5% intraday.
- **Mar 23:** First sustained bounce after crash — explains best trade day in the log (GLD +5.333, SLV +2.102, all K-exits).
- **Mar 31:** Iran de-escalation catalyst — Trump signals end to military campaign, risk-on open. GLD closed +3.79%. Explains second-best day in log (GLD/IAU/SLV all profitable K-exits from open).
- **Mar 24/27/30:** Choppy reversals mid-recovery — explains correlated TS fires and all-loss days.

**GDX structural divergence:** Gold fell 17% in March; GDX fell 29%. Cause: Iran war → oil spike → mining energy costs surge → margin compression. Miners underperformed bullion by ~12 percentage points. GDX bot underperforming backtest predictions is expected given this dynamic — not a model error.

**Implications for the Apr 20 calibration:**

- **Execution layer** (spread, slippage, bar timing) — unaffected by market regime. These mechanics are consistent regardless of what price is doing. The calibration of these parameters is valid.
- **Signal layer** (does StochRSI mean reversion work here?) — the backtest Sharpe of 2.54 was built on 2020–2025 data which didn't include this event. We're inadvertently forward-testing the signal layer under conditions outside the training sample. A weaker-than-predicted result doesn't necessarily mean the backtest is wrong — it may mean the regime is genuinely different.
- **GDX divergence** — structurally explained by oil/energy cost margin compression. Don't chase with parameter adjustments at Apr 20.
- **Choppy, reversing price action** — consistent with a market in the middle of a historic crash and partial recovery. Explains the high rate of 1-bar TS exits and exits near entry throughout Mar 20–31.

**Interpreting Apr 20 results in this context:** if the calibration shows the backtest over-predicting profitability, consider whether it reflects an execution model error or simply an unusual market regime. The execution layer check (trade counts, entry/exit prices, stop slippage) is regime-independent and remains the primary validation target.

### Calibration integrity — signal vs execution layer

All bug fixes applied during testing are in the execution layer (order placement, fill confirmation, stop management, DB logging). None touched signal generation (StochRSI thresholds, ADX check, bar timing). The calibration comparison is asking only: "when strategy thresholds are met, does a trade fire?" — identical in backtest and live. The fixes made mechanics reliable; they didn't change what the strategy does.

One marginal factor: delayed fills at market open (3–4 min on some symbols) can briefly desync bot state, potentially missing a signal the backtest would catch. This is noise, not systematic drift.

### Two types of slippage — only one is modelled

Spread slippage modelled (`--spread 0.0003`). Stop execution slippage not modelled — live shows $0.00–$0.14/share, typically under $0.05. Will surface in Layer 3 of Apr 20 calibration. If systematic, add to backtest model.

### Snapshots

#### Mar 20–Apr 7 (13 trading days) — live equity curve via Alpaca portfolio history

Pulled Apr 8 via `get_portfolio_history` MCP. Base value: $94,353 (Mar 18).

| Date | Equity | Day P&L | Day % |
|------|--------|---------|-------|
| Mar 20 | $94,212 | -$141 | -0.15% |
| Mar 21 | $93,865 | -$347 | -0.37% |
| Mar 23 | $96,411 | +$2,546 | +2.71% |
| Mar 24 | $96,459 | +$47 | +0.05% |
| Mar 25 | $96,370 | -$89 | -0.09% |
| Mar 26 | $96,609 | +$239 | +0.25% |
| Mar 27 | $96,367 | -$241 | -0.25% |
| Mar 30 | $95,762 | -$605 | -0.63% |
| Mar 31 | $96,776 | +$1,013 | +1.06% |
| Apr 1 | $96,642 | -$134 | -0.14% |
| Apr 2 | $97,695 | +$1,053 | +1.09% |
| Apr 6 | $97,423 | -$271 | -0.28% |
| Apr 7 | $97,837 | +$414 | +0.42% |

**Total: +$3,626 (+3.85%) over 13 trading days.** Three big up days (Mar 23, Mar 31, Apr 2) account for +$4,612 — the rest collectively lost. Max single-day drawdown: -$605 (Mar 30, -0.63%). Only one day below starting equity (Mar 21). Apr 7 includes open GLD position (+$735 unrealized).

**Regime note:** 2024–2025 are the best years in the aggressive params backtest — we're live testing in the best historical regime for this strategy. The equity curve looks clean partly because we're in a metals bull market.

---

#### Mar 5–16 (11 trading days) — preliminary, pre-clean-window
Backtest (Jan 1 lead-in, long_only=True) vs live DB:

| Symbol | Backtest trades | Live trades | Backtest return |
|--------|----------------|-------------|----------------|
| GLD    | 8              | 10          | -0.27%          |
| IAU    | 5              | 8           | -0.32%          |
| SLV    | 10             | 10          | -0.36%          |
| GDX    | 6              | 8           | -0.66%          |

SLV exact. GLD close. IAU/GDX off by 2–3 trades — likely data resampling differences plus a couple of bug-affected trades. Too early for conclusions. Repeat at Apr 20.

## Open Questions

- **Residual 0.90x under-prediction — FIXED (Apr 3)** — root cause: live bot was firing `on_bar()` on the session-open 15m bar when only 0–2 min old (partial bar from Alpaca live API). StochRSI K on 1–2 min of data behaved differently than on the complete 15-min bar the backtest uses — marginal OS readings crossed live but not backtest. 7 of 9 market-open live trades in Mar 20–Apr 2 had no backtest match, accounting for the full ~5-trade gap. **Fix deployed Apr 3:** bar-completion guard detects overnight gap >60 min, defers `on_bar()` until bar is ≥14 min old. **For Apr 20 calibration:** expect ratio ~1.0x. If a residual gap persists after this fix, it has a new unexplained cause and needs investigation. Data fetch also corrected (backtest now fetches 15m directly from Alpaca — no impact on trade count but correct for consistency).
- **K/TS exit ratio — FIXED (Apr 4)** — before fix, backtest showed 8% K-exits / 92% stop exits vs live 50/50. Root cause: backtest was ratcheting the trailing stop using the current bar's close, then immediately checking the current bar's low against the newly elevated stop — causing false stop fires on bullish bars. Fix: capture stop level before ratcheting (`sl_for_check`), use that for the intrabar low/high check. Ratcheted level applies from next bar onwards, matching Alpaca server-side behaviour. After fix: backtest 50/50 K/TS ratio, exactly matching live. Validated on Mar 20–Apr 2 window (36 backtest trades: 18 K / 18 stop). Corrected validated-params figures: GLD Sharpe 2.47 / +39.22%, IAU 1.97 / +32.7%, SLV 2.41 / +97.96%, GDX 2.58 / +129.8%. Fix committed Apr 4: `651c5ce`.
- **Stop slippage — CHARACTERISED (updated Apr 8, 33 stop exits)** — all slippage is negative (fill always below stop price for long exits — 100% directional consistency). Mean: ~$0.025/share. Median: $0.010/share. Outliers: $0.140 (GLD Mar 24 — correlated simultaneous exits), $0.297 (GLD Apr 6 — high-volatility day). The mean is skewed upward by outliers; on normal days median $0.010 holds. Slippage spikes on volatile sessions — this is an important calibration caveat. Backtest models zero stop slippage. **Decision: do not model yet.** Known bias — will cause slight P&L overstatement in Layer 4. Add `stop_slippage` parameter only after Apr 20 Layer 3 confirms the bias holds on a larger sample. Median ($0.010) is the more reliable model input if added.
- **Execution layer calibration across regimes** — the Apr 20 calibration is a snapshot of one unusual regime (post-metals-crash recovery, high intraday volatility). Whether spread and slippage assumptions hold in calmer or more strongly trending conditions is untested. Calibration is valid for this window; treat it as a lower bound on confidence, not a universal constant.

### Snapshots

#### Mar 20–27 (8 trading days) — preliminary, pre-correction (do not use)
Backtest (`trading_hours:[13,20]`, no `long_only`) vs live Alpaca audit (31 confirmed round trips):

| Symbol | Backtest trades | Live trades | Ratio |
|--------|----------------|-------------|-------|
| GLD    | 11             | ~8–9        | ~1.3x |
| IAU    | 8              | ~7–8        | ~1.1x |
| SLV    | 10             | ~8–9        | ~1.2x |
| GDX    | 11             | ~7–8        | ~1.4x |
| Total  | 40             | ~31         | ~1.3x |

**Invalidated by Apr 3 discovery.** The 1.3x ratio was not explained by the 13:00–13:29 timing gap — it was caused by short trades in the backtest that the live bot never executes. P&L direction alignment was correct but trade counts are not a valid comparison without `long_only:true`. Do not use this snapshot as a calibration reference.

#### Mar 20–Apr 2 (12 trading days) — corrected mid-point snapshot
Backtest (`trading_hours:[13.5,20]`, `long_only:true`) vs live MCP audit (48 confirmed trades):

| Symbol | Backtest trades | Live trades | Window return (backtest) |
|--------|----------------|-------------|--------------------------|
| GLD    | 10             | 12          | -0.04%                   |
| IAU    | 11             | 10          | -0.37%                   |
| SLV    | 11             | 14          | +0.03%                   |
| GDX    | 11             | 12          | -0.66%                   |
| Total  | 43             | ~48         | —                        |

**Ratio: ~0.90x** — backtest under-predicts live. Gap confirmed as partial-bar market-open effect (Apr 3): live fires on 1–2 min bars at 13:30 open; backtest uses complete 15-min bars. 7 of 9 market-open live trades have no backtest match. P&L direction aligned: GDX weakest in both (-0.66% backtest, 42% win rate live), GLD/SLV near flat. No red flags. Repeat full comparison at Apr 20 with corrected command.
