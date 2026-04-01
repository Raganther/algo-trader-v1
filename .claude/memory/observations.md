# Observations — Algo Trader V1
*Running insights from the forward testing phase. Graduate to confirmed knowledge when settled.*

---

## Graduation Candidates
<!-- Entries ready to graduate this session. git-save-guard blocks if non-empty. -->
<!-- Either graduate to .claude/[domain]/ and clear, or explicitly remove if not ready. -->

---

## Data integrity baseline
- Mar 03–04: gaps (bugs active, acceptable)
- Mar 05 onwards: 100% fill capture
- Mar 16–19: full Alpaca audits — all records matched pm2 logs across all 4 bots
- Mar 20: clean window starts — 9/9 DB records matched Alpaca. 4 intraday trades (SLV TS, GLD K, IAU K, GDX T1 TS) + GDX T2 overnight hold (exits Mar 23).
- Mar 23–31: all days PASS. Full per-trade detail in domain file.
→ Domain file: `.claude/calibration/live-trade-log.md`

---

## Post-calibration research process (planned, Mar 27)
Three-phase loop: Research (backtest, filter Sharpe > 2 / DD < 3% / WF pass) → Validate (4–8 week forward test, goal is prediction accuracy not profit) → Deploy (real money). Execution layer corrections from Apr 20 apply universally; signal layer needs its own forward test per new strategy. Test #1 candidate: XLE 15m — Sharpe 2.06, +85.2%, 3.35% DD, WF 4/4. Forward test starts after Apr 20. Note: calibration window coincides with historically extreme precious metals volatility (Iran war, post-ATH crash) — see domain file for context on interpreting Apr 20 results.
→ Domain file: `.claude/calibration/calibration-notes.md` | XLE card: `.claude/strategies/stochrsi-enhanced-xle.md`

---

## Preliminary calibration check (Mar 27)
No red flags. Backtest (Mar 20–27, aggressive params + trading_hours:[13,20]): 40 trades vs 31 live (1.3x inflation, acceptable). P&L direction aligned across all 4 symbols. Always include `"trading_hours":[13,20]` in calibration backtest params — required to match live market hours gate.
→ Domain file: `.claude/calibration/calibration-notes.md`

---

## "Phantom sell" — blocked short entry (confirmed Mar 27)
Every day, all 4 bots log `⚠️ SELL skipped: no open position — ignoring duplicate exit signal` once during the session. This is NOT a duplicate exit — it's a **blocked short entry attempt**.

What happens: K spends time above overbought (60) → `in_overbought_zone = True`. When K later drops below 50, the strategy's short entry logic fires `self.sell()` with a `stop_loss`. `live_broker.sell()` blocks it (fractional short selling unsupported) and prints the misleading warning. `in_overbought_zone` resets to False (line 295) — no further attempts that session.

State stays clean after it. No bad trades. Fires once per overbought zone crossing.
Two issues: (1) warning message says "duplicate exit" when it's a "blocked short entry" — misleading. (2) `self.current_sl` gets set to the short stop value before the sell is blocked — stale but harmless (overwritten on next long entry, and stop loss check requires `position == 'long'`).
Both resolve naturally when whole-share sizing is implemented and shorts re-enabled.

---

## Trade log analysis (Mar 20–31)
K-exits 76% win rate vs TS exits 14% (43 trades). GDX underperforming vs backtest prediction. Correlated simultaneous GLD/IAU/SLV entries = 6% portfolio exposure — needs position sizing adjustment before real money. News correlation confirmed (Apr 1): Mar 23 best day = first bounce after flash crash; Mar 31 best day = Iran de-escalation news (Trump ends military campaign, GLD +3.79%). Mar 24/27/30 losses = choppy reversals in post-crash volatility. GDX underperformance structurally explained — see calibration-notes.md.
→ Domain file: `.claude/calibration/live-trade-log.md`

---

## Trailing stop pattern (updated Mar 31)
Same-day TS exits: almost always losses (0.5 ATR trail fires on noise before position moves). K-exits: profitable when momentum sustained. Multi-day holds give trail time to ratchet well above entry. Open: overnight stop re-placement fires at restart time (21:10 UTC) not next market open — investigate before Apr 20.
→ Domain file: `.claude/calibration/live-trade-log.md`

---

## Alpaca MCP — integrated (Apr 1)
57 tools audited, now integrated into workflow. "Check bots" uses MCP as primary method (get_clock → get_all_positions → get_orders). Daily trade audit procedure rewritten to use get_orders instead of SSH→DB→Alpaca cross-reference. Validated Apr 1: Mar 23 MCP output matched trade log exactly (26 orders, 7 trades, all prices/timestamps/trail ratchets). SSH retained for pm2 process health and application logs only.
→ Domain file: `.claude/integrations/alpaca-mcp.md`

---

## Two types of slippage — only one is modelled
Spread slippage modelled (`--spread 0.0003`). Stop execution slippage not modelled — live shows $0.00–$0.14/share, typically under $0.05. Will surface in Layer 3 of Apr 20 calibration. If systematic, add to backtest model.
→ Domain file: `.claude/calibration/calibration-notes.md`

---

