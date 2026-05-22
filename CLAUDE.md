# Algo Trader V1

## What it is
Algorithmic trading research and live execution platform. Python backend, Next.js frontend.
Modular strategy engine — strategies register in `runner.py` STRATEGY_MAP, run via CLI.
Phase: Forward testing — verifying live execution mechanics on 4 paper bots before real money.

## Session Start
Read in order on every cold start:
1. `.claude/memory/gitlog.md` — recent git saves
2. `.claude/strategies/research-roadmap.md` — in-flight work + open questions

**Before starting any update, new feature, or bug fix — scan the list below and read any relevant domain files first.**

Read on demand only:
- `.claude/procedures/_index.md` — scan at plan creation for relevant how-to patterns
- `.claude/procedures/daily-trade-audit.md` — read when running a daily MCP/pm2/DB audit on live bot trades, or backfilling calibration-window data
- `.claude/harness-v4.md` — read when working on the memory harness, hooks, or knowledge conventions
- `.claude/strategies/trend-framework-gld.md` — read when working on GLD, reviewing long-only vs full strategy, or checking the audit baseline
- `.claude/strategies/trend-framework-iau.md` — read when working on IAU or reviewing 15m strategy params
- `.claude/strategies/trend-framework-slv.md` — read when working on SLV or reviewing 15m strategy params
- `.claude/strategies/trend-framework-gdx.md` — read when working on GDX or reviewing 15m strategy params
- `.claude/strategies/research-log.md` — read when deciding what to experiment on next, reviewing cross-strategy learnings, or planning new forward tests
- `.claude/strategies/composable-results.md` — read when combining strategies or planning composable bot deployment
- `.claude/strategies/trend-framework-xle.md` — read when working on XLE or planning Rolling Validation Test #1
- `.claude/strategies/trend-framework-oih.md` — read when working on OIH (top-tier candidate from Apr 28 audit, +146% verified, needs WF)
- `.claude/strategies/trend-framework-xbi.md` — read when working on XBI (biotech diversifier candidate from Apr 28 audit, +85% verified, needs WF)
- `.claude/strategies/trend-framework-xop.md` — read when working on XOP (energy E&P candidate from Apr 28 audit, +90% verified, needs WF)
- `.claude/strategies/event-surprise.md` — read when researching economic event strategies or revisiting CPI/NFP trading
- `.claude/calibration/calibration-journal.md` — **the single living calibration document.** Status board (10 components × source-of-truth pointers), findings timeline (Apr 13 / May 7 / May 8), live forward-test milestones + named patterns, Layer 3 running sample, methodology, and the archived Apr 13 full results. Read first for any calibration question. **Per-trade detail not here** — query Alpaca MCP `get_orders` or cloud `live_trade_log` table; use `daily-trade-audit.md` procedure. Replaces the prior `calibration-notes.md` + `forward-test-log.md` split (consolidated May 8).
- `.claude/calibration/archive/calibration-window-mar-apr.md` — frozen per-trade ledger for the Mar 20 – Apr 20 calibration window (test params). Historical reference only, no maintenance. Read only if reconstructing what specifically happened in a given calibration-window trade.
- `.claude/calibration/live-performance-report.md` — read when checking live forward-test health (Sharpe / win-rate / right-tail tripwires) vs backtest expectation. Refresh with `python3 -m backend.analysis.live_performance_report`. Headline tripwires: Sharpe<1.0 at 30d / <2.0 at 60d / <2.5 at 90d → degraded; win-rate<35% on 50+ trades → distributional shift; avg-win/avg-loss<1.3 → right tail collapsing.
- `.claude/calibration/live-vs-backtest-iau-diagnostic.md` — read when reasoning about why live Sharpe differs from backtest Sharpe, debugging individual bot underperformance, considering trail-stop changes, or fixing the `--delay 1` backtest mode. **May 7 finding (refined May 8): backtest is structurally optimistic by ~0.4–0.7 Sharpe** because it doesn't model live's 1-bar polling delay. May 8 falsification audit reproduced 0.42 Sharpe of the artifact via data-shift simulation; 0.7 is now an upper bound. Wider trail (2.5 ATR) does NOT mitigate.
- `.claude/strategies/trail-anchor-hwm.md` — read when reasoning about trail-stop behaviour, the live HWM forward-test, or recalibrating validated-edges Sharpe figures. **May 7 result: HWM delivers +0.78 Sharpe (4.95 → 5.73) and −0.36pp DD (3.41% → 3.05%) on long-window 7-bot backtest** — all 7 symbols improve. **HWM DEPLOYED LIVE on all 7 bots May 7 PM** via `"trail_anchor":"hwm"`. **May 8 AM mechanism audit SUPPORTED** (HWM ~2.8× more delay-resistant than close-anchored). **May 8 PM further finding:** the +0.78 lift was measured under the ADX-filter exit-block bug — both close and HWM cells of the A/B were inflated; HWM A/B needs re-run under `adx_filter_mode='entry_only'`. **Live tripwire anchor revised ~5.50 → ~4.0 ±0.5** after the ADX-bug quantification.
- `.claude/calibration/audit-hwm-delay-mechanism.md` — read when reasoning about how much of HWM's +0.78 backtest lift will transfer to live, deciding the live-tripwire anchor, or deciding whether to invest in fixing `--delay 1` (Path 1). Run via `python3 -m backend.analysis.audit_hwm_delay_sensitivity`. Companion machine-readable record at `audit-hwm-delay-mechanism.json` (regenerated alongside the .md on each run). **Caveat May 8 PM:** this audit was run under the ADX-filter exit-block bug (see calibration-journal.md May 8 PM entries) — Δsharpe(close)=0.42 and Δsharpe(hwm)=0.15 magnitudes were partly conflated with the bug; needs re-run under `adx_filter_mode='entry_only'`.
- `.claude/calibration/audit-adx-filter-exit-block.json` — companion to the May 8 PM ADX-filter audit (no .md report — findings folded directly into `calibration-journal.md` §2 timeline). Read when reasoning about why the buggy backtest captures so much more profit than live, or when planning the packaged release that flips `adx_filter_mode` default. Run via `python3 -m backend.analysis.audit_adx_filter_exit_block`.
- `.claude/calibration/gap-distribution.md` — read when sizing overnight-capable positions, evaluating gap-risk policy, or interpreting an overnight gap loss in live trades
- `.claude/integrations/alpaca-mcp.md` — read when using Alpaca MCP tools, running trade audits via MCP, or checking what data is available without SSH
- `.claude/strategies/regime-analysis.md` — read when working on regime classification, regime-aware sizing, interpreting live performance by market environment, or building the regime frontend
- `.claude/strategies/regime-universe-snapshot.md` — read when checking today's per-asset regime label across the 33-asset rotation universe (refreshed by `regime_universe_scan.py`)
- `.claude/strategies/regime-distribution-history.md` — read when reasoning about whether rotation has selection power, the historical favourable-count distribution, or the universal HIGH_VOL kill-switch idea (refreshed by `regime_distribution_history.py`)
- `.claude/strategies/portfolio-runner-baseline.md` — read when reasoning about portfolio-level Sharpe / DD / cluster co-occupancy, validating the correlation-aware sizing discount, or planning V2 work on the portfolio runner. Refreshed by `python3 -m backend.runner portfolio ...`
- `.claude/strategies/portfolio-runner-rotation-v1.md` — read when reasoning about regime-aware asset rotation, the TRENDING_UP V1 result, the rule-vs-strategy conflict (ADX filter rejects what TRENDING_UP activates), or the universe-expansion leverage finding. Refreshed by `python3 -m backend.runner portfolio ... --rotation`.
- `.claude/strategies/portfolio-runner-cap-shrink.md` — read when reasoning about the per-bot notional cap (`position_cap_frac`), 8-bot best-per-cluster lineup, or whether to flip the strategy default 0.25 → 0.125. Refreshed by `python3 -m backend.runner portfolio ... --position-cap-frac N`.
- `.claude/strategies/portfolio-runner-lineup-selection.md` — **read when reasoning about pruning bots from the current 7-bot lineup, or whether per-asset Sharpe < 2.0 disqualifies a bot.** May 10 finding: under HWM + entry_only, Sharpe is monotonic with bot count (4→3.79, 5→3.87, 6→4.01, 7→4.17). Tighter hand-picked lineups all *lose* Sharpe. Even per-asset losers (GDX 1.46, XOP 1.32) add portfolio Sharpe via diversification. The 2.0 per-asset bar is a candidate-addition screen, not a prune threshold.
- `.claude/strategies/regime-stochrsi-diagnostic.md` — read when interpreting Apr 23 per-regime StochRSI results, deciding whether regime-aware sizing is justified, or comparing metals vs other assets
- `.claude/strategies/regime-sizing-portfolio-diagnostic.md` — read when evaluating whether regime multipliers improve portfolio-level return/drawdown before live sizing
- `.claude/strategies/arbitrage-automation-concepts.md` — read when exploring new strategy families (pairs trading, cross-asset, event-driven), evaluating adjacent business ideas, or planning beyond the current 4-symbol setup
- `.claude/strategies/long-window-validation.md` — read when reasoning about how the strategy performs in real bear regimes (XAUUSD/XAGUSD/WTIUSD spot proxies 2009–2026), or interpreting the spot-vs-ETF Sharpe gap when sizing live
- `.claude/strategies/small-capital-deployment.md` — read when planning a real-money pilot below the original $5–10k threshold (e.g. $1k start), reasoning about whole-share rounding tax at small equity, or deciding which symbols become tradable as equity grows. Empirical $1k backtest: +411.83% / Sharpe 3.83 / DD 4.67% on 4-bot SLV/IAU/GDX/XBI lineup at 50% cap.

## Run Commands

### Check bots (MCP — primary method)
When asked to "check bots", run these Alpaca MCP calls in order:
1. `get_clock` — market open/closed, establishes time context
2. `get_all_positions` — any open positions (overnight holds)
3. `get_orders(status="closed", symbols="GLD,IAU,SLV,GDX,OIH,XBI,XOP", after="<today>T00:00:00Z", direction="asc")` — today's completed trades

### Check bots (SSH — process health only)
Use SSH only when MCP can't answer the question: bot process status, application logs, errors/warnings.
```bash
# Bot process health (running/stopped/errored)
gcloud compute ssh algotrader-us --zone=us-east1-b --command="pm2 status"

# Bot logs — errors, warnings, heartbeats (not trade data — use MCP for that)
gcloud compute ssh algotrader-us --zone=us-east1-b --command="for bot in gld-test iau-test slv-test gdx-test oih-test xbi-test xop-test; do echo \"=== \$bot ===\"; logs=\$(ls -t /home/alistairelliman/.pm2/logs/\${bot}-out*.log | head -2); today=\$(echo \"\$logs\" | head -1); yesterday=\$(echo \"\$logs\" | tail -1); echo \"-- today --\"; grep -E 'LIVE BUY|LIVE SELL|FILLED|TRAILING STOP|SERVER STOP|Starting Live|⚠️|❌|⏳' \"\$today\" 2>/dev/null; echo \"-- yesterday --\"; grep -E 'LIVE BUY|LIVE SELL|FILLED|TRAILING STOP|SERVER STOP|Starting Live|⚠️|❌|⏳' \"\$yesterday\" 2>/dev/null; done"
```

### Other commands
```bash
# Backtest (validated params)
python3 -m backend.runner backtest --strategy TrendFramework --symbol GLD --timeframe 15m --start 2020-01-01 --end 2025-12-31 --source alpaca --spread 0.0003 --delay 0 --parameters '{"rsi_period":7,"stoch_period":14,"overbought":80,"oversold":15,"adx_threshold":20,"skip_adx_filter":false,"sl_atr":2.0,"trailing_stop":true,"trail_atr":2.0,"trail_after_bars":10,"min_hold_bars":10,"skip_days":[0]}'

# Portfolio backtest (shared-timeline, multi-symbol, single capital pool — V1 shipped Apr 29 2026)
python3 -m backend.runner portfolio --strategy TrendFramework --symbols GLD,IAU,SLV,GDX,OIH,XBI,XOP --timeframe 15m --start 2020-07-27 --end 2026-04-27 --source alpaca --spread 0.0003 --initial 94000 --parameters '{"rsi_period":7,"stoch_period":14,"overbought":80,"oversold":15,"adx_threshold":20,"skip_adx_filter":false,"sl_atr":2.0,"trailing_stop":true,"trail_atr":2.0,"trail_after_bars":10,"min_hold_bars":10,"skip_days":[0]}'

# Deploy code changes to cloud
git push origin main
gcloud compute ssh algotrader-us --zone=us-east1-b --command="cd algo-trader-v1 && git pull && pm2 restart all"

# Git save
./scripts/git-save.sh "message"

# Live performance report (refresh tripwire snapshot vs backtest expectation)
python3 -m backend.analysis.live_performance_report

# Discovery engine
python -m backend.optimizer.run_overnight [--scan|--quick|--medium] [--max-hours N] [--symbols X,Y]

# Fetch historical price data — Alpaca (recent, Jul 2020 onward)
python3 scripts/fetch_price_data.py --symbols GLD,IAU,SLV,GDX --start 2020-01-01
# Fetch historical price data — Yahoo Finance (full history back to ETF inception, daily bars only)
python3 scripts/fetch_price_data_yfinance.py
```

## Architecture
- **Runner:** `backend/runner.py` — STRATEGY_MAP registers all strategies, CLI entry point for all backtests
- **Registry:** `STRATEGY_MAP` in `runner.py` — add strategy here to make it available
- **Engine:** `backend/engine/` — backtester, data loaders, live broker, paper trader
- **Strategies:** `backend/strategies/` — 21 strategies
- **Indicators:** `backend/indicators/` — StochRSI, RSI, MACD, ADX, Bollinger, ATR, SMA, CHOP
- **DB:** `backend/research.db` — experiments, live trades
- **Frontend:** `frontend/` — Next.js dashboard, DB-driven
- **Harness spec:** `.claude/harness-v4.md` — knowledge conventions, layer model, hook descriptions
- **Roadmap:** `.claude/strategies/research-roadmap.md` — all in-flight work and open questions
- **Strategy notes:** `.claude/strategies/` — domain files, individually listed in Session Start above
- **Calibration journal:** `.claude/calibration/calibration-journal.md` — single living doc; status board + timeline + milestones + patterns + methodology
- **Calibration window archive:** `.claude/calibration/archive/calibration-window-mar-apr.md` — frozen Mar 20–Apr 20 per-trade ledger
- **OpenBrain category:** `.claude/openbrain-category` — `algo-trader`
- **Alpaca MCP:** configured in `~/.claude/settings.json` — 57 tools for market data, orders, positions, portfolio history. No news endpoint. Requires Claude Code restart to activate. Uses existing Alpaca paper trading keys. `uvx` installed at `~/.local/bin/uvx`.
- **Integrations:** `.claude/integrations/alpaca-mcp.md` — full tool reference, high-value tools ranked, usage notes
- **Hooks:** SessionStart (load-context.sh), PreToolUse guard (git-save-guard.sh), PreToolUse naming guard (domain-naming-guard.sh), PostToolUse OpenBrain audit (openbrain-audit-reminder.sh)

## Current Status
Phase: Forward testing — validated params live, path to real money. **7 paper bots running** on cloud (gld-test, iau-test, slv-test, gdx-test, oih-test, xbi-test, xop-test).
Price action chart live at `/chart` — Stage 1 complete (candlestick chart, symbol/range selector). Stage 2 next: trade overlays on chart.

**Bot lineup ≈ 3 independent economic bets, not 7.** Don't reason about the lineup as "7 diversified bots." It's:
- **Gold/precious-metals cluster:** GLD + IAU + SLV + GDX (4 bots, ~1 underlying bet — gold direction). When metals dump, all 4 lose simultaneously.
- **Energy cluster:** OIH + XOP (2 bots, ~1 underlying bet — oil direction). Highly correlated.
- **Biotech:** XBI (1 bot, 1 bet). The only true diversifier currently deployed.

**Capital binding constraint — read together with the portfolio-cap status.** Each bot can take up to **25% of equity per position** (per-bot notional cap, validated). At $94k equity, this means **max 4 bots fully invested simultaneously = 100% notional**. *That mental model is only the binding constraint when the portfolio-level total-notional cap is OFF.* As of Apr 30 PM the portfolio cap is shipped (`correlation_sizing.PORTFOLIO_CAP_ENABLED`, default OFF currently — recommended flip to ON at FRAC=1.0). When it's ON, the binding constraint is *aggregate notional ≤ equity*, not *bot count*. This unlocks per-bot cap shrinking (e.g. 8 bots × 12.5%) — the actually-untested lever from the rotation debrief. See `research-roadmap.md` → Portfolio Infrastructure.

**Apr 30 PM strategic direction (replaces Apr 29 rotation thesis):** rotation as a research direction is closed for StochRSI mean-reversion (V1 TRENDING_UP and V2 RANGING both fail the +0.30 Sharpe gate — the strategy already self-selects regime via its `ADX < 20` filter, so external rotation is redundant or destructive). The replacement priorities are: (1) flip portfolio cap default to ON ✓ done, (2) test per-bot cap shrinking ✓ done — **passes** (see below), (3) test 4-bot best-per-cluster lineup — partially answered by the 8-bot Run 2 of (2). Universe expansion at our scale is a DD-reducer not a Sharpe-lifter (Run B: Sharpe 4.86 → 4.76, DD 3.58% → 2.45%) — adding IWM as bot #8 won't lift Sharpe meaningfully; de-prioritised as a Sharpe-boost play but still valid as a DD-smoothing play if desired.

**Per-bot cap shrinking experiment (Apr 30 PM, PASSES):** New strategy param `position_cap_frac` (default 0.25 — byte-identical baseline) + portfolio-runner CLI flag `--position-cap-frac`. Three runs over 2020-07 → 2026-04, $94k. **Run 0 (7 bots × 25% baseline):** +424.09% / 3.41% / 4.95 / 4344. **Run 1 (7 bots × 12.5% pure cap-shrink):** +236.86% / 1.87% / **5.23** / 4413 → ΔSharpe +0.28, ΔDD −1.54pp ✓. **Run 2 (8 bots × 12.5% best-per-cluster GLD+SLV+OIH+XOP+IWM+SMH+XBI+IBB):** +262.81% / 2.22% / **5.40** / 5004 / max-conc 8 → ΔSharpe +0.45 ✓, ΔDD −1.19pp ✓ — both decision-rule branches clear independently. Returns drop because Sharpe is sizing-invariant (half-cap → half dollar P&L per trade); the apples-to-apples metric is Sharpe + DD%. **Strategic decision pending** (separate from code-ship) on flipping the strategy default 0.25 → 0.125 + reshuffling the live lineup (7 → 8 bots, swap IAU+GDX out for IWM+SMH+IBB). Snapshot: `.claude/strategies/portfolio-runner-cap-shrink.md`. Files changed: `backend/strategies/trend_framework.py` (param + 3 sizing blocks), `backend/runner.py` (CLI flag + injection).

**Apr 30 PM 4-run rotation study (final, single source of truth):**

| Run | Universe | Cap | Rotation | Return | DD | Sharpe | Trades | Max conc |
|---|---:|---:|---|---:|---:|---:|---:|---:|
| Baseline V2 | 7 | OFF | none | 474.67% | 3.58% | **4.86** | 4413 | 7 |
| A: 7 + cap | 7 | 100% | none | 424.09% | 3.41% | **4.95** (+0.09) | 4344 | 7 |
| B: 20 + cap | 20 | 100% | none | 441.81% | 2.45% | **4.76** (−0.10) | 10627 | 14 |
| C: 20 + cap + TRENDING_UP | 20 | 100% | TRENDING_UP | 154.29% | 2.60% | **3.21** (−1.65) | 2836 | 8 |
| D: 20 + cap + RANGING | 20 | 100% | RANGING | 380.37% | 2.85% | **4.49** (−0.37) | 7894 | 12 |

Decision rule: keep change if Sharpe ≥+0.30 lift OR DD ≥−1pp reduction with Sharpe loss ≤0.10.

**Conclusions:**
- **Rotation is closed for this strategy class.** Both directions tested (V1 TRENDING_UP, V2 RANGING) fail the gate. Reason: the strategy's own `ADX < 20` entry filter already self-selects regime at the right (15m) timeframe; an external daily-bar rotation rule is redundant or destructive. Rotation infrastructure (`backend/engine/rotation.py` + CLI flags `--rotation`, `--rotation-rule`, `--rotation-universe`, `--use-cache`) preserved for cheap rule-swap experiments and for future strategy classes that lack internal regime filters (breakouts, momentum, donchian-trend).
- **Portfolio-level total-notional cap shipped + DEFAULT ON since Apr 30 PM** (`correlation_sizing.portfolio_cap_max_size`, helper at `backend/engine/correlation_sizing.py`, CLI flag `--portfolio-cap-frac N` for diagnostic overrides, sizing blocks `min(risk, 25%-per-pos, cluster_max, portfolio_max)`). Module toggle `PORTFOLIO_CAP_ENABLED = True` (FRAC=1.0). **Live behaviour:** baseline reproduces +424.09% / 3.41% / 4.95 Sharpe / 4344 trades / max-conc 7 — the cap binds on gold N=4 stacking (3.5% of bars in the latest run). Tiny structural improvement (+0.09 Sharpe / −0.17pp DD) and a permanent leverage guard. Without it, any future universe expansion would silently run leveraged.
- **Yesterday's +1013% / 6.20 Sharpe headline was 100% leverage** (max-conc 19 × 25% cap = 475% of equity, outside Alpaca Reg-T). Run B with honest exposure collapses to +441.81% / 4.76 Sharpe / DD 2.45%. **Universe expansion at our scale is a DD-reducer, not a Sharpe-lifter.**
- **Untested lever is per-bot cap shrinking.** Drop per-bot cap from 25% → 12.5% so 8 bots run in parallel instead of fighting for 4 slots. Theoretical Sharpe lift via diversification ≈ √(N_new/N_old). Promoted as next experiment alongside the 4-bot best-per-cluster lineup test.

See `.claude/strategies/portfolio-runner-rotation-v1.md` for the final report. Roadmap rows: Portfolio Infrastructure → "Portfolio-level total-notional cap" + "Rotation V1 / V2" + "Per-bot cap shrinking experiment" + "Best-per-cluster 4-bot experiment".

**Cluster-aware notional cap V1 (Apr 30 2026 PM, default OFF):** Direct follow-up to the V2 finding that the 25% per-position cap is the binding constraint. New `correlation_sizing.cluster_cap_max_size(symbol, broker_positions, equity, entry_price)` returns `(equity * CLUSTER_CAP_FRAC - sum(|peer_size| * peer_avg_price)) / entry_price`; sizing blocks become `min(risk, 25%-per-pos cap, cluster_max)`. Module toggle `CLUSTER_CAP_ENABLED` default **False**; portfolio CLI flag `--cluster-cap` enables for diagnostic. **V2 7-bot result @ FRAC=0.50:** Cap OFF (baseline) +474.67% / 3.58% DD / 4.86 Sharpe / 4413 trades vs Cap ON +413.38% / 2.44% DD / 4.72 / 4279. ΔDD −1.14pp clears the 1pp bar but ΔSharpe −0.14 exceeds the 0.1 loss tolerance — **fails the decision rule by a hair**. Cluster co-occupancy confirms the cap binds gold-only (N=4 4.2% → 1.1%, N=3 15.9% → 13.5%); energy + biotech distributions identical. P&L damage entirely in gold ($−57.6k total). Verdict: keep code for diagnostic + future regime-conditional refinement, ship default OFF. The cap is blunt — fires on every gold-pile-up regardless of regime; the actually-dangerous configuration is correlated p99 overnight gaps, a small subset. Next refinement promoted: *regime-conditional* cluster cap (fire only when daily ATR > N× mean OR 60d cluster correlation > 0.7). See `.claude/strategies/portfolio-runner-baseline.md` → "V2 with-vs-without cluster-aware notional cap" and roadmap row "Cluster-aware notional cap (V1, FRAC=0.50)".

**Correlation-aware sizing V1 (live Apr 29 2026; structurally inactive under V2 — Apr 30 2026):** per-trade risk discounted by cluster occupancy. `risk_frac = 0.02 / N`, N = peers held in same cluster + self. Hardcoded clusters: gold = GLD/IAU/SLV/GDX, energy = OIH/XOP/XLE, biotech = XBI. Lives in `backend/engine/correlation_sizing.py`; applied in all three sizing blocks of `trend_framework.py`. Single-symbol backtest unaffected (N=1 always). **Apr 30 2026 finding — the discount changes a number the 25% notional cap then overwrites.** Position size is `min(risk_amt / stop_dist, equity * 0.25 / price)`. For risk to bind tighter than the cap, `stop_dist / price > 8%` at full risk; on 15m metals/energy bars `2 ATR / price ≈ 0.4–1.0%`. With-vs-without portfolio backtest on V2 7-bot baseline: +474.67% (ON) vs +474.87% (OFF), Sharpe 4.86 = 4.86, DD 3.58 = 3.58, trade counts byte-identical. **The cap is doing the correlated-gap protection work, not the discount.** Apr 23 tail-risk concern bounded by 25% × 4 = 100% notional ceiling regardless of discount state. Discount stays in for documentation + the high-volatility regime where it could bind. Toggle `correlation_sizing.DISCOUNT_ENABLED` (default True) + CLI flag `--no-correlation-discount` on the portfolio runner preserved for future apples-to-apples diagnostics. `[CORR-SIZE]` log lines in pm2 still useful as a wiring check (confirms the import is alive and peers are being counted), no longer a deployment-decision gate. See `.claude/strategies/portfolio-runner-baseline.md` for the comparison + memory `notional_cap_dominates.md` for upstream implications.

**Shared-timeline portfolio runner V2 (shipped Apr 30 2026):** `backend/engine/portfolio_runner.py` + `python3 -m backend.runner portfolio ...`. One PaperTrader, N strategy instances on a unified time grid. V2 adds `equity_mode='fixed'` (each bot sizes risk + 25% notional cap off `initial_capital`, no compounding of the equity reference) which mirrors live mechanics: 7 bots on a single $94k Alpaca account each see the same equity number when sizing. Single-symbol runs default to `equity_mode='live'` (compounding) and remain identical to single-symbol backtests. **7-bot V2 baseline (2020-07 → 2026-04, $94k initial): +474.67% / Max DD 3.58% / Sharpe 4.86 / 4,413 trades.** Gold cluster ≥2 members open on 46.7% of bars (≥3 on 20.1%) — the correlation discount has plenty of opportunity to fire, but per the Apr 30 with-vs-without backtest the 25% notional cap binds first on essentially every entry, making the discount structurally inactive (see correlation-aware sizing note above). Snapshot: `.claude/strategies/portfolio-runner-baseline.md`. **About Sharpe:** sizing-invariant by construction — scaling every position by a constant scales mean return and stdev equally, so the ratio is unchanged. V1's Sharpe 5.55 was *not* an upper-bound artefact (only the +10,496% return and 5.05% DD were); V2's 4.86 is slightly lower because Option A reweights early-vs-late-year contributions, but the metric is structurally robust to sizing changes. The portfolio Sharpe reflects diversification across imperfectly-correlated bots (≈ √N × asset Sharpe at low cross-correlation).

**Confirmed working (execution mechanics — separate from edge attribution):** entry placement + K-exit (76–80% win rate across 67+ trades), server-side stop loss, trailing stop in profit (SLV +$283.86 Apr 20), trail ratcheting, whole-share sizing (340+ shares/position), short entry + K-exit (GLD Apr 16 +$38.50), GTC stops (no overnight expiry gap), pm2 startup registered as systemd service, single-symbol overnight gap risk bounded by 25% notional cap (Apr 23 SLV gap-through = -0.64% equity, within p95 of historical distribution). *Note:* the 76–80% win rate reflects what the framework + StochRSI tilt produces in live conditions; per Apr 28 random-entry control, the bulk of the risk-adjusted edge comes from the framework, not from the StochRSI entry signal.

**Execution layer validated (Apr 13 calibration):** Layers 1/2/4 pass. Backtest engine accurate for test params / intraday regime. See `calibration-journal.md` §7 for full results.

**Remaining before real money:** see `research-roadmap.md` → Critical Path section.

**Live bots (validated params):**

| Bot | Symbol | Deployed | OB/OS | ADX thresh | Hold | Trail | Trades/yr |
|-----|--------|----------|-------|------------|------|-------|-----------|
| gld-test | GLD | Apr 15-16 | 80/15 | 20 | 10 bars | after 10 bars (2.0 ATR) | ~115 |
| iau-test | IAU | Apr 15-16 | 80/15 | 20 | 10 bars | after 10 bars (2.0 ATR) | ~115 |
| slv-test | SLV | Apr 15-16 | 80/15 | 20 | 10 bars | after 10 bars (2.0 ATR) | ~95 |
| gdx-test | GDX | Apr 15-16 | 80/15 | 20 | 10 bars | after 10 bars (2.0 ATR) | ~95 |
| oih-test | OIH | Apr 28 | 80/15 | 20 | 10 bars | after 10 bars (2.0 ATR) | ~95 |
| xbi-test | XBI | Apr 28 | 80/15 | 20 | 10 bars | after 10 bars (2.0 ATR) | ~100 |
| xop-test | XOP | Apr 28 | 80/15 | 20 | 10 bars | after 10 bars (2.0 ATR) | ~100 |

Stop orders use GTC TIF (switched Apr 17 — whole-share sizing makes GTC valid for US equities). Shorts enabled. Skip Monday (`skip_days:[0]`). **HWM trail anchor (`trail_anchor:hwm`) deployed live on all 7 bots May 7 PM** — see `trail-anchor-hwm.md`. Forward-test clock reset May 7; HWM-live data accumulates from this point forward.

**Confirmed working:** bot-initiated exits, trailing stop updates (ratchets up), order cancellation before exit, position sync on restart, heartbeat logging, DAY TIF stops, DB reconciliation on startup, server-side stop FIRING (confirmed Mar 10 — SLV stop at $80.49 auto-filled at $80.43). GDX started trading Mar 16 — resolves zero-trade open question.

**Trailing stop FIRING in profit — confirmed Mar 23.** GDX: entry $80.05 (Mar 20), trail ratcheted to $83.35 over 3-day hold, server stop fired intrabar @ $83.317 (+$958 paper). Both server-side exit mechanics now fully confirmed.

**Long-only baseline (verified Apr 28):** Full → long-only Sharpe: GLD 2.48→**2.57** (long-only better!), IAU 1.95→1.86, SLV 2.46→**2.47** (≈), GDX 2.46→1.89. **GLD and SLV long-only beat full-strategy on Sharpe — shorts hurt DD-adjusted return on these two.** GDX and IAU lose Sharpe when shorts are removed. The Mar 14 / Apr 4 estimates (1.80 / 1.20 / 3.10 / 1.65) were not transcribed correctly; verified figures here supersede.

**Two exit mechanics (not three):** (1) bot K-signal exit at candle close, (2) Alpaca server-side stop auto-execution intrabar — covers both stop loss and trailing stop exits.

**Backtest predictions for test params (Dec 2025 – Mar 2026):**

| Symbol | Return | Max DD | Trades | Win Rate |
|--------|--------|--------|--------|----------|
| GLD | +0.16% | 0.77% | 58 | 48% |
| SLV | +14.25% | 1.15% | 44 | 57% |
| GDX | +2.45% | 0.94% | 69 | 59% |
| IAU | -0.50% | 0.99% | 54 | 37% |

## Validated Edges (verified Apr 27–28 2026 on extended window 2020 → Apr 27 2026)

> **May 7 caveat refined May 8 PM — backtest is materially overstated by an ADX-filter exit-block bug.** Sharpe figures below are computed under `trend_framework.py:211-239` early-return that blocks stops + signal-exits when ADX > threshold mid-trade. **A vs C audit (May 8 PM, long-window 7-bot): bug contributes ~50% of return and ~1.23 of the Sharpe (4.95 buggy → 3.72 fixed).** Per-asset Sharpes are likely overstated by similar fractions — needs re-run under `adx_filter_mode='entry_only'`. The earlier 0.4–0.7 Sharpe "delay artifact" estimate was conflating polling delay with the ADX-bug. **Live partially escapes the bug** via server-side stops + ADX dips; realistic live Sharpe expectation revised from ~5.50 (HWM-corrected) to **~4.0 ±0.5**. See `.claude/calibration/calibration-journal.md` §2 May 8 PM entries for the full quantification. HWM trail anchor (`trail_anchor:'hwm'`) lifts long-window Sharpe +0.45 under the fix (May 9 re-run; +0.78 in buggy mode). **`adx_filter_mode` default flipped `'all'` → `'entry_only'` May 21 2026** — the bug-corrected per-asset Sharpes are the right-hand `(May 9, entry_only)` column below; the `(buggy)` columns are retained as historical reference only. Portfolio baseline under the fix: **+212.28% / 3.72 / 2.06%** (`portfolio-runner-baseline.md`, refreshed May 21). The cap-shrink, rotation, and small-capital figures in the Current Status section above were NOT re-run — they remain buggy-`'all'`-mode and are pending.
>
> **Apr 28 2026 edge resolution — three discriminating tests run, results below. Read before interpreting the Sharpe column.**
>
> Three tests run Apr 28 evening to resolve the question "is the edge real, and if so, what is it?" Full details in `research-log.md` → "Edge Question — Test 1/2/3" + "Edge Question — Synthesis (Apr 28 2026)".
>
> **Test 1 — Buy-and-Hold.** Strategy beats B&H on Sharpe across all 12 tested assets (Δ +0.46 to +1.94, median ~+1.4), DD protection 8.5×–26.2×. Every B&H Sharpe is below 2.0; passive holding doesn't clear the bar.
>
> **Test 2 — Fully-Random Ablation.** Random entries + random exits with the same framework match or beat validated Sharpe on 3 of 4 assets (GLD 2.32 vs 2.48, SLV **2.64** vs 2.46, GDX **2.57** vs 2.46, QQQ **2.28** vs 1.45). **The framework alone produces Sharpe ≥ 2.0 with zero signal information.** The StochRSI signal is at best neutral, slightly net-negative on average.
>
> **Test 3 — Synthetic Inversion.** GLD inverted Sharpe collapses 2.48 → **0.85** (real directional edge, depends on bull-regime). SPY inverted Sharpe 1.36 → 1.53 (direction-agnostic).
>
> **Resolved model:** What we built is a **position-management framework** — ATR stop, trailing stop after 10 bars, ADX-ranging filter, 2% fixed-risk sizing, 25% notional cap, skip-Mon, 10-bar min-hold. This framework converts asset volatility into risk-adjusted return better than passive holding (Test 1). It does this without needing any signal (Test 2). On directional/metals assets the framework's edge is regime-dependent (Test 3); on broad indices it's regime-agnostic. The StochRSI entry/exit logic that the project was named around is decorative.
>
> **Implications for the table below:**
> - Sharpes are real and verified. The numbers are accurate.
> - The *interpretation* of those numbers is "framework Sharpe with StochRSI tilt on this asset," not "StochRSI mean-reversion edge on this asset."
> - **Metals Sharpes likely overstate live expectation, but the bear-regime collapse predicted Apr 28 did NOT reproduce in real history.** Apr 29 long-window backtest on HistData spot proxies (XAUUSD 2009–2026, XAGUSD 2009–2026, WTIUSD 2010–2023) shows the framework held through the 2013–15 metals bear (gold Sharpe +1.44, silver +2.04 — comparable to bull periods) and the 2014–16 oil collapse (Sharpe +1.11). The conservative sizing rule still applies but for a different reason: **spot-proxy Sharpe over the 2020+ overlap is ~1.5 vs ETF Sharpe ~2.5 on Alpaca for the same period.** That 0.8–1.0 Sharpe gap suggests an ETF-microstructure premium in the live data that the spot proxy doesn't have. Size for Sharpe 1.0–1.5 expectation (matches spot proxy, more conservative than Alpaca backtest). See `.claude/strategies/long-window-validation.md`.
> - **IWM is now relatively more attractive.** Sharpe 2.30 with regime-agnostic profile is more robust than metals Sharpe 2.46 with regime-dependence.
> - **Regime preference (Apr 29 finding):** the framework is *strongest* in sustained directional moves (bull or bear, Sharpe 2.0–2.6), *decent* in chop/recovery (~1.5), and *weakest in regime transitions / sharp-top / collapse* (0.8–1.1 with elevated DD). Counter-intuitive for a strategy whose entry signal is a mean-reversion oscillator: the trailing-stop + 10-bar-hold is trend-friendly (this is why it was renamed StochRSIMeanReversion → Trend Framework, May 22 2026). The actually-dangerous regime for the live lineup is **post-peak transition**, not bear. See `long-window-validation.md` for the 18-cell ranking.
> - **Strategic direction — regime-aware asset rotation (Apr 29):** combine the Apr 28 "framework generalises across liquid ETFs" + Apr 29 "framework Sharpe varies by regime" findings → scan a 30–50 ETF universe daily, rotate capital toward strong-regime assets, pause bots whose asset is in TRANSITION. Quality lift, not capacity lift (4-position cap unchanged). **Apr 29 universe scan + rolling history both shipped.** `backend/analysis/regime_universe_scan.py` (snapshot `.claude/strategies/regime-universe-snapshot.md`) + `backend/analysis/regime_distribution_history.py` (snapshot `.claude/strategies/regime-distribution-history.md`, CSV `backend/analysis/regime_distribution_history.csv`). **Today: 7/33 favourable — typical**, sits between p10 and p90 of historical distribution. **Rolling history (807 weekly snapshots, 2010-11 → 2026-05): median favourable count = 8, mean 9.1 — exactly inside the 8–15 selective band. Rotation backtest is justified.** Most of the deployed lineup (GLD/IAU/SLV/GDX/XLE/XOP/XBI) is in RANGING right now; only OIH made the TRENDING set. HIGH_VOL is rare in normal tape (median 0) but spikes universally in panics (March 2020 had 3 weeks with 30+ assets in HIGH_VOL). Next gating dependency for rotation = shared-timeline portfolio runner. See `research-roadmap.md` → "Regime-Aware Asset Rotation".
> - Each per-asset card (`trend-framework-<asset>.md`) is the *same* Trend Framework applied to a different asset — one framework, not 8 strategies.

**Two passes on the extended window.** Apr 27 runs (Return/DD/Trades columns) used `dynamic_adx:true` (strategy default — `dynamic_adx:false` was not passed explicitly) → tighter dynamic threshold → ~10–15% more trades. Apr 28 Sharpe runs explicitly pass `dynamic_adx:false` per recipe spec → trade counts ~10–15% lower. Sharpe column is from the Apr 28 (recipe-correct) runs. Apr 27 Return/DD figures are kept here because the WF validations were done at those settings.

| Strategy | Asset | TF | Return (buggy) | DD (buggy) | Trades (buggy) | Sharpe (Apr 28, buggy) | Sharpe (May 9, entry_only) | Δ |
|---|---|---|---|---|---|---|---|---|
| Trend Framework | GLD | 15m | +49.83% | 1.18% | 728 | 2.48 | **2.28** ✓ | −0.20 |
| Trend Framework | IAU | 15m | +40.05% | 1.31% | 705 | 1.95 | 1.88 | −0.07 |
| Trend Framework | SLV | 15m | +144.26% | 2.00% | 581 | 2.46 | **2.19** ✓ | −0.27 |
| Trend Framework | GDX | 15m | +132.91% | 2.01% | 581 | 2.46 | 1.46 | **−1.00** |
| Trend Framework | XLE | 15m | +80.42% | 3.27% | 570 | 2.30 | 1.55 | −0.75 |
| Trend Framework | OIH | 15m | +146.53% | 2.95% | 589 | 2.33 | 1.91 | −0.42 |
| Trend Framework | XOP | 15m | +90.34% | 3.29% | 629 | 1.98 | 1.32 | −0.66 |
| Trend Framework | XBI | 15m | +84.75% | 2.44% | 602 | 2.18 | 1.18 | **−1.00** |

**May 9 2026 update — per-asset Sharpes re-run under `adx_filter_mode='entry_only'` (close-anchored, single-symbol).** Only **GLD (2.28) and SLV (2.19)** still cleanly clear the 2.0 quality bar. Six of eight assets drop below it under bug correction. **GDX and XBI** lose the most (−1.00 each — they were the heaviest bug-beneficiaries). Caveats before reading too much in: (a) these are close-anchored numbers; HWM lift adds ~0.3–0.5 (live runs HWM); (b) live partially escapes the bug via server-side stops + ADX dips, so live per-asset > pure entry_only backtest; (c) **portfolio Sharpe (4.17 under HWM+entry_only) is much higher than per-asset average due to diversification** — the lineup is a portfolio, not 8 standalone bots. Per-asset numbers below 2.0 don't directly invalidate the lineup; they invalidate the "8-of-8 quality candidates" framing.

**May 10 2026 — lineup-selection experiment confirms keep the 7-bot lineup.** Direct portfolio-level test of three tighter hand-picked lineups (4-bot best-per-cluster, 5-bot drop GDX+XOP, 6-bot drop GDX) all *lose* Sharpe vs the 7-bot baseline. Results: 4 bots → 3.79, 5 bots → 3.87, 6 bots → 4.01, 7 bots → **4.17**. Sharpe is monotonic with bot count; each additional bot adds ~+0.10–0.15 Sharpe via diversification. None of the trimmed lineups clear the decision rule (ΔSharpe ≥ +0.30 OR ΔDD ≤ −1pp with Sharpe loss ≤ 0.10). **Even per-asset losers GDX (1.46) and XOP (1.32) contribute net positive at the portfolio level.** The 2.0 per-asset bar is a candidate-addition screen, not a prune threshold. Next experiment: per-bot cap-shrink under entry_only — the only remaining lever with a credible path past Sharpe 4.17. Snapshot: `.claude/strategies/portfolio-runner-lineup-selection.md`.

**Long-only metals Sharpe (Apr 28):** GLD 2.57, SLV 2.47, GDX 1.89, IAU 1.86. **GLD and SLV long-only Sharpes exceed full-strategy** — shorts hurt DD-adjusted return on these two; GDX/IAU lose Sharpe when shorts are removed.

**Boundary-index Sharpe (Apr 28):** IWM **2.30 ✓** (clears bar — only broad-index deployment candidate by quality standard), DIA 1.83, QQQ 1.45, SPY 1.36. Returns scale with underlying volatility per learning #8.

### Rejected (below quality bar)

| Strategy | Asset | TF | Return | Max DD | Trades | Win Rate | Reason |
|---|---|---|---|---|---|---|---|
| Trend Framework | TLT | 15m | +20.87% | 1.16% | 866 | 40% | Bonds dominated by rates dynamics, not range-bound — confirmed Apr 28 |

> **Sharpe figures verified Apr 28 2026** — backtester now computes annualised Sharpe from the equity curve (`backend/engine/backtester.py`), runner prints it (`backend/runner.py`). Previous card claims (GLD 2.47 / IAU 1.97 / SLV 2.41 / GDX 2.58 / XLE 2.06) were close to verified values for GLD/SLV but underestimated GDX (now 2.46 vs claimed 2.58 — claim was higher), and overestimated IAU (1.95 vs 1.97). XLE verified at 2.30 vs 2.06.
>
> **Apr 27 2026 verification:** Returns are higher than the cards previously claimed for 4 of 5 assets (SLV most dramatically — +144% vs claimed +98%). Trade counts are higher across the board. Drawdowns are slightly higher (1–2% rather than <1% for the metals). Engine itself is healthy — the Apr 4 stop-check fix is in place. Card discrepancies traced to Apr 4 transcription errors. See individual strategy cards for full per-asset correction notes.

**Thesis:** Precious metals + energy mean-revert at 15m within trend. Same params work across all 5 without retuning.

**Other strategies tested:**

| Strategy | Asset | TF | Result | Status |
|---|---|---|---|---|
| EventSurprise (CPI) | GLD | 15m | +2.36%, 86% WR, 14 trades | Built |
| StochRSI | GLD | 1h | Sharpe 1.44 | Validated |
| StochRSI | IAU | 1h | Sharpe 1.22 | Validated |
| StochRSI | XLE | 1h | Sharpe 1.11 | Validated |
| StochRSI | SPY/QQQ/IWM | 5m-15m | No alpha | Dead end |

## Constraints

### Timezones and Market Hours
- **All server logs and Alpaca timestamps are UTC**
- **Irish time = UTC+0 (GMT) until last Sunday of March, then UTC+1 (IST)**
- **US market hours (post-DST, from second Sunday of March): 13:30–20:00 UTC**
- **US market hours (pre-DST, until second Sunday of March): 14:30–21:00 UTC**
- **DST 2026 started March 8** — market hours are currently 13:30–20:00 UTC
- Always run `date -u` on server first when checking bots to establish current UTC time. Never assume time from earlier in the conversation.

### Trading Rules
- `--delay 1` is broken — never use. Always use `--delay 0`
- `--spread 0.0003 --delay 0` are the validated backtest settings — do not change
- Never run two bots on the same symbol — Alpaca position conflicts
- Stop orders must use DAY TIF for fractional shares (GTC rejected by Alpaca)
- Live fetch window must stay ≥7 days in runner.py (weekends need 150+ bars)
- Server is `e2-small` (2 GB RAM) — upgraded from e2-micro Apr 28 2026 to support 5–7 bots. ~110 MB per bot, ~1.2 GB headroom available. Heavy SSH commands during market hours are now safe but still discouraged unless needed.
- Deploy to cloud only when bot code changes — docs/memory changes don't need deploy
- Shorts enabled — whole-share sizing deployed Apr 15-16. First short confirmed working Apr 16 (GLD)
- Alpaca timestamps are UTC, not ET — confirmed Mar 14
- `dynamic_adx` defaults to True in strategy — always pass `"dynamic_adx": false` in backtest params, otherwise `adx_threshold` is ignored and a tighter dynamic threshold (20-30) is used instead
- `adx_filter_mode` default is `'entry_only'` since May 21 2026 (the bug-fixed mode — ADX gate blocks new *entries* only; stops and signal-exits run regardless of ADX). Backtests need no flag for honest results. Pass `"adx_filter_mode":"all"` **only** to reproduce a pre-May-21 backtest byte-identical (the legacy buggy mode — see `calibration-journal.md` §2). The 7 live bot run scripts are explicitly pinned to `"adx_filter_mode":"all"`, so live trading is byte-unchanged pending a deliberate deploy decision
