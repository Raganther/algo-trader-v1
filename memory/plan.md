# Active Plan — Forward Testing & Mechanics Verification
Started: 2026-02-27

## Goal
Verify that the live execution infrastructure works correctly before committing real money.
The backtested edge is validated. What we're confirming now is that the bots execute reliably in the wild.

## Steps

### Debugging (complete)
- [x] Fix live fetch window (2 days → 7 days, was silently skipping all signals)
- [x] Fix zombie trades on pm2 restart (graceful SIGTERM handler)
- [x] Fix wash trade rejection (cancel ALL open orders before exit)
- [x] Fix server-side stop orders rejected (GTC → DAY TIF for fractional shares)
- [x] Fix fill timeout too short (5s → 30s)
- [x] Fix trailing stop gap (fallback re-places at old price if update fails)
- [x] Fix DB reconciliation gap (server stops + overnight fills now logged)
- [x] Reliability hardening: heartbeat logging, order IDs, shutdown cleanup, pm2-logrotate
- [x] Fix timed-out buy orders never logged (pending_fills was sells-only)
- [x] Extend reconcile/lookback window 3 → 7 days
- [x] Fix get_filled_orders always returning empty (status case mismatch: 'OrderStatus.FILLED' vs 'filled')
- [x] Fix reconcile_trades never matching (side case mismatch: 'BUY' vs 'buy')

**Note on last 2 fixes (Mar 09):** These meant reconcile_trades() was a complete no-op since deploy.
It said "DB up to date" every restart because it was comparing 0 Alpaca orders against 0 DB matches.
Now fixed — reconcile actually works. Deployed and confirmed on Mar 09 restart.

### Mechanics verification (in progress)
- [x] Bot-initiated exits (signal-based sell with stop cancellation)
- [x] Trailing stop UPDATE confirmed (ratchets up on each bar — observed SLV Mar 09: 76.15 → 77.23)
- [x] DAY TIF stop orders
- [x] Position sync on restart
- [x] DB reconciliation on startup (confirmed working after Mar 09 case fixes)
- [ ] **Server-side stop FIRING** — Alpaca auto-executes stop between candles when price drops through stop level. Not yet observed in live data.
- [ ] **Trailing stop FIRING** — price rises → trail ratchets → price reverses intrabar below trail → Alpaca auto-fills. Note: Mar 09 SLV trade had trail ratchet (76.15 → 77.23) but bot K-signal exited first at 77.92. Stop was cancelled before it could fire. Still unconfirmed.

### After mechanics verified
- [ ] Compare live results to backtest predictions (2-4 weeks of data needed)
- [ ] Switch to validated params (OB 80/OS 15, hold 10, trail 10, skip Monday)
- [ ] Start real-money micro trading (€100-200, fractional shares)

## Trade Completeness Audit (Mar 09)
Run `python3 scripts/audit_trades.py --days 7` on server to verify DB vs Alpaca.

Current state:
- Mar 03: ~60-80% (early bugs active — gaps are historical, acceptable)
- Mar 04: ~67-100% (improving)
- Mar 05 onwards: **100% every day** — all fills captured automatically
- Mar 09 (today): 100% across all 4 symbols, 10/10 fills matched

The 9 historical gaps (Mar 03-04) are expected. Bugs were active then. Not worth filling — they don't affect live operation.

## Key insight
We are not going in circles. The progression is:
- Week 1: infrastructure bugs (execution, orders, TIF)
- Mar 09: data integrity bugs (reconcile was silently broken since deploy)
- Mar 05+ live data: 100% clean — confirms fixes are working

The remaining two unconfirmed mechanics require specific market conditions to occur. They cannot be forced. Let the bots run.

---

# Plan — Price Action Chart + Regime Analysis Dashboard
Started: 2026-03-07

## Goal
Build a chart view in the frontend showing historical 15m price action for each symbol, with trade overlays and regime shading — to visually validate backtest predictions against live results and understand which market conditions the strategy performs in.

## Architecture decisions
- **Data storage:** Local SQLite (`research.db`, new `price_data` table) — fetch from Alpaca once, sync on demand
- **Charting library:** TradingView Lightweight Charts — purpose-built for OHLCV, free, performant
- **Regime classification:** ADX + SMA slope combined — trending-up, trending-down, ranging (3 buckets)

## Stages

### Stage 1 — Historical data pipeline + candlestick chart
- [x] Add `price_data` table to `research.db` (symbol, timestamp, open, high, low, close, volume)
- [x] Script to fetch 15m OHLCV from Alpaca and populate table (`scripts/fetch_price_data.py`)
- [x] Frontend page with TradingView Lightweight Charts rendering candlesticks (`/chart`)
- [x] Symbol selector (GLD/IAU/SLV/GDX) + time range (1M–5Y) via URL params

### Stage 2 — Trade overlays (next)
- [ ] Fetch entries/exits from `live_trade_log` and backtest `experiments`
- [ ] Plot markers on chart (entry, exit, stop level)
- [ ] Toggle: live trades vs backtest trades

### Stage 3 — Regime shading + performance breakdown
- [ ] Compute ADX + SMA slope on stored price data, classify each bar
- [ ] Shade chart background by regime (trending-up / trending-down / ranging)
- [ ] Side panel: win rate and avg return per regime

## Notes
- Idea originally logged as #21 in docs/dev.md
- Hypothesis: losses cluster in trending regimes (mean-reversion strategy works against strong trends)
