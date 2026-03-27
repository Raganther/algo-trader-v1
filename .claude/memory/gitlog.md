# Recent Git History

> Auto-generated on git save. Do not edit manually.

----
**2026-03-27** — chore: correct Mar 23 trade count (9 → 7)
Cross-referenced Mar 23 Alpaca export against pm2 log-based observation. 7 round trips confirmed (GLD×2, SLV×2, IAU×2, GDX T2 close). Original '9' was a counting error from log events, not a forward test bug.

 .claude/memory/observations.md | 2 +-
 1 file changed, 1 insertion(+), 1 deletion(-)

----
**2026-03-27** — chore: note phantom sell = blocked short entry
Investigated daily SELL skipped warning on all 4 bots. Confirmed it is the strategy's short entry logic firing (in_overbought_zone + K < 50) and being blocked by live_broker.sell() fractional short guard. Not a duplicate exit — warning message is misleading. State stays clean; resolves when whole-share sizing enables shorts.

 .claude/memory/gitlog.md       | 23 +++++++++--------------
 .claude/memory/observations.md | 12 ++++++++++++
 2 files changed, 21 insertions(+), 14 deletions(-)

----
**2026-03-26** — fix: place server stop after delayed buy fill (pending_fills gap)
When a buy fill timed out (30s) and was queued to pending_fills, stop_loss was not stored — so no server-side stop was placed when the fill eventually resolved. Confirmed on Mar 26: SLV ran 43 min unprotected. Fix: store stop_loss in pending_fills entry at timeout; place stop in get_new_trades() when fill resolves. Deployed to cloud.

 .claude/memory/gitlog.md       | 21 +++++++++++----------
 .claude/memory/observations.md |  6 ++++--
 .claude/memory/plan.md         |  1 +
 backend/engine/live_broker.py  | 21 ++++++++++++++++++++-
 4 files changed, 36 insertions(+), 13 deletions(-)

----
**2026-03-26** — chore: extract memory harness compliance audit procedure
First procedure extracted from this project. Covers how to audit hook scripts, domain files, and CLAUDE.md against the global spec. Includes example from Mar 26 session. Registered in .claude/procedures/_index.md.

 .claude/memory/gitlog.md                           | 38 ++++++++++----------
 .claude/memory/observations.md                     |  2 +-
 .claude/procedures/_index.md                       |  2 +-
 .../procedures/memory-harness-compliance-audit.md  | 40 ++++++++++++++++++++++
 4 files changed, 62 insertions(+), 20 deletions(-)

----
**2026-03-26** — chore: compliance audit — sync hooks and domain files with global CLAUDE.md
Added procedure extraction (Step 2) to openbrain-audit-reminder, Check 5 to git-save-guard, and created .claude/procedures/_index.md. Replaced directory-level strategy pointer in CLAUDE.md with 7 individual file listings, fixing the Check 2 gap. Added Status: current to all 7 domain files. Cleaned stale forward testing sections from strategy cards — mechanics are all confirmed, cards now refer to CLAUDE.md/calibration_notes.md for operational state.

 .claude/calibration/calibration_notes.md    |  2 ++
 .claude/hooks/git-save-guard.sh             | 28 +++++++++++++++++++++++-
 .claude/hooks/openbrain-audit-reminder.sh   | 17 ++++++++++-----
 .claude/memory/gitlog.md                    | 33 ++++++++++++++++++-----------
 .claude/memory/observations.md              | 12 +++++++----
 .claude/memory/plan.md                      |  2 +-
 .claude/procedures/_index.md                |  5 +++++
 .claude/strategies/composable_results.md    |  4 +++-
 .claude/strategies/event_surprise.md        | 15 ++++++-------
 .claude/strategies/stochrsi_enhanced_gdx.md | 13 ++++++------
 .claude/strategies/stochrsi_enhanced_gld.md | 28 ++++++------------------
 .claude/strategies/stochrsi_enhanced_iau.md | 11 +++++-----
 .claude/strategies/stochrsi_enhanced_slv.md | 13 ++++++------
 CLAUDE.md                                   | 14 ++++++++----
 14 files changed, 120 insertions(+), 77 deletions(-)

----
**2026-03-25** — chore: sync hooks with global CLAUDE.md — graduation enforcement
Added Check 4 to git-save-guard (blocks if Graduation Candidates section non-empty). Updated openbrain-audit-reminder to structured KEEP/GRADUATE/REMOVE triage plus domain file revision check. Created plan-domain-reminder.sh (fires on plan.md edits, prompts domain file review). Registered new hook in settings.json. Added Graduation Candidates section to observations.md and Domain files consulted line to plan.md.

 .claude/hooks/git-save-guard.sh           | 28 ++++++++++++++++++++++++++++
 .claude/hooks/openbrain-audit-reminder.sh | 22 +++++++++++++++++-----
 .claude/hooks/plan-domain-reminder.sh     | 31 +++++++++++++++++++++++++++++++
 .claude/memory/gitlog.md                  | 29 +++++++++++++++--------------
 .claude/memory/observations.md            |  6 ++++++
 .claude/memory/plan.md                    |  1 +
 .claude/settings.json                     | 18 ++++++++++++++++++
 7 files changed, 116 insertions(+), 19 deletions(-)

----
**2026-03-25** — chore: Mar 25 audit — 1 GDX trade
Mar 25: GDX only trade. Buy .80, trail updated to .49 after 1 bar, server stop fired .48 (below entry). GLD/IAU/SLV flat. Alpaca audit matched: 3 records per trailing-stop trade (buy + initial stop canceled + trail stop filled) — confirmed normal pattern.

 .claude/memory/gitlog.md       | 36 ++++++++++++++++++------------------
 .claude/memory/observations.md |  1 +
 2 files changed, 19 insertions(+), 18 deletions(-)

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

