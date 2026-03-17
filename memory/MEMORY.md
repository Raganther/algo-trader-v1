# Recent Git History

> Auto-generated on git save. Do not edit manually.

----
**2026-03-17** — chore: Mar 17 bot check — all 4 flat, no trades
Routine session check. All bots healthy, market open, no trades today. Yesterday's SLV fill timeout confirmed as pre-fix artifact. No code changes this session.

 CLAUDE.md              | 1 +
 memory/observations.md | 1 +
 2 files changed, 2 insertions(+)

----
**2026-03-17** — chore: add git-save guard hook + document memory restructure
Added PreToolUse hook (git-save-guard.sh) that blocks git-save.sh if memory files are unchanged since last commit — ensures plan.md and observations.md are always updated before saving. Updated settings.json to register the hook. Documented the memory restructure rationale in observations.md.

 .claude/hooks/git-save-guard.sh | 24 ++++++++++++++++++++++++
 .claude/settings.json           | 11 +++++++++++
 memory/MEMORY.md                | 27 ++++++++++++---------------
 memory/observations.md          |  7 +++++++
 4 files changed, 54 insertions(+), 15 deletions(-)

----
**2026-03-17** — chore: update session start hook — correct file paths
Hook was referencing stale paths (.claude/claude.md, recent_history.md). Updated to show the actual read order: MEMORY.md, plan.md, observations.md.

 .claude/hooks/load-context.sh |  7 ++++---
 memory/MEMORY.md              | 19 +++++++++----------
 2 files changed, 13 insertions(+), 13 deletions(-)

----
**2026-03-17** — chore: restructure memory — split plan.md into steps + observations
Created memory/observations.md as a dedicated home for running insights, calibration methodology, and open questions. plan.md now holds active steps only and stays short. Removed resolved bugs list from CLAUDE.md (13 items, all in git history). Updated global CLAUDE.md to document the six-file system and new git save workflow.

 CLAUDE.md              | 18 ++------------
 memory/MEMORY.md       | 26 +++++++++-----------
 memory/observations.md | 66 ++++++++++++++++++++++++++++++++++++++++++++++++++
 memory/plan.md         | 59 +-------------------------------------------
 4 files changed, 81 insertions(+), 88 deletions(-)

----
**2026-03-17** — chore: document layered calibration comparison framework
Added layered calibration framework to plan.md observations — trade count confirms signal generation, entry/exit prices confirm spread assumption, stop fill prices confirm intrabar stop modeling, aggregate P&L confirms overall accuracy. Added caveats: paper vs real fills, snapshot nature, needs 80-100 trades. Calibration confirms the simulator is faithful; paper-to-real transfer is a separate question answered by micro-trading.

 memory/MEMORY.md | 21 ++++++++++-----------
 memory/plan.md   | 17 +++++++++++++++++
 2 files changed, 27 insertions(+), 11 deletions(-)

----
**2026-03-16** — chore: note Observations section in session start
Added one-line clarification to CLAUDE.md session start so future sessions know plan.md Observations holds active working insights, not just plan steps.

 CLAUDE.md        |  2 +-
 memory/MEMORY.md | 24 ++++++++++--------------
 2 files changed, 11 insertions(+), 15 deletions(-)

----
**2026-03-16** — chore: consolidate plan.md active steps
Removed unnecessary chart section — trade overlays are just another active step, not a separate plan. Keeps plan.md flat and readable.

 memory/MEMORY.md | 28 +++++++++++-----------------
 memory/plan.md   | 15 ++++-----------
 2 files changed, 15 insertions(+), 28 deletions(-)

----
**2026-03-16** — chore: restructure plan.md + calibration baseline Mar 5-16
Restructured plan.md: removed completed debugging history, added Observations section for working insights. First calibration snapshot: backtest vs live Mar 5-16 shows reasonable alignment (SLV exact, GLD close, IAU/GDX within 2-3 trades). Established calibration methodology using Jan 1 lead-in to eliminate warmup distortion. Fixed adx_threshold documentation — test bots use 50 not 20. Next calibration check due ~Apr 16.

 CLAUDE.md        |  12 ++---
 memory/MEMORY.md |  24 ++++-----
 memory/plan.md   | 149 ++++++++++++++++++++-----------------------------------
 3 files changed, 73 insertions(+), 112 deletions(-)

