# Calibration Notes — Algo Trader V1

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
  --parameters '{"rsi_period":7,"stoch_period":14,"overbought":60,"oversold":40,"adx_threshold":50,"skip_adx_filter":false,"sl_atr":2.0,"dynamic_adx":false,"trailing_stop":true,"trail_atr":0.5,"trail_after_bars":1,"min_hold_bars":3,"skip_days":[],"long_only":true}'

# Pre-window baseline (subtract to isolate Mar 20 – Apr 20)
# Same command with --end 2026-03-20
```

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
