# Active Plan — Forward Testing & Mechanics Verification
Started: 2026-02-27

## Goal
Verify that the live execution infrastructure works correctly before committing real money.
The backtested edge is validated. What we're confirming now is that the bots execute reliably in the wild.

## Steps

### Debugging (week 1 — complete)
- [x] Fix live fetch window (2 days → 7 days, was silently skipping all signals)
- [x] Fix zombie trades on pm2 restart (graceful SIGTERM handler)
- [x] Fix wash trade rejection (cancel ALL open orders before exit, not just tracked stop)
- [x] Fix server-side stop orders rejected (GTC → DAY TIF for fractional shares)
- [x] Fix fill timeout too short (5s → 30s)
- [x] Fix trailing stop gap (fallback re-places at old price if update fails)
- [x] Fix DB reconciliation gap (server stops + overnight fills now logged)
- [x] Reliability hardening: heartbeat logging, order IDs, shutdown cleanup, pm2-logrotate

### Mechanics verification (in progress)
- [x] Bot-initiated exits (signal-based sell with stop cancellation)
- [x] Trailing stop UPDATE (ratchets up on each bar)
- [x] DAY TIF stop orders (confirmed working after fix)
- [x] Position sync on restart
- [x] DB reconciliation on startup
- [ ] Server-side stop FIRING (Alpaca auto-executes stop between candles when price drops)
- [ ] Trailing stop FIRING (price rises → trail ratchets → price reverses → profit locked)

### After mechanics verified
- [ ] Compare live results to backtest predictions (2-4 weeks of data needed)
- [ ] Switch to validated params (OB 80/OS 15, hold 10, trail 10, skip Monday)
- [ ] Start real-money micro trading (€100-200, fractional shares)

## Notes
- All bug fixes are summarised in CLAUDE.md "Bugs found & fixed" section
- Full commit detail accessible via `git log` or commit messages in memory/MEMORY.md
- Backtest predictions for test params in CLAUDE.md — use to validate backtest engine accuracy
- Server: algotrader2026 (europe-west2-a) — `gcloud compute ssh algotrader2026 --zone=europe-west2-a --command="pm2 status"`

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

### Stage 2 — Trade overlays
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
- Start with Stage 1 only — get the chart rendering before adding complexity
