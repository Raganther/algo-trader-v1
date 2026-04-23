Status: current | Epistemic: mixed | Last verified: 2026-04-21

# Research Roadmap — Algo Trader V1

Single source of truth for all open ideas, questions, and in-flight work.
Domain files hold confirmed knowledge. This file tracks everything we're still figuring out.

Status labels: `idea` | `in progress` | `validated` | `rejected` | `monitoring`

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
| Layer 3 — stop slippage aggregation | in progress | Refresh median/mean with Apr 9–20 stop exits (33 → ~50 samples). Current: median $0.010/share, mean $0.025/share, 100% negative direction. Decision: add `stop_slippage` param to backtest only after Layer 3 confirms the bias holds on a larger sample. Median ($0.010) is the more reliable model input. |
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
| Per-regime strategy performance analysis | in progress | Tag validated-params backtest trades with daily regime at entry. Compute per-regime win rate / Sharpe / avg P&L. Validates regime sizing empirically rather than theoretically. Gate: portfolio runner. |
| Regime-aware sizing backtest | idea | Run fixed 2% vs dynamic regime-sized (proposed multipliers from regime-analysis.md: RANGING 1.0×, TRENDING_UP 0.75×, HIGH_VOL/DOWN 0.25×) across all 4 symbols. Compare Sharpe and drawdown. Gate: portfolio runner + per-regime analysis. |
| SLV 2026 HIGH_VOL anomaly | monitoring | SLV showing 27.7% HIGH_VOL in 2026 vs 17% for GLD (corrected from earlier 49% figure which used Alpaca-only 5.5yr window). Silver's naturally higher volatility makes the fixed ATR multiplier (1.5×) more sensitive for SLV. Consider symbol-specific ATR thresholds before implementing live regime detection. |
| 15m micro-regime vs daily macro-regime | idea | Current classifier operates on daily bars. A 15m intraday ranging/trending layer may add signal — whether the two layers are independent or redundant is unknown. Test post-portfolio-runner. |
| Post-HIGH_VOL transition as supplementary entry signal | idea | HIGH_VOL → TRENDING_UP 77% of the time for GLD/IAU. First bars of a new uptrend after a volatility spike are often strong. Speculative — requires backtesting before use. |

---

## Regime-First Research Programme

Paradigm shift: treat profitability as a regime × strategy interaction rather than a strategy property. A strategy isn't "good" or "bad" — it's "good in RANGING, bad in TRENDING_DOWN." Compose a portfolio of regime-specialist strategies, route capital by current regime. Resurrect previously-rejected strategies (their aggregate-Sharpe rejection may have hidden regime-specific edges).

| Item | Status | Notes |
|------|--------|-------|
| Phase 1 — per-regime trade tagging (diagnostic) | idea | Tag every validated-params backtest trade with its entry regime. Compute per-regime: win rate, Sharpe, avg P&L, max DD, trade count across GLD/IAU/SLV/GDX. Output: `strategy × asset × regime → performance` table. Answers "does a regime-performance relationship actually exist in our own data?" before building anything further. Cheap — no new infrastructure. Can run before portfolio runner. Overlaps with existing "Per-regime strategy performance analysis" item in Regime-Aware Sizing — merge. |
| Phase 2 — resurrect dead strategies regime-segmented | idea | Re-run old failures (SPY/QQQ/IWM StochRSI 5m-15m, EventSurprise variants, 1h StochRSI on XLE) with validated params, segmented by regime. Hypothesis: aggregate-Sharpe-near-zero is consistent with "works in RANGING, cancels out elsewhere." Gate: Phase 1 confirms regime-performance relationship. |
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
| EventSurprise: test wider hold windows (8/16 bars) | idea | Current default is hold_bars=4 (1h on 15m TF). Test whether longer holds capture more of the post-event move. |
| EventSurprise: test on SLV/IAU | idea | Same precious metals drivers as GLD. May generalise — backtests would confirm. |
| EventSurprise: explore FOMC rate decisions | idea | Similar economic surprise structure to CPI. Research phase only — need to add FOMC to event data loader. |
| EventSurprise: combine with StochRSI as entry filter | idea | Use StochRSI oversold as an additional gate for event entries. May reduce false positives on all-events config. |
| EventSurprise: explore surprise magnitude for position sizing | idea | Larger surprise → stronger expected move → larger position. Needs per-event-type magnitude distribution analysis. |

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

Numbers that are directionally valid but compute against the pre-Apr-4 stop-check logic (or are otherwise estimates). Not blocking — rerun once a real-money sample is large enough for direct comparison.

| Item | Status | Notes |
|------|--------|-------|
| Rerun post-fix backtests across GLD/IAU/SLV/GDX/XLE | deferred | Headline Sharpe / return / max DD figures in the asset strategy cards were computed pre-Apr-4 stop-check fix. Rerun with corrected engine once real-money P&L sample justifies direct comparison. |
| Long-only Sharpe baseline rerun | deferred | Current long-only Sharpe figures (e.g. GLD ~1.80, SLV ~3.10) are estimates. Rerun with `long_only:true` to get clean baselines. Low priority — bots trade both directions. |
| Year-by-year + parameter sensitivity tables | deferred | All 4 strategy cards have year-by-year tables and trail_atr sensitivity tables on pre-fix engine. Rerun alongside item above. |
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
| Short stop-loss execution confirmation | Server-side stop mechanism is direction-agnostic — confirmed working for longs (SLV Apr 20 trail, GLD Mar 10 hard stop). Short path uses the same broker plumbing. Awaiting organic short-against-us fire for final sample, but no longer gating real money. | Apr 20 2026 |
| pm2 startup registered as systemd service | Survives server reboots permanently. Registered Apr 20. | Apr 20 2026 |
| GDX zero trades (pre-Mar 16) | Resolved — GDX started trading Mar 16 after zero trades previously. Cause was threshold mismatch. | Mar 16 2026 |
| Pre-market signal bug | Fixed Mar 16 — market hours gate added to runner.py on_bar(). | Mar 16 2026 |
| Trailing stop race condition (GDX) | Fixed Mar 19 — cancel async + 1s sleep before new stop placed after shares freed. | Mar 19 2026 |
| Overnight stop gap (DAY TIF expiry) | Fixed Apr 2 — loop re-places stop before on_bar if pending_stop_order_id is None. | Apr 2 2026 |
| Bar-completion guard (partial bar at open) | Fixed Apr 3 — detects overnight gap >60 min, defers on_bar until bar ≥14 min old. | Apr 3 2026 |
| Phantom sell warning (blocked short entry logged as duplicate exit) | Resolved by whole-share sizing deployment Apr 15-16. Shorts now execute — the blocked-short condition no longer occurs. | Apr 16 2026 |
| Wash trade prevention | Fixed Mar 16 — cancel_all_orders_for_symbol called at top of long-entry path before placing order. | Mar 16 2026 |
