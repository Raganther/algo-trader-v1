# Recent Git History

> Auto-generated on git save. Do not edit manually.

----
**2026-04-04** — fix: backtest stop-check ordering bug — use pre-ratchet stop level for intrabar low/high check

 backend/strategies/stoch_rsi_mean_reversion.py | 19 ++++++++++++-------
 1 file changed, 12 insertions(+), 7 deletions(-)

----
**2026-04-03** — chore: update CLAUDE.md — Apr 3 bar-completion guard fix documented

 .claude/memory/gitlog.md | 18 +++++++++---------
 CLAUDE.md                |  1 +
 2 files changed, 10 insertions(+), 9 deletions(-)

----
**2026-04-03** — fix: bar-completion guard — skip generate_signals on partial bar, deduplicate deferral log

 .claude/memory/gitlog.md | 36 +++++++++---------------------------
 backend/runner.py        | 21 ++++++++++++++-------
 2 files changed, 23 insertions(+), 34 deletions(-)

----
**2026-04-03** — fix: bar-completion guard — skip on_bar for partial session-open bar at market open

 .claude/memory/gitlog.md | 22 ++++++++++------------
 backend/runner.py        | 22 +++++++++++++++++++---
 2 files changed, 29 insertions(+), 15 deletions(-)

----
**2026-04-03** — chore: diagnose 0.90x trade count gap — partial market-open bar confirmed as cause

 .claude/calibration/calibration-notes.md |  4 ++--
 .claude/memory/gitlog.md                 | 19 +++++++++----------
 backend/runner.py                        |  9 ++++++++-
 3 files changed, 19 insertions(+), 13 deletions(-)

----
**2026-04-03** — fix: calibration command corrected — long_only:true required, trading_hours:[13.5,20] exact gate match

 .claude/calibration/calibration-notes.md       | 42 +++++++++++++++++---------
 .claude/calibration/live-trade-log.md          |  1 +
 .claude/memory/gitlog.md                       | 25 ++++++---------
 backend/strategies/stoch_rsi_mean_reversion.py |  4 ++-
 4 files changed, 41 insertions(+), 31 deletions(-)

----
**2026-04-03** — chore: restructure calibration files to v3 format — add Plan and Open Questions sections

 .claude/calibration/calibration-notes.md |  8 ++++++++
 .claude/calibration/live-trade-log.md    | 17 +++++++++++++++++
 .claude/memory/gitlog.md                 | 20 ++++++++++----------
 3 files changed, 35 insertions(+), 10 deletions(-)

----
**2026-04-03** — chore: add signal vs full-edge distinction to analysis — K-exit confirms signal, not full validated edge

 .claude/calibration/live-trade-log.md |  8 ++++++++
 .claude/memory/gitlog.md              | 20 ++++++++------------
 2 files changed, 16 insertions(+), 12 deletions(-)

