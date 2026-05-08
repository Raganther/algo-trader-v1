# Recent Git History

> Auto-generated on git save. Do not edit manually.

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
 .claude/strategies/research-log.md                 |  30 +++
 .claude/strategies/research-roadmap.md             |   5 +-
 .claude/strategies/trail-anchor-hwm.md             |   2 +
 CLAUDE.md                                          |   7 +-
 backend/analysis/audit_adx_filter_exit_block.py    | 214 +++++++++++++++++++++
 backend/strategies/stoch_rsi_mean_reversion.py     |  36 +++-
 10 files changed, 402 insertions(+), 20 deletions(-)

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

----
**2026-05-07** — IAU live-vs-backtest diagnostic — identifies 1-bar polling delay artifact (~0.7 Sharpe). Anchor live tripwires to corrected expectation.

 .claude/calibration/live-performance-report.md     |  27 +++--
 .../calibration/live-vs-backtest-iau-diagnostic.md | 119 +++++++++++++++++++++
 .claude/memory/gitlog.md                           |  27 ++---
 .claude/strategies/portfolio-runner-baseline.md    |  48 ++++-----
 .claude/strategies/research-roadmap.md             |   2 +
 CLAUDE.md                                          |   1 +
 backend/analysis/live_performance_report.py        |  20 +++-
 7 files changed, 192 insertions(+), 52 deletions(-)

----
**2026-05-05** — Wire live perf report into CLAUDE.md run commands + roadmap rows

 .claude/memory/gitlog.md               | 20 +++++++++-----------
 .claude/strategies/research-roadmap.md |  4 ++--
 CLAUDE.md                              |  3 +++
 3 files changed, 14 insertions(+), 13 deletions(-)

----
**2026-05-05** — Live performance report — automated tripwire monitoring vs backtest

 .claude/calibration/live-performance-report.md |  70 ++++++
 .claude/memory/gitlog.md                       |  24 +--
 CLAUDE.md                                      |   1 +
 backend/analysis/live_performance_report.py    | 288 +++++++++++++++++++++++++
 4 files changed, 369 insertions(+), 14 deletions(-)

----
**2026-05-04** — Document $1k small-capital deployment plan + backtest validation

 .claude/memory/gitlog.md                        |  20 ++--
 .claude/strategies/portfolio-runner-baseline.md |   2 +-
 .claude/strategies/research-roadmap.md          |   3 +-
 .claude/strategies/small-capital-deployment.md  | 145 ++++++++++++++++++++++++
 CLAUDE.md                                       |   1 +
 5 files changed, 160 insertions(+), 11 deletions(-)

----
**2026-04-30** — Apr 30 PM: per-bot cap shrinking experiment — PASSES decision rule on both branches. New strategy param `position_cap_frac` (default 0.25 — byte-identical baseline) plus portfolio-runner CLI flag `--position-cap-frac`. Three runs over 2020-07 → 2026-04 on $94k. Run 0 (7 bots × 25%, baseline reproduction): +424.09% / 3.41% / 4.95 / 4344 — byte-identical to 070e3dc, confirms refactor is no-op at default. Run 1 (7 bots × 12.5%, pure cap-shrink ablation): +236.86% / 1.87% / 5.23 / 4413 — ΔSharpe +0.28, ΔDD −1.54pp, passes DD branch. Run 2 (8 bots × 12.5%, best-per-cluster GLD+SLV+OIH+XOP+IWM+SMH+XBI+IBB): +262.81% / 2.22% / 5.40 / 5004 / max-conc 8 — ΔSharpe +0.45, ΔDD −1.19pp, passes both branches independently. Returns drop by design (Sharpe is sizing-invariant — half-cap = half dollar P&L per trade); apples-to-apples is Sharpe + DD%. Lineup change (Run 1 → Run 2) contributes +0.17 Sharpe; bulk of lift is the cap-shrink itself. SMH, IBB, IWM (no live deployment) collectively contribute $80.8k of $247k aggregate P&L in Run 2. Strategic decision pending separately on whether to flip strategy default 0.25 → 0.125 and reshuffle live lineup (deploy IWM/SMH/IBB, retire IAU/GDX) — real-money trade-off (less absolute return today vs higher Sharpe with headroom to scale). Code shipped only; live bots untouched (default 0.25 preserved). Files: backend/strategies/stoch_rsi_mean_reversion.py (position_cap_frac param + 3 sizing blocks at L268/L314/L369), backend/runner.py (--position-cap-frac CLI flag + injection at L586), .claude/strategies/portfolio-runner-cap-shrink.md (new snapshot), .claude/strategies/research-roadmap.md (Per-bot cap shrinking row resolved; Best-per-cluster 4-bot row partially answered via Run 2), CLAUDE.md (strategic-direction block updated with experiment result + new on-demand snapshot ref). Bot check during session: 3 trades fired today (OIH short +$60, SLV long +$110, XOP long stop-out −$103), net +$67 paper; all entries sized at ~26% of equity confirming the 25% cap binds on every entry as theorised; trailing-stop ratchet visible on XOP (cancel-and-replace cycle 18:53/18:59/19:01); no errors, currently flat.

 .claude/memory/gitlog.md                          | 71 ++++++++++++++------
 .claude/strategies/portfolio-runner-cap-shrink.md | 81 +++++++++++++++++++++++
 .claude/strategies/research-roadmap.md            |  4 +-
 CLAUDE.md                                         |  5 +-
 backend/runner.py                                 |  8 +++
 backend/strategies/stoch_rsi_mean_reversion.py    |  9 ++-
 6 files changed, 151 insertions(+), 27 deletions(-)

----
**2026-04-30** — Apr 30 PM: flip portfolio total-notional cap default ON.
PORTFOLIO_CAP_ENABLED = True (FRAC=1.0) in correlation_sizing.py. Live bots
now have an aggregate-notional safety guard that fires when total open
positions exceed 100% of equity. On the 7-bot lineup this rarely binds
(only on gold N=4 stacking ≈ 3.5% of bars in latest run), producing a tiny
structural improvement: Sharpe 4.86 → 4.95, DD 3.58% → 3.41%, trades
4413 → 4344. Headline figure for the live lineup is now +424.09% / 4.95.

The guard's main value isn't the small Sharpe lift — it's preventing the
silent leverage trap that universe expansion would otherwise hit (verified
yesterday: 20-bot run hit max-conc 19 = ~4.75× leverage on $94k without
this cap; with the cap, max-conc 14 stays inside 100% notional).

Runner override semantics: --portfolio-cap-frac N still works as a
diagnostic CLI flag; --portfolio-cap-frac 0 disables for comparison runs.
No CLI flag = module default (now ON).

Verified: portfolio backtest with 7-bot lineup reproduces Run A figures
(+424.09% / 3.41% / 4.95 / 4344) byte-for-byte.

Files: backend/engine/correlation_sizing.py (PORTFOLIO_CAP_ENABLED
flipped True; comment updated with deployment context), backend/runner.py
(diagnostic-print logic clarified for module-default vs CLI-override),
.claude/strategies/research-roadmap.md (status updated to "shipped +
default ON"), .claude/strategies/portfolio-runner-baseline.md (auto-refreshed
by the verification run), CLAUDE.md (sister note updated to reflect
default-on status).

Co-Authored-By: Claude Opus 4.7 <noreply@anthropic.com>

 .claude/strategies/portfolio-runner-baseline.md | 64 ++++++++++---------------
 .claude/strategies/research-roadmap.md          |  2 +-
 CLAUDE.md                                       |  2 +-
 backend/engine/correlation_sizing.py            | 12 ++++-
 backend/runner.py                               | 12 +++--
 5 files changed, 46 insertions(+), 46 deletions(-)

