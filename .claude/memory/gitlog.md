# Recent Git History

> Auto-generated on git save. Do not edit manually.

----
**2026-04-03** — fix: calibration command corrected — long_only:true required, trading_hours:[13.5,20] exact gate match

 .claude/calibration/calibration-notes.md       | 42 +++++++++++++++++---------
 .claude/calibration/live-trade-log.md          |  1 +
 backend/strategies/stoch_rsi_mean_reversion.py |  4 ++-
 3 files changed, 31 insertions(+), 16 deletions(-)

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

----
**2026-04-02** — chore: extend analysis to Apr 2 — 50 trades, K 80% / TS 16%, GLD TS win first same-day

 .claude/calibration/live-trade-log.md | 26 ++++++++++++++------------
 .claude/memory/gitlog.md              | 20 ++++++++------------
 2 files changed, 22 insertions(+), 24 deletions(-)

----
**2026-04-02** — chore: log Apr 2 trades — 6 trades, 5 profitable, GLD TS fire in profit

 .claude/calibration/live-trade-log.md | 17 +++++++++++++++++
 .claude/memory/gitlog.md              | 19 ++++++++-----------
 2 files changed, 25 insertions(+), 11 deletions(-)

----
**2026-04-02** — chore: migrate memory harness to v3

 .claude/calibration/calibration-notes.md       |  43 +++++-----
 .claude/calibration/live-trade-log.md          | 114 +++++++++----------------
 .claude/hooks/git-save-guard.sh                |  42 ++-------
 .claude/hooks/load-context.sh                  |   3 +-
 .claude/hooks/openbrain-audit-reminder.sh      |  22 ++---
 .claude/hooks/plan-domain-reminder.sh          |  31 -------
 .claude/integrations/alpaca-mcp.md             |  68 ++++++---------
 .claude/memory/gitlog.md                       |  37 +++++---
 .claude/memory/observations.md                 |  74 ++--------------
 .claude/memory/plan.md                         |  41 ---------
 .claude/procedures/memory-harness-migration.md |  11 +++
 .claude/settings.json                          |  18 ----
 .claude/strategies/composable-results.md       |  18 ++--
 .claude/strategies/event-surprise.md           |  46 +++++-----
 .claude/strategies/stochrsi-enhanced-gdx.md    |  26 +++---
 .claude/strategies/stochrsi-enhanced-gld.md    |  46 +++++-----
 .claude/strategies/stochrsi-enhanced-iau.md    |  28 +++---
 .claude/strategies/stochrsi-enhanced-slv.md    |  26 +++---
 .claude/strategies/stochrsi-enhanced-xle.md    |  33 ++++---
 CLAUDE.md                                      |   5 +-
 20 files changed, 264 insertions(+), 468 deletions(-)

----
**2026-04-02** — chore: log Apr 1 trades, correct Mar 31 T3 stop note
Added Apr 1 trade log entry: SLV 2 trades (overnight SS exit -0.259/share, same-day TS exit -0.078/share), GLD/IAU/GDX 0 trades. Also corrected Mar 31 T3 overnight hold note — the $67.50 stop at 21:10 UTC was REJECTED by Alpaca (market closed), not placed as originally recorded. Confirmed from Alpaca UI during the overnight stop gap investigation.

 .claude/calibration/live-trade-log.md | 17 +++++++++++++++--
 .claude/memory/gitlog.md              | 25 ++++++++++++-------------
 .claude/memory/observations.md        |  2 +-
 3 files changed, 28 insertions(+), 16 deletions(-)

----
**2026-04-02** — fix: overnight stop gap — re-place DAY stop at market open
DAY stops expire at 20:00 UTC. Startup sync may fail post-market (rejected by Alpaca), leaving position unprotected at next market open. Loop now re-places stop before on_bar if pending_stop_order_id is None. Gap existed since Mar 4 — cedc865 noted the intention but never built it. Discovered via rejected stop order in Alpaca UI (Mar 31 21:10 UTC). Also logged Apr 1 audit: SLV 2 trades, GLD/IAU/GDX 0 trades, all bots flat EOD.

 .claude/memory/gitlog.md       | 45 +++++++++++++++++++++++-------------------
 .claude/memory/observations.md |  8 ++++++--
 CLAUDE.md                      |  3 ++-
 3 files changed, 33 insertions(+), 23 deletions(-)

