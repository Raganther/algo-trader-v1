# Active Plan — Forward Testing & Mechanics Verification
Started: 2026-02-27

## What we're doing right now
Running 4 paper bots with aggressive test params (OB 60/OS 40, ADX 50, 3-bar hold/trail) to:
1. Verify live execution mechanics before real money
2. Generate a calibration dataset to validate the backtest engine

All known long-side bugs are fixed. Bots are running cleanly from Mar 16 onwards.

---

## Active steps

### Mechanics still to confirm
- [ ] **Trailing stop FIRING in profit** — passive wait. Needs a trade where trail ratchets above entry before price reverses intrabar. Mar 16: trail ratcheted on SLV and GDX but both closed via K-signal.

### Short trading — must be enabled before real money
- [ ] **Fix live_broker sell() guard** — current guard blocks ALL sells from flat. Need to distinguish: (a) closing a long = allow, (b) opening a short from flat = allow when `long_only=False`, (c) duplicate exit = block. Fix: check strategy position state, not Alpaca position.
- [ ] **Verify short mechanics in live** — short entry, buy stop loss (above entry), trailing stop ratchets DOWN, short exit. Full mechanics checklist same as longs.

### Calibration comparison (ongoing)
- [ ] **Repeat calibration check ~Apr 16** — run same backtest subtraction method with ~1 month of clean live data. Expect ~80-100 trades per symbol. That's when the comparison is meaningful.

### After mechanics verified (long + short)
- [ ] Compare live results to backtest predictions
- [ ] Switch to validated params (OB 80/OS 15, hold 10, trail 10, skip Monday)
- [ ] Start real-money micro trading (€100-200, fractional shares)

---

## Chart — Price Action Dashboard
Stage 1 complete. Stage 2 next.

- [x] Price data pipeline + candlestick chart at `/chart`
- [x] Symbol selector + time range
- [ ] **Stage 2:** Trade overlays — fetch entries/exits from `live_trade_log`, plot markers (entry, exit, stop level), toggle live vs backtest
- [ ] **Stage 3:** Regime shading (ADX + SMA slope), win rate by regime

---

## Observations
*Working insights from the current testing phase. Graduate to CLAUDE.md or strategy cards when confirmed.*

### Calibration methodology (established Mar 16)
The test params (OB 60/OS 40, ADX 50) are not a trading strategy — they're a calibration instrument. By running the same params in backtest and live simultaneously, we can check whether the backtest engine faithfully models reality.

**How to run the comparison:**
```bash
# Full window + lead-in (for warmup)
python3 -m backend.runner backtest --strategy StochRSIMeanReversion --symbol GLD \
  --timeframe 15m --start 2026-01-01 --end 2026-04-16 --source alpaca \
  --spread 0.0003 --delay 0 \
  --parameters '{"rsi_period":7,"stoch_period":14,"overbought":60,"oversold":40,"adx_threshold":50,"skip_adx_filter":false,"sl_atr":2.0,"dynamic_adx":false,"trailing_stop":true,"trail_atr":2.0,"trail_after_bars":3,"min_hold_bars":3,"skip_days":[],"long_only":true}'

# Pre-window baseline (subtract to isolate the live test window)
# Same command with --end 2026-03-05
```
Run both, subtract trade counts, divide returns to isolate the window. Do this for all 4 symbols.

**Why the lead-in matters:** backtest needs ~50 bars of warmup before indicators are valid. A short window without lead-in will show fewer trades than live (which was already running). Starting from Jan 1 ensures warmup completes silently before the comparison window opens.

### First calibration snapshot — Mar 5–16 (11 trading days)
Backtest (with Jan 1 lead-in, long_only=True) vs live DB:

| Symbol | Backtest trades | Live trades | Backtest return |
|--------|----------------|-------------|----------------|
| GLD    | 8              | 10          | -0.27%          |
| IAU    | 5              | 8           | -0.32%          |
| SLV    | 10             | 10          | -0.36%          |
| GDX    | 6              | 8           | -0.66%          |

SLV exact. GLD close. IAU/GDX off by 2-3 trades — likely data resampling differences (backtest uses 1m→15m resample, live hits API directly) plus a couple of bug-affected trades in early window. Direction correct — both show losses in a downtrending metals market. Too early for firm conclusions; repeat at ~Apr 16.

### adx_threshold: live bots use 50, not 20
Validated params use adx_threshold:20. Test bots use adx_threshold:50. These are different — do not mix them. The bot scripts (`scripts/run_*_test.sh`) are the source of truth for live params.

### Data integrity baseline
- Mar 03–04: gaps (bugs active, acceptable)
- Mar 05 onwards: 100% fill capture
- Mar 16: full Alpaca order audit — all records matched pm2 logs perfectly
- Clean calibration data effectively starts Mar 16 (all known bugs now fixed)
