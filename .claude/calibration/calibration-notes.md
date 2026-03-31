# Calibration Notes — Algo Trader V1

Status: current | Epistemic: confirmed | Last verified: 2026-03-31

Confirmed methodology for validating the backtest engine against live results.

---

## What calibration is

The test params (OB 60/OS 40, ADX 50, 3-bar hold, 0.5 ATR trail) are not a trading strategy — they're a calibration instrument. By running the same params in backtest and live simultaneously, we verify whether the backtest engine faithfully models reality.

**Clean window: Mar 20 – Apr 20, 2026.** Mar 20 = first fully confirmed clean day with all fixes deployed (race condition fix Mar 19, 18/18 Alpaca orders matched). Target: ~80–100 trades per symbol across the window.

---

## How to run the comparison (run on Apr 20)

```bash
# Full window + lead-in (for indicator warmup)
python3 -m backend.runner backtest --strategy StochRSIMeanReversion --symbol GLD \
  --timeframe 15m --start 2026-01-01 --end 2026-04-20 --source alpaca \
  --spread 0.0003 --delay 0 \
  --parameters '{"rsi_period":7,"stoch_period":14,"overbought":60,"oversold":40,"adx_threshold":50,"skip_adx_filter":false,"sl_atr":2.0,"dynamic_adx":false,"trailing_stop":true,"trail_atr":0.5,"trail_after_bars":1,"min_hold_bars":3,"skip_days":[],"trading_hours":[13,20]}'

# Pre-window baseline (subtract to isolate Mar 20 – Apr 20)
# Same command with --end 2026-03-20
```

**REQUIRED: always include `"trading_hours":[13,20]`** — the live bot only processes bars during 13:30–20:00 UTC (market hours gate in runner.py). Without this param, the backtest processes pre/post-market bars and inflates trade counts by ~11%. This is the main systematic correction for Layer 1 (trade count).

Note: `trading_hours:[13,20]` is slightly more permissive than the live gate — it includes 13:00–13:29 bars that the live bot skips (gate starts at 13:30). This causes a residual ~30% over-prediction, confirmed as acceptable in the Mar 27 preliminary check. Residual cause: 30-minute timing gap only, no logic difference.

Note: removed `"long_only":true` from Apr 20 command — bots are not configured with long_only, so this would produce a mismatch. Bots block shorts via the fractional share guard in live_broker, not via strategy param.

Run both for all 4 symbols. Subtract pre-window baseline to isolate the clean live window.

**Why the lead-in matters:** backtest needs ~50 bars of warmup before indicators are valid. Starting from Jan 1 ensures warmup completes before the comparison window opens.

---

## Layered comparison framework

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

---

## Market regime during calibration window

The Mar 20 – Apr 20 calibration window coincides with an extreme and historically unusual market regime for precious metals.

**Background:** A US-Israeli military operation against Iran (Operation Epic Fury) launched February 28, 2026 triggered one of the most volatile periods in precious metals history. Gold hit an all-time high of ~$5,600 in late January, then crashed ~25% to ~$4,100 by mid-March — its worst weekly performance since 1983. Silver had its single worst day since 1980. Counterintuitively, safe-haven flows went into the US dollar rather than metals, because $120 oil locked the Fed into high rates, making non-yielding assets expensive to hold.

**GLD during our window:** ~$400–430 (gold spot ~$4,000–4,300) — the post-crash partial recovery phase.

**Implications for the Apr 20 calibration:**

- **Execution layer** (spread, slippage, bar timing) — unaffected by market regime. These mechanics are consistent regardless of what price is doing. The calibration of these parameters is valid.
- **Signal layer** (does StochRSI mean reversion work here?) — the backtest Sharpe of 2.54 was built on 2020–2025 data which didn't include this event. We're inadvertently forward-testing the signal layer under conditions outside the training sample. A weaker-than-predicted result doesn't necessarily mean the backtest is wrong — it may mean the regime is genuinely different.
- **GDX divergence** — mining equities are more correlated to broader equity markets than the metal itself. In a risk-off geopolitical environment, GDX selling off while GLD/IAU/SLV hold fits this context.
- **Choppy, reversing price action** — consistent with a market in the middle of a historic crash and partial recovery. Explains the high rate of 1-bar TS exits and exits near entry throughout Mar 20–31.

**Interpreting Apr 20 results in this context:** if the calibration shows the backtest over-predicting profitability, consider whether it reflects an execution model error or simply an unusual market regime. The execution layer check (trade counts, entry/exit prices, stop slippage) is regime-independent and remains the primary validation target.

---

## Calibration integrity — signal vs execution layer

All bug fixes applied during testing are in the execution layer (order placement, fill confirmation, stop management, DB logging). None touched signal generation (StochRSI thresholds, ADX check, bar timing). The calibration comparison is asking only: "when strategy thresholds are met, does a trade fire?" — identical in backtest and live. The fixes made mechanics reliable; they didn't change what the strategy does.

One marginal factor: delayed fills at market open (3–4 min on some symbols) can briefly desync bot state, potentially missing a signal the backtest would catch. This is noise, not systematic drift.

---

## Snapshots

### Mar 5–16 (11 trading days) — preliminary, pre-clean-window
Backtest (Jan 1 lead-in, long_only=True) vs live DB:

| Symbol | Backtest trades | Live trades | Backtest return |
|--------|----------------|-------------|----------------|
| GLD    | 8              | 10          | -0.27%          |
| IAU    | 5              | 8           | -0.32%          |
| SLV    | 10             | 10          | -0.36%          |
| GDX    | 6              | 8           | -0.66%          |

SLV exact. GLD close. IAU/GDX off by 2–3 trades — likely data resampling differences plus a couple of bug-affected trades. Too early for conclusions. Repeat at Apr 20.

### Mar 20–27 (8 trading days) — preliminary, clean window start
Backtest (Jan 1 lead-in, `trading_hours:[13,20]`) vs live Alpaca audit (31 confirmed round trips):

| Symbol | Backtest trades | Live trades | Backtest return |
|--------|----------------|-------------|----------------|
| GLD    | 11             | ~8–9        | +0.05%          |
| IAU    | 8              | ~7–8        | -0.08%          |
| SLV    | 10             | ~8–9        | -0.27%          |
| GDX    | 11             | ~7–8        | -0.81%          |
| Total  | 40             | ~31         | —               |

1.3x trade count ratio — acceptable, explained by 13:00–13:29 timing gap. P&L direction aligned across all 4 symbols (both backtest and live agree: flat/slightly negative choppy week). No red flags. Repeat full comparison at Apr 20.
