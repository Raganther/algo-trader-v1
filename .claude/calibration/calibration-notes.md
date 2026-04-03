Status: current | Epistemic: confirmed | Last verified: 2026-04-01

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

- **Intrabar stop timing in backtest** — backtest may fire stops at bar close rather than intrabar. If so, it would under-predict TS exits and over-predict K-exits relative to the live 50/50 split. This is the most likely source of K/TS ratio divergence at Apr 20. If confirmed, the stop execution model needs an intrabar simulation component.
- **Residual 0.90x under-prediction — CAUSE CONFIRMED (Apr 3)** — with `long_only:true` and `trading_hours:[13.5,20]`, backtest predicts ~10% fewer trades than live. Root cause identified: **partial bar at market open**. At 13:30 UTC, the live bot polls Alpaca and sees the first bar of the day appearing (0–2 minutes old). It fires `on_bar()` on this incomplete bar. StochRSI K computed on 1–2 minutes of data behaves differently than on the complete 15-min bar the backtest uses — when the OS reading is marginal, only the partial bar crosses the threshold (live fires, backtest doesn't). When the OS reading is very deep, both fire (IAU Mar 31, SLV Mar 26). Of 9 market-open live trades in the Mar 20–Apr 2 window, 7 have no backtest match — this accounts for the full ~5-trade gap. The data fetch was also corrected (backtest now fetches 15m directly from Alpaca, matching live bot — no impact on trade count but correct for consistency). **For Apr 20 calibration:** expect ~0.90–0.95x ratio to persist. This is explained and not a model error. If exact 1:1 matching is required, live bot would need a partial-bar guard (check `bar_open_time + 15min <= now` before calling `on_bar()`). Not worth implementing before real money; revisit post-Apr-20.
- **Execution layer calibration across regimes** — the Apr 20 calibration is a snapshot of one unusual regime (post-metals-crash recovery, high intraday volatility). Whether spread and slippage assumptions hold in calmer or more strongly trending conditions is untested. Calibration is valid for this window; treat it as a lower bound on confidence, not a universal constant.
- **Whether stop slippage is systematic** — live range $0.00–$0.14/share, most under $0.05. Sample is 50 trades across 12 days — too small to determine if there's a directional bias. Apr 20 Layer 3 will give a larger sample. If systematic (e.g. always negative, always under $0.05), worth adding a fixed slippage assumption to the backtest stop model.

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
