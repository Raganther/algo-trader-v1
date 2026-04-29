# Recent Git History

> Auto-generated on git save. Do not edit manually.

----
**2026-04-29** — Apr 29 XBI gap-through-stop bug — log + fix outcome documented. forward-test-log.md: new dated section for Apr 29 XBI emergency-market exit (-$313.61), new exit type EM (emergency market, gap-through-stop guard). Realised P&L summary updated to 13 closed trades, total -$1,142.39. Memory recurring_bug_pattern.md: extended from one TIF bug to three closely-related failure modes — TIF mismatch (resolved Apr 17), gap-through-stop on re-placement (resolved today via defensive guard in [SYNC] + [LOOP] paths), and a 'where to look' index for future stop-related debugging. Outstanding: root cause of why pending_stop_order_id was None despite live GTC stop — defensive fix is sufficient for safety; investigation still open.

 .claude/calibration/forward-test-log.md | 29 ++++++++++++++++++++++++++++-
 1 file changed, 28 insertions(+), 1 deletion(-)

----
**2026-04-29** — fix: extend gap-through-stop guard to [SYNC] startup path. Same logic as the [LOOP] guard from the previous commit, applied at bot-restart sync time so we don't sit unprotected for up to 15 min waiting for the next bar's [LOOP] iteration. Changes runner.py:672-715 — if reconstructed SL is on the wrong side of current price, place market exit + reset strategy state to flat instead of attempting a stop that Alpaca will reject.

 .claude/memory/gitlog.md | 19 +++++++--------
 backend/runner.py        | 62 +++++++++++++++++++++++++++++++++++-------------
 2 files changed, 54 insertions(+), 27 deletions(-)

----
**2026-04-29** — fix: gap-through-stop guard in DAY-stop recovery path. When a position is held overnight and price gaps through the intended stop level, Alpaca rejects the new stop order (stop above market for longs, below for shorts), leaving the bot in a retry loop with no active protection. Surfaced today on XBI: long entry .25 Apr 28, GTC stop $130.85 was canceled by the gap-recovery path at session re-open, intended re-place at $130.68 rejected because price had gapped to $130.30. Manual safety stop placed at $128.50 GTC for the live position; code fix prevents recurrence. Behavior change in runner.py:943-983: before cancel-and-replace, check whether intended stop is already breached by current price (long: SL >= price; short: SL <= price). If breached, cancel orders + place market exit (the stop's intent 'exit if we get here' is already satisfied) and reset strategy state. Otherwise, original cancel-and-replace path runs unchanged. Does NOT fix the upstream question of why pending_stop_order_id was None despite a live GTC stop — defensive guard means we no longer end up unprotected even when the gate spuriously triggers.

 .claude/memory/gitlog.md | 17 +++++++-------
 backend/runner.py        | 60 ++++++++++++++++++++++++++++++++++++------------
 2 files changed, 53 insertions(+), 24 deletions(-)

----
**2026-04-29** — regime-aware asset rotation captured as strategic direction: combines Apr 28 generalisation + Apr 29 regime-preference into 'rotate across a wide universe' thesis. New roadmap section with 7 items, gating prerequisites, and the cheap first step (30-asset observational scan). Bot lineup framing updated to clarify 'no more fixed bots; rotation is the next strategic move.' regime-analysis.md notes the classifier's highest-leverage application is selection not sizing. Memory entry captures cross-session decision context.

 .claude/memory/gitlog.md               | 21 ++++++++++-----------
 .claude/strategies/regime-analysis.md  |  4 +++-
 .claude/strategies/research-roadmap.md | 26 +++++++++++++++++++++++++-
 CLAUDE.md                              |  1 +
 4 files changed, 39 insertions(+), 13 deletions(-)

----
**2026-04-29** — regime preference doc updates from Apr 29 long-window finding: framework is strongest in sustained directional moves (bull or bear, S 2.0-2.6), decent in chop (~1.5), WEAKEST in sharp-top / regime transitions (0.8-1.1 with elevated DD). Counter-intuitive for a mean-reversion-named strategy. Updates: regime-analysis.md (revised strategy-implication column), research-roadmap.md (superseded the 'downsize in TRENDING_DOWN' idea, promoted sharp-top/transition detector), CLAUDE.md (added regime preference bullet), long-window-validation.md (added 18-cell ranking section). Original 'downsize in bear' rule was wrong — bear is a strong regime; transition is the dangerous one.

 .claude/memory/gitlog.md                     | 24 +++++++++++-------------
 .claude/strategies/long-window-validation.md | 26 ++++++++++++++++++++++++++
 .claude/strategies/regime-analysis.md        | 21 +++++++++++++++------
 .claude/strategies/research-roadmap.md       |  3 ++-
 CLAUDE.md                                    |  1 +
 5 files changed, 55 insertions(+), 20 deletions(-)

----
**2026-04-29** — long-window validation via HistData spot proxies — 17 yr XAUUSD, 16 yr XAGUSD, 13 yr WTIUSD backtested through real bear regimes. Headline: framework HELD in 2013-15 metals bear (gold S=1.44, silver S=2.04, both better than B&H by 2+ Sharpe) and 2014-16 oil collapse (S=1.11). Apr 28 inversion-test prediction (metals Sharpe drops to ~1/3 in non-bull regime) did NOT reproduce on real history. Spot-proxy 2020+ Sharpe ~1.5 vs ETF Sharpe ~2.5 — 0.8-1.0 gap suggests ETF microstructure premium; CLAUDE.md sizing guidance reaffirmed at 1.0-1.5. New: HistDataLoader + fetcher + long_window_validation.py orchestrator + domain doc.

 .claude/memory/gitlog.md                     |  32 ++--
 .claude/strategies/long-window-validation.md |  62 +++++++
 .claude/strategies/research-roadmap.md       |   3 +-
 CLAUDE.md                                    |   3 +-
 backend/analysis/long_window_validation.py   | 254 +++++++++++++++++++++++++++
 backend/engine/histdata_loader.py            | 195 ++++++++++++++++++++
 backend/runner.py                            |   9 +-
 scripts/fetch_price_data_histdata.py         |  79 +++++++++
 8 files changed, 616 insertions(+), 21 deletions(-)

----
**2026-04-29** — doc updates for correlation-aware sizing V1: roadmap gating language updated (IWM gate downgraded from 'gated on sizing landing' to 'gated on live verification'), Live Observation Framework adds [CORR-SIZE] discount audit measurement, forward-test-log records what to capture on each post-Apr-29 entry

 .claude/calibration/forward-test-log.md | 17 +++++++++++++++++
 .claude/memory/gitlog.md                | 20 +++++++++-----------
 .claude/strategies/research-roadmap.md  | 11 ++++++-----
 3 files changed, 32 insertions(+), 16 deletions(-)

----
**2026-04-29** — correlation-aware sizing V1 — equal-split risk parity discount applied at entry, risk_frac = 0.02 / N where N = cluster peers held + self. Hardcoded clusters (gold/energy/biotech). 13/13 unit tests pass; GLD backtest regression Sharpe 2.48 unchanged (N=1 in single-symbol). Live audit signal: [CORR-SIZE] lines on discounted entries. V1 limitations: race on simultaneous fires, no resize of already-open peers, no shared-timeline backtest validation — accepted.

 .claude/memory/gitlog.md                       |  27 +++----
 .claude/strategies/research-roadmap.md         |   2 +-
 CLAUDE.md                                      |   4 +-
 backend/engine/correlation_sizing.py           |  56 ++++++++++++++
 backend/strategies/stoch_rsi_mean_reversion.py |  22 ++++--
 backend/tests/test_correlation_sizing.py       | 102 +++++++++++++++++++++++++
 6 files changed, 191 insertions(+), 22 deletions(-)

----
**2026-04-28** — Apr 28 — durable framings from post-resolution discussion: bot lineup ≈ 3 independent bets (gold/energy/biotech), capital cap binds at 4 simultaneous positions, IWM is sole valid expansion candidate (gated on correlation sizing), held-out 12 + boundary 4 deprioritised as deployment path, Live Observation Framework added to roadmap + forward-test-log with 4 specific measurements to convert time-passing into real-money confidence.

 .claude/calibration/forward-test-log.md | 16 +++++++++++++++-
 .claude/memory/gitlog.md                | 21 ++++++++++-----------
 .claude/strategies/research-roadmap.md  | 20 +++++++++++++++++++-
 CLAUDE.md                               |  9 ++++++++-
 4 files changed, 52 insertions(+), 14 deletions(-)

----
**2026-04-28** — Apr 28 — edge resolution documentation pass: CLAUDE.md callout updated with Tests 1/2/3 results + resolved model, roadmap Framework Attribution section moved to resolved (with new diagnostic + research items), 8 strategy card status lines updated to 'framework IS the edge (signal decorative); regime-dependence' framing. Three-test edge resolution complete.

 .claude/memory/gitlog.md                    | 29 +++++++++++++++++------------
 .claude/strategies/research-roadmap.md      | 23 +++++++++++++----------
 .claude/strategies/stochrsi-enhanced-gdx.md |  2 +-
 .claude/strategies/stochrsi-enhanced-gld.md |  2 +-
 .claude/strategies/stochrsi-enhanced-iau.md |  2 +-
 .claude/strategies/stochrsi-enhanced-oih.md |  2 +-
 .claude/strategies/stochrsi-enhanced-slv.md |  2 +-
 .claude/strategies/stochrsi-enhanced-xbi.md |  2 +-
 .claude/strategies/stochrsi-enhanced-xle.md |  2 +-
 .claude/strategies/stochrsi-enhanced-xop.md |  2 +-
 CLAUDE.md                                   | 19 ++++++++++++++++---
 11 files changed, 54 insertions(+), 33 deletions(-)

----
**2026-04-28** — Apr 28 — Edge Test 3 + synthesis: GLD inverted Sharpe collapses 2.48→0.85 (real directional edge, regime-dependent), SPY direction-agnostic 1.36→1.53. Three-test resolution: framework IS the edge (Test 2), beats B&H universally (Test 1), but metals edge depends on bull-regime (Test 3). Honest model: position-management framework, not StochRSI mean-reversion. Live bots should size for Sharpe 1.0-1.5 not 2.46.

 .claude/memory/gitlog.md           | 31 ++++----------
 .claude/strategies/research-log.md | 86 ++++++++++++++++++++++++++++++++++++++
 backend/runner.py                  | 19 +++++++++
 3 files changed, 114 insertions(+), 22 deletions(-)

----
**2026-04-28** — Apr 28 — Edge Test 2: fully-random ablation matches/beats validated on 3 of 4 assets (GLD 2.32 vs 2.48, SLV 2.64 vs 2.46, GDX 2.57 vs 2.46, QQQ 2.28 vs 1.45). Framework alone clears Sharpe ≥2.0 with zero signal information. The StochRSI entry + K-cross exit signals are at best neutral, slightly net-negative on average. Framework IS the edge.

 .claude/memory/gitlog.md                       | 29 ++++++------------
 .claude/strategies/research-log.md             | 42 ++++++++++++++++++++++++++
 backend/strategies/stoch_rsi_mean_reversion.py | 16 ++++++++--
 3 files changed, 65 insertions(+), 22 deletions(-)

----
**2026-04-28** — Apr 28 — Edge Test 1: B&H comparison passes cleanly. Strategy beats B&H on all 12 assets by Δ Sharpe +0.46 to +1.94 (median ~+1.4), DD protection 8.5×-26.2×. Framework adds real risk-adjusted value over passive holding.

 .claude/memory/gitlog.md                    |  47 +++++------
 .claude/strategies/research-log.md          |  42 ++++++++++
 backend/analysis/buy_and_hold_comparison.py | 122 ++++++++++++++++++++++++++++
 3 files changed, 188 insertions(+), 23 deletions(-)

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

