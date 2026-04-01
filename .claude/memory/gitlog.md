# Recent Git History

> Auto-generated on git save. Do not edit manually.

----
**2026-04-01** — chore: add reverse domain file check to triage, backfill MCP domain file
Added Step 1c to openbrain-audit-reminder.sh — reverse domain file check forces verification that domain file bodies (not just status lines) reflect session work. Added Related domain file header convention to procedures for traceability. Backfilled alpaca-mcp.md with Integration status section: 3 tools validated and in use, 5 untested, SSH-only items listed. Updated global CLAUDE.md hook code block to match.

 .claude/hooks/openbrain-audit-reminder.sh |  5 +++++
 .claude/integrations/alpaca-mcp.md        | 31 ++++++++++++++++++++++++++++++-
 .claude/memory/observations.md            |  4 ++--
 .claude/procedures/daily-trade-audit.md   |  1 +
 4 files changed, 38 insertions(+), 3 deletions(-)

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

----
**2026-03-31** — chore: correct Mar 31 timestamps IST→UTC, co-locate trade log analysis
All Mar 31 entry/exit times were 1h fast (Irish DST started Mar 29, Alpaca UI showing UTC+1 after that). Corrected all Mar 31 timestamps to UTC. Mar 21 and Mar 28 backfilled as confirmed zero-trade days. Trade log analysis (43 trades, K-exit 76% vs TS 14%, GDX divergence, correlated entry risk) moved from observations.md into live-trade-log.md — co-located with the data it describes. observations.md now holds a one-line pointer.

 .claude/calibration/live-trade-log.md | 87 +++++++++++++++++++++++++++--------
 .claude/memory/gitlog.md              | 19 ++++----
 .claude/memory/observations.md        |  9 +++-
 3 files changed, 86 insertions(+), 29 deletions(-)

----
**2026-03-31** — chore: log Mar 31 trades, correct Mar 30 notes, deploy metadata fix
Mar 31 audit: PASS 36/36 Alpaca records matched. Strong metals rally day — 5/7 closed trades profitable (GLD/IAU/SLV K-exits, GDX both server stops near entry). SLV T3 overnight hold active. Metadata fix confirmed working — no set_entry_metadata warnings on today's delayed fills. Also corrected Mar 30 T1/T2 exit notes (local SL hits, not min_hold bypass) and deployed live_broker metadata fix that was committed but not yet pulled to server.

 .claude/calibration/live-trade-log.md | 23 +++++++++++++++++++++--
 .claude/memory/gitlog.md              | 19 ++++++++++---------
 .claude/memory/observations.md        |  6 +++++-
 3 files changed, 36 insertions(+), 12 deletions(-)

----
**2026-03-30** — fix: attach entry metadata to delayed fill trades in live_broker
When buy() timed out (>30s market open fills), set_entry_metadata() was called but new_trades was empty — metadata silently dropped. Fix: store in _pending_entry_metadata[symbol], attach when pending_fills resolves the fill. entry_time/entry_hour/entry_dow/atr_at_entry now correctly written to DB for all delayed fill trades.

 .claude/calibration/live-trade-log.md | 12 +++++++++++-
 .claude/memory/gitlog.md              | 20 +++++++++++---------
 .claude/memory/observations.md        |  9 ++++++---
 backend/engine/live_broker.py         | 20 +++++++++++++-------
 4 files changed, 41 insertions(+), 20 deletions(-)

