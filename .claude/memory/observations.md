# Observations — Algo Trader V1
Staging area for new topics and cross-domain coordination.

---

## Active Work

1. **Calibration comparison — Apr 20** — run backtest with identical params over Mar 20–Apr 20 window, compare trade counts, entry/exit prices, aggregate P&L. See `## Plan` in `.claude/calibration/calibration-notes.md`.
2. **Chart trade overlays (Stage 2)** — fetch entries/exits from `live_trade_log`, plot markers on chart (entry, exit, stop level), toggle live vs backtest. No domain file yet.
3. **Post-Apr-20: switch to validated params** — OB 80/OS 15, hold 10, trail 10, skip Monday. Affects all 4 bots. See strategy domain files.
4. **Post-Apr-20: XLE forward test** — deploy as 5th paper bot after calibration passes. See `## Plan` in `.claude/strategies/stochrsi-enhanced-xle.md`.
5. **Short trading deferred** — Alpaca rejects fractional short sells. Long-only until capital supports whole-share sizing.

## Staging

- **"Phantom sell"** — every session, bots log `⚠️ SELL skipped: no open position`. Not a duplicate exit — it's a blocked short entry attempt. K above OB (60) → `in_overbought_zone = True` → K drops below 50 → `sell()` fires → `live_broker.py` blocks it (fractional short unsupported) → misleading warning logged. State stays clean after block. `in_overbought_zone` resets to False. Two issues: (1) warning says "duplicate exit" — should say "blocked short entry"; (2) `current_sl` set to short stop value before block — stale but harmless. Both resolve when whole-share sizing added. No domain file yet.
- **Year-by-year tables need rerunning** — all 4 strategy domain files (GLD/IAU/SLV/GDX) have year-by-year tables computed with the old stop-check logic (pre Apr 4 fix). Flagged in-file as pre-fix. Rerun post-Apr-20 alongside parameter sensitivity tables. Low priority until calibration complete.
- **Long-only Sharpe figures are estimates** — all 4 strategy files have estimated long-only Sharpe based on pre-fix values. Rerun with `long_only:true` post-Apr-20 to get corrected figures. Confirmed Apr 8: validated params headline Sharpe (2.47 etc.) includes short trades — long-only figures need explicit rerun.
- **Live trade log current to Apr 7** — Alpaca MCP verified. pm2/DB audit pending for Apr 6 and Apr 7 entries. Run SSH audit before Apr 20 calibration to confirm DB records match.
- **Aggressive params baseline confirmed (Apr 8)** — long-only backtest 2020–2025 run for all 4 symbols. Results in research-log.md. Key finding: params have real but weak edge (~5–17% over 6 years vs ~25–60% for validated long-only). Live performance regime-dependent — 2024–2025 are the best years historically for these params.
