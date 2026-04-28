# Recent Git History

> Auto-generated on git save. Do not edit manually.

----
**2026-04-28** — Apr 28 — deploy OIH/XBI/XOP paper bots, e2-small upgrade complete

 CLAUDE.md               | 23 +++++++++++++----------
 scripts/run_oih_test.sh |  9 +++++++++
 scripts/run_xbi_test.sh |  9 +++++++++
 scripts/run_xop_test.sh |  9 +++++++++
 4 files changed, 40 insertions(+), 10 deletions(-)

----
**2026-04-28** — Apr 28 — walk-forward 4/4 passed for OIH/XBI/XOP; promoted from candidate to validated, lineup now 8 assets

 .claude/memory/gitlog.md                    | 22 +++++++++++++---------
 .claude/strategies/research-log.md          |  2 ++
 .claude/strategies/research-roadmap.md      |  4 +++-
 .claude/strategies/stochrsi-enhanced-oih.md | 23 +++++++++++++++++------
 .claude/strategies/stochrsi-enhanced-xbi.md | 25 ++++++++++++++++++-------
 .claude/strategies/stochrsi-enhanced-xop.md | 21 ++++++++++++++++-----
 CLAUDE.md                                   | 12 ++++++------
 7 files changed, 75 insertions(+), 34 deletions(-)

----
**2026-04-28** — Apr 28 — verified all metals/XLE/long-only baselines, discovered OIH/XBI/XOP candidates from forgotten-asset audit, rejected TLT, fixed Apr 4 transcription error

 .claude/memory/gitlog.md                    | 27 ++++++---
 .claude/strategies/research-log.md          | 56 ++++++++++++++++++
 .claude/strategies/research-roadmap.md      | 29 +++++++--
 .claude/strategies/stochrsi-enhanced-gdx.md | 64 ++++++++++++--------
 .claude/strategies/stochrsi-enhanced-gld.md | 68 ++++++++++++---------
 .claude/strategies/stochrsi-enhanced-iau.md | 60 +++++++++++--------
 .claude/strategies/stochrsi-enhanced-oih.md | 91 +++++++++++++++++++++++++++++
 .claude/strategies/stochrsi-enhanced-slv.md | 64 ++++++++++++--------
 .claude/strategies/stochrsi-enhanced-xbi.md | 89 ++++++++++++++++++++++++++++
 .claude/strategies/stochrsi-enhanced-xle.md | 33 +++++------
 .claude/strategies/stochrsi-enhanced-xop.md | 73 +++++++++++++++++++++++
 CLAUDE.md                                   | 33 ++++++++---
 12 files changed, 544 insertions(+), 143 deletions(-)

----
**2026-04-27** — Apr 27 forward-test log — Apr 15-24 validated-params trades, organic short stop fire confirmed, Layer 3 sample 33→41

 .claude/calibration/forward-test-log.md | 177 ++++++++++++++++++++++++++++++++
 .claude/memory/gitlog.md                |  19 ++--
 .claude/strategies/research-roadmap.md  |   4 +-
 AGENTS.md                               | 170 ++++++++++++++++++++++++++++++
 CLAUDE.md                               |   1 +
 5 files changed, 361 insertions(+), 10 deletions(-)

----
**2026-04-23** — chore: Apr 23 regime sizing replay rejects broad multipliers

 .claude/harness-v4.md                              |   1 +
 .claude/memory/gitlog.md                           |  31 ++-
 .claude/strategies/regime-analysis.md              |   4 +-
 .../regime-sizing-portfolio-diagnostic.md          |  49 +++++
 .claude/strategies/research-log.md                 |   2 +
 .claude/strategies/research-roadmap.md             |   2 +-
 CLAUDE.md                                          |   1 +
 backend/analysis/regime_sizing_portfolio.py        | 244 +++++++++++++++++++++
 backend/analysis/stochrsi_regime_performance.py    |  10 +
 9 files changed, 330 insertions(+), 14 deletions(-)

----
**2026-04-23** — chore: align regime diagnostic with harness v4.2

 .claude/harness-v4.md                            |  6 +++++-
 .claude/memory/gitlog.md                         | 19 +++++++++++--------
 .claude/strategies/regime-stochrsi-diagnostic.md |  4 +++-
 CLAUDE.md                                        |  1 +
 backend/analysis/stochrsi_regime_performance.py  |  4 +++-
 5 files changed, 23 insertions(+), 11 deletions(-)

----
**2026-04-23** — chore: Apr 23 regime diagnostic shows partial gradient

 .claude/memory/gitlog.md                         |  21 +-
 .claude/strategies/regime-analysis.md            |   7 +-
 .claude/strategies/regime-stochrsi-diagnostic.md | 100 +++++++
 .claude/strategies/research-log.md               |  23 +-
 .claude/strategies/research-roadmap.md           |   6 +-
 backend/analysis/stochrsi_regime_performance.py  | 365 +++++++++++++++++++++++
 6 files changed, 506 insertions(+), 16 deletions(-)

----
**2026-04-23** — chore: Apr 23 — overnight gap analysis closes single-symbol gap policy, correlation-aware sizing flagged as sole remaining tail risk

 .claude/calibration/calibration-notes.md       |   2 +
 .claude/calibration/gap-distribution.md        |  73 ++++++
 .claude/calibration/live-trade-log.md          |  37 ++-
 .claude/memory/gitlog.md                       |  30 ++-
 .claude/procedures/_index.md                   |   1 -
 .claude/procedures/memory-harness-migration.md |  41 ----
 .claude/strategies/event-surprise.md           |   2 +-
 .claude/strategies/regime-analysis.md          |   4 +-
 .claude/strategies/research-log.md             |  16 +-
 .claude/strategies/research-roadmap.md         |  41 +++-
 .claude/strategies/stochrsi-enhanced-gdx.md    |   2 +-
 .claude/strategies/stochrsi-enhanced-gld.md    |   4 +-
 .claude/strategies/stochrsi-enhanced-iau.md    |   4 +-
 .claude/strategies/stochrsi-enhanced-slv.md    |   6 +-
 CLAUDE.md                                      |   4 +-
 backend/analysis/gap_distribution.py           | 302 +++++++++++++++++++++++++
 16 files changed, 492 insertions(+), 77 deletions(-)

----
**2026-04-21** — chore: migrate to harness v4.2 — single roadmap, retire observations.md, enforce domain purity

 .claude/calibration/calibration-notes.md    |  20 +--
 .claude/calibration/live-trade-log.md       |  19 +--
 .claude/harness-v4.md                       | 138 ++++++++++++++++
 .claude/hooks/git-save-guard.sh             | 237 +++++++++++++++++-----------
 .claude/hooks/load-context.sh               |  35 ++--
 .claude/integrations/alpaca-mcp.md          |  10 +-
 .claude/memory/gitlog.md                    |  65 +++++++-
 .claude/memory/observations.md              |  72 ---------
 .claude/strategies/event-surprise.md        |  12 +-
 .claude/strategies/regime-analysis.md       |  72 +--------
 .claude/strategies/research-roadmap.md      | 106 +++++++++++++
 .claude/strategies/stochrsi-enhanced-xle.md |   7 +-
 CLAUDE.md                                   |  36 ++---
 scripts/git-save.sh                         |  96 +++++++++--
 14 files changed, 576 insertions(+), 349 deletions(-)

----
**2026-04-21** — chore: Apr 21 — validated trail fired in profit (SLV +$283.86), pm2 startup registered, path to real money updated

 .claude/memory/gitlog.md       | 17 ++++++++---------
 .claude/memory/observations.md | 21 +++++++++++----------
 2 files changed, 19 insertions(+), 19 deletions(-)

----
**2026-04-19** — chore: Apr 19 — trail ratcheting confirmed, server migration complete, all files updated

 .claude/hooks/load-context.sh  |  4 ++--
 .claude/memory/gitlog.md       | 20 +++++++++++---------
 .claude/memory/observations.md | 24 ++++++++++++++++--------
 CLAUDE.md                      |  4 ++--
 4 files changed, 31 insertions(+), 21 deletions(-)

----
**2026-04-19** — chore: migrate to algotrader-us (us-east1-b) — update server refs, trail ratcheting confirmed

 .claude/memory/gitlog.md | 20 ++++++++++----------
 CLAUDE.md                |  6 +++---
 2 files changed, 13 insertions(+), 13 deletions(-)

----
**2026-04-17** — chore: Apr 17 update — validated params live, first short confirmed, GTC stop fix deployed

 .claude/memory/gitlog.md       | 64 +++++++++++++++++++++++++++---------------
 .claude/memory/observations.md | 27 ++++++++++--------
 CLAUDE.md                      | 30 ++++++++------------
 3 files changed, 67 insertions(+), 54 deletions(-)

----
**2026-04-17** — fix: switch stop orders to GTC TIF — eliminates overnight expiry gap
DAY stops expire at 20:00 UTC each session. With fractional shares this
was unavoidable (Alpaca rejects GTC for fractional). Whole-share sizing
(deployed Apr 17) removes that constraint — GTC stops now persist across
sessions without daily re-placement.

Root cause of current bug: bots running continuously (3D uptime) never
cleared pending_stop_order_id when DAY stop expired, so the re-placement
guard never triggered. GTC removes the expiry problem entirely.

Co-Authored-By: Claude Sonnet 4.6 <noreply@anthropic.com>

 backend/engine/alpaca_trader.py | 11 ++++-------
 1 file changed, 4 insertions(+), 7 deletions(-)

----
**2026-04-13** — feat: deploy full validated strategy — whole-share sizing + shorts + validated params
- stoch_rsi_mean_reversion.py: math.floor sizing (long + short), skip sub-1-share signals
- alpaca_trader.py: int(qty) for stock market + stop orders
- live_broker.py: unblock short entry in sell(), place buy-stop with pending_stop_side='buy'
- all 4 bot scripts: OB 80/OS 15, ADX 20, 10-bar hold, 2.0 ATR trail after 10 bars, skip Monday, 13:30-20:00 UTC

 backend/engine/alpaca_trader.py                |  4 ++--
 backend/engine/live_broker.py                  | 31 +++++++++++++++++++++++---
 backend/strategies/stoch_rsi_mean_reversion.py | 11 +++++++--
 scripts/run_gdx_test.sh                        |  5 ++---
 scripts/run_gld_test.sh                        |  5 ++---
 scripts/run_iau_test.sh                        |  5 ++---
 scripts/run_slv_test.sh                        |  5 ++---
 7 files changed, 47 insertions(+), 19 deletions(-)

