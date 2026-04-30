# Recent Git History

> Auto-generated on git save. Do not edit manually.

----
**2026-04-30** — Apr 30 PM: per-bot cap shrinking experiment — PASSES decision rule on both branches. New strategy param `position_cap_frac` (default 0.25 — byte-identical baseline) plus portfolio-runner CLI flag `--position-cap-frac`. Three runs over 2020-07 → 2026-04 on $94k. Run 0 (7 bots × 25%, baseline reproduction): +424.09% / 3.41% / 4.95 / 4344 — byte-identical to 070e3dc, confirms refactor is no-op at default. Run 1 (7 bots × 12.5%, pure cap-shrink ablation): +236.86% / 1.87% / 5.23 / 4413 — ΔSharpe +0.28, ΔDD −1.54pp, passes DD branch. Run 2 (8 bots × 12.5%, best-per-cluster GLD+SLV+OIH+XOP+IWM+SMH+XBI+IBB): +262.81% / 2.22% / 5.40 / 5004 / max-conc 8 — ΔSharpe +0.45, ΔDD −1.19pp, passes both branches independently. Returns drop by design (Sharpe is sizing-invariant — half-cap = half dollar P&L per trade); apples-to-apples is Sharpe + DD%. Lineup change (Run 1 → Run 2) contributes +0.17 Sharpe; bulk of lift is the cap-shrink itself. SMH, IBB, IWM (no live deployment) collectively contribute $80.8k of $247k aggregate P&L in Run 2. Strategic decision pending separately on whether to flip strategy default 0.25 → 0.125 and reshuffle live lineup (deploy IWM/SMH/IBB, retire IAU/GDX) — real-money trade-off (less absolute return today vs higher Sharpe with headroom to scale). Code shipped only; live bots untouched (default 0.25 preserved). Files: backend/strategies/stoch_rsi_mean_reversion.py (position_cap_frac param + 3 sizing blocks at L268/L314/L369), backend/runner.py (--position-cap-frac CLI flag + injection at L586), .claude/strategies/portfolio-runner-cap-shrink.md (new snapshot), .claude/strategies/research-roadmap.md (Per-bot cap shrinking row resolved; Best-per-cluster 4-bot row partially answered via Run 2), CLAUDE.md (strategic-direction block updated with experiment result + new on-demand snapshot ref). Bot check during session: 3 trades fired today (OIH short +$60, SLV long +$110, XOP long stop-out −$103), net +$67 paper; all entries sized at ~26% of equity confirming the 25% cap binds on every entry as theorised; trailing-stop ratchet visible on XOP (cancel-and-replace cycle 18:53/18:59/19:01); no errors, currently flat.

 .claude/strategies/portfolio-runner-cap-shrink.md | 81 +++++++++++++++++++++++
 .claude/strategies/research-roadmap.md            |  4 +-
 CLAUDE.md                                         |  5 +-
 backend/runner.py                                 |  8 +++
 backend/strategies/stoch_rsi_mean_reversion.py    |  9 ++-
 5 files changed, 101 insertions(+), 6 deletions(-)

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

----
**2026-04-29** — Apr 29 evening: regime-aware rotation infrastructure + shared-timeline portfolio runner V1.
Three new analysis tools shipped, three roadmap items resolved.

regime_universe_scan.py — daily regime classification across 33-asset ETF universe, snapshot to .claude/strategies/regime-universe-snapshot.md. First reading 2026-04-29: 7/33 favourable (TRENDING_UP), 26 RANGING, 0 TRENDING_DOWN, 0 HIGH_VOL. Most of deployed lineup (GLD/IAU/SLV/GDX/XLE/XOP/XBI) currently in RANGING; only OIH made the TRENDING set. Notable that today's TRENDING set (DBA/ITA/IWM/OIH/QQQ/SMH/XLK) is largely undeployed — first concrete evidence of the rotation thesis premise.

regime_distribution_history.py — rolling weekly snapshots over 2010-11 to 2026-05 (807 weekly snapshots, 33-asset universe). HEADLINE: median favourable count = 8, mean 9.1 — exactly inside the 8-15 selective band. Rotation backtest is justified. Today's 7/33 reading is between p10 (3) and p90 (16), i.e. typical historical territory not anomalous. HIGH_VOL is rare in normal tape (median 0, mean 1.4) but spikes universally in panics — March 2020 had 3 consecutive weeks with 30+ assets in HIGH_VOL, plus April 2025. Promoted as candidate kill-switch trigger (separate roadmap item). Year-by-year averages cluster 8-11; outliers 2011 metals/EU-debt period (avg 6.2) and 2026 YTD (avg 12.9, currently above-average trending). CSV at backend/analysis/regime_distribution_history.csv for plotting.

portfolio_runner.py + runner.py 'portfolio' subcommand — shared-timeline portfolio backtester. One PaperTrader, N strategies on unified time grid. Single-symbol equivalence verified (GLD-only run matches per-symbol card on return / trades / win rate). FIRST V1 FINDING: gold cluster has 2+ members open on 46.7% of bars and 3+ on 20.1% over 2020-07 to 2026-04 — the Apr 29 correlation-aware sizing discount fires materially in historical conditions. Single-symbol backtest could never see this (N=1 always). Energy cluster has 2+ open on 15.4%; biotech 35.1%. Snapshot at .claude/strategies/portfolio-runner-baseline.md. V1 CAVEAT: total return / Sharpe figures are model upper-bounds (no per-bot allocation cap → shared-capital compounds aggressively, +10,496% over 5.7yr is artefact). Apples-to-apples comparisons still valid because both sides share the same compounding mechanic. V2 (per-bot cap) promoted to roadmap as next item before quoting headline portfolio Sharpe.

Domain file updates:
- regime-analysis.md: added Apr 29 callout block at top with rolling-history headline and universe-scan observations.
- research-roadmap.md: 30-asset scan + rolling history both marked shipped with results inlined; Universal HIGH_VOL kill-switch promoted as standalone roadmap item; portfolio runner V1 marked shipped; new V2 row (per-bot allocation cap) and V2 correlation-sizing backtest validation rows added; rotation rule backtest expected-lift envelope added (0.5-1.0 Sharpe theoretical, +0.3 bar to beat).
- CLAUDE.md: strategic-direction bullet updated with shipped scripts + headline numbers; Validated Edges section gets Confirmed-working bullet for the portfolio runner V1 finding; on-demand domain-file reads list adds three new files; Run Commands gets the portfolio invocation.

 .claude/memory/gitlog.md                          |  41 +-
 .claude/strategies/portfolio-runner-baseline.md   |  68 ++
 .claude/strategies/regime-analysis.md             |  15 +
 .claude/strategies/regime-distribution-history.md |  94 +++
 .claude/strategies/regime-universe-snapshot.md    | 103 +++
 .claude/strategies/research-roadmap.md            |  16 +-
 CLAUDE.md                                         |  10 +-
 backend/analysis/regime_distribution_history.csv  | 808 ++++++++++++++++++++++
 backend/analysis/regime_distribution_history.py   | 346 +++++++++
 backend/analysis/regime_universe_scan.py          | 275 ++++++++
 backend/engine/portfolio_runner.py                | 173 +++++
 backend/runner.py                                 | 199 +++++-
 12 files changed, 2130 insertions(+), 18 deletions(-)

----
**2026-04-29** — doc + memory: capture Apr 29 stop-handling fixes + post-mortem. research-roadmap.md Resolved table extended with two entries — gap-through-stop guard and SYNC race condition. Memory recurring_bug_pattern.md restructured from 'one TIF bug' to 'four closely-related stop-handling failure modes' (TIF mismatch Apr 17, trailing-stop race Mar 19, SYNC race Apr 29, gap-through-stop Apr 29). Memory now explains the structural reason the SYNC race surfaced only on Apr 29 (DAY-TIF era pre-Apr-17 had nothing for cancel to race against; Apr 29 correlation-sizing deploy hit the race on all overnight-position bots simultaneously and XBI was the unlucky one due to biotech gap-profile). Added a 'where to look' index covering SYNC block, LOOP gate, SERVER STOP FIRED detection, alpaca_trader, and live_broker for future stop-related debugging.

 .claude/memory/gitlog.md               | 30 ++++++++----------------------
 .claude/strategies/research-roadmap.md |  2 ++
 2 files changed, 10 insertions(+), 22 deletions(-)

----
**2026-04-29** — fix: SYNC race upstream — adopt existing GTC stop on restart instead of cancel-and-replace. Root cause of Apr 29 XBI bug identified post-mortem: cancel_all_orders_for_symbol is async on Alpaca's side, but the SYNC block calls place_stop_order immediately after — the cancel is queued, the existing GTC stop still holds the qty, place fails with 'insufficient qty available', SYNC catches and prints 'bot will manage locally' but doesn't set pending_stop_order_id. The cancel propagates a few seconds later, killing the original GTC stop. Position is now unprotected on Alpaca AND the bot has no record of any stop. This race fired on every overnight-position bot at the correlation-sizing pm2 restart this morning; XBI was the unlucky one because biotech gaps at the open and the [LOOP] gap-recovery hit a price already past the intended SL. Same pattern was fixed Mar 19 in live_broker.py trailing-stop path with a 1s sleep. New: alpaca_trader.get_open_stop_order(symbol, side) returns the first open stop matching side, with id/qty/stop_price. SYNC block now: (1) check if an existing stop exists and is within $0.50 of reconstructed SL; if yes, adopt its order_id and snap current_sl to the live level (no cancel, no race); (2) if no existing stop or level differs materially, fall back to cancel + 1s sleep + place. Both changes preserve the Apr 29 defensive guards (gap-through-stop breach detection + emergency market exit). The defensive guard from Apr 29 still applies — this fix is the upstream version that prevents the unprotected window in the first place.

 .claude/memory/gitlog.md        | 19 +++++++-------
 backend/engine/alpaca_trader.py | 25 +++++++++++++++++++
 backend/runner.py               | 55 ++++++++++++++++++++++++++++++++---------
 3 files changed, 77 insertions(+), 22 deletions(-)

----
**2026-04-29** — Apr 29 XBI gap-through-stop bug — log + fix outcome documented. forward-test-log.md: new dated section for Apr 29 XBI emergency-market exit (-$313.61), new exit type EM (emergency market, gap-through-stop guard). Realised P&L summary updated to 13 closed trades, total -$1,142.39. Memory recurring_bug_pattern.md: extended from one TIF bug to three closely-related failure modes — TIF mismatch (resolved Apr 17), gap-through-stop on re-placement (resolved today via defensive guard in [SYNC] + [LOOP] paths), and a 'where to look' index for future stop-related debugging. Outstanding: root cause of why pending_stop_order_id was None despite live GTC stop — defensive fix is sufficient for safety; investigation still open.

 .claude/calibration/forward-test-log.md | 29 ++++++++++++++++++++++++++++-
 .claude/memory/gitlog.md                | 22 +++++++++-------------
 2 files changed, 37 insertions(+), 14 deletions(-)

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

