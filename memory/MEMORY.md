# Recent Git History

> Auto-generated on git save. Do not edit manually.

----
**2026-03-24** — chore: sync hooks with global CLAUDE.md updates
Updated git-save-guard.sh to enforce domain file discoverability (blocks if .claude/memory/ files not listed in CLAUDE.md). Updated openbrain-audit-reminder.sh Step 1 to require update-in-place check before appending. Removed docs/dev.md reference from project CLAUDE.md. All hooks now in sync with global CLAUDE.md.

 .claude/hooks/git-save-guard.sh           | 29 ++++++++++++++++++++++++++---
 .claude/hooks/openbrain-audit-reminder.sh | 10 +++++-----
 CLAUDE.md                                 |  3 +--
 memory/observations.md                    |  5 +++++
 4 files changed, 37 insertions(+), 10 deletions(-)

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

----
**2026-03-22** — chore: set up OpenBrain workflow and identify first candidates
Confirmed OpenBrain hooks are live (all three: SessionStart, PreToolUse guard, PostToolUse audit reminder). Identified 10 candidates for first OpenBrain write: 5 Alpaca API gotchas, 4 trading system methodology patterns, 1 validated edge. Removed redundant openbrain_guide.md — global CLAUDE.md description is sufficient to guide candidate selection.

 memory/MEMORY.md       | 40 +++++++++++++++++++++-------------------
 memory/observations.md |  2 ++
 2 files changed, 23 insertions(+), 19 deletions(-)

----
**2026-03-22** — chore: add OpenBrain audit hook to memory system
Added openbrain-audit-reminder.sh PostToolUse hook — fires after every git save and prompts OpenBrain audit for cross-project knowledge candidates. Project now has all three standard hooks. Future git saves will include an OpenBrain audit step.

Co-Authored-By: Claude Sonnet 4.6 <noreply@anthropic.com>

 .claude/hooks/openbrain-audit-reminder.sh | 19 +++++++++++++++++++
 .claude/settings.json                     | 11 +++++++++++
 CLAUDE.md                                 |  1 +
 memory/observations.md                    |  5 +++++
 4 files changed, 36 insertions(+)

----
**2026-03-21** — chore: update calibration window to Mar 20 – Apr 20
Adjusted calibration window start from Mar 16 to Mar 20 — first fully confirmed clean day with current params (trail_atr=0.5, trail_after_bars=1) and all fixes deployed (race condition fix Mar 19, 18/18 audit passed Mar 20). End date moved from Apr 19 to Apr 20 to maintain exactly 1 month window. Updated CLAUDE.md, plan.md, and observations.md.

 CLAUDE.md              |  4 ++--
 memory/MEMORY.md       | 22 +++++++++++-----------
 memory/observations.md | 12 +++++++-----
 memory/plan.md         |  4 ++--
 4 files changed, 22 insertions(+), 20 deletions(-)

