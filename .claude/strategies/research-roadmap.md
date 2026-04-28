Status: current | Epistemic: mixed | Last verified: 2026-04-28

# Research Roadmap — Algo Trader V1

Single source of truth for all open ideas, questions, and in-flight work.
Domain files hold confirmed knowledge. This file tracks everything we're still figuring out.

Status labels: `idea` | `in progress` | `validated` | `rejected` | `monitoring`

---

## Framework Attribution — Apr 28 2026 (NEW, blocking interpretation of all signal work)

Random-entry control (`research-log.md` → "Random-Entry Control") shows the StochRSI entry contributes only a small fraction of total Sharpe; the framework (trail + ADX filter + sizing + K-cross exit + min-hold) is doing most of the work. Future "does the strategy work on X?" tests are uninformative until ablations identify which framework component is load-bearing. **All "test on more assets" items are deprioritised below this section.**

| Item | Status | Notes |
|------|--------|-------|
| Ablation 1 — fully random (random entries + random exits + stop only) | next | Establishes baseline Sharpe for the trail+stop+sizing framework with no signal. Run on GLD/SLV/QQQ. If Sharpe stays ≥1.5, framework alone is the edge. |
| Ablation 2 — no trailing stop (fixed stop only) | next | If Sharpe collapses, the trail is the load-bearing component. |
| Ablation 3 — no ADX filter | next | If Sharpe collapses, the ranging-regime constraint is the load-bearing component. |
| Ablation 4 — no K-cross exit (stop/trail only) | next | Tests whether the K signal carries exit information. |
| Ablation 5 — no min-hold | next | If Sharpe survives, min-hold isn't load-bearing. |
| Long-bias / regime artefact control (synthetic price inversion) | next | Run validated recipe on inverted price series for SPY/GLD. If Sharpe survives, the strategy is direction-agnostic (volatility capture). If it collapses, real directional edge exists. Cheap proxy for "what would this look like outside a bull market." |
| Buy-and-hold comparison | next | For GLD/SLV/SPY: how does the strategy's return + Sharpe compare to simple buy-and-hold over the same window? If buy-and-hold matches or exceeds, we're capturing pure beta + position-sizing risk-adjustment. |

---

## Critical Path — To Real Money

| Item | Status | Notes |
|------|--------|-------|
| Correlation-aware sizing | in progress | GLD/IAU/SLV enter simultaneously multiple times per week. At 2% risk per trade, 3 simultaneous entries = 6% portfolio in one correlated move. Need shared-timeline portfolio runner first. Then: tally joint outcomes by year → decide fixed exposure cap vs scaling function. Pre-real-money requirement. **Apr 23: identified as the single remaining tail-risk concern after gap-distribution analysis closed the single-symbol gap-policy item. A correlated 4-symbol overnight gap at p99 = ~5% single-day equity DD — the largest unbounded tail in the system today.** |
| ATR-based position sizing | in progress | Back-calculate shares from fixed max risk % (e.g. 1% of account ÷ stop distance = shares). Normalises risk per trade across volatile/calm sessions. Implement alongside correlation sizing — both are pre-real-money. |
| Late-session entry guard | in progress | Block or halve size when entry fires within ~30 min of market close. GTC stops survive overnight, but DAY stops (any remaining fractional positions) expire before providing protection. Apr 8 triple late-entry data point (SLV/GLD/GDX at 19:46 UTC): resolved next morning, net slightly negative on a sample of 3. Testable with existing single-symbol engine (simple time condition in on_bar). |
| Overnight hold / gap policy | resolved | Apr 23 2026. Gap distribution analysis (`.claude/calibration/gap-distribution.md`, `backend/analysis/gap_distribution.py`) shows single-symbol gap risk is already bounded by the 25% notional cap: SLV p99 gap 5.25% × 25% = 1.31% equity DD, worst historical gap (SLV -13.87%) = 3.47%. Apr 23 actual: -0.64%. An explicit 1% gap budget is a no-op at current equity (notional cap binds first for all 4 symbols). No code change needed. Residual tail risk is **correlated gaps across all 4 symbols simultaneously** — addressed under the existing Correlation-aware sizing item, not a separate fix. |

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
| Regime-aware sizing backtest | monitoring | Apr 23 closed-trade portfolio replay complete: `python3 -m backend.analysis.regime_sizing_portfolio` writes `.claude/strategies/regime-sizing-portfolio-diagnostic.md`. Broad regime multipliers do **not** improve drawdown-adjusted performance: baseline daily Sharpe 4.27 beats conservative 4.15, aggressive 4.00, high-vol-only 4.19. Conservative reduces max DD by ~$90 but gives up ~$4,041 P&L. Treat regime as context/high-conviction filter only; do not implement broad live regime sizing. Full shared-timeline runner still needed for correlation-aware sizing and intratrade capital overlap. |
| SLV 2026 HIGH_VOL anomaly | monitoring | SLV showing 27.7% HIGH_VOL in 2026 vs 17% for GLD (corrected from earlier 49% figure which used Alpaca-only 5.5yr window). Silver's naturally higher volatility makes the fixed ATR multiplier (1.5×) more sensitive for SLV. Consider symbol-specific ATR thresholds before implementing live regime detection. |
| 15m micro-regime vs daily macro-regime | idea | Current classifier operates on daily bars. A 15m intraday ranging/trending layer may add signal — whether the two layers are independent or redundant is unknown. Test post-portfolio-runner. |
| Post-HIGH_VOL transition as supplementary entry signal | idea | HIGH_VOL → TRENDING_UP 77% of the time for GLD/IAU. First bars of a new uptrend after a volatility spike are often strong. Speculative — requires backtesting before use. |

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
| WF validation for held-out passers + SPY/QQQ/IWM/DIA | **promoted — pending** | Apr 28 boundary retest confirmed broad indices also pass; combined held-out + boundary universe is now 16 single-run passers (12 held-out + 4 indices). WF 4-window + Sharpe + cross-correlation analysis needed before any qualifies as a deployment candidate. **Lower priority than getting the validated 8 to real money** — adding more assets without correlation-aware sizing increases tail risk rather than reducing it. Triage by DD-adjusted return / correlation profile when revisited. |

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
