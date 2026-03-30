# Recent Git History

> Auto-generated on git save. Do not edit manually.

----
**2026-03-30** — feat: create live-trade-log.md — per-trade calibration data Mar 20-27
Created .claude/calibration/live-trade-log.md to capture per-trade detail (entry/exit prices, stop levels, slippage) for the Mar 20–Apr 20 calibration window. Populated Mar 20–27 from DB + Alpaca cross-reference — all days PASS (9+13+16+2+14+6 = 60 records matched). Corrected Mar 24 server stop count from 5→6 in observations.md. Domain file registered in CLAUDE.md.

 .claude/calibration/live-trade-log.md | 136 ++++++++++++++++++++++++++++++++++
 .claude/memory/observations.md        |  14 ++--
 CLAUDE.md                             |   2 +
 3 files changed, 146 insertions(+), 6 deletions(-)

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

----
**2026-03-28** — chore: confirm OpenBrain auto-backup to GitHub is active
Verified ~/.openbrain/ git repo, sync.sh, and three global PostToolUse hooks all in place. Every OpenBrain write auto-syncs to Raganther/openbrain private repo. Global infrastructure — no per-project changes needed.

 .claude/memory/gitlog.md       | 18 +++++++++---------
 .claude/memory/observations.md |  1 +
 2 files changed, 10 insertions(+), 9 deletions(-)

----
**2026-03-28** — chore: note Mar 28 memory system and workflow updates
Session summary: domain file check instruction added to both CLAUDE.md files, tested successfully with XLE research via plan mode. git-save.sh pull-rebase safety net added. GitHub repo confirmed already syncing on every save — no functional change to normal workflow.

 .claude/memory/gitlog.md       | 20 ++++++++++----------
 .claude/memory/observations.md | 10 +++++++++-
 2 files changed, 19 insertions(+), 11 deletions(-)

----
**2026-03-28** — chore: add pull --rebase before push in git-save.sh
Ensures local is synced with remote before pushing. Prevents push failures if remote has diverged (e.g. edits via GitHub web UI or from another machine). Matches the pull-rebase+push pattern documented in global CLAUDE.md.

 .claude/memory/gitlog.md | 20 +++++++++-----------
 scripts/git-save.sh      |  3 ++-
 2 files changed, 11 insertions(+), 12 deletions(-)

----
**2026-03-28** — feat: XLE 15m research — Sharpe 2.06, WF 4/4, Rolling Validation Test #1
XLE 15m backtest with validated precious metals params (no retuning): Sharpe 2.06, +85.2% return, 3.35% DD, WF 4/4. Every year 2020-2025 profitable. Confirms StochRSI mean reversion at 15m works across sectors, not just precious metals. Strategy card created. Forward test queued as Rolling Validation Test #1 after Apr 20 calibration.

 .claude/memory/gitlog.md                    | 25 ++++----
 .claude/memory/observations.md              |  2 +
 .claude/memory/plan.md                      |  2 +-
 .claude/strategies/stochrsi_enhanced_xle.md | 91 +++++++++++++++++++++++++++++
 CLAUDE.md                                   |  1 +
 5 files changed, 108 insertions(+), 13 deletions(-)

