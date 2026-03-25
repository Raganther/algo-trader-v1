# Recent Git History

> Auto-generated on git save. Do not edit manually.

----
**2026-03-25** — chore: audit cleanup — remove redundant and legacy files
Deleted .claude/workflows/git_save.md (old superseded process doc referencing scripts that no longer exist), .claude/memory/MEMORY.md (legacy relic with wrong timezone instruction), and .claude/archive/ (3 completed plan docs). Insights from archived plans already live in strategy cards, calibration_notes.md, and OpenBrain. Git history preserves the originals. .claude/ is now clean.

 .claude/archive/edge_enhancement_plan.md     |  188 ----
 .claude/archive/forward_testing_plan.md      |  735 -------------
 .claude/archive/strategy_discovery_engine.md | 1483 --------------------------
 .claude/memory/MEMORY.md                     |    5 -
 .claude/workflows/git_save.md                |  116 --
 memory/observations.md                       |    5 +-
 6 files changed, 3 insertions(+), 2529 deletions(-)

----
**2026-03-25** — chore: add Check 3 to git-save-guard (core memory file discoverability)
git-save-guard.sh now has three checks matching global CLAUDE.md spec. Check 3 blocks if memory/plan.md, memory/observations.md, or memory/MEMORY.md are missing from CLAUDE.md Session Start section. Closes the gap identified in the gap analysis — auto-load files are now enforced as well as domain files.

 .claude/hooks/git-save-guard.sh | 15 +++++++++++++++
 memory/MEMORY.md                | 23 ++++++++++-------------
 memory/observations.md          |  4 ++--
 3 files changed, 27 insertions(+), 15 deletions(-)

----
**2026-03-25** — chore: Mar 24 audit + slippage observation
Mar 24: 8 trades, full Alpaca audit passed, 5 server stop fires in choppy metals market. GLD+IAU stops fired simultaneously twice — correlated asset behaviour confirmed. Identified two distinct slippage types: spread (modelled in backtest) vs stop execution (not modelled). Stop execution slippage small but consistent (~0.01-0.14/share), will surface in Layer 3 of Apr 20 calibration.

 memory/MEMORY.md       | 20 +++++++++-----------
 memory/observations.md | 10 ++++++++--
 2 files changed, 17 insertions(+), 13 deletions(-)

----
**2026-03-24** — chore: sync hooks with global CLAUDE.md updates
Updated git-save-guard.sh to enforce domain file discoverability (blocks if .claude/memory/ files not listed in CLAUDE.md). Updated openbrain-audit-reminder.sh Step 1 to require update-in-place check before appending. Removed docs/dev.md reference from project CLAUDE.md. All hooks now in sync with global CLAUDE.md.

 .claude/hooks/git-save-guard.sh           | 29 ++++++++++++++++++++++++++---
 .claude/hooks/openbrain-audit-reminder.sh | 10 +++++-----
 CLAUDE.md                                 |  3 +--
 memory/MEMORY.md                          | 23 ++++++++++++-----------
 memory/observations.md                    |  5 +++++
 5 files changed, 49 insertions(+), 21 deletions(-)

----
**2026-03-24** — chore: graduate observations, create calibration_notes, fix OpenBrain setup
Graduated calibration methodology from observations.md into .claude/memory/calibration_notes.md. Pruned observations.md to active-only insights (3 sections, down from 9). Created .claude/openbrain-category (algo-trader), updated openbrain-audit-reminder.sh to three-step format with update_memory guidance, migrated 10 OpenBrain memories from wrong categories to algo-trader.

 .claude/hooks/openbrain-audit-reminder.sh |  27 +++++--
 .claude/memory/calibration_notes.md       |  72 ++++++++++++++++++
 .claude/openbrain-category                |   1 +
 CLAUDE.md                                 |   2 +
 memory/MEMORY.md                          |  25 ++++---
 memory/observations.md                    | 119 +++---------------------------
 6 files changed, 120 insertions(+), 126 deletions(-)

----
**2026-03-23** — chore: plan preliminary backtest check for Mar 30
All long-side mechanics now confirmed. Decision: let bots run until Apr 20 for full calibration. Preliminary diagnostic backtest planned for ~Mar 30 as early warning check — not the calibration, just sanity check for obvious misalignments. Proper comparison needs ~80-100 trades per symbol.

 memory/MEMORY.md | 24 ++++++++++--------------
 memory/plan.md   |  1 +
 2 files changed, 11 insertions(+), 14 deletions(-)

----
**2026-03-23** — chore: document calibration integrity reasoning
Confirmed that all bug fixes are in the execution layer — signal generation is untouched. Calibration comparison between backtest and live is clean. Documented signal vs execution layer separation in observations.md as a key insight for the Apr 20 calibration review.

 memory/MEMORY.md       | 26 ++++++++++++--------------
 memory/observations.md |  7 +++++++
 2 files changed, 19 insertions(+), 14 deletions(-)

----
**2026-03-23** — feat: trailing stop fire in profit confirmed + Mar 23 audit
GDX server stop fired intrabar at $83.317 vs entry $80.05 — first confirmed trailing stop fire in profit. Full Alpaca audit passed (9 trades, all records matched). Both server-side exit mechanics now verified: stop loss (Mar 10) and trailing stop in profit (Mar 23). Marked step complete in plan.md.

 CLAUDE.md              |  2 +-
 memory/MEMORY.md       | 27 ++++++++++++---------------
 memory/observations.md |  1 +
 memory/plan.md         |  2 +-
 4 files changed, 15 insertions(+), 17 deletions(-)

