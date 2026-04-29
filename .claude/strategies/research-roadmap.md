Status: current | Epistemic: mixed | Last verified: 2026-04-28

# Research Roadmap — Algo Trader V1

Single source of truth for all open ideas, questions, and in-flight work.
Domain files hold confirmed knowledge. This file tracks everything we're still figuring out.

Status labels: `idea` | `in progress` | `validated` | `rejected` | `monitoring`

---

## Framework Attribution — Apr 28 2026 (RESOLVED)

Three discriminating tests run Apr 28 evening. Results recorded in `research-log.md` → "Edge Question — Test 1/2/3" and "Edge Question — Synthesis (Apr 28 2026)".

**Resolved finding:** What we built is a position-management framework (ATR stop / trailing stop after 10 bars / ADX-ranging filter / 2% fixed-risk sizing / 25% notional cap / skip-Mon / 10-bar min-hold). The framework alone produces Sharpe ≥ 2.0 with zero signal information (Test 2). It beats B&H on every tested asset (Test 1). On directional/metals assets the framework's edge is regime-dependent — GLD inverted Sharpe collapses 2.48 → 0.85 (Test 3). On broad indices the framework is direction-agnostic (SPY 1.36 → 1.53). The StochRSI entry + K-cross exit signals are at best neutral, slightly net-negative on average across the assets tested.

| Item | Status | Notes |
|------|--------|-------|
| Buy-and-hold comparison | **resolved — Apr 28** | Strategy beats B&H on all 12 assets by Δ Sharpe +0.46 to +1.94 (median ~+1.4), DD protection 8.5×–26.2×. `backend/analysis/buy_and_hold_comparison.py`. |
| Fully-random ablation (random entries + random exits + stop only) | **resolved — Apr 28** | Framework alone clears Sharpe ≥ 2.0 on every asset tested (GLD 2.32, SLV **2.64**, GDX **2.57**, QQQ **2.28**). On 3 of 4 assets, fully-random matches or beats validated. Signal contribution is at best neutral. `random_entry_prob` + `random_exit_prob` params in `stoch_rsi_mean_reversion.py`. |
| Synthetic price inversion | **resolved — Apr 28; refined Apr 29** | GLD inverted Sharpe collapses 2.48 → 0.85 on Alpaca window — directional edge confirmed. **Apr 29 long-window test refines this:** the ~⅓ collapse predicted for real bear regimes does NOT reproduce. XAUUSD validated Sharpe in the 2013–15 real metals bear is +1.44 (B&H -0.82); XAGUSD +2.04 (B&H -0.85). Framework holds in real bears. The synthetic inversion captured something about price-shape symmetry, not real bear-regime microstructure. Magnitude prediction was wrong; directional finding (some directional dependence exists) stands. See `long-window-validation.md`. |
| Long-window spot-proxy validation (HistData 2009–2026) | **resolved — Apr 29** | Framework backtested on XAUUSD (17 yr), XAGUSD (16 yr), WTIUSD (13 yr) spot proxies, segmented by regime. Full-window Sharpes: gold 1.60, silver 1.68, oil 1.35. Bear-period results above. **2020+ overlap shows spot Sharpe ~1.5 vs ETF Sharpe ~2.5 for the same window** — 0.8–1.0 gap too large for expense-ratio drag alone, suggests an ETF microstructure premium in the live data. Practical: live-money sizing should anchor to spot-proxy 1.5 Sharpe baseline (matches existing CLAUDE.md "size for 1.0–1.5"). See `long-window-validation.md`. Tooling: `backend/engine/histdata_loader.py`, `scripts/fetch_price_data_histdata.py`, `backend/analysis/long_window_validation.py`. |
| Granular framework ablations (no-trail / no-ADX / no-min-hold individually) | deferred — diagnostic only | Now diagnostic, not gating. The framework attribution itself is settled. Useful for understanding which component is most load-bearing but doesn't change deployment decisions. Run when convenient. |
| OIH/XBI/XOP/XLE/IAU inversion + random tests | idea | Confirm whether each behaves like GLD (regime-dependent) or SPY (regime-agnostic). Most likely GLD-like since they're all directional sector ETFs. Useful before any sizing decision specific to one of these bots. |
| Real-time regime detector + regime-aware sizing | idea — promoted | Apr 28 result makes this more concrete: if metals framework Sharpe varies 2× to 3× by regime, a regime detector + dynamic size could meaningfully improve live risk-adjusted return. Existing regime work is descriptive; this would be predictive. Lower priority than Critical Path technical items. |
| Alternative framework parameters / variants | idea | The current framework parameters (2.0 ATR stop / 2.0 trail / 10 bar after / ADX 20 / 10 bar hold) were tuned on metals. Worth a sensitivity sweep on the framework parameters specifically (no signal logic in scope). Tightest answer: optimise the framework, not the signal. |
| Composable signal search (now well-posed) | idea | The StochRSI doesn't add value over the framework. Other signals (e.g. order-flow imbalance, opening-range break, volume profile) might. Worth an exploratory composable search using the framework as the position-management chassis. Lower priority than understanding regime dependence. |

---

## Critical Path — To Real Money

> **Apr 28 2026 status (post-resolution):** Three discriminating tests resolved the edge question (see Framework Attribution section above + `research-log.md` → "Edge Question — Synthesis"). The framework is the edge; it beats B&H on all assets; on metals it's regime-dependent. The remaining Critical Path items below (ATR portfolio sizing, late-session guard) are still required pre-real-money. **Apr 29 2026 update:** correlation-aware sizing V1 is now live — see table below. **Sizing recommendation:** size for expected Sharpe 1.0–1.5 on metals (not the 2.46 backtest figure) to budget for regime variation. IWM is a more attractive deployment candidate than its raw Sharpe suggests due to direction-agnostic profile.
>
> **Bot lineup framing (added Apr 28 evening, updated Apr 29):** the 7 deployed bots represent ~3 independent economic bets — gold cluster (GLD/IAU/SLV/GDX), energy cluster (OIH/XOP), and biotech (XBI). Capital cap binds at 4 simultaneous full positions (25% notional × 4 = 100% equity). **Adding more bots as a fixed lineup is NOT the next move** — it's "let the existing 7 produce live data + verify the new correlation discount fires correctly." See "Live Observation Framework" section below for what to measure. Adding fixed bots is now gated on (a) ~~correlation-aware sizing landing~~ **done — V1 live Apr 29**, (b) **live verification that the discount fires on the next correlated entry** (replaces "landing first"), (c) the new bot adding an independent cluster, not a correlated one. Only IWM currently meets the cluster-independence criterion.
>
> **Apr 29 strategic direction — regime-aware asset rotation.** The Apr 29 long-window finding (framework's Sharpe varies materially by regime — see `long-window-validation.md`) plus the Apr 28 generalisation finding (framework works on any liquid non-rates ETF) jointly suggest the better long-term move than "more fixed bots" is "scan a wider universe and rotate capital to whichever assets are currently in a strong regime." Rotation is a quality lift, not a capacity lift (4-position cap unchanged). See "Regime-Aware Asset Rotation" section below — cheapest first step is the 30-asset regime scan, no live changes required.

| Item | Status | Notes |
|------|--------|-------|
| Correlation-aware sizing | **V1 live — Apr 29 2026** | Equal-split risk parity discount applied at entry: `risk_frac = 0.02 / N` where N = existing peers in cluster + self. Hardcoded clusters (gold = GLD/IAU/SLV/GDX, energy = OIH/XOP/XLE, biotech = XBI). `backend/engine/correlation_sizing.py` + 3 sizing blocks in `stoch_rsi_mean_reversion.py`. Already-open peers are not resized (loose cap: total cluster risk grows sublinearly 2%→3%→3.67%→4% vs prior 2%→4%→6%→8%). Backtest is single-symbol so N=1 always — Sharpe regression matches (GLD 2.48 ✓). Known V1 limitations: race condition on simultaneous fires (both bots may see N=1 if polling within ~1s — accepted, occasional ~4% exposure vs target 3%); no resize of already-open peers; no shared-timeline backtest validation. Next: (a) live audit of `[CORR-SIZE]` log lines on next gold-cluster simultaneous entry; (b) build shared-timeline runner for V2 backtest validation; (c) consider race-condition serialization (DB advisory lock or staggered polling) if live data shows it materialising. **Apr 23: identified as the single remaining tail-risk concern after gap-distribution analysis closed the single-symbol gap-policy item. A correlated 4-symbol overnight gap at p99 = ~5% single-day equity DD — the largest unbounded tail in the system today.** |
| ATR-based position sizing | in progress | Back-calculate shares from fixed max risk % (e.g. 1% of account ÷ stop distance = shares). Normalises risk per trade across volatile/calm sessions. Implement alongside correlation sizing — both are pre-real-money. |
| Late-session entry guard | in progress | Block or halve size when entry fires within ~30 min of market close. GTC stops survive overnight, but DAY stops (any remaining fractional positions) expire before providing protection. Apr 8 triple late-entry data point (SLV/GLD/GDX at 19:46 UTC): resolved next morning, net slightly negative on a sample of 3. Testable with existing single-symbol engine (simple time condition in on_bar). |
| Overnight hold / gap policy | resolved | Apr 23 2026. Gap distribution analysis (`.claude/calibration/gap-distribution.md`, `backend/analysis/gap_distribution.py`) shows single-symbol gap risk is already bounded by the 25% notional cap: SLV p99 gap 5.25% × 25% = 1.31% equity DD, worst historical gap (SLV -13.87%) = 3.47%. Apr 23 actual: -0.64%. An explicit 1% gap budget is a no-op at current equity (notional cap binds first for all 4 symbols). No code change needed. Residual tail risk is **correlated gaps across all 4 symbols simultaneously** — addressed under the existing Correlation-aware sizing item, not a separate fix. |

---

## Live Observation Framework — What to Measure While Bots Run

> **Apr 28 2026 — added after edge resolution.** Letting the 7 bots run is the right plan, but it has to be active. These are the specific things that, observed over 3–6 months of live data, would convert backtest evidence into real-money confidence. Without these measurements, time-passing-with-bots-running adds little.

| Item | Status | Notes |
|------|--------|-------|
| Live Sharpe vs backtest Sharpe (per cluster) | next | Once ~3 months of live trades accumulated, compute live daily-resampled Sharpe per cluster (gold/energy/biotech) and compare to backtest figures (2.30–2.48 metals, 2.18–2.33 energy, 2.18 biotech). Decision rule: live within ~30% of backtest = framework + execution model is sound; live <1.0 = something in slippage/spread/timing is mis-modelled. Build as a recurring weekly report, not a one-off. |
| Slippage tracking + Layer 3 expansion | in progress | `forward-test-log.md` already captures per-trade fills vs intended prices. Aggregate quarterly. Backtest assumes ~$0.013/share median slippage on stops. If live measures higher consistently, the backtest Sharpe is overstated by ~the slippage delta × annual stop-fire count. Sample is at 41 fires Apr 27; target 50+. |
| Regime check during live window | monitoring | If metals enter a bear or sustained chop while bots run, **that's the data we don't have anywhere else.** Don't act on a few weeks of metals weakness — record it carefully. The Test 3 inversion result predicts metals Sharpe drops materially in a non-bull regime. Live observation is the only way to validate that prediction. |
| Correlated-entry frequency | next | Track how often 3+ correlated bots enter simultaneously (e.g. GLD + IAU + SLV all long within 30 min). Theoretical concern from `gap-distribution.md` is real-time correlated gap risk; live data tells us how often this materialises in practice. Trivial to build from `live_trade_log` queries. |
| `[CORR-SIZE]` discount audit (V1 verification) | **next — gating IWM expansion** | Confirm the new correlation-aware sizing discount actually fires correctly. Grep pm2 logs for `[CORR-SIZE]` lines; expect them to appear on the 2nd+ bot to enter within a cluster. Compare the resulting Alpaca position size to a recent comparable solo entry — should be ~1/N. Also: tally how often two bots in the same cluster fire within ~1s of each other (the V1 race-condition window) — if frequent, prioritise V2 serialization (DB advisory lock or staggered polling). Check after the first 3–5 cluster simultaneous entries (~1–2 weeks of running). |
| Live-vs-backtest dashboard | idea — high value | Frontend page showing live Sharpe / DD / win rate per bot vs backtest expectation, updated daily. Saves the manual quarterly check. Build alongside the chart Stage 2 work. |
| Metals regime detector v1 | **superseded by transition detector — Apr 29** | The original idea was to downsize in TRENDING_DOWN. Apr 29 long-window evidence shows TRENDING_DOWN (sustained bear) is actually a STRONG regime for the framework — XAGUSD 2013–15 bear Sharpe +2.04. Downsizing metals in a real bear would have left money on the table. The actually-dangerous regime is the *transition* (sharp-top / post-peak), not the bear itself. See "Sharp-top / transition detector" row below. |
| Sharp-top / transition detector | **idea — promoted from Apr 29 long-window finding** | The 18-cell HistData backtest identifies sharp regime transitions as the worst environment (XAGUSD 2011 peak +0.80; XAUUSD 2011 transition +0.86; WTIUSD 2014–16 collapse +1.11 with 5.51% DD). None of the existing 4 regime labels (RANGING / TRENDING_UP / TRENDING_DOWN / HIGH_VOL) isolate this case cleanly. Candidate definition: ATR spike >2× 50-bar mean **and** close crosses 200-SMA in the direction opposite to the prior 60-day trend **and** ADX rising. If detected on metals/energy daily bars, downsize the corresponding cluster bots (1% risk, halve notional cap, or skip entries) until the regime stabilises. Lower-priority than Critical Path technical items but high information-value once shipped — would tag the highest-risk environment specifically for the live lineup. |
| Real-money pilot ($1–5k) when ready | idea — gating | Once: (1) 6+ months live forward test on 7 bots within 30% of backtest, (2) correlation-aware sizing **V1 shipped Apr 29** + live-verified on ~5 cluster simultaneous entries (in progress), (3) live slippage measured and incorporated into backtest model, (4) shared-timeline backtest validation of the V1 discount rule (V2 work). Pilot at small real capital to measure execution friction at scale-of-real. **Not a near-term action.** |

---

## Calibration

| Item | Status | Notes |
|------|--------|-------|
| Layer 3 — stop slippage aggregation | in progress | Apr 27 expansion: 33 → 41 intraday fires (+8 from validated-params forward test, see `forward-test-log.md`). Updated mean ~$0.025/share, median ~$0.013/share — consistent with prior. **Direction no longer 100% negative** — 3 of 8 new fires are positive (+0.004 to +0.010), all on buy-stops (short covers and a ratchet-just-in-time long sell-stop). Sell-stops on long positions remain mostly negative. Decision: add `stop_slippage` param to backtest only after sample reaches 50 and direction split stabilises. Median is still the reliable model input. |
| Execution layer calibration across regimes | monitoring | Apr 20 calibration is a snapshot of one unusual regime (post-metals-crash recovery, high intraday volatility). Whether spread and slippage assumptions hold in calmer or more strongly trending conditions is untested. Treat Apr 20 calibration as valid for this window, not a universal constant. |

---

## Portfolio Infrastructure

| Item | Status | Notes |
|------|--------|-------|
| Shared-timeline portfolio runner | in progress | Run all 4 symbols simultaneously on a shared timeline, aggregate P&L across symbols. Required for: (1) correlation analysis — tally simultaneous entry/exit outcomes by year; (2) regime-sizing backtest — apply dynamic sizing rules; (3) rigorous Layer 4 aggregate P&L validation — current $10k-per-symbol backtest vs $94k shared-capital live. Single build unlocks all three. |

---

## Regime-Aware Sizing

| Item | Status | Notes |
|------|--------|-------|
| Per-regime strategy performance analysis / Phase 1 diagnostic | monitoring | Apr 23 diagnostic complete: `python3 -m backend.analysis.stochrsi_regime_performance` writes `.claude/strategies/regime-stochrsi-diagnostic.md`. Primary grain is symbol × regime × direction; cells with N < 10 flagged directional-only; metals aggregate footer included. Result: **partial gradient** — RANGING strongest on aggregate Sharpe, HIGH_VOL long exposure uneven, TRENDING_DOWN not a clean skip signal. Use regime as high-conviction sizing/filter input only until portfolio-runner validation. |
| Regime-aware sizing backtest | monitoring | Apr 23 closed-trade portfolio replay complete: `python3 -m backend.analysis.regime_sizing_portfolio` writes `.claude/strategies/regime-sizing-portfolio-diagnostic.md`. Broad regime multipliers do **not** improve drawdown-adjusted performance: baseline daily Sharpe 4.27 beats conservative 4.15, aggressive 4.00, high-vol-only 4.19. Conservative reduces max DD by ~$90 but gives up ~$4,041 P&L. Treat regime as context/high-conviction filter only; do not implement broad live regime sizing. Full shared-timeline runner still needed for V2 correlation-sizing backtest validation and intratrade capital overlap (V1 live discount shipped Apr 29 without it — backtest is single-symbol so N=1 always). |
| SLV 2026 HIGH_VOL anomaly | monitoring | SLV showing 27.7% HIGH_VOL in 2026 vs 17% for GLD (corrected from earlier 49% figure which used Alpaca-only 5.5yr window). Silver's naturally higher volatility makes the fixed ATR multiplier (1.5×) more sensitive for SLV. Consider symbol-specific ATR thresholds before implementing live regime detection. |
| 15m micro-regime vs daily macro-regime | idea | Current classifier operates on daily bars. A 15m intraday ranging/trending layer may add signal — whether the two layers are independent or redundant is unknown. Test post-portfolio-runner. |
| Post-HIGH_VOL transition as supplementary entry signal | idea | HIGH_VOL → TRENDING_UP 77% of the time for GLD/IAU. First bars of a new uptrend after a volatility spike are often strong. Speculative — requires backtesting before use. |

---

## Regime-Aware Asset Rotation (strategic direction — Apr 29 2026)

Combines two settled findings:
1. **Framework generalises across liquid ETFs.** Apr 28 held-out test (12 novel assets, all positive single-run) + boundary verification (SPY/QQQ/IWM/DIA all pass on validated recipe). The position-management framework works on any reasonably liquid intraday-volatile asset whose driver is not rates-dominated.
2. **Framework's Sharpe varies by regime.** Apr 29 long-window backtest (`long-window-validation.md`) ranks regimes: sustained directional moves +2.0–2.6 Sharpe (strongest) > chop ~+1.5 (decent) > sharp-top / transition +0.8–1.1 (weakest, with elevated DD).

**Thesis:** instead of running 7 fixed bots, scan a 30–50 ETF universe daily, classify each asset's regime, and route capital toward assets currently in a strong-regime state. Assets in TRANSITION pause; assets in TRENDING_UP / sustained TRENDING_DOWN activate. The cluster-correlation problem (gold 4-bot pile-up) softens because if metals are in TRANSITION, capital flows elsewhere.

**This does NOT add capacity.** 25% notional cap × 4 simultaneous positions = 100% equity. Rotation is a *quality* lift (better-regime selection), not a *capacity* lift. The right question is whether avoiding bad regimes adds enough Sharpe to justify the engineering work.

| Item | Status | Notes |
|------|--------|-------|
| 30-asset regime scan (observational) | **next — cheap first step** | One-evening project. Pick ~30 liquid ETFs (gold cluster + energy + 6 sectors XLF/XLK/XLI/XLV/XLY/XLP + biotech + small-cap + REITs + EFA/EEM + GBTC + TLT + DBA + UUP + VXX + IBB + SMH + KRE + ITA + ARKK + EWZ + others). Fetch daily bars via yfinance. Run `regime_classifier.py` on each. Print today's classification + duration in regime + 60-day trend persistence. Decision rule: if 8–15 of 30 are in favourable regime on a typical day, rotation has real selection power; if 25+ are favourable always, rotation lift is small. **No live changes.** Output: a script `backend/analysis/regime_universe_scan.py` + a snapshot `.claude/strategies/regime-universe-snapshot.md` updated weekly. |
| Historical regime distribution (rolling) | next | Once the snapshot script exists, extend it to compute the time-series of "how many assets in favourable regime" across 2009–2026. If the count is stable around 8–15, rotation works. If it spikes to 28 in bull-everything markets and drops to 3 in 2008-style universal-bear, rotation has structural blind spots worth knowing about. Uses HistData where available + yfinance daily for the rest. |
| Sharp-top / transition detector | depends on (above) | Already promoted in Regime-Aware Sizing section. The exit signal for rotation is the entry signal for "pause this bot." Definition candidate: ATR spike >2× 50-bar mean **and** close crosses 200-SMA opposite to 60-day prior trend **and** ADX rising. Backtest the detector on the 18-cell HistData windows — does it correctly tag the XAGUSD 2011 peak / WTIUSD 2014–16 collapse / XAUUSD 2011 transition? If yes, ship it. |
| Shared-timeline portfolio runner | **gating — already on Critical Path** | Cannot honestly backtest rotation rules without it. Rotation requires simulating "today, which 4 of 30 are active" across years of history, with shared capital and correlation-aware sizing. Same prerequisite as V2 correlation-sizing validation. |
| Rotation rule backtest | idea — depends on portfolio runner | Once shared-timeline runner exists, backtest rules of form: "activate top N assets by sustained-trend score, deactivate on TRANSITION." Compare to fixed-7-bot baseline on Sharpe / DD / max correlated exposure. Decision rule: rotation lift > +0.3 Sharpe over fixed lineup → build coordinator. |
| Live coordinator architecture | idea — multi-week | If rotation backtest passes, build a daily scan + bot activation/deactivation system. Currently each bot is an independent pm2 process; coordinator needs to start/stop them based on the morning's regime scan. Real engineering work — defer until backtest evidence justifies it. |
| Universe selection bias | watch | "Pick today's 30 liquid ETFs" is a survivorship-biased universe. To honestly backtest, the universe at backtest-date T should reflect what was liquid at T, not what's liquid in 2026. Acceptable shortcut for v1: filter to ETFs that existed at the start of the backtest window. Hard fix: requires historical liquidity data. |

---

## Regime-First Research Programme

Paradigm shift: treat profitability as a regime × strategy interaction rather than a strategy property. A strategy isn't "good" or "bad" — it's "good in RANGING, bad in TRENDING_DOWN." Compose a portfolio of regime-specialist strategies, route capital by current regime. Resurrect previously-rejected strategies (their aggregate-Sharpe rejection may have hidden regime-specific edges).

| Item | Status | Notes |
|------|--------|-------|
| Phase 1 — per-regime trade tagging (diagnostic) | merged | Merged into Regime-Aware Sizing → "Per-regime strategy performance analysis / Phase 1 diagnostic". Apr 23 result is partial gradient, not a broad green light for live regime-aware sizing. |
| Phase 2 — resurrect dead strategies regime-segmented | idea, partially pre-empted | **Apr 28 update:** the boundary-verification rerun of SPY/QQQ/IWM/DIA on validated recipe (now urgent in "Deferred / Rerun" section above) will partially answer this without needing regime segmentation. If they pass aggregate, Phase 2 is moot — they're just validated assets. If they still fail aggregate, Phase 2 (regime-segmented rerun) becomes the next test. Defer until aggregate retest result is in. (Original concrete candidates: SPY/QQQ/IWM/DIA at 15m, 1h XLE/OIH/XOP at 15m, MACDBollinger at validated TFs.) Gate unchanged: regime-segmented Sharpe ≥ 2.0 with N ≥ 50 trades in that regime. |
| Cross-asset regime generalisation test | idea | Does a strategy tuned for GLD-RANGING work on SLV-RANGING, XLE-RANGING, SPY-RANGING? Two hypotheses: (1) regime is universal physics — one strategy per regime across all assets; (2) regime + asset family is the right grain — metals-RANGING generalises but ≠ equity-RANGING. Existing evidence hints at #2 (GDX vs GLD transition asymmetry) but validated params work on all 4 metals without retuning. Gate: Phase 1. |
| Regime-predictive entry signal | idea | Use transition-matrix probabilities + current regime duration as supplementary entry gate. Example: HIGH_VOL → TRENDING_UP 77% for GLD, so late-HIGH_VOL entries get a confidence boost. Supersedes "Post-HIGH_VOL transition as supplementary entry signal" in Regime-Aware Sizing. Speculative — requires backtesting. |
| Per-regime parameter optimisation | idea | Maybe the right OB/OS in RANGING isn't the right OB/OS in TRENDING_UP. Walk-forward honestly: train on regime segments in years 1-N, test on same regime in year N+1. High overfitting risk — keep parameter grids small. Gate: Phase 2. |

**Known risks / caveats:**
- **Sample size collapse** — per-regime trade counts get small fast. HIGH_VOL has ~120 bars across 20 years; some strategy/regime pairs will have single-digit trade counts.
- **Regime detection lag** — classifier uses 200 SMA + 14 ADX; by the time "TRENDING_UP" is labelled, you're 10-20 days in. Backtests must simulate lag honestly for live-relevant conclusions.
- **Regime boundaries aren't crisp** — ADX 24 (RANGING) vs ADX 26 (TRENDING_UP) are near-identical in character. Threshold artefacts.
- **Overfitting multiplies** — N strategies × 4 regimes × 4+ symbols × parameter sweeps is a large search space.

---

## Strategy Validation

| Item | Status | Notes |
|------|--------|-------|
| XLE: deploy as 5th paper bot | idea | Lower priority than getting core 4 to real money. Gate: calibration ✅ + trail confirmed ✅ + sizing implemented. 4–8 week forward test as Rolling Validation Test #1. See stochrsi-enhanced-xle.md for validated params and performance. |
| EventSurprise: paper test CPI-only config | idea | CPI-only is strongest signal (86% WR, 14 trades over 5 years). Paper test on cloud first. See event-surprise.md for strategy params and backtest commands. |
| EventSurprise: rerun with extended data through Apr 2026 | idea | Adds ~3 CPI prints since Feb 17 backtest. Sample is so small (14 trades) that 2–3 more is materially significant for win-rate confidence. Cheap rerun. |
| EventSurprise: test wider hold windows (8/16 bars) | idea | Current default is hold_bars=4 (1h on 15m TF). Test whether longer holds capture more of the post-event move. |
| EventSurprise: test on SLV/IAU | idea | Same precious metals drivers as GLD. May generalise — backtests would confirm. |
| EventSurprise: explore FOMC rate decisions | idea | Similar economic surprise structure to CPI. Research phase only — need to add FOMC to event data loader. |
| EventSurprise: combine with StochRSI as entry filter | idea | Use StochRSI oversold as an additional gate for event entries. May reduce false positives on all-events config. |
| EventSurprise: explore surprise magnitude for position sizing | idea | Larger surprise → stronger expected move → larger position. Needs per-event-type magnitude distribution analysis. |

### Held-out generalisation test — Apr 28 2026

| Item | Status | Notes |
|------|--------|-------|
| Held-out test on 12 novel assets (XLF/XLV/XLI/XLK/KRE/UUP/GBTC/EWZ/ITA/VXX/ARKK/TQQQ) | **complete — interpretation resolved Apr 28** | All 12 produced positive returns single-run on validated recipe + extended window. Range +10% (UUP) to +200% (VXX). Combined with the Apr 28 boundary verification (SPY/QQQ/IWM/DIA all also pass), the through-line is consistent: the strategy is a general 15m microstructure mean-reversion edge that works on liquid ETFs whose driver is not rates/curve dynamics. Returns scale with underlying volatility (learning #8). Artefact risks (long-bias, survivorship, recipe over-robustness) remain valid concerns but the simpler explanation now fits. See `research-log.md` → "Held-Out Generalisation Test" + "Boundary Verification — Apr 28 2026". |
| **Boundary verification: re-run SPY/QQQ/IWM/DIA/TLT with validated recipe** | **resolved — Apr 28 2026** | All 4 broad indices pass: IWM +57.42% / 1.43% DD / 655 / 46% WR; DIA +27.32% / 2.56% / 639 / 40%; QQQ +27.17% / 2.19% / 733 / 40%; SPY +21.94% / 2.02% / 655 / 40% (window 2020-07-27 → 2026-04-27, Alpaca's 15m horizon). TLT already rejected separately. **Boundary on broad indices was illusory** — driven by old params + broken stop-check engine. Real boundary is on driver class (rates-dominated assets like TLT fail), not asset class. Returns scale with underlying volatility per learning #8. Cross-cutting learning #10 updated. See `research-log.md` → "Boundary Verification — Apr 28 2026" for full interpretation. |
| Long-bias / regime artefact control | idea | The 2020–2026 window is a sustained bull market. Even VXX shorts won because vol declined on average. Worth running the strategy on intraday data from a non-bull regime (2007–2010 bear, 2000–2003 dot-com unwind) — but Alpaca history doesn't reach back that far. Alternative: synthetic stress test by inverting the price series, or reweight the equity curve to remove the rising-tide component. Speculative — not actionable until we have a way to source older intraday data. |
| Survivorship bias check | idea | Test set was all liquid 2026 survivors. Strategy might fail on names that delisted or crashed. Hard to test cleanly — need a list of failed ETFs with intraday data. Low priority until boundary is resolved. |
| WF validation for held-out passers + SPY/QQQ/IWM/DIA | **deprioritised** — not a deployment path | Apr 28 evening reframing: the 16 single-run passers (12 held-out + 4 indices) are NOT viable deployment candidates without (a) WF validation, (b) Sharpe verification per-asset, (c) random-entry test on each, (d) inversion test to check regime-dependence, (e) correlation analysis vs existing 3 clusters. **Of the 16, only IWM has Sharpe ≥ 2.0 verified AND direction-agnostic profile (Test 3) AND low correlation to the existing lineup.** IWM is the *only* sensible single-bot expansion candidate. **Apr 29 update:** correlation-aware sizing V1 is shipped, so the IWM gate is now downgraded from "still gated on correlation-aware sizing" to "gated on live verification of the discount mechanism on the existing 7 bots." The other 15 are interesting data points, not next bots. |

### Forgotten-asset retests (Apr 27 2026 audit) — first-pass results in

DB inventory found 5,380 experiments from Feb 11–12 2026 — pre-Apr-4-fix, pre-validated-recipe, on shorter data window. Several borderline candidates (Sharpe 1.0–1.5) sat close enough to the 2.0 quality bar that a current-best-practices rerun could promote them. See `research-log.md` → "Forgotten Testing Surface Audit" for inventory and rationale.

**Apr 28 2026 first-pass result: 3 of 4 forgotten StochRSI candidates passed the single-run gate.** Walk-forward validation is the next required step before any deployment.

| Item | Status | Notes |
|------|--------|-------|
| XBI 15m StochRSI Enhanced rerun | **passed first gate** | +84.75% / 2.44% DD / 602 trades / 43% WR. Domain file `stochrsi-enhanced-xbi.md`. Likely diversifier (biotech largely uncorrelated with metals/energy). 2025–2026 weakening worth investigating. **Walk-forward 4-window required before deployment.** |
| OIH 15m StochRSI Enhanced rerun | **passed first gate** ⭐ | **+146.53% / 2.95% DD / 589 trades / 42% WR — highest single-asset return ever tested.** Domain file `stochrsi-enhanced-oih.md`. Every full year +12% to +22%. **Walk-forward 4-window required before deployment.** |
| TLT 15m StochRSI Enhanced rerun | **rejected** | +20.87% / 1.16% DD / 866 trades / 40% WR over ~6 years. Below quality bar. Confirms bonds don't have intraday mean-reversion edge — rates dynamics dominate. Useful negative finding: the StochRSI 15m edge isn't truly universal. No domain file. |
| XOP 15m StochRSI Enhanced rerun | **passed first gate** | +90.34% / 3.29% DD / 629 trades / 42% WR. Domain file `stochrsi-enhanced-xop.md`. Highly correlated with XLE/OIH — pick strongest of the three rather than running all. **Walk-forward 4-window required before deployment.** |
| Walk-forward validation for OIH/XBI/XOP | **resolved** | Apr 28: all 3 pass 4/4 windows positive. OIH +35–57% per window, XBI +17–39%, XOP +25–40%. Win rates 41–47% across all windows. Edge generalises across COVID/post-COVID/2022 bear/2023 recovery/2024–2025 bull. Cards updated; status promoted from candidate to validated. Sharpe + cross-correlation analysis still pending before deployment. |
| Cross-correlation analysis: XLE/OIH/XOP overlap | **next** | All three energy ETFs validated, but they likely move together. Running multiple energy bots = amplifying portfolio risk, not diversifying. Compute pairwise correlations of the equity curves; pick the strongest one for deployment. Quick analysis on existing data, no new backtest needed. |
| Cross-correlation: XBI vs metals | **next** | Diversification claim for XBI is unverified. If XBI's equity curve correlates near-zero with the metals, it's the strongest portfolio addition (most directly relevant to Critical Path correlation-aware-sizing). If it correlates highly, it adds less than expected. |
| Sharpe computation for all verified runs | **resolved — Apr 28 2026** | Extended `backend/engine/backtester.py` to compute annualised Sharpe from the equity curve (daily-resampled, √252 annualisation); runner prints it. Verified for all 8 validated assets full-strategy, 4 metals long-only, and 4 boundary indices. Headline: **6 of 8 validated lineup cleanly clear Sharpe ≥ 2.0** (GLD 2.48, SLV 2.46, GDX 2.46, OIH 2.33, XLE 2.30, XBI 2.18). XOP at 1.98 is at the bar; IAU at 1.95 falls just under. **GLD and SLV long-only Sharpes exceed full-strategy** (2.57, 2.47) — shorts hurt DD-adjusted return on these two. **IWM 2.30 ✓** is the only broad index that clears the quality bar; SPY/QQQ/DIA below. See CLAUDE.md → Validated Edges for full table. |
| DonchianBreakoutStrategy on metals (validated mindset) | idea | Old GLD 15m result Sharpe 1.50 with 3,226 trades — high trade count suggests over-trading, but Sharpe is real and undocumented. Donchian is trend-breakout, the *opposite* shape from StochRSI mean-reversion — could be a regime-complement (works in TRENDING_UP where StochRSI Sharpe drops to ~3.3 on metals). Apply skip Monday + ADX filter, run on GLD/IAU/SLV/GDX 15m. Gate: regime-segmented Sharpe ≥ 2.0 in TRENDING_UP with N ≥ 50. |
| MACDBollingerStrategy: confirm dead | idea | Old best Sharpe 0.46 (IWM 4h). Cheap single rerun on GLD 15m with validated mindset. If it stays below 1.0, mark dead in research-log and stop revisiting. |

---

## Chart / Frontend

| Item | Status | Notes |
|------|--------|-------|
| Chart trade overlays (Stage 2) | in progress | Fetch entries/exits from live_trade_log, plot entry/exit markers on existing candlestick chart at /chart. No blockers — can be done anytime. |

---

## Platform / Housekeeping

| Item | Status | Notes |
|------|--------|-------|
| Time-of-day filter backtest | idea | Market open (13:31–14:15 UTC) is consistently the most active and profitable window in the live dataset. Whether this is a persistent edge or regime-specific (post-crash bouncing at open) is unknown. Test as explicit entry_hour_start/end parameter post-real-money. |
| GDX separate params investigation | monitoring | GDX behaves structurally differently (mining equity beta layered on physical metal beta). Wait for real-money data window before deciding. Do not adjust params before clear evidence of structural divergence vs regime effect. |
| Overnight hold strategy variant | idea | The GDX Mar 20→23 multi-day hold (+3.267/share) outperformed 49 other trades. Validated params partially capture this (trail after 10 bars). An explicit multi-day hold variant (wider trail, longer min_hold) is a post-calibration, post-validated-params question. |
| Alpaca MCP: validate remaining tools | idea | get_portfolio_history, get_stock_bars, get_calendar, get_corporate_action_announcements, get_account_activities(FILL) — referenced in alpaca-mcp.md as planned for Apr 20 use but not yet formally confirmed. Use in next audit session and promote confirmed behaviour to alpaca-mcp.md Knowledge. |
| Daily-bar split-adjustment consistency | idea | Surfaced Apr 23 during gap-distribution analysis. `price_data_daily` for IAU has a ~1.0× split-adjustment inconsistency at the Alpaca/Yahoo data-source boundary (2 artifact rows). SLV has 1. Current gap analysis filters `|gap| > 15%` as a workaround. Real fix: refetch with unified adjustment (yfinance uses `auto_adjust=True`; Alpaca adjustments may differ). Low priority — only affects daily-bar analyses, not the 15m intraday backtests. |

---

## Deferred / Rerun When Real-Money Window Matures

> **Apr 27 2026 escalation:** The Apr 4 "post-fix" headlines on the GLD card (and likely the other metals cards) are **transcription errors**, not stale-but-correct figures. Today's verified rerun on GLD shows 689 trades / +42.25% on the 2020–2025 window, vs the card's claimed 465 trades / +39.22%. The Apr 4 stop-check fix IS in place and active — engine is healthy. The fix produces a small (~3%) trade-count reduction, not the 35% claimed. See `stochrsi-enhanced-gld.md` → Apr 27 correction for the full investigation. **This makes the rerun queue more urgent: the strategy cards are wrong, not just stale.** Until rerun, treat headline figures on IAU/SLV/GDX cards (and all derived numbers in CLAUDE.md and elsewhere) as suspect.

| Item | Status | Notes |
|------|--------|-------|
| Rerun post-fix backtests across IAU/SLV/GDX/XLE | **resolved** | All 5 verified Apr 27. Returns higher than cards claimed for 4 of 5 (GLD +49.83%, IAU +40.05%, SLV **+144.26%**, GDX +132.91%, XLE +80.42% on 2020 → Apr 27 window). SLV most dramatically wrong on the prior card (+144% verified vs +98% transcribed). Trade counts higher across the board. DDs slightly higher (1–2% rather than <1% for metals). Cards updated with verified figures and per-asset correction notes. |
| Recompute Sharpe for verified runs | **resolved — Apr 28 2026** | Backtester now computes Sharpe (daily-resampled equity curve × √252); runner prints it. See Strategy Validation → "Sharpe computation for all verified runs" above for the headline. Net result vs unverified card claims: GLD 2.48 vs 2.47 ✓, SLV 2.46 vs 2.41 ✓, GDX 2.46 vs 2.58 (lower than claim), IAU 1.95 vs 1.97 (~match, just under bar), XLE 2.30 vs 2.06 (higher than claim). |
| Long-only Sharpe baseline rerun | **resolved** | Verified Apr 28 (extended window). GLD +37.46% / 0.89% DD / 494 trades; IAU +26.09% / 0.68% / 467; **SLV +94.53% / 1.14% / 359**; GDX +79.87% / 1.21% / 375. Same pattern as full-strategy reruns — old estimates were too pessimistic, especially SLV (~+65% estimate vs +94.53% verified). All 4 still profitable long-only with smaller DDs than full strategy (long-only is the smoother / slower variant). **Sharpe verified Apr 28: GLD 2.57, SLV 2.47, GDX 1.89, IAU 1.86 — GLD and SLV long-only beat their full-strategy Sharpes (2.48, 2.46), shorts hurt DD-adjusted return on these two; GDX/IAU lose Sharpe when shorts are removed.** Cards updated. |
| Year-by-year + parameter sensitivity tables | deferred | GLD year-by-year now verified (Apr 27). IAU/SLV/GDX/XLE year-by-year still pre-fix. Param sensitivity (trail_atr=1.5/2.5, trail_after_bars 5/15, OB/OS variants, min_hold_bars 5/15) all pre-fix on all cards. Special interest: Feb 27 audit flagged trail_atr=1.5 at +47.5% vs +43% — if that holds post-fix, it's a parameter improvement worth deploying live. |
| pm2 + DB cross-check of Apr 8–13 live trades | deferred | live-trade-log.md Apr 8–13 rows are MCP-verified but pm2/DB cross-check was never completed. Calibration closed Apr 13, MCP is canonical. Backfill only if a future audit needs full three-source reconciliation. Low priority. |

---

## Resolved

| Item | Resolution | Date |
|------|-----------|------|
| Calibration Layers 1 / 2 / 4 | PASS — 75/75 trades 1.00x ratio, Layer 2 intraday aligned, Layer 4 directional correct (2.8× live vs backtest explained by shared-capital stacking) | Apr 13 2026 |
| Overnight stop model hypothesis | Refuted — live runner.py:934 and backtester both preserve current_sl across overnight gap. Symmetric. No fix needed. | Apr 13 2026 |
| Residual 0.90x under-prediction | Fixed — partial-bar guard at market open. Bar-completion guard detects overnight gap >60 min, defers on_bar until bar ≥14 min old. | Apr 3 2026 |
| K/TS exit ratio backtest mismatch (92% stops) | Fixed — stop-check ordering bug. Backtest was ratcheting trail then immediately checking low against new stop. Fix: capture sl_for_check before ratchet. Now 50/50 K/TS matching live. | Apr 4 2026 |
| Stop slippage characterised | Median $0.010, mean $0.025, 100% negative direction on 33 exits. Known bias — will cause slight P&L overstatement in Layer 4. No model change yet — revisit after Layer 3 with ~50 samples. | Apr 8 2026 |
| Validated params whole-share sizing + short broker code | Deployed Apr 15-16. 340+ shares per position confirmed. First short (GLD Apr 16, K-exit +$38.50) confirmed working. | Apr 16 2026 |
| GTC stop fix | Stop orders switched to GTC TIF — eliminates overnight DAY expiry gap permanently. Whole-share sizing removes Alpaca's GTC restriction for fractional. | Apr 17 2026 |
| Validated 2.0 ATR trail fires in profit | Confirmed — SLV Apr 20: trail ratcheted $70.72→$72.14, server stop executed at $72.12 (entry $71.29 → +$283.86). The mechanism that drives Sharpe 2.47 is live and working. | Apr 20 2026 |
| Short stop-loss execution confirmation | Server-side stop mechanism is direction-agnostic — confirmed working for longs (SLV Apr 20 trail, GLD Mar 10 hard stop). **Organic short stop fire confirmed Apr 23** — IAU short entered 13:44 @ $89.05, buy-stop @ $89.09 fired 16:51 @ $89.10 against us. Slippage +0.010/share. Closes the awaited data point. | Apr 23 2026 |
| pm2 startup registered as systemd service | Survives server reboots permanently. Registered Apr 20. | Apr 20 2026 |
| GDX zero trades (pre-Mar 16) | Resolved — GDX started trading Mar 16 after zero trades previously. Cause was threshold mismatch. | Mar 16 2026 |
| Pre-market signal bug | Fixed Mar 16 — market hours gate added to runner.py on_bar(). | Mar 16 2026 |
| Trailing stop race condition (GDX) | Fixed Mar 19 — cancel async + 1s sleep before new stop placed after shares freed. | Mar 19 2026 |
| Overnight stop gap (DAY TIF expiry) | Fixed Apr 2 — loop re-places stop before on_bar if pending_stop_order_id is None. | Apr 2 2026 |
| Bar-completion guard (partial bar at open) | Fixed Apr 3 — detects overnight gap >60 min, defers on_bar until bar ≥14 min old. | Apr 3 2026 |
| Phantom sell warning (blocked short entry logged as duplicate exit) | Resolved by whole-share sizing deployment Apr 15-16. Shorts now execute — the blocked-short condition no longer occurs. | Apr 16 2026 |
| Wash trade prevention | Fixed Mar 16 — cancel_all_orders_for_symbol called at top of long-entry path before placing order. | Mar 16 2026 |
