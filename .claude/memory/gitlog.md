# Recent Git History

> Auto-generated on git save. Do not edit manually.

----
**2026-04-28** — Apr 28 — Edge Test 1: B&H comparison passes cleanly. Strategy beats B&H on all 12 assets by Δ Sharpe +0.46 to +1.94 (median ~+1.4), DD protection 8.5×-26.2×. Framework adds real risk-adjusted value over passive holding.

 .claude/strategies/research-log.md          |  42 ++++++++++
 backend/analysis/buy_and_hold_comparison.py | 122 ++++++++++++++++++++++++++++
 2 files changed, 164 insertions(+)

----
**2026-04-28** — Apr 28 — full domain-file audit: propagate framework-attribution finding to all 8 StochRSI cards, regime cards, calibration logs, CLAUDE.md, and roadmap. Verified Sharpe values now in cards. Headline returns/DD unchanged; interpretation flagged as 'headline confirmed; edge attribution under review' across the board. Critical Path now requires framework ablations + buy-and-hold comparison before real money.

 .claude/calibration/forward-test-log.md            |  4 ++-
 .claude/calibration/live-trade-log.md              |  6 ++--
 .claude/memory/gitlog.md                           | 32 +++++++++++++++-------
 .claude/strategies/regime-analysis.md              |  4 ++-
 .../regime-sizing-portfolio-diagnostic.md          |  4 ++-
 .claude/strategies/regime-stochrsi-diagnostic.md   |  4 ++-
 .claude/strategies/research-roadmap.md             |  2 ++
 .claude/strategies/stochrsi-enhanced-gdx.md        | 10 ++++++-
 .claude/strategies/stochrsi-enhanced-gld.md        | 14 ++++++++--
 .claude/strategies/stochrsi-enhanced-iau.md        | 10 ++++++-
 .claude/strategies/stochrsi-enhanced-oih.md        | 10 ++++++-
 .claude/strategies/stochrsi-enhanced-slv.md        | 10 ++++++-
 .claude/strategies/stochrsi-enhanced-xbi.md        | 10 ++++++-
 .claude/strategies/stochrsi-enhanced-xle.md        | 10 ++++++-
 .claude/strategies/stochrsi-enhanced-xop.md        | 12 ++++++--
 CLAUDE.md                                          | 10 +++++--
 16 files changed, 122 insertions(+), 30 deletions(-)

----
**2026-04-28** — Apr 28 — random-entry control: StochRSI signal is NOT the primary edge. Random entries match validated Sharpe on GLD (2.46 vs 2.48), beat it on QQQ (1.99 vs 1.45). Framework (trail/ADX/sizing/exit) is doing most of the work. Reframes learning #10, opens framework-ablation queue.

 .claude/memory/gitlog.md                       | 18 +++++----
 .claude/strategies/research-log.md             | 51 ++++++++++++++++++++++++++
 .claude/strategies/research-roadmap.md         | 16 ++++++++
 backend/strategies/stoch_rsi_mean_reversion.py | 43 ++++++++++++++++++++++
 4 files changed, 120 insertions(+), 8 deletions(-)

----
**2026-04-28** — Apr 28 — Sharpe instrumentation added to backtester, 16 runs verified: 6 of 8 validated lineup clear ≥2.0 cleanly (GLD/SLV/GDX/OIH/XLE/XBI), IWM is only broad index that passes, GLD/SLV long-only beat full-strategy

 .claude/memory/gitlog.md               | 21 +++++++++--------
 .claude/strategies/research-log.md     | 42 ++++++++++++++++++++++++++++++++++
 .claude/strategies/research-roadmap.md |  6 ++---
 CLAUDE.md                              | 30 +++++++++++++++---------
 backend/engine/backtester.py           | 16 +++++++++++++
 backend/runner.py                      |  1 +
 6 files changed, 93 insertions(+), 23 deletions(-)

----
**2026-04-28** — Apr 28 — boundary verification: SPY/QQQ/IWM/DIA all pass validated recipe, broad-index boundary thesis refuted; real boundary is on driver class (rates), not asset class

 .claude/memory/gitlog.md               | 26 ++++++++-------------
 .claude/strategies/research-log.md     | 42 ++++++++++++++++++++++++++++++++--
 .claude/strategies/research-roadmap.md |  8 +++----
 3 files changed, 53 insertions(+), 23 deletions(-)

----
**2026-04-28** — Apr 28 — held-out generalisation test on 12 novel assets all passed; boundary thesis in question pending SPY/QQQ retest

 .claude/memory/gitlog.md               | 34 ++++++++++----------------
 .claude/strategies/research-log.md     | 44 ++++++++++++++++++++++++++++++++--
 .claude/strategies/research-roadmap.md | 12 +++++++++-
 3 files changed, 66 insertions(+), 24 deletions(-)

----
**2026-04-28** — Apr 28 — deploy OIH/XBI/XOP paper bots, e2-small upgrade complete

 .claude/memory/gitlog.md | 20 +++++++++++---------
 CLAUDE.md                | 23 +++++++++++++----------
 scripts/run_oih_test.sh  |  9 +++++++++
 scripts/run_xbi_test.sh  |  9 +++++++++
 scripts/run_xop_test.sh  |  9 +++++++++
 5 files changed, 51 insertions(+), 19 deletions(-)

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

