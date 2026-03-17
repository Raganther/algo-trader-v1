# Observations — Algo Trader V1
*Running insights from the forward testing phase. Graduate to CLAUDE.md or strategy cards when confirmed.*

---

## Calibration methodology (established Mar 16)
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

**Layered comparison framework (Mar 17):**
Each level of comparison confirms something different:

| What you compare | What it confirms |
|---|---|
| Trade count | Signal generation is faithful — indicators, bar timing, entry/exit logic match |
| Entry/exit prices (trade by trade) | Whether the 0.03% spread assumption reflects reality |
| Stop fill prices vs backtest | How accurately backtest models intrabar server-side stop execution |
| Aggregate P&L | Overall model accuracy |

**Caveats:**
- Paper fills ≠ real-money fills — Alpaca paper simulates at market price; thin/fast markets may differ in live trading
- Calibration is a snapshot — valid for the market conditions during the test window only
- Need ~80-100 trades for P&L comparison to be statistically meaningful (10 trades = one outlier dominates)

**What the calibration ultimately answers:** "Is my backtest testing the same strategy my bot is running?" That confirms the simulator is faithful. Whether paper results transfer to real money is the next layer — answered by micro-trading.

---

## First calibration snapshot — Mar 5–16 (11 trading days)
Backtest (with Jan 1 lead-in, long_only=True) vs live DB:

| Symbol | Backtest trades | Live trades | Backtest return |
|--------|----------------|-------------|----------------|
| GLD    | 8              | 10          | -0.27%          |
| IAU    | 5              | 8           | -0.32%          |
| SLV    | 10             | 10          | -0.36%          |
| GDX    | 6              | 8           | -0.66%          |

SLV exact. GLD close. IAU/GDX off by 2-3 trades — likely data resampling differences (backtest uses 1m→15m resample, live hits API directly) plus a couple of bug-affected trades in early window. Direction correct — both show losses in a downtrending metals market. Too early for firm conclusions; repeat at ~Apr 16.

---

## Memory system restructure (Mar 17)
Split plan.md into two files — plan.md (active steps only) and observations.md (running insights). Steps have a different lifecycle to insights: steps complete and get cleared, insights accumulate and graduate to strategy cards. Keeping them in the same file caused observations to crowd out steps as the project grew.

Added git-save guard hook (PreToolUse on Bash): blocks git-save.sh if plan.md and observations.md are unchanged since last commit. Ensures memory files are always updated before a save.

---

## adx_threshold: live bots use 50, not 20
Validated params use adx_threshold:20. Test bots use adx_threshold:50. These are different — do not mix them. The bot scripts (`scripts/run_*_test.sh`) are the source of truth for live params.

---

## Data integrity baseline
- Mar 03–04: gaps (bugs active, acceptable)
- Mar 05 onwards: 100% fill capture
- Mar 16: full Alpaca order audit — all records matched pm2 logs perfectly
- Clean calibration data effectively starts Mar 16 (all known bugs now fixed)
