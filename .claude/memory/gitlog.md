# Recent Git History

> Auto-generated on git save. Do not edit manually.

----
**2026-03-31** — chore: correct Mar 31 timestamps IST→UTC, co-locate trade log analysis
All Mar 31 entry/exit times were 1h fast (Irish DST started Mar 29, Alpaca UI showing UTC+1 after that). Corrected all Mar 31 timestamps to UTC. Mar 21 and Mar 28 backfilled as confirmed zero-trade days. Trade log analysis (43 trades, K-exit 76% vs TS 14%, GDX divergence, correlated entry risk) moved from observations.md into live-trade-log.md — co-located with the data it describes. observations.md now holds a one-line pointer.

 .claude/calibration/live-trade-log.md | 87 +++++++++++++++++++++++++++--------
 .claude/memory/observations.md        |  9 +++-
 2 files changed, 76 insertions(+), 20 deletions(-)

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

----
**2026-03-30** — chore: add daily-trade-audit procedure
Extracted the daily trade audit process as a reusable procedure. Covers querying cloud DB, cross-referencing Alpaca records, reconstructing trades, and logging to live-trade-log.md. Based on the Mar 20-27 backfill work done this session.

 .claude/memory/gitlog.md                | 23 ++++++++--------
 .claude/memory/observations.md          |  2 +-
 .claude/procedures/_index.md            |  1 +
 .claude/procedures/daily-trade-audit.md | 47 +++++++++++++++++++++++++++++++++
 4 files changed, 60 insertions(+), 13 deletions(-)

----
**2026-03-30** — feat: create live-trade-log.md — per-trade calibration data Mar 20-27
Created .claude/calibration/live-trade-log.md to capture per-trade detail (entry/exit prices, stop levels, slippage) for the Mar 20–Apr 20 calibration window. Populated Mar 20–27 from DB + Alpaca cross-reference — all days PASS (9+13+16+2+14+6 = 60 records matched). Corrected Mar 24 server stop count from 5→6 in observations.md. Domain file registered in CLAUDE.md.

 .claude/calibration/live-trade-log.md | 136 ++++++++++++++++++++++++++++++++++
 .claude/memory/gitlog.md              |  24 +++---
 .claude/memory/observations.md        |  14 ++--
 CLAUDE.md                             |   2 +
 4 files changed, 159 insertions(+), 17 deletions(-)

----
**2026-03-30** — chore: rename domain files to hyphenated convention, add migration procedure
Renamed all 8 domain files from underscores to hyphens to comply with lowercase-hyphenated naming convention enforced by the new domain-naming-guard.sh. Updated all cross-references across CLAUDE.md, plan.md, observations.md, and internal strategy card links. Also committed procedure file memory-harness-migration.md and updated _index.md — these were written last session but not yet committed.

 .../{calibration_notes.md => calibration-notes.md} |  0
 .claude/memory/gitlog.md                           | 31 +++++++++++++++-------
 .claude/memory/observations.md                     | 10 ++++---
 .claude/memory/plan.md                             |  2 +-
 .claude/procedures/_index.md                       |  1 +
 .claude/procedures/memory-harness-migration.md     | 30 +++++++++++++++++++++
 ...composable_results.md => composable-results.md} |  0
 .../{event_surprise.md => event-surprise.md}       |  0
 ...si_enhanced_gdx.md => stochrsi-enhanced-gdx.md} |  2 +-
 ...si_enhanced_gld.md => stochrsi-enhanced-gld.md} |  2 +-
 ...si_enhanced_iau.md => stochrsi-enhanced-iau.md} |  2 +-
 ...si_enhanced_slv.md => stochrsi-enhanced-slv.md} |  2 +-
 ...si_enhanced_xle.md => stochrsi-enhanced-xle.md} |  0
 CLAUDE.md                                          | 18 ++++++-------
 14 files changed, 72 insertions(+), 28 deletions(-)

----
**2026-03-30** — chore: memory harness migration — check 6, naming guard, epistemic headers, read-when pointers
Migrated project to updated global CLAUDE.md spec. Added git-save-guard Check 6 (blocks missing Epistemic/Last verified headers), created domain-naming-guard.sh (PreToolUse Write, enforces lowercase-hyphenated naming), extended all 8 domain file headers with Epistemic and Last verified fields (dates from git log), and reformatted CLAUDE.md domain file pointers from content summaries to read-when-X trigger conditions.

 .claude/calibration/calibration_notes.md    |  2 +-
 .claude/hooks/domain-naming-guard.sh        | 34 +++++++++++++++++++++++++++++
 .claude/hooks/git-save-guard.sh             | 32 ++++++++++++++++++++++++++-
 .claude/memory/gitlog.md                    | 34 +++++++++++++++++++----------
 .claude/memory/observations.md              | 16 +++++++++-----
 .claude/settings.json                       |  9 ++++++++
 .claude/strategies/composable_results.md    |  2 +-
 .claude/strategies/event_surprise.md        |  2 +-
 .claude/strategies/stochrsi_enhanced_gdx.md |  2 +-
 .claude/strategies/stochrsi_enhanced_gld.md |  2 +-
 .claude/strategies/stochrsi_enhanced_iau.md |  2 +-
 .claude/strategies/stochrsi_enhanced_slv.md |  2 +-
 .claude/strategies/stochrsi_enhanced_xle.md |  2 +-
 CLAUDE.md                                   | 20 ++++++++---------
 14 files changed, 126 insertions(+), 35 deletions(-)

----
**2026-03-28** — chore: clarify short trading is deferred, not blocking real money
Short trading cannot be enabled at starting capital (€100) because Alpaca rejects fractional short selling and whole-share sizing is not feasible at that level. Removed from the 'remaining before real money' checklist. Long-only until capital grows. Also corrects a session where short trading was mistakenly suggested as the next priority.

 .claude/memory/gitlog.md | 22 +++++++++++-----------
 .claude/memory/plan.md   |  5 ++---
 CLAUDE.md                |  2 +-
 3 files changed, 14 insertions(+), 15 deletions(-)

