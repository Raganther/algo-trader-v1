# Observations — Algo Trader V1
Staging area for new topics and cross-domain coordination.

---

## Overall Status (Apr 10 2026)

**Two of three strategy components confirmed live. One regime. Test params.**

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

Path to real money: Apr 20 calibration → switch to validated params → second clean window (confirm trail) → short trading (requires whole-share sizing).

---

## Active Work

1. **Calibration comparison — Apr 20** — run backtest with identical params over Mar 20–Apr 20 window, compare trade counts, entry/exit prices, aggregate P&L. See `## Plan` in `.claude/calibration/calibration-notes.md`.
2. **Chart trade overlays (Stage 2)** — fetch entries/exits from `live_trade_log`, plot markers on chart (entry, exit, stop level), toggle live vs backtest. No domain file yet.
3. **Post-Apr-20: switch to validated params** — OB 80/OS 15, hold 10, trail 10, skip Monday. Affects all 4 bots. See strategy domain files.
4. **Post-real-money: XLE forward test** — deploy as 5th paper bot after calibration + trail confirmed + sizing implemented. Lower priority than core 4 bots at real money. See `## Plan` in `.claude/strategies/stochrsi-enhanced-xle.md`.
5. **Post-Apr-20: portfolio correlation analysis** — run all 4 symbols on validated params simultaneously, align on shared timeline, tally joint outcomes of simultaneous positions (all win / all lose / mixed) split by year. Read-only — no execution logic needed, simpler than full portfolio backtester. Informs whether correlation-aware sizing is needed and at what scale. Do this before implementing sizing logic.
6. **Post-Apr-20: regime-aware sizing** — regime classifier built and working (`backend/indicators/regime.py`, `scripts/analyse_regimes.py`). Daily bars stored in `price_data_daily`. Next step: tag backtest trades with entry regime, compute per-regime P&L to validate sizing rationale empirically. Then implement live regime detection + dynamic sizing in `live_broker.py`. See `.claude/strategies/regime-analysis.md`.
7. **Short trading deferred** — Alpaca rejects fractional short sells. Long-only until capital supports whole-share sizing.

## Staging

- **SLV 2026 HIGH_VOL anomaly** — SLV showing 49% HIGH_VOL in 2026 vs 22% for GLD/GDX. Likely the fixed ATR multiplier (1.5×) is too sensitive for SLV's naturally higher volatility. Consider symbol-specific ATR thresholds or normalising ATR as % of price before implementing live regime detection. See regime-analysis.md.
- **ATR-based position sizing (post-calibration enhancement)** — current sizing deploys equal capital per symbol (~25% of account). Risk per trade is not fixed — it varies with ATR on the day. ATR-based sizing would back-calculate share count from a fixed max risk % (e.g. 1% of account ÷ stop distance = shares to buy). Normalises risk per trade across volatile and calm sessions. Implement post-Apr-20 alongside correlation-aware sizing — both are pre-real-money requirements. Also unlocks GTC stops (whole-share sizing removes Alpaca's fractional short/GTC restriction). See research-log.md cross-cutting learning #6.
- **Late-session entry guard** — block or halve position size when entry signal fires within ~30 min of market close. DAY stops expire before providing meaningful intraday protection; position carries overnight naked until bot re-places stop at open. Testable with existing single-symbol engine (simple time condition in `on_bar()`). Pre-real-money requirement alongside correlation-aware sizing. Implement after correlation analysis.
- **"Phantom sell"** — every session, bots log `⚠️ SELL skipped: no open position`. Not a duplicate exit — it's a blocked short entry attempt. K above OB (60) → `in_overbought_zone = True` → K drops below 50 → `sell()` fires → `live_broker.py` blocks it (fractional short unsupported) → misleading warning logged. State stays clean after block. `in_overbought_zone` resets to False. Two issues: (1) warning says "duplicate exit" — should say "blocked short entry"; (2) `current_sl` set to short stop value before block — stale but harmless. Both resolve when whole-share sizing added. No domain file yet.
- **Year-by-year tables need rerunning** — all 4 strategy domain files (GLD/IAU/SLV/GDX) have year-by-year tables computed with the old stop-check logic (pre Apr 4 fix). Flagged in-file as pre-fix. Rerun post-Apr-20 alongside parameter sensitivity tables. Low priority until calibration complete.
- **Long-only Sharpe figures are estimates** — all 4 strategy files have estimated long-only Sharpe based on pre-fix values. Rerun with `long_only:true` post-Apr-20 to get corrected figures. Confirmed Apr 8: validated params headline Sharpe (2.47 etc.) includes short trades — long-only figures need explicit rerun.
- **Live trade log current to Apr 10** — Alpaca MCP verified through Apr 10. pm2/DB audit pending for Apr 6–10 entries. Run SSH audit before Apr 20 calibration to confirm DB records match. GLD/SLV/GDX open overnight Apr 10 — carrying into Monday Apr 13.
- **Aggressive params baseline confirmed (Apr 8)** — long-only backtest 2020–2025 run for all 4 symbols. Results in research-log.md. Key finding: params have real but weak edge (~5–17% over 6 years vs ~25–60% for validated long-only). Live performance regime-dependent — 2024–2025 are the best years historically for these params.
