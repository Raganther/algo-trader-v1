# Recent Git History

> Auto-generated on git save. Do not edit manually.

----
**2026-06-16** — Fix position desync accumulation bug (GLD short → 464sh / 8x cap)
Root cause: GLD bot's believed direction inverted vs broker (likely a
cancel-vs-fill race during May 22/26-27 churn), then never re-synced —
startup SYNC is the only full reconciliation and the process ran 34 days
without restart. The in-loop check only caught 'believe held, broker flat'
(current_pos==0), never an opposite-sign or believed-flat-but-holding
mismatch. The stop-replacement block then sized a protective stop off
abs(broker position) but chose the SIDE from the believed direction; with
belief inverted it placed a SELL stop on an actual short, doubling the
short on every fill (58 -> 116 -> 232 -> 464, ~193% notional, naked).

Fix in backend/runner.py run_live_trading loop:
1. Bidirectional reconciliation after broker.refresh(): if broker sign
   contradicts belief (opposite sign, or believed-flat-but-holding), latch
   _desync_halt, cancel resting orders (kills the amplifier), alert, and
   skip all order logic until a human restart re-runs SYNC.
2. Stop-replacement now derives side from the ACTUAL broker position sign,
   not the belief; refuses any belief-sided stop that would increase exposure.
3. Heartbeat renders DESYNC-HALT so the condition is visible in pm2 logs.

Live remediation done separately: gld-test stopped, 464 short flattened via
market-on-open order. pm2 restart all pending after the flatten fills.

Co-Authored-By: Claude Opus 4.8 <noreply@anthropic.com>

 backend/runner.py | 58 ++++++++++++++++++++++++++++++++++++++++++++++++++++---
 1 file changed, 55 insertions(+), 3 deletions(-)

----
**2026-05-22** — Rename strategy StochRSIMeanReversion -> TrendFramework
Renamed the strategy to reflect what it actually is. The Apr 28
framework-attribution work showed the StochRSI signal is decorative and the
position-management framework (trend-favouring) carries the edge -- so
MeanReversion was misleading on both counts.

Code: backend/strategies/stoch_rsi_mean_reversion.py -> trend_framework.py;
class StochRSIMeanReversionStrategy -> TrendFrameworkStrategy; runner.py
STRATEGY_MAP gains canonical key TrendFramework and keeps StochRSIMeanReversion
as a legacy alias. The 7 live bot run scripts still pass the old name and
resolve via the alias -- live trading byte-unchanged. Verified: identical
backtest under both keys.

Docs: 8 per-asset cards renamed stochrsi-enhanced-*.md -> trend-framework-*.md;
references updated across 37 .claude domain files + CLAUDE.md; git-save.sh
domain checklist updated.

Not renamed (separate subsystems, pending a decision): AGENTS.md / .Codex
parallel harness (stale), frontend card registry, docs/ pinescript.

Co-Authored-By: Claude Opus 4.7 <noreply@anthropic.com>

 .claude/calibration/audit-hwm-delay-mechanism.md   |  4 +-
 .claude/calibration/calibration-journal.md         | 10 +--
 .../calibration/live-vs-backtest-iau-diagnostic.md |  6 +-
 .claude/harness-v4.md                              | 14 ++--
 .claude/memory/gitlog.md                           | 80 +++++++++++++++++++---
 .claude/strategies/long-window-validation.md       |  2 +-
 .claude/strategies/portfolio-runner-baseline.md    |  2 +-
 .claude/strategies/portfolio-runner-cap-shrink.md  |  6 +-
 .../portfolio-runner-lineup-selection.md           |  2 +-
 .claude/strategies/portfolio-runner-rotation-v1.md |  2 +-
 .../regime-sizing-portfolio-diagnostic.md          |  2 +-
 .claude/strategies/regime-stochrsi-diagnostic.md   |  4 +-
 .claude/strategies/research-log.md                 | 22 +++---
 .claude/strategies/research-roadmap.md             | 24 +++----
 .claude/strategies/small-capital-deployment.md     |  2 +-
 .claude/strategies/trail-anchor-hwm.md             |  6 +-
 ...hrsi-enhanced-gdx.md => trend-framework-gdx.md} |  6 +-
 ...hrsi-enhanced-gld.md => trend-framework-gld.md} | 10 +--
 ...hrsi-enhanced-iau.md => trend-framework-iau.md} |  6 +-
 ...hrsi-enhanced-oih.md => trend-framework-oih.md} |  8 +--
 ...hrsi-enhanced-slv.md => trend-framework-slv.md} |  8 +--
 ...hrsi-enhanced-xbi.md => trend-framework-xbi.md} |  8 +--
 ...hrsi-enhanced-xle.md => trend-framework-xle.md} |  4 +-
 ...hrsi-enhanced-xop.md => trend-framework-xop.md} |  6 +-
 CLAUDE.md                                          | 48 ++++++-------
 backend/analysis/audit_adx_filter_exit_block.py    |  6 +-
 backend/analysis/audit_hwm_delay_sensitivity.py    |  4 +-
 backend/analysis/long_window_validation.py         |  4 +-
 backend/optimizer/enhancement_sweep.py             |  4 +-
 backend/optimizer/pipeline.py                      |  4 +-
 backend/optimizer/run_sweep.py                     |  4 +-
 backend/optimizer/trade_analysis.py                |  4 +-
 backend/runner.py                                  |  7 +-
 backend/scripts/event_trade_analysis.py            |  4 +-
 backend/strategies/hybrid_regime.py                |  4 +-
 backend/strategies/hybrid_regime_v2.py             |  4 +-
 backend/strategies/regime_gated_stoch.py           |  4 +-
 backend/strategies/stoch_rsi_limit.py              |  4 +-
 backend/strategies/stoch_rsi_next_open.py          |  4 +-
 backend/strategies/stoch_rsi_quant.py              |  4 +-
 ...ch_rsi_mean_reversion.py => trend_framework.py} | 14 +++-
 scripts/git-save.sh                                |  6 +-
 scripts/run_focused_tests.py                       |  2 +-
 scripts/run_validation.py                          | 12 ++--
 scripts/window_backtest.py                         |  4 +-
 45 files changed, 235 insertions(+), 160 deletions(-)

----
**2026-05-21** — ADX-filter exit-block bug — flip default to entry_only, pin live bots, re-baseline
Default adx_filter_mode flipped all -> entry_only in stoch_rsi_mean_reversion.py;
the May 8 bug fix is now the codebase default. All 7 live run scripts explicitly
pinned to adx_filter_mode=all so live trading is byte-unchanged pending a
deliberate deploy decision (live bots not restarted; cloud code synced only).

Driven by the May 20 matched-window live-vs-backtest comparison: over the 5-week
verified-params tape the buggy all-mode backtest (+8,978) has zero predictive
value for live (-653); the entry_only backtest (+372) predicts live within noise.

portfolio-runner-baseline.md re-run under the fix: +212.28% / 3.72 / 2.06% /
4486 trades (was buggy +424.09% / 4.95 / 3.41% / 4344).

New scripts/window_backtest.py reproducer for the day-14/30/60 live-vs-backtest
gates. Docs updated: calibration-journal (May 20 + May 21 entries), research-log,
research-roadmap, CLAUDE.md. Remaining buggy-mode re-runs pending: cap-shrink,
small-cap, rotation.

Co-Authored-By: Claude Opus 4.7 <noreply@anthropic.com>

 .claude/calibration/calibration-journal.md      |  50 ++++++++++-
 .claude/memory/gitlog.md                        |  51 ++++++++---
 .claude/strategies/portfolio-runner-baseline.md |  49 +++++------
 .claude/strategies/research-log.md              |  20 ++++-
 .claude/strategies/research-roadmap.md          |   4 +-
 CLAUDE.md                                       |   3 +-
 backend/strategies/stoch_rsi_mean_reversion.py  |  16 ++--
 scripts/run_gdx_test.sh                         |   2 +-
 scripts/run_gld_test.sh                         |   2 +-
 scripts/run_iau_test.sh                         |   2 +-
 scripts/run_oih_test.sh                         |   2 +-
 scripts/run_slv_test.sh                         |   2 +-
 scripts/run_xbi_test.sh                         |   2 +-
 scripts/run_xop_test.sh                         |   2 +-
 scripts/window_backtest.py                      | 108 ++++++++++++++++++++++++
 15 files changed, 259 insertions(+), 56 deletions(-)

----
**2026-05-13** — Fix trailing-stop idempotency — broker no-op when rounded stop price unchanged
GDX May 12 audit revealed 4 cancel+replace cycles all at $96.92.
Root cause: strategy stores current_sl as raw float, but
alpaca_trader.place_stop_order rounds to $0.01. Successive bars
produce tiny float deltas that pass the strategy's > / < check but
round to identical broker prices, triggering wasted cancel+replace
round-trips with no actual stop change.

Fix: LiveBroker.update_stop_order now early-returns when the rounded
new_stop_price matches rounded _last_stop_price. Single-line guard
at the broker boundary applies to all strategies regardless of
trail_anchor or trail_atr settings.

SLV single-ratchet anomaly investigated and confirmed NOT a bug —
pm2 logs show all 32 May 11 fifteen-minute bars processed; HWM-ATR
trail formula correctly stayed below initial $72.15 stop until the
final bar (expanding-volatility uptrend kept trail wide by design).

 .claude/memory/gitlog.md      | 35 ++++++++++++++++++++++++-----------
 backend/engine/live_broker.py |  7 +++++++
 2 files changed, 31 insertions(+), 11 deletions(-)

----
**2026-05-10** — May 10 lineup-selection — pruning closed, 7-bot lineup wins, domain sweep
Tested three trimmed lineups vs the 7-bot HWM+entry_only baseline (Sharpe 4.17).
Run A (4-bot best-per-cluster GLD/SLV/OIH/XBI): 3.79.
Run B (5-bot drop GDX+XOP): 3.87.
Run C (6-bot drop GDX): 4.01.

Sharpe is monotonic with bot count — each additional bot adds +0.10-0.15 via
diversification. All trimmed lineups fail the decision rule (Sharpe branch:
lose 0.16-0.38; DD branch: best -0.13pp, far short of 1pp bar).

Verdict: keep the 7-bot lineup. Even per-asset losers GDX (1.46) and XOP (1.32)
add net positive at portfolio level. The May 9 per-asset 2.0 Sharpe bar is a
candidate-addition screen, not a prune threshold. Closes the lineup-pruning
research direction.

Next experiment promoted: per-bot cap-shrink under entry_only. Apr 30 PM
+0.45 Sharpe finding (4.95 -> 5.40 on 8 bots * 12.5%) needs re-validation
under bug fix.

Domain sweep: new portfolio-runner-lineup-selection.md; per-asset cards
(GDX/XOP/IAU/XBI/OIH) get May 10 keep-in-lineup banners; redundant May 7
caveats removed from all 8 cards. Status board in calibration-journal updated
to mark tripwires shipped and lineup-pruning resolved. audit-hwm-delay-mechanism
Live-tripwires section superseded note added. trail-anchor-hwm forward-test-reset
section refreshed. CLAUDE.md domain-file list gains lineup-selection pointer.

 .claude/calibration/audit-hwm-delay-mechanism.md   |   7 +-
 .claude/calibration/calibration-journal.md         |  21 ++++-
 .claude/memory/gitlog.md                           |  72 ++++++++++----
 .../portfolio-runner-lineup-selection.md           | 105 +++++++++++++++++++++
 .claude/strategies/research-log.md                 |  25 ++++-
 .claude/strategies/research-roadmap.md             |   7 +-
 .claude/strategies/stochrsi-enhanced-gdx.md        |   6 +-
 .claude/strategies/stochrsi-enhanced-gld.md        |   4 +-
 .claude/strategies/stochrsi-enhanced-iau.md        |   6 +-
 .claude/strategies/stochrsi-enhanced-oih.md        |   6 +-
 .claude/strategies/stochrsi-enhanced-slv.md        |   4 +-
 .claude/strategies/stochrsi-enhanced-xbi.md        |   6 +-
 .claude/strategies/stochrsi-enhanced-xle.md        |   4 +-
 .claude/strategies/stochrsi-enhanced-xop.md        |   6 +-
 .claude/strategies/trail-anchor-hwm.md             |  29 +++---
 CLAUDE.md                                          |   3 +
 16 files changed, 237 insertions(+), 74 deletions(-)

----
**2026-05-09** — May 9 calibration update — tripwires recalibrated, HWM A/B + per-asset Sharpes re-run under entry_only
Tripwire anchor 5.73 → 4.0 ±0.5 in live_performance_report.py (bars 1.8/2.5/3.0
at 30/60/90d, ~2σ below lower-band edge given Sharpe SE ≈ 1/sqrt(days)).

HWM A/B re-run under adx_filter_mode='entry_only': close 3.72 → HWM 4.17,
Δ +0.45 Sharpe (vs +0.78 buggy). About 58% of the buggy-mode lift survives
bug correction. Decision-rule still passes; HWM stays live on all 7 bots.
The '+0.78 ≈ 0.7 delay-artifact identity' framing is dead.

Per-asset Sharpe table refresh under entry_only (close-anchored, single-symbol):
only GLD (2.28) and SLV (2.19) clear the 2.0 quality bar at the per-asset level.
GDX (2.46→1.46) and XBI (2.18→1.18) are the heaviest bug-beneficiaries.
Portfolio Sharpe (4.17) remains much higher than per-asset average due to
cross-asset diversification — the lineup is a portfolio, not 8 standalone bots.

Domain-file sweep: research-roadmap, research-log, calibration-journal,
trail-anchor-hwm, audit-hwm-delay-mechanism, live-vs-backtest-iau-diagnostic,
long-window-validation, all 8 per-asset cards, CLAUDE.md validated-edges
table — all updated with May 9 figures and bug-corrected interpretation.

 .claude/calibration/audit-hwm-delay-mechanism.md   |  6 +-
 .claude/calibration/calibration-journal.md         | 36 ++++++++++
 .../calibration/live-vs-backtest-iau-diagnostic.md |  4 +-
 .claude/memory/gitlog.md                           | 81 +++++++++++-----------
 .claude/strategies/long-window-validation.md       |  2 +-
 .claude/strategies/research-log.md                 | 40 ++++++++++-
 .claude/strategies/research-roadmap.md             |  8 +--
 .claude/strategies/stochrsi-enhanced-gdx.md        |  4 +-
 .claude/strategies/stochrsi-enhanced-gld.md        |  4 +-
 .claude/strategies/stochrsi-enhanced-iau.md        |  4 +-
 .claude/strategies/stochrsi-enhanced-oih.md        |  4 +-
 .claude/strategies/stochrsi-enhanced-slv.md        |  4 +-
 .claude/strategies/stochrsi-enhanced-xbi.md        |  4 +-
 .claude/strategies/stochrsi-enhanced-xle.md        |  4 +-
 .claude/strategies/stochrsi-enhanced-xop.md        |  4 +-
 .claude/strategies/trail-anchor-hwm.md             | 14 +++-
 CLAUDE.md                                          | 22 +++---
 backend/analysis/live_performance_report.py        | 45 ++++++------
 18 files changed, 200 insertions(+), 90 deletions(-)

----
**2026-05-08** — ADX-filter exit-block bug — discovered, quantified, parameterized fix shipped behind opt-in flag
Strategy bug found in stoch_rsi_mean_reversion.py:211-239 — `if current_adx > adx_threshold: return` exits on_data early when ADX is high. Intent was to block new entries during trends; actual effect blocks stop checks (line 242), entry block (line 269), AND signal-exit blocks (lines 428, 445). Trail-update runs before the filter so trails ratchet, but exits cannot fire mid-trade in high-ADX regimes. Live partially escapes via server-side Alpaca stops + K-exits firing on transient ADX dips; backtest cannot escape.

Discovery trigger: investigating why backtest didn't reproduce the live OIH +$22.53 short (May 5 entry, May 8 K-exit). Backtest fired the same entry but couldn't exit through May 6-8 even when K dropped to 0.0.

A vs C audit (long-window 7-bot, $94k, 2020-07 → 2026-04):
- A 'all' (buggy): +424.09% / Sharpe 4.95 / DD 3.41% / 4344 trades
- C 'entry_only' (fix): +212.28% / Sharpe 3.72 / DD 2.06% / 4486 trades
- Bug contributes ~50% of headline return and ~1.23 Sharpe; per-symbol P&L drops uniformly across the lineup (effect is structural)

Parameterized fix shipped: new `adx_filter_mode` parameter on stoch_rsi_mean_reversion. Default 'all' preserves prior backtests byte-identical. 'entry_only' is the proper fix — ADX gate blocks new entries only, stops and signal-exits run regardless. Live bots unchanged. Strategic decision deferred — needs full A/B re-suite (validated edges, HWM A/B, cap-shrink, small-cap) under entry_only before deciding whether to flip default + deploy live.

Implications cascading through the calibration journey:
- All validated-edges per-asset Sharpes (GLD 2.48, IAU 1.95, etc.) are upper bounds — true Sharpes lower
- HWM A/B (+0.78 lift, May 7) was computed under bug — direction preserved, magnitude needs re-run
- May 7-8 'delay artifact' 0.4-0.7 Sharpe estimate was conflating polling delay AND ADX-bug expressing differently in live vs backtest. True delay magnitude likely smaller
- Live Sharpe expectation: 5.73 (HWM backtest) → 5.50 (HWM-corrected May 8 AM) → ~4.0 ±0.5 (ADX-bug-corrected May 8 PM)
- live_performance_report.py tripwires need re-anchoring to ~4.0 (NOT yet applied)

Code: backend/strategies/stoch_rsi_mean_reversion.py (param + ADX gate + entry-block check), backend/analysis/audit_adx_filter_exit_block.py (audit script). JSON record: .claude/calibration/audit-adx-filter-exit-block.json.

Domain updates:
- calibration-journal.md restructured: status board + timeline (Apr 13 / May 7 / May 8 AM HWM / May 8 PM ADX), removed duplicate Aggregate-Sharpe row, fixed timeline ordering
- research-roadmap.md: new ADX-bug row (deferred packaged release), HWM row updated with caveat
- CLAUDE.md validated-edges caveat banner rewritten + new audit reference
- trail-anchor-hwm.md, audit-hwm-delay-mechanism.md, live-vs-backtest-iau-diagnostic.md: May 8 PM caveats added flagging bug contamination
- research-log.md: May 8 PM entry above May 8 AM HWM audit
- New memory: adx_filter_exit_block_bug.md + MEMORY.md index updated

 .../calibration/audit-adx-filter-exit-block.json   |  47 +++++
 .claude/calibration/audit-hwm-delay-mechanism.md   |  11 ++
 .claude/calibration/calibration-journal.md         |  68 ++++++-
 .../calibration/live-vs-backtest-iau-diagnostic.md |   2 +
 .claude/memory/gitlog.md                           |  63 ++++--
 .claude/strategies/research-log.md                 |  30 +++
 .claude/strategies/research-roadmap.md             |   5 +-
 .claude/strategies/trail-anchor-hwm.md             |   2 +
 CLAUDE.md                                          |   7 +-
 backend/analysis/audit_adx_filter_exit_block.py    | 214 +++++++++++++++++++++
 backend/strategies/stoch_rsi_mean_reversion.py     |  36 +++-
 11 files changed, 446 insertions(+), 39 deletions(-)

----
**2026-05-08** — Calibration docs consolidation — single living journal
Calibration cluster: 7 files → 4 active + 1 archive.

- New: .claude/calibration/calibration-journal.md — single living document. 8 sections: status board, findings timeline, live forward-test milestones, named patterns, Layer 3 sample, methodology, Apr 13 full results, historical snapshots. Single entry point for any calibration question.
- Removed: calibration-notes.md, forward-test-log.md (content merged into journal)
- Archived: live-trade-log.md → archive/calibration-window-mar-apr.md (frozen Mar 20–Apr 20 per-trade ledger, no maintenance)
- Updated daily-trade-audit.md procedure: per-trade tables no longer persisted to any domain file (cloud live_trade_log + MCP are source of truth, query on demand). Only durable findings (milestones, patterns, anomalies, Layer 3 entries) get written to journal.
- Cross-references updated in CLAUDE.md, harness-v4.md, research-log.md, research-roadmap.md, 4 strategy cards.

Net: cleaner mental map (the journal, two long standalone reports, the auto-generated tripwire report), single update path for new findings, no more stale per-trade tables.

 .../calibration-window-mar-apr.md}                 |   0
 .claude/calibration/calibration-journal.md         | 233 ++++++++++++++++++
 .claude/calibration/calibration-notes.md           | 268 ---------------------
 .claude/calibration/forward-test-log.md            |  78 ------
 .claude/harness-v4.md                              |   6 +-
 .claude/memory/gitlog.md                           |  41 +++-
 .claude/procedures/daily-trade-audit.md            |  15 +-
 .claude/strategies/research-log.md                 |   2 +-
 .claude/strategies/research-roadmap.md             |   6 +-
 .claude/strategies/stochrsi-enhanced-gdx.md        |   2 +-
 .claude/strategies/stochrsi-enhanced-gld.md        |   2 +-
 .claude/strategies/stochrsi-enhanced-iau.md        |   2 +-
 .claude/strategies/stochrsi-enhanced-slv.md        |   2 +-
 CLAUDE.md                                          |  11 +-
 14 files changed, 287 insertions(+), 381 deletions(-)

----
**2026-05-08** — HWM mechanism falsification audit (May 8) + calibration docs restructure
- New audit script backend/analysis/audit_hwm_delay_sensitivity.py — data-shift falsification of the May 7 'HWM is delay-immune' causal claim
- Verdict SUPPORTED with caveats: HWM ~2.8x more delay-resistant than close-anchored (Δsharpe close=0.42 vs hwm=0.15) but only 0.42 of predicted 0.7 artifact reproduced; live HWM gap likely ~0.2-0.3 Sharpe, recommended live tripwire anchor ~5.50 not 5.73
- Audit report .claude/calibration/audit-hwm-delay-mechanism.md + JSON summary
- calibration-notes.md restructured: status board (10 components, source-of-truth pointers) + findings timeline (Apr 13 / May 7 / May 8)
- forward-test-log.md slimmed from per-trade ledger to milestones+patterns format — per-trade detail now queried on-demand from Alpaca MCP / cloud live_trade_log
- Magnitude refinements propagated: '~0.7 Sharpe artifact' → '0.4-0.7 Sharpe'; '+0.78 ≈ 0.7' identity softened to directional rhyme across trail-anchor-hwm.md, iau-diagnostic, research-log, research-roadmap, CLAUDE.md
- Live bot config unchanged — pure docs + analysis script

 .claude/calibration/audit-hwm-delay-mechanism.json |  66 +++++
 .claude/calibration/audit-hwm-delay-mechanism.md   | 111 +++++++++
 .claude/calibration/calibration-notes.md           |  39 ++-
 .claude/calibration/forward-test-log.md            | 251 ++++---------------
 .claude/calibration/live-performance-report.md     |   2 +-
 .../calibration/live-vs-backtest-iau-diagnostic.md |   4 +-
 .claude/memory/gitlog.md                           |  39 ++-
 .claude/strategies/research-log.md                 |  20 +-
 .claude/strategies/research-roadmap.md             |   5 +-
 .claude/strategies/trail-anchor-hwm.md             |   6 +-
 .gitignore                                         |   3 +
 CLAUDE.md                                          |   9 +-
 backend/analysis/audit_hwm_delay_sensitivity.py    | 269 +++++++++++++++++++++
 13 files changed, 591 insertions(+), 233 deletions(-)

----
**2026-05-07** — Update roadmap, CLAUDE.md, memory, live perf report — HWM is LIVE; tripwires re-anchored to HWM expectations (Sharpe 5.73 baseline)

 .claude/calibration/live-performance-report.md | 62 ++++++--------------------
 .claude/memory/gitlog.md                       | 41 +++++------------
 .claude/strategies/research-roadmap.md         |  2 +-
 CLAUDE.md                                      |  4 +-
 backend/analysis/live_performance_report.py    | 51 ++++++++++++---------
 5 files changed, 59 insertions(+), 101 deletions(-)

----
**2026-05-07** — Deploy HWM trail anchor to all 7 live bots — trail_anchor:hwm in run_*_test.sh scripts. Existing OIH position continues with close-anchored fallback (HWM only initializes on entry); new trades use HWM.

 .claude/memory/gitlog.md               | 31 +++++++++++++++++++------------
 .claude/strategies/trail-anchor-hwm.md | 11 +++++++++++
 scripts/run_gdx_test.sh                |  2 +-
 scripts/run_gld_test.sh                |  2 +-
 scripts/run_iau_test.sh                |  2 +-
 scripts/run_oih_test.sh                |  2 +-
 scripts/run_slv_test.sh                |  2 +-
 scripts/run_xbi_test.sh                |  2 +-
 scripts/run_xop_test.sh                |  2 +-
 9 files changed, 37 insertions(+), 19 deletions(-)

----
**2026-05-07** — Domain audit — propagate May 7 delay-artifact + HWM findings across all Sharpe-referencing files. Adds memory entries, research-log entry, uniform caveat banners on per-asset and infrastructure files.

 .claude/calibration/calibration-notes.md           |  4 ++-
 .claude/calibration/forward-test-log.md            |  4 ++-
 .claude/memory/gitlog.md                           | 35 ++++++++++++++++------
 .claude/strategies/composable-results.md           |  2 ++
 .claude/strategies/long-window-validation.md       |  2 ++
 .claude/strategies/portfolio-runner-cap-shrink.md  |  4 +++
 .claude/strategies/portfolio-runner-rotation-v1.md |  2 ++
 .../regime-sizing-portfolio-diagnostic.md          |  2 ++
 .claude/strategies/regime-stochrsi-diagnostic.md   |  2 ++
 .claude/strategies/research-log.md                 | 23 +++++++++++++-
 .claude/strategies/small-capital-deployment.md     |  2 ++
 .claude/strategies/stochrsi-enhanced-gdx.md        |  2 ++
 .claude/strategies/stochrsi-enhanced-gld.md        |  2 ++
 .claude/strategies/stochrsi-enhanced-iau.md        |  2 ++
 .claude/strategies/stochrsi-enhanced-oih.md        |  2 ++
 .claude/strategies/stochrsi-enhanced-slv.md        |  2 ++
 .claude/strategies/stochrsi-enhanced-xbi.md        |  2 ++
 .claude/strategies/stochrsi-enhanced-xle.md        |  2 ++
 .claude/strategies/stochrsi-enhanced-xop.md        |  2 ++
 CLAUDE.md                                          |  2 ++
 20 files changed, 88 insertions(+), 12 deletions(-)

----
**2026-05-07** — Restore canonical Run 0 baseline snapshot (+424.09% / 4.95 / 3.41%) overwritten during HWM A/B testing

 .claude/memory/gitlog.md                        | 16 ++++-----
 .claude/strategies/portfolio-runner-baseline.md | 46 ++++++++++++++-----------
 2 files changed, 34 insertions(+), 28 deletions(-)

----
**2026-05-07** — Path 2 SHIPPED — HWM trail anchor delivers +0.78 Sharpe / -0.36pp DD vs close-anchored. Opt-in via trail_anchor parameter. Live deployment pending strategic decision.

 .claude/memory/gitlog.md                        |  20 +++--
 .claude/strategies/portfolio-runner-baseline.md |  46 +++++-----
 .claude/strategies/research-roadmap.md          |   2 +-
 .claude/strategies/trail-anchor-hwm.md          | 107 ++++++++++++++++++++++++
 CLAUDE.md                                       |   1 +
 backend/strategies/stoch_rsi_mean_reversion.py  |  30 ++++++-
 6 files changed, 169 insertions(+), 37 deletions(-)

----
**2026-05-07** — Disambiguate IAU delay finding from Apr 28-29 XBI gap-through-stop incident — unrelated

 .claude/calibration/live-vs-backtest-iau-diagnostic.md | 14 ++++++++++++++
 .claude/memory/gitlog.md                               | 16 ++++++++--------
 2 files changed, 22 insertions(+), 8 deletions(-)

