# Recent Git History

> Auto-generated on git save. Do not edit manually.

----
**2026-03-28** — chore: confirm OpenBrain auto-backup to GitHub is active
Verified ~/.openbrain/ git repo, sync.sh, and three global PostToolUse hooks all in place. Every OpenBrain write auto-syncs to Raganther/openbrain private repo. Global infrastructure — no per-project changes needed.

 .claude/memory/observations.md | 1 +
 1 file changed, 1 insertion(+)

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

----
**2026-03-28** — chore: add domain file check instruction to global and project CLAUDE.md
Added explicit workflow instruction: before any update, new feature, or bug fix, scan and read relevant domain files first. Added to global CLAUDE.md Workflow section and project CLAUDE.md Session Start section. Closes the gap where unplanned work bypassed the domain file review loop entirely.

 .claude/memory/gitlog.md | 30 +++++++++---------------------
 CLAUDE.md                |  2 ++
 2 files changed, 11 insertions(+), 21 deletions(-)

----
**2026-03-27** — chore: note post-calibration research process and rolling validation plan
Strategic discussion: after Apr 20 calibration, use rolling 4-8 week forward tests on new assets/strategies to continuously validate the backtester. Execution layer calibrations apply universally; signal layer needs per-strategy forward test. Three-phase loop: research → validate → deploy. Added to observations and plan.

 .claude/memory/gitlog.md       | 24 ++++++++++--------------
 .claude/memory/observations.md | 20 ++++++++++++++++++++
 .claude/memory/plan.md         |  4 ++++
 3 files changed, 34 insertions(+), 14 deletions(-)

----
**2026-03-27** — chore: update calibration_notes — trading_hours required, Mar 27 snapshot
Added trading_hours:[13,20] as a required param for all Apr 20 calibration backtest runs. Without it, backtest inflates trade count by ~11% by processing pre/post-market bars. Added Mar 20-27 preliminary snapshot (40 backtest vs 31 live, 1.3x, P&L direction aligned). Also removed long_only:true from the Apr 20 command — bots don't use that param.

 .claude/calibration/calibration_notes.md | 21 ++++++++++++++++++++-
 .claude/memory/gitlog.md                 | 18 +++++++++---------
 2 files changed, 29 insertions(+), 10 deletions(-)

----
**2026-03-27** — chore: preliminary calibration check — Mar 27
Ran backtest (aggressive params + trading_hours filter) over Mar 20-27 calibration window. Backtest predicts 40 trades vs 31 live (1.3x); P&L direction aligned (near-zero/slightly negative across all 4 symbols). No red flags. For Apr 20 calibration: always add trading_hours:[13,20] to match live bot's market hours gate — the main systematic correction required.

 .claude/memory/gitlog.md       | 29 +++++++++++------------------
 .claude/memory/observations.md | 19 +++++++++++++++++++
 .claude/memory/plan.md         |  2 +-
 3 files changed, 31 insertions(+), 19 deletions(-)

