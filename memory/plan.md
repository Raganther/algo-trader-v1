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
- [ ] **Trailing stop FIRING in profit** — passive wait. Mar 18 diagnostic confirmed: with OLD trail params (2.0 ATR, 3 bars), backtest predicts ZERO profitable trail fires in Jan-Mar 2026 — matches live exactly. With TIGHTENED params (0.5 ATR, 1 bar, live since Mar 17), backtest predicts ~5 per symbol for same window. Only 2 days on new params so far — just need the right conditions (oversold bounce that rallies enough for trail to ratchet above entry before reversing intrabar).

### Short trading — must be enabled before real money
- [ ] **Fix live_broker sell() guard** — current guard blocks ALL sells from flat. Need to distinguish: (a) closing a long = allow, (b) opening a short from flat = allow when `long_only=False`, (c) duplicate exit = block. Fix: check strategy position state, not Alpaca position.
- [ ] **Verify short mechanics in live** — short entry, buy stop loss (above entry), trailing stop ratchets DOWN, short exit. Full mechanics checklist same as longs.

### Chart — trade overlays (Stage 2)
- [ ] Fetch entries/exits from `live_trade_log`, plot markers on chart (entry, exit, stop level), toggle live vs backtest
- [ ] Stage 3 (after): regime shading (ADX + SMA slope), win rate per regime

### Calibration comparison (ongoing)
- [ ] **Repeat calibration check ~Apr 16** — run same backtest subtraction method with ~1 month of clean live data. Expect ~80-100 trades per symbol. That's when the comparison is meaningful.

### After mechanics verified (long + short)
- [ ] Switch to validated params (OB 80/OS 15, hold 10, trail 10, skip Monday)
- [ ] Start real-money micro trading (€100-200, fractional shares)

---

*Running insights → `memory/observations.md`*
