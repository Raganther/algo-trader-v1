# Recent Git History

> Auto-generated on git save. Do not edit manually.

----
**2026-03-09** — docs: update plan.md — Mar 09 audit complete, reconcile fixed, completeness baseline established

 memory/plan.md | 49 +++++++++++++++++++++++++++++++++----------------
 1 file changed, 33 insertions(+), 16 deletions(-)

----
**2026-03-09** — fix: case-insensitive side comparison in trade matching (BUY/SELL vs buy/sell)
Alpaca SDK returns side as uppercase ('BUY'/'SELL') but DB stores
lowercase ('buy'/'sell'). This caused reconcile_trades and audit_trades
to never match any orders, silently treating all fills as missing.
Same root cause as the status field case bug.

Co-Authored-By: Claude Sonnet 4.6 <noreply@anthropic.com>

 backend/runner.py       | 2 +-
 scripts/audit_trades.py | 2 +-
 2 files changed, 2 insertions(+), 2 deletions(-)

----
**2026-03-09** — fix: case-insensitive status check in get_filled_orders (was silently returning empty)
Alpaca SDK returns 'OrderStatus.FILLED' (uppercase) but the filter
checked for 'OrderStatus.filled' (lowercase) — case mismatch caused
get_filled_orders() to always return []. reconcile_trades() was
therefore always seeing 0 Alpaca orders and reporting 'DB up to date'
even when fills were missing. Every reconcile since deploy has been
a no-op.

Co-Authored-By: Claude Sonnet 4.6 <noreply@anthropic.com>

 backend/engine/alpaca_trader.py | 2 +-
 1 file changed, 1 insertion(+), 1 deletion(-)

----
**2026-03-09** — feat: trade completeness audit script — Alpaca vs DB by day
Shows completeness rate per symbol per day. Trending toward 100%
over time verifies bug fixes are actually working.

Co-Authored-By: Claude Sonnet 4.6 <noreply@anthropic.com>

 scripts/audit_trades.py | 102 ++++++++++++++++++++++++++++++++++++++++++++++++
 1 file changed, 102 insertions(+)

----
**2026-03-09** — fix: pending_fills for buys, reconcile window 7d, manual DB inserts

 CLAUDE.md        |  2 ++
 memory/MEMORY.md | 45 ++++++++++++++++++++++++---------------------
 memory/plan.md   |  3 +++
 3 files changed, 29 insertions(+), 21 deletions(-)

----
**2026-03-09** — fix: queue timed-out buys in pending_fills, extend reconcile lookback to 7 days
Buy orders that hit the 30s fill timeout were silently dropped — only sells
were queued in pending_fills for retry. Today's SLV buy (filled after 5min)
was never logged, leaving an orphaned sell in the DB. Same retry logic now
applied to buys. Reconcile lookback extended from 3 to 7 days to catch fills
that fall outside the previous window (e.g. pre-market DAY orders).

Co-Authored-By: Claude Sonnet 4.6 <noreply@anthropic.com>

 backend/engine/alpaca_trader.py | 4 ++--
 backend/engine/live_broker.py   | 3 ++-
 backend/runner.py               | 4 ++--
 3 files changed, 6 insertions(+), 5 deletions(-)

----
**2026-03-07** — feat: UI redesign — Inter font, sidebar nav, max-width, consistent page structure

 CLAUDE.md                                 |  1 +
 frontend/src/app/chart/page.tsx           | 92 +++++++++++++++----------------
 frontend/src/app/globals.css              |  1 +
 frontend/src/app/layout.tsx               | 29 ++++++----
 frontend/src/app/page.tsx                 | 14 ++---
 frontend/src/app/strategy/[slug]/page.tsx | 32 +++++------
 frontend/src/components/Nav.tsx           | 51 +++++++++++++++++
 memory/MEMORY.md                          | 21 ++++---
 8 files changed, 151 insertions(+), 90 deletions(-)

----
**2026-03-07** — feat: Stage 1 price action chart — price_data table, fetch script, TradingView candlestick chart

 CLAUDE.md                              |  7 ++-
 backend/database.py                    | 65 ++++++++++++++++++++++++-
 frontend/src/app/chart/page.tsx        | 84 ++++++++++++++++++++++++++++++++
 frontend/src/components/PriceChart.tsx | 88 ++++++++++++++++++++++++++++++++++
 frontend/src/lib/db.ts                 | 49 +++++++++++++++++++
 memory/MEMORY.md                       | 32 ++++++-------
 memory/plan.md                         | 36 ++++++++++++++
 scripts/fetch_price_data.py            | 71 +++++++++++++++++++++++++++
 8 files changed, 413 insertions(+), 19 deletions(-)

