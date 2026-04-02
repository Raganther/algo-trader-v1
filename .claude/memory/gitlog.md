# Recent Git History

> Auto-generated on git save. Do not edit manually.

----
**2026-04-02** — chore: log Apr 2 trades — 6 trades, 5 profitable, GLD TS fire in profit

 .claude/calibration/live-trade-log.md | 17 +++++++++++++++++
 1 file changed, 17 insertions(+)

----
**2026-04-02** — chore: migrate memory harness to v3

 .claude/calibration/calibration-notes.md       |  43 +++++-----
 .claude/calibration/live-trade-log.md          | 114 +++++++++----------------
 .claude/hooks/git-save-guard.sh                |  42 ++-------
 .claude/hooks/load-context.sh                  |   3 +-
 .claude/hooks/openbrain-audit-reminder.sh      |  22 ++---
 .claude/hooks/plan-domain-reminder.sh          |  31 -------
 .claude/integrations/alpaca-mcp.md             |  68 ++++++---------
 .claude/memory/gitlog.md                       |  37 +++++---
 .claude/memory/observations.md                 |  74 ++--------------
 .claude/memory/plan.md                         |  41 ---------
 .claude/procedures/memory-harness-migration.md |  11 +++
 .claude/settings.json                          |  18 ----
 .claude/strategies/composable-results.md       |  18 ++--
 .claude/strategies/event-surprise.md           |  46 +++++-----
 .claude/strategies/stochrsi-enhanced-gdx.md    |  26 +++---
 .claude/strategies/stochrsi-enhanced-gld.md    |  46 +++++-----
 .claude/strategies/stochrsi-enhanced-iau.md    |  28 +++---
 .claude/strategies/stochrsi-enhanced-slv.md    |  26 +++---
 .claude/strategies/stochrsi-enhanced-xle.md    |  33 ++++---
 CLAUDE.md                                      |   5 +-
 20 files changed, 264 insertions(+), 468 deletions(-)

----
**2026-04-02** — chore: log Apr 1 trades, correct Mar 31 T3 stop note
Added Apr 1 trade log entry: SLV 2 trades (overnight SS exit -0.259/share, same-day TS exit -0.078/share), GLD/IAU/GDX 0 trades. Also corrected Mar 31 T3 overnight hold note — the $67.50 stop at 21:10 UTC was REJECTED by Alpaca (market closed), not placed as originally recorded. Confirmed from Alpaca UI during the overnight stop gap investigation.

 .claude/calibration/live-trade-log.md | 17 +++++++++++++++--
 .claude/memory/gitlog.md              | 25 ++++++++++++-------------
 .claude/memory/observations.md        |  2 +-
 3 files changed, 28 insertions(+), 16 deletions(-)

----
**2026-04-02** — fix: overnight stop gap — re-place DAY stop at market open
DAY stops expire at 20:00 UTC. Startup sync may fail post-market (rejected by Alpaca), leaving position unprotected at next market open. Loop now re-places stop before on_bar if pending_stop_order_id is None. Gap existed since Mar 4 — cedc865 noted the intention but never built it. Discovered via rejected stop order in Alpaca UI (Mar 31 21:10 UTC). Also logged Apr 1 audit: SLV 2 trades, GLD/IAU/GDX 0 trades, all bots flat EOD.

 .claude/memory/gitlog.md       | 45 +++++++++++++++++++++++-------------------
 .claude/memory/observations.md |  8 ++++++--
 CLAUDE.md                      |  3 ++-
 3 files changed, 33 insertions(+), 23 deletions(-)

----
**2026-04-02** — fix: re-place DAY stop at market open for overnight positions
DAY stops expire at 20:00 UTC. Startup sync may fail post-market (rejected
by Alpaca), leaving the position unprotected until the first on_bar fires
at ~13:45 UTC — a 15-minute gap at market open. New loop check re-places
the stop at strategy.current_sl on the first market-hours bar if no
pending_stop_order_id is set. Also ensures trail logic can run on that bar
(update_stop_order silently skips if pending_stop_order_id is None).

Co-Authored-By: Claude Opus 4.6 <noreply@anthropic.com>

 backend/runner.py | 28 ++++++++++++++++++++++++++++
 1 file changed, 28 insertions(+)

----
**2026-04-01** — chore: add traceability rule to global CLAUDE.md, update hook description
Documented the Related domain file convention as a formal rule in global CLAUDE.md (the traceability rule). Updated PostToolUse hook description to accurately reflect all four steps including Step 1c reverse domain file check. Completes the harness improvements from this session — all changes now reflected in both project and global config.

 .claude/memory/gitlog.md       | 20 +++++++++-----------
 .claude/memory/observations.md |  2 +-
 2 files changed, 10 insertions(+), 12 deletions(-)

----
**2026-04-01** — chore: add reverse domain file check to triage, backfill MCP domain file
Added Step 1c to openbrain-audit-reminder.sh — reverse domain file check forces verification that domain file bodies (not just status lines) reflect session work. Added Related domain file header convention to procedures for traceability. Backfilled alpaca-mcp.md with Integration status section: 3 tools validated and in use, 5 untested, SSH-only items listed. Updated global CLAUDE.md hook code block to match.

 .claude/hooks/openbrain-audit-reminder.sh |  5 +++++
 .claude/integrations/alpaca-mcp.md        | 31 ++++++++++++++++++++++++++++++-
 .claude/memory/gitlog.md                  | 23 ++++++++++++-----------
 .claude/memory/observations.md            |  4 ++--
 .claude/procedures/daily-trade-audit.md   |  1 +
 5 files changed, 50 insertions(+), 14 deletions(-)

----
**2026-04-01** — chore: integrate Alpaca MCP into check-bots and trade audit workflows
Rewrote CLAUDE.md Run Commands — check bots now uses MCP as primary method (get_clock, get_all_positions, get_orders), SSH retained for pm2 process health only. Rewrote daily-trade-audit procedure to use get_orders instead of SSH→DB→Alpaca cross-reference. Validated by comparing Mar 23 MCP output against existing trade log — 26 orders, 7 trades, all prices and trail ratchets matched exactly.

 .claude/integrations/alpaca-mcp.md      |  2 +-
 .claude/memory/gitlog.md                | 23 ++++-----
 .claude/memory/observations.md          |  4 +-
 .claude/procedures/daily-trade-audit.md | 86 ++++++++++++++++++++++-----------
 CLAUDE.md                               | 24 ++++++---
 5 files changed, 89 insertions(+), 50 deletions(-)

