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
- `.claude/strategies/stochrsi-enhanced-gld.md` — read when working on GLD, reviewing long-only vs full strategy, or checking the audit baseline
- `.claude/strategies/stochrsi-enhanced-iau.md` — read when working on IAU or reviewing 15m strategy params
- `.claude/strategies/stochrsi-enhanced-slv.md` — read when working on SLV or reviewing 15m strategy params
- `.claude/strategies/stochrsi-enhanced-gdx.md` — read when working on GDX or reviewing 15m strategy params
- `.claude/strategies/research-log.md` — read when deciding what to experiment on next, reviewing cross-strategy learnings, or planning new forward tests
- `.claude/strategies/composable-results.md` — read when combining strategies or planning composable bot deployment
- `.claude/strategies/stochrsi-enhanced-xle.md` — read when working on XLE or planning Rolling Validation Test #1
- `.claude/strategies/stochrsi-enhanced-oih.md` — read when working on OIH (top-tier candidate from Apr 28 audit, +146% verified, needs WF)
- `.claude/strategies/stochrsi-enhanced-xbi.md` — read when working on XBI (biotech diversifier candidate from Apr 28 audit, +85% verified, needs WF)
- `.claude/strategies/stochrsi-enhanced-xop.md` — read when working on XOP (energy E&P candidate from Apr 28 audit, +90% verified, needs WF)
- `.claude/strategies/event-surprise.md` — read when researching economic event strategies or revisiting CPI/NFP trading
- `.claude/calibration/calibration-notes.md` — read when running calibration, checking Apr 20 methodology, or comparing backtest vs live
- `.claude/calibration/live-trade-log.md` — read when auditing trades, filling in daily trade data, or running the Apr 20 calibration comparison
- `.claude/calibration/forward-test-log.md` — read when auditing validated-params trades (Apr 15+), tracking forward-test win-rate convergence, or expanding the Layer 3 stop-slippage sample
- `.claude/calibration/gap-distribution.md` — read when sizing overnight-capable positions, evaluating gap-risk policy, or interpreting an overnight gap loss in live trades
- `.claude/integrations/alpaca-mcp.md` — read when using Alpaca MCP tools, running trade audits via MCP, or checking what data is available without SSH
- `.claude/strategies/regime-analysis.md` — read when working on regime classification, regime-aware sizing, interpreting live performance by market environment, or building the regime frontend
- `.claude/strategies/regime-stochrsi-diagnostic.md` — read when interpreting Apr 23 per-regime StochRSI results, deciding whether regime-aware sizing is justified, or comparing metals vs other assets
- `.claude/strategies/regime-sizing-portfolio-diagnostic.md` — read when evaluating whether regime multipliers improve portfolio-level return/drawdown before live sizing
- `.claude/strategies/arbitrage-automation-concepts.md` — read when exploring new strategy families (pairs trading, cross-asset, event-driven), evaluating adjacent business ideas, or planning beyond the current 4-symbol setup

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
python3 -m backend.runner backtest --strategy StochRSIMeanReversion --symbol GLD --timeframe 15m --start 2020-01-01 --end 2025-12-31 --source alpaca --spread 0.0003 --delay 0 --parameters '{"rsi_period":7,"stoch_period":14,"overbought":80,"oversold":15,"adx_threshold":20,"skip_adx_filter":false,"sl_atr":2.0,"trailing_stop":true,"trail_atr":2.0,"trail_after_bars":10,"min_hold_bars":10,"skip_days":[0]}'

# Deploy code changes to cloud
git push origin main
gcloud compute ssh algotrader-us --zone=us-east1-b --command="cd algo-trader-v1 && git pull && pm2 restart all"

# Git save
./scripts/git-save.sh "message"

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
- **Calibration notes:** `.claude/calibration/calibration-notes.md` — methodology, Apr 20 commands, snapshots
- **Live trade log:** `.claude/calibration/live-trade-log.md` — per-trade records for Mar 20–Apr 20 calibration window
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

**Capital cap binds at 4 simultaneous positions.** Each bot can take up to 25% of equity per position (notional cap, validated). At $94k equity, **at most 4 bots can hold full positions at once** — so 7 bots ≠ 7 simultaneous exposures; it means more bots are sometimes idle while their correlated peers are in. Adding bots beyond ~4 doesn't add capacity, only diversification of *which* assets the framework is exposed to. Adding correlated bots adds neither. **First valid expansion candidate = IWM** (small-cap equities — Test 3 confirmed direction-agnostic, low correlation to existing 3 clusters); correlation-aware sizing V1 is now live (Apr 29 2026), so the IWM gate is unblocked subject to live verification of the discount mechanism. See `research-roadmap.md` Critical Path.

**Correlation-aware sizing V1 (live Apr 29 2026):** per-trade risk discounted by cluster occupancy. `risk_frac = 0.02 / N`, N = peers held in same cluster + self. Hardcoded clusters: gold = GLD/IAU/SLV/GDX, energy = OIH/XOP/XLE, biotech = XBI. Lives in `backend/engine/correlation_sizing.py`; applied in all three sizing blocks of `stoch_rsi_mean_reversion.py`. Single-symbol backtest unaffected (N=1 always). Watch for `[CORR-SIZE]` lines in pm2 logs to verify the discount fires on the next correlated entry.

**Confirmed working (execution mechanics — separate from edge attribution):** entry placement + K-exit (76–80% win rate across 67+ trades), server-side stop loss, trailing stop in profit (SLV +$283.86 Apr 20), trail ratcheting, whole-share sizing (340+ shares/position), short entry + K-exit (GLD Apr 16 +$38.50), GTC stops (no overnight expiry gap), pm2 startup registered as systemd service, single-symbol overnight gap risk bounded by 25% notional cap (Apr 23 SLV gap-through = -0.64% equity, within p95 of historical distribution). *Note:* the 76–80% win rate reflects what the framework + StochRSI tilt produces in live conditions; per Apr 28 random-entry control, the bulk of the risk-adjusted edge comes from the framework, not from the StochRSI entry signal.

**Execution layer validated (Apr 13 calibration):** Layers 1/2/4 pass. Backtest engine accurate for test params / intraday regime. See calibration-notes.md for full results.

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

Stop orders use GTC TIF (switched Apr 17 — whole-share sizing makes GTC valid for US equities). Shorts enabled. Skip Monday (`skip_days:[0]`).

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
> - **Metals Sharpes overstate live expectation.** Inverted-GLD test + Feb 27 daily-bar bear test both suggest live metals Sharpe in a non-bull regime is ~½ to ⅓ of backtest. Size for Sharpe 1.0–1.5 expectation, not 2.46.
> - **IWM is now relatively more attractive.** Sharpe 2.30 with regime-agnostic profile is more robust than metals Sharpe 2.46 with regime-dependence.
> - "StochRSI Enhanced" should be read as "Framework v1 applied to <asset>" — the strategy library is one framework, not 8 strategies.

**Two passes on the extended window.** Apr 27 runs (Return/DD/Trades columns) used `dynamic_adx:true` (strategy default — `dynamic_adx:false` was not passed explicitly) → tighter dynamic threshold → ~10–15% more trades. Apr 28 Sharpe runs explicitly pass `dynamic_adx:false` per recipe spec → trade counts ~10–15% lower. Sharpe column is from the Apr 28 (recipe-correct) runs. Apr 27 Return/DD figures are kept here because the WF validations were done at those settings.

| Strategy | Asset | TF | Return | Max DD | Trades | Win Rate | WF | Sharpe (Apr 28) |
|---|---|---|---|---|---|---|---|---|
| StochRSI Enhanced | GLD | 15m | +49.83% | 1.18% | 728 | 43% | 4/4 | **2.48** ✓ |
| StochRSI Enhanced | IAU | 15m | +40.05% | 1.31% | 705 | 41% | 4/4 | 1.95 (under) |
| StochRSI Enhanced | SLV | 15m | +144.26% | 2.00% | 581 | 47% | 4/4 | **2.46** ✓ |
| StochRSI Enhanced | GDX | 15m | +132.91% | 2.01% | 581 | 46% | 4/4 | **2.46** ✓ |
| StochRSI Enhanced | XLE | 15m | +80.42% | 3.27% | 570 | 45% | 4/4 | **2.30** ✓ |
| StochRSI Enhanced | **OIH** | 15m | **+146.53%** ⭐ | 2.95% | 589 | 42% | **4/4** | **2.33** ✓ |
| StochRSI Enhanced | XOP | 15m | +90.34% | 3.29% | 629 | 42% | **4/4** | 1.98 (at bar) |
| StochRSI Enhanced | XBI | 15m | +84.75% | 2.44% | 602 | 43% | **4/4** | **2.18** ✓ |

**Sharpe verified Apr 28 2026** — runner now prints annualised Sharpe (daily-resampled equity curve × √252). 6 of 8 cleanly clear Sharpe ≥ 2.0; XOP at 1.98 is at the bar; IAU at 1.95 is the weakest of the metals on a DD-adjusted basis.

**Long-only metals Sharpe (Apr 28):** GLD 2.57, SLV 2.47, GDX 1.89, IAU 1.86. **GLD and SLV long-only Sharpes exceed full-strategy** — shorts hurt DD-adjusted return on these two; GDX/IAU lose Sharpe when shorts are removed.

**Boundary-index Sharpe (Apr 28):** IWM **2.30 ✓** (clears bar — only broad-index deployment candidate by quality standard), DIA 1.83, QQQ 1.45, SPY 1.36. Returns scale with underlying volatility per learning #8.

### Rejected (below quality bar)

| Strategy | Asset | TF | Return | Max DD | Trades | Win Rate | Reason |
|---|---|---|---|---|---|---|---|
| StochRSI Enhanced | TLT | 15m | +20.87% | 1.16% | 866 | 40% | Bonds dominated by rates dynamics, not range-bound — confirmed Apr 28 |

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
