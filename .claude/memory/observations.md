# Observations — Algo Trader V1
Staging area for new topics and cross-domain coordination.

---

## Overall Status (Apr 21 2026)

**Validated 2.0 ATR trail FIRED in profit (Apr 20). All 4 bots flat, watching for new signals.**

What's confirmed:
- Entry signal + K-exit has real alpha (76–80% K-exit win rate across 67 completed trades)
- Both server-side exit mechanics work (stop loss + trailing stop in profit — test params confirmed Mar 23)
- Execution infrastructure sound (100% audit integrity, all known bugs fixed)
- Signal generalises across 4 assets — confirmed in backtest, consistent in live direction
- Calibration Layers 1, 2, 4 pass (Apr 13) — backtest engine accurate for test params / intraday regime
- Whole-share sizing working — 340+ shares per position, confirmed Apr 15
- Short mechanics confirmed working — GLD shorted Apr 16, K-exit +$38.50. Entry, stop, trail ratchet, K-exit all correct.
- GTC stop fix deployed Apr 17 — eliminates overnight expiry gap permanently
- Validated 2.0 ATR trail confirmed ratcheting (Apr 17-18) — stops climbed significantly during Friday's session.
- **Validated 2.0 ATR trail FIRED in profit (Apr 20)** — SLV trail ratcheted from $70.72 → $72.14 over the session, price pulled back, server stop executed at $72.12 (entry $71.29 → +$283.86). This is the mechanism that drives Sharpe 2.47. Fully confirmed live.
- pm2 startup registered as systemd service (Apr 20) — survives server reboots permanently.

What's not yet confirmed:
- Short stop-loss execution — first short was K-exit. Need a short to run against us and server-side stop trigger.
- Long-only validated Sharpe — headline figures (2.47 etc.) include shorts. Long-only needs explicit rerun.

Apr 20 session P&L (pm2 outage cost locked profits on GLD/IAU):
- GLD: -$6.05 (stopped near breakeven — stop reconstructed low after outage)
- IAU: -$4.22 (stopped near breakeven — same reason)
- SLV: +$283.86 (trail fired in profit)
- Net: +$273.59

Key red flags to track:
- **Regime dependency** — live performance is in the best historical regime for this strategy (2024–2025 metals bull).
- **Correlated entries** — GLD/IAU/SLV all long simultaneously. Pre-real-money requirement: correlation-aware sizing.
- **Slippage spikes on volatile days** — median $0.010/share but outliers at $0.140 and $0.297. Not modelled in backtest.

Path to real money: ~~calibration~~ ✅ Apr 13 → ~~whole-share sizing + short broker code~~ ✅ Apr 15-16 → ~~validated 2.0 ATR trail fires in profit~~ ✅ Apr 20 → **confirm short stop-loss + correlation-aware sizing → real money.**

---

## Active Work

### Critical path — sequenced

1. ~~**Calibration complete Apr 13 — Layers 1, 2, 4 all pass.**~~ ✅ Done. Full summary in `.claude/calibration/calibration-notes.md`. Layer 3 (slippage aggregation) still pending — low priority.

2. ~~**Whole-share sizing + short broker code**~~ ✅ Done. Deployed Apr 15-16 (commit cd507aa). Whole shares confirmed working (340+ shares per position). First short trade confirmed Apr 16 (GLD, K-exit, +$38.50).

3. **Validated params with shorts — NOW RUNNING.** OB 80/OS 15, hold 10 bars, trail 2.0 ATR after 10 bars, skip Monday. First trades: SLV long Apr 15, GLD short+long Apr 16, IAU long Apr 16. All three carrying overnight into weekend (Apr 17 close): SLV +$872, GLD +$326, IAU +$321. Second clean window started — need to confirm: (1) validated 2.0 ATR trail fires in profit, (2) short stop-loss executes correctly.

4. **Portfolio correlation analysis** — run all 4 symbols on validated params simultaneously, shared timeline, tally joint outcomes split by year. Read-only, no execution logic. Do before implementing correlation-aware sizing. Can run in parallel with the validated params forward test window.

5. **Regime-aware sizing** — regime classifier built (`backend/indicators/regime.py`, `scripts/analyse_regimes.py`). Next: build shared-timeline portfolio runner (same piece needed for correlation analysis), tag trades with entry regime, run comparison matrix. See `.claude/strategies/regime-analysis.md`.

### Parallel / lower priority

6. **Chart trade overlays (Stage 2)** — fetch entries/exits from `live_trade_log`, plot markers on chart. No blockers, can be done anytime.

7. **Post-real-money: XLE forward test** — deploy as 5th paper bot after calibration + trail confirmed + sizing implemented. Lower priority than core 4 bots at real money. See `## Plan` in `.claude/strategies/stochrsi-enhanced-xle.md`.

## Staging

- **SLV 2026 HIGH_VOL anomaly** — SLV showing 27.7% HIGH_VOL in 2026 vs 17% for GLD — still the highest in the dataset but less extreme than earlier estimate (prior 49% figure was from Alpaca-only 5.5yr window, now corrected with 20yr Yahoo Finance data). Silver's naturally higher volatility still makes the fixed ATR multiplier (1.5×) more sensitive for SLV. Consider symbol-specific ATR thresholds before implementing live regime detection. See regime-analysis.md.
- **ATR-based position sizing (post-calibration enhancement)** — current sizing deploys equal capital per symbol (~25% of account). Risk per trade is not fixed — it varies with ATR on the day. ATR-based sizing would back-calculate share count from a fixed max risk % (e.g. 1% of account ÷ stop distance = shares to buy). Normalises risk per trade across volatile and calm sessions. Implement post-Apr-20 alongside correlation-aware sizing — both are pre-real-money requirements. Also unlocks GTC stops (whole-share sizing removes Alpaca's fractional short/GTC restriction). See research-log.md cross-cutting learning #6.
- **Late-session entry guard** — block or halve position size when entry signal fires within ~30 min of market close. DAY stops expire before providing meaningful intraday protection; position carries overnight naked until bot re-places stop at open. Testable with existing single-symbol engine (simple time condition in `on_bar()`). Pre-real-money requirement alongside correlation-aware sizing. Implement after correlation analysis.
- **"Phantom sell"** — every session, bots log `⚠️ SELL skipped: no open position`. Not a duplicate exit — it's a blocked short entry attempt. K above OB (60) → `in_overbought_zone = True` → K drops below 50 → `sell()` fires → `live_broker.py` blocks it (fractional short unsupported) → misleading warning logged. State stays clean after block. `in_overbought_zone` resets to False. Two issues: (1) warning says "duplicate exit" — should say "blocked short entry"; (2) `current_sl` set to short stop value before block — stale but harmless. Both resolve when whole-share sizing added. No domain file yet.
- **Year-by-year tables need rerunning** — all 4 strategy domain files (GLD/IAU/SLV/GDX) have year-by-year tables computed with the old stop-check logic (pre Apr 4 fix). Flagged in-file as pre-fix. Rerun post-Apr-20 alongside parameter sensitivity tables. Low priority until calibration complete.
- **Long-only Sharpe figures are estimates** — all 4 strategy files have estimated long-only Sharpe based on pre-fix values. Rerun with `long_only:true` post-Apr-20 to get corrected figures. Confirmed Apr 8: validated params headline Sharpe (2.47 etc.) includes short trades — long-only figures need explicit rerun.
- **Live trade log current to Apr 13** — Alpaca MCP verified through Apr 13. pm2/DB audit pending for Apr 6–13 entries. Run SSH audit before calibration to confirm DB records match. All bots flat EOD Apr 13 — weekend carries resolved at open (1 TS win GDX +0.440, 2 TS losses SLV/GLD) + 5 intraday round-trips net positive.
- **Late-session entry guard — first data point** — Apr 8 triple late-session entry (SLV/GLD/GDX at 19:46 UTC, 14 min before close) resolved Apr 13 at open: GDX +0.440, SLV -0.330, GLD -0.201. Net slightly negative on a sample of 3. Doesn't prove the hypothesis but consistent with it — stops re-placed at open fired within 20 min on gap-down, no chance for the trade to develop. Keep the guard on the pre-real-money list.
- **Aggressive params baseline confirmed (Apr 8)** — long-only backtest 2020–2025 run for all 4 symbols. Results in research-log.md. Key finding: params have real but weak edge (~5–17% over 6 years vs ~25–60% for validated long-only). Live performance regime-dependent — 2024–2025 are the best years historically for these params.
