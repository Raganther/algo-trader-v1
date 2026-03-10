# Recent Git History

> Auto-generated on git save. Do not edit manually.

----
**2026-03-10** — fix: correct bot log check command + document log format
Logs rotate at midnight via pm2-logrotate — previous command searched only the current log file, missing all same-day trades. New command takes the 2 most recent log files per bot covering both cases. Actual log keywords documented in system_manual.md (LIVE BUY, FILLED, TRAILING STOP etc). CLAUDE.md run command updated. Dev.md updated with agent ideas (#22).

 .claude/memory/system_manual.md | 22 ++++++++++++++++++++++
 CLAUDE.md                       |  7 ++-----
 docs/dev.md                     | 21 +++++++++++++++++++++
 3 files changed, 45 insertions(+), 5 deletions(-)

----
**2026-03-09** — fix: pass body argument to git commit in git-save.sh
git commit -m "$1" ${2:+-m "$2"} — body was silently dropped, MEMORY.md only ever showed subject + file stats. Now both subject and body are captured in the commit and appear in MEMORY.md.

 scripts/git-save.sh | 2 +-
 1 file changed, 1 insertion(+), 1 deletion(-)

----
**2026-03-09** — docs: update plan.md — Mar 09 audit complete, reconcile fixed, completeness baseline established

 memory/MEMORY.md | 86 +++++++++++++++++++++++++++++++-------------------------
 memory/plan.md   | 49 +++++++++++++++++++++-----------
 2 files changed, 80 insertions(+), 55 deletions(-)

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

