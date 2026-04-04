# Recent Git History

> Auto-generated on git save. Do not edit manually.

----
**2026-04-04** — chore: add pre-fix notes to all year-by-year tables across strategy domain files

 .claude/strategies/stochrsi-enhanced-gdx.md | 2 ++
 .claude/strategies/stochrsi-enhanced-gld.md | 2 ++
 .claude/strategies/stochrsi-enhanced-iau.md | 2 ++
 .claude/strategies/stochrsi-enhanced-slv.md | 2 ++
 4 files changed, 8 insertions(+)

----
**2026-04-04** — chore: sweep all domain files — fix stale narrative figures post stop-check correction

 .claude/memory/gitlog.md                    | 27 +++++++++++++++------------
 .claude/strategies/stochrsi-enhanced-gdx.md |  4 ++--
 .claude/strategies/stochrsi-enhanced-gld.md | 20 ++++++++++----------
 .claude/strategies/stochrsi-enhanced-iau.md |  8 ++++----
 .claude/strategies/stochrsi-enhanced-slv.md |  6 +++---
 .claude/strategies/stochrsi-enhanced-xle.md | 10 +++++-----
 CLAUDE.md                                   |  2 +-
 7 files changed, 40 insertions(+), 37 deletions(-)

----
**2026-04-04** — chore: document stop slippage analysis and K/TS fix in calibration notes

 .claude/calibration/calibration-notes.md |  4 ++--
 .claude/calibration/live-trade-log.md    |  4 ++--
 .claude/memory/gitlog.md                 | 18 +++++++++---------
 3 files changed, 13 insertions(+), 13 deletions(-)

----
**2026-04-04** — chore: update strategy domain files and CLAUDE.md with corrected backtest figures post stop-check fix

 .claude/memory/gitlog.md                    | 20 ++++++----
 .claude/strategies/stochrsi-enhanced-gdx.md | 22 ++++++-----
 .claude/strategies/stochrsi-enhanced-gld.md | 57 +++++++++++++++--------------
 .claude/strategies/stochrsi-enhanced-iau.md | 30 ++++++++-------
 .claude/strategies/stochrsi-enhanced-slv.md | 22 ++++++-----
 CLAUDE.md                                   |  8 ++--
 6 files changed, 85 insertions(+), 74 deletions(-)

----
**2026-04-04** — fix: backtest stop-check ordering bug — use pre-ratchet stop level for intrabar low/high check

 .claude/memory/gitlog.md                       | 18 +++++++++---------
 backend/strategies/stoch_rsi_mean_reversion.py | 19 ++++++++++++-------
 2 files changed, 21 insertions(+), 16 deletions(-)

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

