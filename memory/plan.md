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
- [x] **Server-side stop FIRING** — confirmed Mar 10. SLV stop at $80.49 auto-filled by Alpaca at $80.43 (18:00 UTC, 43min after last trail ratchet). New bug found and fixed: fill logging failed due to API propagation delay — now queries by specific order ID, falls back to pending_fills retry.
- [ ] **Trailing stop FIRING (in profit)** — same Alpaca server-side mechanism as above, just needs trail to have ratcheted above entry before firing. Not yet observed. Two mechanics total: (1) bot K-signal exit, (2) Alpaca server-side stop — covers both stop loss and trailing stop.

### Short trading — must be enabled before real money

**Long-only baseline established (Mar 14 2026):**

| Asset | Full Sharpe | LO Sharpe~ | Full Return | LO Return | Verdict |
|-------|------------|------------|-------------|-----------|---------|
| GLD | 2.54 | ~1.91 | +44.7% | +31.2% | Shorts add alpha — fix needed |
| IAU | ~2.0 | ~1.33 | +32.6% | +21.7% | Shorts add alpha — fix needed |
| SLV | 2.54 | ~3.29 | +105.3% | +68.3% | Long-only actually better risk-adjusted |
| GDX | 2.41 | ~1.54 | +114.1% | +65.8% | Shorts critical — biggest impact |

SLV is viable long-only. GLD, IAU, GDX are meaningfully weaker without shorts.

Discovered Mar 11: the live bots are long-only. The guard in `live_broker.sell()` (added to prevent duplicate exit signals) also blocks short entries from flat. The backtest has always run both long and short — the Sharpe 2.54 figure includes short trade P&L. Running long-only in live means we are trading half the strategy.

- [x] **Add `long_only` parameter to strategy** — done Mar 14. Defaults False (backtest unchanged). Long-only backtests run across all 4 assets, baseline established (see table above).
- [ ] **Fix live_broker sell() guard** — current guard blocks ALL sells from flat. Need to distinguish: (a) closing a long = allow, (b) opening a short from flat = allow when `long_only=False`, (c) duplicate exit = block. Fix: check strategy position state, not just Alpaca position.
- [ ] **Verify short mechanics in live** — short entry, buy stop loss (above entry), trailing stop ratchets DOWN, short exit buy order. All need the same verification the long mechanics went through.
- [ ] **Re-run mechanics verification for short trades** — same checklist as longs once short trading is enabled.

### Open questions
- [ ] **GDX zero trades** — gdx-test bot has generated zero trades since launch. No activity in pm2 logs for the full test period. Either no signals have fired (possible — GDX is more volatile, fewer extreme OS readings) or there is a silent issue. Needs investigation next trading week.

### Known issues (logged, not yet fixed)
- [ ] **Wash trade: pre-market pending sell collision** — when a sell order is placed pre-market (e.g. pending_fills retry at 8:00 UTC), it sits open in Alpaca for up to 5.5 hours until market open. If a new buy signal fires during that window, Alpaca rejects it as a wash trade. Root cause confirmed Mar 14 via SLV Mar 13 audit: overnight hold closed via pending_fills sell at 8:00 UTC, new buy signal fired before fill, rejected. Fix: before placing a new entry, cancel any open sell orders on the same symbol first.

### After mechanics verified (long + short)
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
