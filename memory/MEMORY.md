# Recent Git History

> Auto-generated on git save. Do not edit manually.

----
**2026-03-17** — chore: add git-save guard hook + document memory restructure
Added PreToolUse hook (git-save-guard.sh) that blocks git-save.sh if memory files are unchanged since last commit — ensures plan.md and observations.md are always updated before saving. Updated settings.json to register the hook. Documented the memory restructure rationale in observations.md.

 .claude/hooks/git-save-guard.sh | 24 ++++++++++++++++++++++++
 .claude/settings.json           | 11 +++++++++++
 memory/observations.md          |  7 +++++++
 3 files changed, 42 insertions(+)

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

----
**2026-03-16** — fix: wash trade prevention — cancel open orders before long entry
pending_fills retries can leave a hanging sell order on Alpaca pre-market. When a new buy signal fires, Alpaca rejects it as a wash trade. Fix: cancel_all_orders_for_symbol before every long entry in live_broker.buy() — same pattern already used in the short-close path. Root cause confirmed via SLV Mar 13 audit. All known long-side bugs now fixed. Remaining before real money: trailing stop firing in profit (passive wait), short entry guard fix, short mechanics verification.

 CLAUDE.md        |  4 ++--
 memory/MEMORY.md | 57 +++++++++++++++++++++++++-------------------------------
 memory/plan.md   |  2 +-
 3 files changed, 28 insertions(+), 35 deletions(-)

