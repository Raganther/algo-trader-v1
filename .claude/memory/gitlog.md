# Recent Git History

> Auto-generated on git save. Do not edit manually.

----
**2026-04-11** — chore: update regime-analysis implications — validated params timing, second window caveat, HIGH_VOL sizing rationale, empirical validation gate

 .claude/strategies/regime-analysis.md | 33 ++++++++++++++++++++++-----------
 1 file changed, 22 insertions(+), 11 deletions(-)

----
**2026-04-11** — chore: sync memory and CLAUDE.md — updated sequencing, yfinance script, live test duration, SLV HIGH_VOL figure corrected

 .claude/memory/gitlog.md       | 17 +++++++++--------
 .claude/memory/observations.md |  6 +++---
 CLAUDE.md                      |  6 ++++--
 3 files changed, 16 insertions(+), 13 deletions(-)

----
**2026-04-11** — feat: extend regime history to ETF inception — Yahoo Finance daily bars back to 2004, dedup Alpaca overlap, rerun analysis, update domain file

 .claude/memory/gitlog.md              | 17 ++++---
 .claude/strategies/regime-analysis.md | 93 +++++++++++++++++++++--------------
 scripts/fetch_price_data_yfinance.py  | 82 ++++++++++++++++++++++++++++++
 3 files changed, 146 insertions(+), 46 deletions(-)

----
**2026-04-11** — chore: update sequencing — calibration Mon/Tue, whole-share sizing + shorts before validated params, short trading moved to critical path

 .claude/calibration/calibration-notes.md |  6 +++---
 .claude/memory/gitlog.md                 | 19 ++++++++++---------
 .claude/memory/observations.md           | 24 +++++++++++++++++-------
 .claude/strategies/research-log.md       | 18 ++++++++++--------
 4 files changed, 40 insertions(+), 27 deletions(-)

----
**2026-04-10** — chore: domain/memory audit — fix stale stats, duplicate numbering, XLE gate conflict, compress regime items in research-log

 .claude/calibration/live-trade-log.md       | 16 ++++++++++++++++
 .claude/memory/gitlog.md                    | 19 +++++++++++--------
 .claude/memory/observations.md              | 11 ++++++-----
 .claude/strategies/research-log.md          | 25 ++++++++++---------------
 .claude/strategies/stochrsi-enhanced-xle.md |  2 +-
 5 files changed, 44 insertions(+), 29 deletions(-)

----
**2026-04-10** — chore: add post-Apr-20 regime sizing backtest plan to regime-analysis domain file

 .claude/memory/gitlog.md              | 18 +++++------
 .claude/strategies/regime-analysis.md | 56 +++++++++++++++++++++++++++++++++++
 2 files changed, 64 insertions(+), 10 deletions(-)

----
**2026-04-10** — chore: document regime analysis findings — new domain file, CLAUDE.md updated, observations updated

 .claude/memory/gitlog.md              |  19 +++--
 .claude/memory/observations.md        |   2 +
 .claude/strategies/regime-analysis.md | 154 ++++++++++++++++++++++++++++++++++
 CLAUDE.md                             |   1 +
 4 files changed, 167 insertions(+), 9 deletions(-)

----
**2026-04-10** — feat: regime classifier — daily bar fetch, RegimeClassifier module, analyse_regimes script

 .claude/memory/gitlog.md     |  22 ++++-----
 backend/database.py          |  67 +++++++++++++++++++++++++
 backend/indicators/regime.py | 108 ++++++++++++++++++++++++++++++++++++++++
 scripts/analyse_regimes.py   | 114 +++++++++++++++++++++++++++++++++++++++++++
 scripts/fetch_price_data.py  |  33 ++++++++-----
 5 files changed, 322 insertions(+), 22 deletions(-)

