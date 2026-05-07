# Recent Git History

> Auto-generated on git save. Do not edit manually.

----
**2026-05-07** — Update roadmap, CLAUDE.md, memory, live perf report — HWM is LIVE; tripwires re-anchored to HWM expectations (Sharpe 5.73 baseline)

 .claude/calibration/live-performance-report.md | 62 ++++++--------------------
 .claude/strategies/research-roadmap.md         |  2 +-
 CLAUDE.md                                      |  4 +-
 backend/analysis/live_performance_report.py    | 51 ++++++++++++---------
 4 files changed, 48 insertions(+), 71 deletions(-)

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

----
**2026-04-30** — Apr 30 PM: rotation closed for StochRSI mean-reversion + portfolio total-notional cap shipped (default OFF). 4-run study (V2 baseline 7-bot / Run A 7+cap / Run B 20+cap / Run C 20+cap+TRENDING_UP / Run D 20+cap+RANGING) finalises the rotation question. Both rotation rules fail the +0.30 Sharpe gate: V1 TRENDING_UP 3.21 (ΔSharpe −1.65), V2 RANGING 4.49 (ΔSharpe −0.37). Reason: the strategy's own ADX<20 entry filter already self-selects regime at the right (15m) timeframe — adding a daily-bar rotation rule on top is redundant or destructive (TRENDING_UP) or strips marginal edge with no compensating signal (RANGING). Rotation is dead for StochRSI mean-reversion; remains a candidate for strategy classes without internal regime filters (breakouts, momentum, donchian-trend). Yesterday's +1013% / 6.20 Sharpe universe-expansion headline was 100% leverage (max-conc 19 × 25% cap = 475% of equity) — Run B with honest accounting collapses to +441.81% / 4.76 Sharpe / DD 2.45%, confirming universe expansion at our scale is a DD-reducer not a Sharpe-lifter. Code shipped: backend/engine/rotation.py (RotationController, build_weekly_regime_panel, ROTATION_RULES registry with 4 rules: trending_up, ranging, no_bad_regime, always_active), W-FRI boundary detection in portfolio_runner.py, single-line rotation_paused flag in stoch_rsi_mean_reversion.py:138 OR'd into existing skip_entry, CLI flags --rotation / --rotation-rule / --rotation-universe / --use-cache. Validation gates passed: V1 cache parity byte-identical, V2 always_active byte-identical, V3 pause-flag observable (300 weekly rebalances logged), V4 pause integrity. Side finding promoted from leverage discovery: portfolio-level total-notional cap shipped (correlation_sizing.portfolio_cap_max_size, helper returns (equity*FRAC - sum(|peer|*avg_price))/entry_price, sizing block now min(risk, 25%-per-pos, cluster_max, portfolio_max), CLI flag --portfolio-cap-frac N, default OFF currently — recommend default ON at FRAC=1.0). Run A on 7-bot lineup (+424.09% / 3.41% / 4.95 Sharpe / 4344 trades): cap binds on gold N=4 stacking (4.2% of bars), tiny structural improvement +0.09 Sharpe / -0.17pp DD; the Run B 20-bot result clears decision rule on DD branch. Mental-model update: previous '4 simultaneous full positions × 25% = 100% binding constraint' framing only valid with portfolio cap OFF; once ON the binding constraint becomes aggregate notional, unlocking the per-bot-cap-shrinking experiment (12.5% × 8 bots, 5% × 20 bots) as the genuinely-untested next lever. Roadmap promoted next: per-bot cap shrinking (theoretical √2 Sharpe lift via diversification), best-per-cluster 4-bot lineup (GLD+OIH+IWM+XBI). IWM-as-bot-#8 de-prioritised as Sharpe-boost play (Run B says no). Files: backend/engine/correlation_sizing.py (PORTFOLIO_CAP_ENABLED + PORTFOLIO_CAP_FRAC toggles, portfolio_cap_max_size helper), backend/engine/rotation.py (new), backend/engine/portfolio_runner.py (W-FRI boundary), backend/strategies/stoch_rsi_mean_reversion.py (skip_entry rotation hook + 4-cap min stack), backend/runner.py (CLI flags + DB cache load path), .claude/strategies/portfolio-runner-rotation-v1.md (final 4-run study, single source of truth), .claude/strategies/portfolio-runner-baseline.md (navigational callout), .claude/strategies/regime-analysis.md + regime-distribution-history.md + regime-universe-snapshot.md (FALSIFIED Apr 30 PM callouts), .claude/strategies/research-roadmap.md (rotation V1/V2 + portfolio cap + per-bot cap + best-per-cluster rows; falsification preamble on Regime-Aware Asset Rotation section; live-coordinator dropped; sharp-top detector repointed at regime-conditional cluster cap), CLAUDE.md (consolidated rotation/cap blocks, mental-model update, strategic direction rewrite). Memories: asset_rotation_thesis.md (full rewrite — FALSIFIED status), rotation_rule_conflict.md (full rewrite — 2-rule conclusion), portfolio_total_notional_cap.md (shipped status), notional_cap_dominates.md (full rewrite — sizing-cap stack), correlation_sizing.md (4-cap stack reminder), regime_preference.md (rotation-closed + sharp-top repointed), MEMORY.md index refreshed. Live bots untouched (default OFF on all new toggles); pm2 restart not required.

 .claude/memory/gitlog.md                           |  36 ++--
 .claude/strategies/portfolio-runner-baseline.md    | 104 +++++-----
 .claude/strategies/portfolio-runner-rotation-v1.md | 128 ++++++++++++
 .claude/strategies/regime-analysis.md              |   6 +-
 .claude/strategies/regime-distribution-history.md  |   4 +-
 .claude/strategies/regime-universe-snapshot.md     |   4 +-
 .claude/strategies/research-roadmap.md             |  45 +++--
 CLAUDE.md                                          |  27 ++-
 backend/engine/correlation_sizing.py               | 112 +++++++++++
 backend/engine/portfolio_runner.py                 |  22 +++
 backend/engine/rotation.py                         | 217 +++++++++++++++++++++
 backend/runner.py                                  | 105 ++++++++--
 backend/strategies/stoch_rsi_mean_reversion.py     |  29 ++-
 13 files changed, 721 insertions(+), 118 deletions(-)

----
**2026-04-30** — Apr 30 (PM): correlation-sizing with-vs-without backtest — discount is structurally inactive under V2 fixed-equity. New CLI flag --no-correlation-discount + module toggle correlation_sizing.DISCOUNT_ENABLED (default True; live bots, single-symbol backtests, default portfolio runs unaffected) enable the apples-to-apples comparison. 7-bot V2 baseline (2020-07 → 2026-04, $94k): discount ON +474.67% / 3.58% DD / Sharpe 4.86 / 4413 trades; discount OFF +474.87% / 3.58% / 4.86 / 4413. Trade counts and per-symbol win rates byte-identical. Reason: position size is min(risk_amt / stop_dist, equity * 0.25 / price). For risk to bind tighter than the 25% notional cap, stop_dist/price must exceed 8% at full risk; on 15m metals/energy bars 2 ATR/price ≈ 0.4–1.0%. The cap wins on every entry the strategy actually takes, overwriting whatever the discount sets. Verdict per roadmap rule: neutral (Sharpe and DD unchanged to 2 d.p.) — keep the discount for documentation + the high-volatility regime where it could bind, but reframe: the cap is doing the correlated-gap protection work, not the discount. Apr 23 tail-risk concern bounded by 25% × 4 = 100% notional ceiling regardless of discount state. IWM expansion gate is now unblocked from the discount-validation perspective; live [CORR-SIZE] log audit downgraded from deployment-decision gate to wiring check. Upstream implication: future portfolio-level sizing work should focus on the notional cap (e.g. cluster-aware cap) rather than risk-fraction adjustments. Files: backend/engine/correlation_sizing.py (DISCOUNT_ENABLED toggle), backend/runner.py (CLI flag + diagnostic snapshot path routes to a separate file to preserve the V2 baseline), .claude/strategies/portfolio-runner-baseline.md (full comparison + interpretation), .claude/strategies/research-roadmap.md (row 81 resolved with finding), CLAUDE.md (Correlation-aware sizing note rewritten to reflect cap-binds-first; IWM gate flipped to unblocked). Memories added: notional_cap_dominates.md (the structural finding) + correlation_sizing.md updated with Apr 30 note.

 .claude/memory/gitlog.md                        | 21 +++++++------
 .claude/strategies/portfolio-runner-baseline.md | 40 ++++++++++++++++++++++---
 .claude/strategies/research-roadmap.md          |  2 +-
 CLAUDE.md                                       |  6 ++--
 backend/engine/correlation_sizing.py            |  9 ++++++
 backend/runner.py                               | 16 +++++++++-
 6 files changed, 76 insertions(+), 18 deletions(-)

----
**2026-04-30** — Apr 30: portfolio runner V2 — fixed-equity reference + Sharpe-invariance learning. Each strategy now reads equity_mode param: 'live' (default → broker.get_equity(), single-symbol backtester + live deployment unchanged) or 'fixed' (→ initial_capital, no compounding of the equity reference). PortfolioRunner injects equity_mode='fixed' so 7 bots on a shared $94k pool size off the same $94k each — mirrors live mechanics where 7 bots on one Alpaca account each see the same equity number. V1 artefact (every bot sizing 2% off the inflated total equity → +10,496%/Sharpe 5.55) replaced with V2 baseline +474.67%/3.58% DD/Sharpe 4.86/4413 trades on the validated 7-bot lineup (2020-07 → 2026-04). Trade counts and cluster co-occupancy (gold ≥2 on 46.7%, ≥3 on 20.1%) identical to V1 — entry logic unchanged. Important learning recorded across CLAUDE.md, research-roadmap.md, and the snapshot interpretation note: Sharpe is sizing-invariant by construction (scaling positions by a constant scales mean and stdev equally), so V1's Sharpe was NOT an upper-bound artefact — only the +10,496% return and 5.05% DD were. The earlier 'V1 caveat' framing in CLAUDE.md/roadmap that lumped Sharpe with return/DD was wrong. V2's slightly lower 4.86 vs V1's 5.55 reflects Option A's reweighting of early-vs-late-year contributions, not a metric fix. Files: backend/strategies/stoch_rsi_mean_reversion.py (equity_mode + initial_capital captured, three sizing blocks updated), backend/engine/portfolio_runner.py (injects equity_mode='fixed'), backend/runner.py (snapshot interpretation note rewritten). Roadmap rows updated: portfolio runner V2 row flipped to 'shipped'; correlation-sizing with-vs-without backtest promoted to 'next — gating IWM expansion' with V2 baseline as the comparison anchor. Snapshot at .claude/strategies/portfolio-runner-baseline.md.

 .claude/memory/gitlog.md                        | 22 +++++++------
 .claude/strategies/portfolio-runner-baseline.md | 41 +++++++++++++++++--------
 .claude/strategies/research-roadmap.md          |  6 ++--
 CLAUDE.md                                       |  2 +-
 backend/engine/portfolio_runner.py              |  3 ++
 backend/runner.py                               | 26 ++++++++++------
 backend/strategies/stoch_rsi_mean_reversion.py  | 12 ++++++--
 7 files changed, 74 insertions(+), 38 deletions(-)

