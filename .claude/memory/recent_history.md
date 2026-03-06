# Recent Git History

### 2fabd07 - fix: DB reconciliation — log server stops, retry timed-out fills, startup sync (2026-03-06)
- AlpacaTrader: add get_filled_orders() and get_recent_filled_sell()
- LiveBroker: track timed-out sells in pending_fills, retry each bar in get_new_trades()
- DatabaseManager: add get_recent_live_trades(), order_id column, migration
- runner.py: log server-side stop exits to DB; reconcile_trades() on startup

Co-Authored-By: Claude Sonnet 4.6 <noreply@anthropic.com>

### 43da77c - docs: update memory — Mar 6, week 1 complete, all bots flat into weekend (2026-03-06)
- Week 1 paper trading summary: all 4 bots flat by market close Mar 5
- Mar 5 trade results logged (~-$512 paper rough day)
- Confirmed mechanics checklist updated (DAY TIF stops, heartbeats)
- Still waiting: server-side stop firing, trailing stop profit lock-in
- Next steps updated

Co-Authored-By: Claude Sonnet 4.6 <noreply@anthropic.com>

### e9b5791 - docs: add idea #21 — price action charts + regime analysis dashboard (2026-03-04)
Analyse strategy performance across market regimes (trending/ranging)
to separate edge alpha from directional beta. Triggered by SLV's
strong test-param results possibly being a bull-trend false positive.

Co-Authored-By: Claude Opus 4.6 <noreply@anthropic.com>

### b30d612 - docs: update memory — trade results, backtest predictions for test params (2026-03-04)
Mar 4 evening trades: SLV sold -$12.80, GDX sold +$75.27, GLD+IAU held.
Added backtest predictions with test params (Dec-Mar) for live comparison.
Updated next steps checklist with confirmed/remaining milestones.

Co-Authored-By: Claude Opus 4.6 <noreply@anthropic.com>

### 7ca7366 - docs: update memory files — Mar 4 evening, reliability hardening + DAY TIF fix (2026-03-04)
Co-Authored-By: Claude Opus 4.6 <noreply@anthropic.com>

### cedc865 - fix: use DAY TIF for fractional stop orders (GTC rejected by Alpaca) (2026-03-04)
GTC was set in c8fbf38 to persist overnight, but Alpaca rejects GTC
for fractional shares. All server-side stops were silently failing.

Co-Authored-By: Claude Opus 4.6 <noreply@anthropic.com>

### 096dda5 - feat: bot reliability improvements before real-money trading (2026-03-04)
- Extend fill timeout 5s → 30s (15 retries × 2s) for volatile markets
- Add order_id to all trade logs for Alpaca audit trail
- Cancel open orders on graceful shutdown (prevents orphaned stops)
- Add 50-bar minimum data guard at runner level (clearer than silent skip)
- Fix trailing stop gap: re-place at old price if update fails
- Add heartbeat logging every ~15 min for easy bot health checks
- Add pm2-logrotate setup script (10MB max, 3 retained)

Co-Authored-By: Claude Opus 4.6 <noreply@anthropic.com>

### c8fbf38 - fix: full position sync on restart + GTC stop orders (2026-03-04)
Position sync now reconstructs entry_price, current_sl (from ATR),
entry_bar, and places a server-side stop order on restart. Previously
only recovered position direction, leaving trades unprotected.

Stop orders changed from DAY to GTC so they persist overnight.

Co-Authored-By: Claude Opus 4.6 <noreply@anthropic.com>

### fc09dfe - docs: update memory files — Mar 4 session, wash trade fix deployed (2026-03-04)
Co-Authored-By: Claude Opus 4.6 <noreply@anthropic.com>

### b45bbeb - fix: cancel all open orders before sell to prevent wash trade rejections (2026-03-04)
When server-side stop fires and bot also tries to sell, Alpaca rejects
the sell as a wash trade due to the existing stop order. Now cancels ALL
open orders for the symbol (not just the tracked one) before placing
exit orders, with cleanup on server stop detection too.

Co-Authored-By: Claude Opus 4.6 <noreply@anthropic.com>

### 4a6baaf - docs: update recent_history.md (2026-03-03)
Co-Authored-By: Claude Opus 4.6 <noreply@anthropic.com>

### 27a5b8d - fix: add graceful shutdown handler to prevent zombie trades on pm2 restart (2026-03-03)
PM2 sends SIGTERM on restart but old process could linger and place orders.
Now catches SIGTERM/SIGINT, sets shutdown flag, exits within 1 second.
Sleep broken into 1s intervals for fast response. Bar processing skipped
if shutdown requested.

Co-Authored-By: Claude Opus 4.6 <noreply@anthropic.com>

### a697957 - feat: add server-side stop losses for fractional share orders (2026-03-03)
Alpaca doesn't support bracket orders with fractional shares, so stop
losses were silently not being placed. Now we:

1. Place a separate stop sell order after BUY fill (server-side protection)
2. Cancel + replace stop order when trailing stop ratchets up
3. Cancel stop order before signal-based exits
4. Detect when server-side stop fires externally and reset strategy state

This ensures positions are protected even if the bot hangs or data feed stalls.

Co-Authored-By: Claude Opus 4.6 <noreply@anthropic.com>

### 73f4432 - docs: update claude.md — current status, fix outdated info (2026-03-03)
- Updated to reflect 4 test bots (added GDX), removed gld-15m-enhanced
- Fixed fractional shares status (confirmed working, was incorrectly listed as whole shares only)
- Added bugs found/fixed (fetch window, OOM), known issues, server specs
- Added test vs validated params comparison table
- Removed redundant/outdated sections, consolidated reference info

Co-Authored-By: Claude Opus 4.6 <noreply@anthropic.com>

### 2cd7f16 - docs: update recent_history.md (2026-03-02)
Co-Authored-By: Claude Opus 4.6 <noreply@anthropic.com>

### 3b7364a - fix: increase live fetch window from 2 to 7 days (2026-03-02)
The on_bar guard (i < 50) was silently skipping all signal evaluation
because the 2-day fetch only returned ~32 bars of 15m data (especially
over weekends). This meant zero trades fired today despite big moves.
7 days guarantees 50+ bars even over weekends.

Co-Authored-By: Claude Opus 4.6 <noreply@anthropic.com>

### 1535880 - temp: enable Monday trading for testing (2026-03-02)
All 4 test bots (GLD/IAU/SLV/GDX) — skip_days changed from [0] to [] so they trade today.

Co-Authored-By: Claude Opus 4.6 <noreply@anthropic.com>

### 8476d9f - feat: add GDX 15m test bot script (2026-03-02)
4th precious metals bot — same aggressive test params as GLD/IAU/SLV
for mechanics verification before switching to validated params.

Co-Authored-By: Claude Opus 4.6 <noreply@anthropic.com>

### 9e919c6 - docs: add portfolio manager idea (#20) to ideas.md (2026-02-28)
Dynamic cross-bot position sizing across all 4 validated 15m strategies.
20% total risk budget, compounding on account equity, shared PortfolioManager class.
Expected blended return ~14.8%/yr. Natural next step after execution mechanics verified.

Co-Authored-By: Claude Sonnet 4.6 <noreply@anthropic.com>

### 5b0858b - feat: add IAU 15m to frontend registry (2026-02-28)
Links IAU 15m to stochrsi_enhanced_iau.md for detail page notes.

Co-Authored-By: Claude Sonnet 4.6 <noreply@anthropic.com>
