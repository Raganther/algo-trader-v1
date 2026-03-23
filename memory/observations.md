# Observations — Algo Trader V1
*Running insights from the forward testing phase. Graduate to CLAUDE.md or strategy cards when confirmed.*

---

## Memory system upgrade (2026-03-22)
Added PostToolUse hook (openbrain-audit-reminder.sh) — fires after every git save and prompts OpenBrain audit. This project now has all three hooks: SessionStart, PreToolUse guard, PostToolUse audit reminder. Future git saves will include an OpenBrain audit step for cross-project knowledge candidates.

OpenBrain is live. First batch of candidates identified (2026-03-22) — pending write after this git save. 10 candidates across 3 categories: broker-alpaca (5 API gotchas), trading-system (4 methodology patterns), strategy-research (1 validated edge). Global CLAUDE.md description confirmed sufficient to guide candidate selection — no project-level guide file needed.

---

## Calibration methodology (established Mar 16)
The test params (OB 60/OS 40, ADX 50) are not a trading strategy — they're a calibration instrument. By running the same params in backtest and live simultaneously, we can check whether the backtest engine faithfully models reality.

**Target date: Apr 20, 2026.** Keep aggressive params running until then. Clean window: Mar 20 – Apr 20.

Mar 20 chosen as window start: first fully confirmed clean day with current params (trail_atr=0.5, trail_after_bars=1) and all fixes deployed (race condition fix Mar 19). 18/18 Alpaca orders matched on Mar 20 audit.

**How to run the comparison (run on Apr 20):**
```bash
# Full window + lead-in (for warmup)
python3 -m backend.runner backtest --strategy StochRSIMeanReversion --symbol GLD \
  --timeframe 15m --start 2026-01-01 --end 2026-04-20 --source alpaca \
  --spread 0.0003 --delay 0 \
  --parameters '{"rsi_period":7,"stoch_period":14,"overbought":60,"oversold":40,"adx_threshold":50,"skip_adx_filter":false,"sl_atr":2.0,"dynamic_adx":false,"trailing_stop":true,"trail_atr":0.5,"trail_after_bars":1,"min_hold_bars":3,"skip_days":[],"long_only":true}'

# Pre-window baseline (subtract to isolate Mar 20 – Apr 20)
# Same command with --end 2026-03-20
```
Run both for all 4 symbols, subtract pre-window baseline to isolate the clean live window. Compare trade counts first, then entry/exit prices, then aggregate P&L.

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

## Trailing stop diagnostic — Mar 18
Ran per-trade exit-type breakdown using PaperTrader directly (not via CLI — required calling `broker.update_price()` per bar and passing `dynamic_adx: False` in params).

**Finding: with OLD trail params (trail_atr=2.0, trail_after_bars=3), backtest predicts ZERO profitable trailing stop fires in Jan-Mar 2026.** All exits in profit go via K-signal. Stop fires all below entry (stop losses). This matches live exactly — no bug.

With TIGHTENED params (trail_atr=0.5, trail_after_bars=1), backtest predicts ~5 profitable trail fires per symbol for the same window. These are possible because the tighter trail needs only a small rally (~0.5 ATR above entry) before it ratchets above entry, then fires on any intrabar reversal.

The Sharpe improvement from trailing stops was earned over a full 5-year backtest that includes gold bull phases. In the Feb-Mar 2026 metals selloff, every oversold entry is a dead-cat bounce — trail never gets above entry with the old params. With 0.5 ATR trail, even a 1-2 bar bounce is enough. Just need the right trade.

**Gotcha — `dynamic_adx` defaults to True:** If running backtest without explicitly setting `"dynamic_adx": false`, the strategy ignores `adx_threshold` and uses a tighter dynamic threshold (20-30), blocking most entries. Always include `"dynamic_adx": false` in any backtest params that set a specific `adx_threshold`. The CLI calibration command in observations.md already has this correct.

---

## Trailing stop update race condition — fixed Mar 19
`update_stop_order` cancels the old stop then immediately places the new one. `cancel_order_by_id` is a blocking HTTP call but Alpaca processes the cancel async server-side — so the shares can still appear "held_for_orders" when the new stop is placed, causing error 40310000 ("insufficient qty available").

**Fix:** 1s `time.sleep()` between cancel and place in `live_broker.update_stop_order`. Location: `backend/engine/live_broker.py` ~line 312.

**History:** The fallback (re-place at old price on failure) was added proactively on Mar 4 — it was anticipated but the root cause was never fixed. The race condition always existed but was only reliably triggered by the tightened trail params (trail_after_bars 1 vs 3), which fire the update call much sooner after the initial stop placement. IAU on Mar 17 updated successfully (trail_after_bars 3, more time had elapsed) — GDX on Mar 19 failed (trail_after_bars 1, update fired very early). The fallback kept the position protected throughout; only the ratchet was lost.

---

## adx_threshold: live bots use 50, not 20
Validated params use adx_threshold:20. Test bots use adx_threshold:50. These are different — do not mix them. The bot scripts (`scripts/run_*_test.sh`) are the source of truth for live params.

---

## Data integrity baseline
- Mar 03–04: gaps (bugs active, acceptable)
- Mar 05 onwards: 100% fill capture
- Mar 16: full Alpaca order audit — all records matched pm2 logs perfectly
- Clean calibration data effectively starts Mar 16 (all known bugs now fixed)
- Mar 17: 4 trades across all 4 bots. Full Alpaca audit — all records matched pm2 logs perfectly. GLD/IAU: buy → K-signal exit (small losses). SLV: buy → trail ratcheted → K-signal exit (near breakeven). GDX: buy → SERVER STOP FIRED @ $93.640351 (19:06 UTC) — stop loss exit, caught post-check. Another server-side stop firing confirmation. Trailing stop firing in profit still unconfirmed — trails ratcheted on SLV/GDX but neither fired above entry.
- Mar 17 EOD: tightened trail params on all 4 bots (trail_atr 2.0→0.5, trail_after_bars 3→1) to maximise chance of seeing trailing stop fire in profit. Paper money — calibration impact acceptable.
- Mar 18: 4 trades across all 4 bots, all flat by EOD (20:23 UTC). GLD/GDX/IAU: K-signal exits (small losses). SLV: server stop fired (stop loss, another confirmation). IAU trail ratcheted ($91.00→$91.21) but still below entry ($91.74) — K-signal exit before trail could fire in profit. All bots clean, no errors.
- Mar 19: 4 trades, all 4 bots flat by ~18:46 UTC. GLD/IAU/SLV: K-signal exits (all losses — metals continuing lower, GLD dropped from $448 to $426). SLV near breakeven (+$0.05/share). GDX: trail update fired but failed (race condition — see below), K-signal exit at small profit ($82.28 vs $81.80 entry). Full Alpaca audit: all 12 orders matched pm2 logs. IAU had two data-fetch empty warnings but trading was unaffected.
- Mar 23: 9 trades across all 4 bots. Full Alpaca audit — all records matched pm2 logs. GLD/SLV first buys took 3-4 min to fill (market open 13:31 UTC — thin spread window, 30s pending_fills timeout fired correctly, fills confirmed later). GDX: entry $80.05 (Mar 20 close), trail ratcheted to $83.35, SERVER STOP FIRED intrabar @ $83.317 (+$958 paper) — **trailing stop fire in profit confirmed**. GLD trail reached $404.64 (above entry $403.63) but K-signal fired first at $406.13. IAU trail reached $82.70 (above entry $82.55) but K-signal fired first at $83.23. Pattern: same-day trades tend to K-exit before trail fires; multi-day holds give trail time to ratchet far enough above entry.
