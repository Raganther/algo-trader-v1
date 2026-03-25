# Recent Git History

> Auto-generated on git save. Do not edit manually.

----
**2026-03-25** — chore: Mar 25 audit — 1 GDX trade
Mar 25: GDX only trade. Buy .80, trail updated to .49 after 1 bar, server stop fired .48 (below entry). GLD/IAU/SLV flat. Alpaca audit matched: 3 records per trailing-stop trade (buy + initial stop canceled + trail stop filled) — confirmed normal pattern.

 .claude/memory/observations.md | 1 +
 1 file changed, 1 insertion(+)

----
**2026-03-25** — chore: migrate domain files out of memory/ into domain folders
Moved .claude/memory/strategies/ → .claude/strategies/ and .claude/memory/calibration_notes.md → .claude/calibration/calibration_notes.md. Updated CLAUDE.md Architecture and Session Start sections to reference new paths. .claude/memory/ now holds only the three core files (plan.md, observations.md, gitlog.md) per global CLAUDE.md spec. Future graduated files go in .claude/[domain]/, never in memory/.

 .../{memory => calibration}/calibration_notes.md   |  0
 .claude/memory/gitlog.md                           | 27 ++++++++++++++--------
 .claude/memory/observations.md                     |  3 ++-
 .../{memory => }/strategies/composable_results.md  |  0
 .claude/{memory => }/strategies/event_surprise.md  |  0
 .../strategies/stochrsi_enhanced_gdx.md            |  0
 .../strategies/stochrsi_enhanced_gld.md            |  0
 .../strategies/stochrsi_enhanced_iau.md            |  0
 .../strategies/stochrsi_enhanced_slv.md            |  0
 CLAUDE.md                                          |  8 +++----
 10 files changed, 23 insertions(+), 15 deletions(-)

----
**2026-03-25** — chore: migrate memory files to .claude/memory/
Move plan.md, observations.md, MEMORY.md (renamed gitlog.md) from memory/ root into .claude/memory/ to consolidate all Claude files under .claude/. Update git-save.sh, git-save-guard.sh, load-context.sh, and CLAUDE.md to use new paths. Matches updated global CLAUDE.md design.

 .claude/hooks/git-save-guard.sh              | 12 ++++++------
 .claude/hooks/load-context.sh                |  6 +++---
 memory/MEMORY.md => .claude/memory/gitlog.md | 26 +++++++++++++++-----------
 {memory => .claude/memory}/observations.md   |  0
 {memory => .claude/memory}/plan.md           |  0
 CLAUDE.md                                    |  6 +++---
 scripts/git-save.sh                          |  9 ++++-----
 7 files changed, 31 insertions(+), 28 deletions(-)

----
**2026-03-25** — chore: audit cleanup — remove redundant and legacy files
Deleted .claude/workflows/git_save.md (old superseded process doc referencing scripts that no longer exist), .claude/memory/MEMORY.md (legacy relic with wrong timezone instruction), and .claude/archive/ (3 completed plan docs). Insights from archived plans already live in strategy cards, calibration_notes.md, and OpenBrain. Git history preserves the originals. .claude/ is now clean.

 .claude/archive/edge_enhancement_plan.md     |  188 ----
 .claude/archive/forward_testing_plan.md      |  735 -------------
 .claude/archive/strategy_discovery_engine.md | 1483 --------------------------
 .claude/memory/MEMORY.md                     |    5 -
 .claude/workflows/git_save.md                |  116 --
 memory/MEMORY.md                             |   23 +-
 memory/observations.md                       |    5 +-
 7 files changed, 17 insertions(+), 2538 deletions(-)

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

