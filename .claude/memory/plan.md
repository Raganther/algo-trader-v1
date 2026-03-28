# Active Plan — Forward Testing & Mechanics Verification
Started: 2026-02-27
Domain files consulted: None

## What we're doing right now
Running 4 paper bots with aggressive test params (OB 60/OS 40, ADX 50, 3-bar hold/trail) to:
1. Verify live execution mechanics before real money
2. Generate a calibration dataset to validate the backtest engine

All known long-side bugs are fixed. Bots are running cleanly from Mar 16 onwards.
Mar 26: pending_fills no-stop bug fixed — stop_loss now carried through delayed fill path.

---

## Active steps

### Mechanics still to confirm
- [x] **Trailing stop FIRING in profit** — confirmed Mar 23. GDX: entry $80.05 (Mar 20), trail ratcheted to $83.35, server stop fired intrabar @ $83.317 (+$3.27/share, ~$958 paper). Multi-day hold gave trail time to ratchet well above entry before intrabar reversal triggered it.

### Short trading — deferred (not blocking real money)
Alpaca rejects fractional short selling. At starting capital (€100) fractional shares are required — whole-share sizing not possible. Long-only until capital grows to support whole-share qty. Not a blocker for the micro-trading phase.

### Chart — trade overlays (Stage 2)
- [ ] Fetch entries/exits from `live_trade_log`, plot markers on chart (entry, exit, stop level), toggle live vs backtest
- [ ] Stage 3 (after): regime shading (ADX + SMA slope), win rate per regime

### Calibration comparison — target Apr 20
- [x] **Preliminary check ~Mar 27** — done. See observations.md. No red flags. Backtest predicts 40 trades vs 31 live (1.3x) for Mar 20–27; P&L direction aligned (both near-zero/slightly negative). `trading_hours:[13,20]` required for all calibration backtest runs.
- [ ] **Run calibration on Apr 20** — keep current aggressive params (OB 60/OS 40, trail 0.5 ATR after 1 bar) running until Apr 20. Then run backtest with identical params over the same window and compare trade counts, entry/exit prices, and aggregate P&L. Clean data window: Mar 20 – Apr 20 (Mar 20 = first fully confirmed clean day with current params and all fixes deployed). Expect ~80-100 trades per symbol across the full window. Aggressive params are intentionally kept for this — they generate ~2x more trades than validated params, making the calibration comparison more statistically meaningful.

### After mechanics verified (long + short)
- [ ] Switch to validated params (OB 80/OS 15, hold 10, trail 10, skip Monday)
- [ ] Start real-money micro trading (€100-200, fractional shares)

### After Apr 20 calibration passes
- [ ] Apply calibration corrections (spread adjustment, stop slippage param if needed)
- [ ] Rolling Validation Test #1 — deploy XLE as 5th paper bot (4–8 weeks). Strategy card: `.claude/strategies/stochrsi_enhanced_xle.md`

---

*Running insights → `.claude/memory/observations.md`*
