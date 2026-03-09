# Recent Git History

> Auto-generated on git save. Do not edit manually.

----
**2026-03-09** — fix: pending_fills for buys, reconcile window 7d, manual DB inserts

 CLAUDE.md      | 2 ++
 memory/plan.md | 3 +++
 2 files changed, 5 insertions(+)

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

----
**2026-03-07** — docs: restore full idea detail to dev.md from git history

 docs/dev.md      | 313 ++++++++++++++++++++++++++++++++++++++++++++++++++-----
 memory/MEMORY.md |  28 ++---
 2 files changed, 298 insertions(+), 43 deletions(-)

----
**2026-03-07** — chore: update git-save.sh to full commit detail format (8 saves, stat)

 memory/MEMORY.md    | 94 +++++++++++++++++++++++++++++++++++++++++++++++------
 memory/plan.md      | 39 ++++++++++++++++++++--
 scripts/git-save.sh |  6 ++--
 3 files changed, 124 insertions(+), 15 deletions(-)

----
**2026-03-07** — chore: complete filing system migration — retire .claude/CLAUDE.md, consolidate into root

 .claude/claude.md                | 210 ---------------------
 .claude/memory/ideas.md          | 391 ---------------------------------------
 .claude/memory/recent_history.md | 139 --------------
 CLAUDE.md                        |  67 ++++++-
 docs/dev.md                      |  16 +-
 memory/MEMORY.md                 |   2 +-
 memory/plan.md                   |  18 +-
 scripts/update_memory.sh         |  11 --
 8 files changed, 77 insertions(+), 777 deletions(-)

----
**2026-03-07** — docs: add filing system migration plan

 CLAUDE.md        |  3 ++-
 memory/MEMORY.md |  2 +-
 memory/plan.md   | 19 ++++++++++++++++---
 3 files changed, 19 insertions(+), 5 deletions(-)

