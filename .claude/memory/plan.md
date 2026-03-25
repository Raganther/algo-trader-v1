# Active Plan — Forward Testing & Mechanics Verification
Started: 2026-02-27
Domain files consulted: None

## What we're doing right now
Running 4 paper bots with aggressive test params (OB 60/OS 40, ADX 50, 3-bar hold/trail) to:
1. Verify live execution mechanics before real money
2. Generate a calibration dataset to validate the backtest engine

All known long-side bugs are fixed. Bots are running cleanly from Mar 16 onwards.

---

## Active steps

### Mechanics still to confirm
- [x] **Trailing stop FIRING in profit** — confirmed Mar 23. GDX: entry $80.05 (Mar 20), trail ratcheted to $83.35, server stop fired intrabar @ $83.317 (+$3.27/share, ~$958 paper). Multi-day hold gave trail time to ratchet well above entry before intrabar reversal triggered it.

### Short trading — must be enabled before real money
- [ ] **Fix live_broker sell() guard** — current guard blocks ALL sells from flat. Need to distinguish: (a) closing a long = allow, (b) opening a short from flat = allow when `long_only=False`, (c) duplicate exit = block. Fix: check strategy position state, not Alpaca position.
- [ ] **Verify short mechanics in live** — short entry, buy stop loss (above entry), trailing stop ratchets DOWN, short exit. Full mechanics checklist same as longs.

### Chart — trade overlays (Stage 2)
- [ ] Fetch entries/exits from `live_trade_log`, plot markers on chart (entry, exit, stop level), toggle live vs backtest
- [ ] Stage 3 (after): regime shading (ADX + SMA slope), win rate per regime

### Calibration comparison — target Apr 20
- [ ] **Preliminary check ~Mar 30** — run backtest over Mar 20–30 window as an early diagnostic only. Not the calibration — just an early warning check for obvious misalignments. Do not draw conclusions from ~10 trades per symbol.
- [ ] **Run calibration on Apr 20** — keep current aggressive params (OB 60/OS 40, trail 0.5 ATR after 1 bar) running until Apr 20. Then run backtest with identical params over the same window and compare trade counts, entry/exit prices, and aggregate P&L. Clean data window: Mar 20 – Apr 20 (Mar 20 = first fully confirmed clean day with current params and all fixes deployed). Expect ~80-100 trades per symbol across the full window. Aggressive params are intentionally kept for this — they generate ~2x more trades than validated params, making the calibration comparison more statistically meaningful.

### After mechanics verified (long + short)
- [ ] Switch to validated params (OB 80/OS 15, hold 10, trail 10, skip Monday)
- [ ] Start real-money micro trading (€100-200, fractional shares)

---

*Running insights → `memory/observations.md`*
