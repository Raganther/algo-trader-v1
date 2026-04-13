# Observations — Algo Trader V1
Staging area for new topics and cross-domain coordination.

---

## Overall Status (Apr 13 2026)

**Calibration partial pass. New finding: backtest over-predicts overnight hold P&L.**

What's confirmed:
- Entry signal + K-exit has real alpha (76–80% K-exit win rate across 67 completed trades)
- Both server-side exit mechanics work (stop loss + trailing stop in profit)
- Execution infrastructure sound (100% audit integrity, all known bugs fixed)
- Signal generalises across 4 assets — confirmed in backtest, consistent in live direction

What's not yet confirmed:
- The trail at validated params (2.0 ATR, after 10 bars) — never fired live. This is the component that captures extended moves and drives the Sharpe 2.47. Test params trail (0.5 ATR, 1 bar) is a noise-driven stop — a different mechanism entirely.
- Backtest P&L model accuracy — Apr 20 calibration is the gate (Layers 2–4: entry/exit prices, stop slippage, aggregate P&L)
- Long-only validated Sharpe — headline figures (2.47 etc.) include shorts the bots can't execute. Long-only is estimated at ~1.20–3.10 depending on symbol.

Key red flags to track:
- **Regime dependency** — live performance is in the best historical regime for this strategy (2024–2025 metals bull). 2020 would have been negative at aggressive params.
- **Correlated entries** — GLD/IAU/SLV enter simultaneously. 2% risk × 3 = 6% in one correlated move. Pre-real-money requirement: correlation-aware sizing.
- **Slippage spikes on volatile days** — median $0.010/share but outliers at $0.140 and $0.297. Not modelled in backtest.

Path to real money: calibration (Mon/Tue Apr 14–15) → whole-share sizing + short broker code → validated params with shorts → second clean window (confirm trail + short mechanics) → real money.

---

## Active Work

### Critical path — sequenced

1. **Calibration run Apr 13 — Layer 1 PASS, Layer 2 PARTIAL.** Full snapshot in `.claude/calibration/calibration-notes.md`. Trade counts match exactly (75 vs 75, 1.00x ratio). Entry prices match on intraday trades. **Multi-day holds diverge: backtest captures 2–3× more of extended moves than live.** Root cause hypothesis: backtest keeps trailing stop continuously across overnight gaps; live re-places DAY stop at next open and resets the ratchet chain. **Next critical-path task: investigate and fix the overnight stop model before trusting validated-params Sharpe 2.47 projection.** Layer 3 (slippage) and Layer 4 (aggregate P&L) deferred until this is resolved.

2. **Whole-share sizing + short broker code** — implement immediately after calibration passes. Two parts: (1) position sizing: `floor(risk_budget / stop_distance) = whole shares` replacing fractional allocation; (2) audit `live_broker.py` for direction-aware logic — stop placement, trail ratcheting, and exit order type all need to handle short side. Short signal code already exists and is blocked in `live_broker.py` — unblock once sizing is in place. One day's work, needs to be done carefully (a stop placed in the wrong direction on a short is catastrophic).

3. **Switch to validated params with shorts enabled** — OB 80/OS 15, hold 10, trail 2.0 ATR after 10 bars, skip Monday. Do this immediately after sizing + short code is confirmed. No intermediate parameter phase needed — short mechanics verification is simpler than long (only 4 things to verify vs 7+ at launch). Expect ~3–4 short trades/week across 4 symbols on validated params — 2 weeks sufficient to confirm short mechanics. This starts the second clean window needed to confirm the trail component (the only unconfirmed part of the strategy).

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
