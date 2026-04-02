# Recent Git History

> Auto-generated on git save. Do not edit manually.

----
**2026-04-02** — fix: overnight stop gap — re-place DAY stop at market open
DAY stops expire at 20:00 UTC. Startup sync may fail post-market (rejected by Alpaca), leaving position unprotected at next market open. Loop now re-places stop before on_bar if pending_stop_order_id is None. Gap existed since Mar 4 — cedc865 noted the intention but never built it. Discovered via rejected stop order in Alpaca UI (Mar 31 21:10 UTC). Also logged Apr 1 audit: SLV 2 trades, GLD/IAU/GDX 0 trades, all bots flat EOD.

 .claude/memory/observations.md | 8 ++++++--
 CLAUDE.md                      | 3 ++-
 2 files changed, 8 insertions(+), 3 deletions(-)

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

----
**2026-04-01** — chore: add Alpaca MCP domain file — full 57-tool audit
Audited all Alpaca MCP tools and created .claude/integrations/alpaca-mcp.md as a reference. 57 tools across 11 categories — high-value tools ranked for trade audit and calibration workflows. No news endpoint confirmed (web search still needed). Paper accounts must use feed=iex. Registered in CLAUDE.md and observations.md.

 .claude/integrations/alpaca-mcp.md | 121 +++++++++++++++++++++++++++++++++++++
 .claude/memory/gitlog.md           |  32 ++++------
 .claude/memory/observations.md     |   6 ++
 CLAUDE.md                          |   4 +-
 4 files changed, 141 insertions(+), 22 deletions(-)

----
**2026-04-01** — chore: add Alpaca MCP, correlate trade log with news
Configured official Alpaca MCP server (uvx alpaca-mcp-server) in global Claude settings — provides live news, market data, and account access. Requires restart to activate. Cross-referenced Mar 20–31 trade log with news: Mar 23 best day = post-crash bounce; Mar 31 best day = Iran de-escalation (Trump ends campaign, GLD +3.79%); choppy loss days tied to post-crash whipsaw volatility. GDX underperformance confirmed structural — gold -17% vs GDX -29% due to mining margin compression from oil spike. Added specific news triggers and GDX -29% figure to calibration-notes.md.

 .claude/calibration/calibration-notes.md | 12 ++++++++++--
 .claude/memory/gitlog.md                 | 32 +++++++++++---------------------
 .claude/memory/observations.md           |  2 +-
 CLAUDE.md                                |  1 +
 4 files changed, 23 insertions(+), 24 deletions(-)

----
**2026-03-31** — chore: update memory harness, add market regime context to calibration notes
Revised global CLAUDE.md memory harness: observations.md now acts as short-term memory with domain file links; new living domain file rule (update in place, don't re-graduate); triage options updated to GRADUATE/UPDATE-DOMAIN/REMOVE. Cleaned observations.md — removed resolved entries (memory system changelog, market open fill delays), trimmed remaining entries to one-line summaries with domain file links. Added market regime section to calibration-notes.md: calibration window coincides with historic precious metals crash (Iran war, gold -25% from ATH) — documented implications for interpreting Apr 20 execution vs signal layer results.

 .claude/calibration/calibration-notes.md  | 21 ++++++-
 .claude/hooks/openbrain-audit-reminder.sh |  7 ++-
 .claude/memory/gitlog.md                  | 21 +++----
 .claude/memory/observations.md            | 93 ++++---------------------------
 4 files changed, 47 insertions(+), 95 deletions(-)

