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
- `.claude/strategies/event-surprise.md` — read when researching economic event strategies or revisiting CPI/NFP trading
- `.claude/calibration/calibration-notes.md` — read when running calibration, checking Apr 20 methodology, or comparing backtest vs live
- `.claude/calibration/live-trade-log.md` — read when auditing trades, filling in daily trade data, or running the Apr 20 calibration comparison
- `.claude/calibration/gap-distribution.md` — read when sizing overnight-capable positions, evaluating gap-risk policy, or interpreting an overnight gap loss in live trades
- `.claude/integrations/alpaca-mcp.md` — read when using Alpaca MCP tools, running trade audits via MCP, or checking what data is available without SSH
- `.claude/strategies/regime-analysis.md` — read when working on regime classification, regime-aware sizing, interpreting live performance by market environment, or building the regime frontend
- `.claude/strategies/arbitrage-automation-concepts.md` — read when exploring new strategy families (pairs trading, cross-asset, event-driven), evaluating adjacent business ideas, or planning beyond the current 4-symbol setup

## Run Commands

### Check bots (MCP — primary method)
When asked to "check bots", run these Alpaca MCP calls in order:
1. `get_clock` — market open/closed, establishes time context
2. `get_all_positions` — any open positions (overnight holds)
3. `get_orders(status="closed", symbols="GLD,IAU,SLV,GDX", after="<today>T00:00:00Z", direction="asc")` — today's completed trades

### Check bots (SSH — process health only)
Use SSH only when MCP can't answer the question: bot process status, application logs, errors/warnings.
```bash
# Bot process health (running/stopped/errored)
gcloud compute ssh algotrader-us --zone=us-east1-b --command="pm2 status"

# Bot logs — errors, warnings, heartbeats (not trade data — use MCP for that)
gcloud compute ssh algotrader-us --zone=us-east1-b --command="for bot in gld-test iau-test slv-test gdx-test; do echo \"=== \$bot ===\"; logs=\$(ls -t /home/alistairelliman/.pm2/logs/\${bot}-out*.log | head -2); today=\$(echo \"\$logs\" | head -1); yesterday=\$(echo \"\$logs\" | tail -1); echo \"-- today --\"; grep -E 'LIVE BUY|LIVE SELL|FILLED|TRAILING STOP|SERVER STOP|Starting Live|⚠️|❌|⏳' \"\$today\" 2>/dev/null; echo \"-- yesterday --\"; grep -E 'LIVE BUY|LIVE SELL|FILLED|TRAILING STOP|SERVER STOP|Starting Live|⚠️|❌|⏳' \"\$yesterday\" 2>/dev/null; done"
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
Phase: Forward testing — validated params live, path to real money. 4 paper bots running on cloud (gld-test, iau-test, slv-test, gdx-test).
Price action chart live at `/chart` — Stage 1 complete (candlestick chart, symbol/range selector). Stage 2 next: trade overlays on chart.

**Confirmed working:** entry signal + K-exit (76–80% win rate across 67+ trades), server-side stop loss, trailing stop in profit (SLV +$283.86 Apr 20), trail ratcheting, whole-share sizing (340+ shares/position), short entry + K-exit (GLD Apr 16 +$38.50), GTC stops (no overnight expiry gap), pm2 startup registered as systemd service, single-symbol overnight gap risk bounded by 25% notional cap (Apr 23 SLV gap-through = -0.64% equity, within p95 of historical distribution).

**Execution layer validated (Apr 13 calibration):** Layers 1/2/4 pass. Backtest engine accurate for test params / intraday regime. See calibration-notes.md for full results.

**Remaining before real money:** see `research-roadmap.md` → Critical Path section.

**Live bots (validated params, deployed Apr 15-16):**

| Bot | Symbol | OB/OS | ADX thresh | Hold | Trail | Trades/yr |
|-----|--------|-------|------------|------|-------|-----------|
| gld-test | GLD | 80/15 | 20 | 10 bars | after 10 bars (2.0 ATR) | ~107 |
| iau-test | IAU | 80/15 | 20 | 10 bars | after 10 bars (2.0 ATR) | ~107 |
| slv-test | SLV | 80/15 | 20 | 10 bars | after 10 bars (2.0 ATR) | ~107 |
| gdx-test | GDX | 80/15 | 20 | 10 bars | after 10 bars (2.0 ATR) | ~107 |

Stop orders use GTC TIF (switched Apr 17 — whole-share sizing makes GTC valid for US equities). Shorts enabled. Skip Monday (`skip_days:[0]`).

**Confirmed working:** bot-initiated exits, trailing stop updates (ratchets up), order cancellation before exit, position sync on restart, heartbeat logging, DAY TIF stops, DB reconciliation on startup, server-side stop FIRING (confirmed Mar 10 — SLV stop at $80.49 auto-filled at $80.43). GDX started trading Mar 16 — resolves zero-trade open question.

**Trailing stop FIRING in profit — confirmed Mar 23.** GDX: entry $80.05 (Mar 20), trail ratcheted to $83.35 over 3-day hold, server stop fired intrabar @ $83.317 (+$958 paper). Both server-side exit mechanics now fully confirmed.

**Long-only baseline established (Mar 14):** Bots currently run long-only. Full vs long-only Sharpe (corrected Apr 4): GLD 2.47→~1.80, IAU 1.97→~1.20, SLV 2.41→~3.10 (better!), GDX 2.58→~1.65. SLV viable long-only; GLD/IAU/GDX meaningfully weaker. See strategy cards for full breakdown.

**Two exit mechanics (not three):** (1) bot K-signal exit at candle close, (2) Alpaca server-side stop auto-execution intrabar — covers both stop loss and trailing stop exits.

**Backtest predictions for test params (Dec 2025 – Mar 2026):**

| Symbol | Return | Max DD | Trades | Win Rate |
|--------|--------|--------|--------|----------|
| GLD | +0.16% | 0.77% | 58 | 48% |
| SLV | +14.25% | 1.15% | 44 | 57% |
| GDX | +2.45% | 0.94% | 69 | 59% |
| IAU | -0.50% | 0.99% | 54 | 37% |

## Validated Edges

| Strategy | Asset | TF | Sharpe | Return | Max DD | WF |
|---|---|---|---|---|---|---|
| StochRSI Enhanced | GLD | 15m | 2.47 | +39.22% | 0.73% | Audited |
| StochRSI Enhanced | SLV | 15m | 2.41 | +97.96% | 2.00% | 4/4 |
| StochRSI Enhanced | GDX | 15m | 2.58 | +129.8% | 2.02% | 4/4 |
| StochRSI Enhanced | IAU | 15m | 1.97 | +32.7% | 0.89% | 4/4 |

**Thesis:** Precious metals mean-revert at 15m within trend. Same params work across all 4 without retuning.

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
- Server RAM tight — avoid heavy SSH commands while bots are processing bars
- Deploy to cloud only when bot code changes — docs/memory changes don't need deploy
- Shorts enabled — whole-share sizing deployed Apr 15-16. First short confirmed working Apr 16 (GLD)
- Alpaca timestamps are UTC, not ET — confirmed Mar 14
- `dynamic_adx` defaults to True in strategy — always pass `"dynamic_adx": false` in backtest params, otherwise `adx_threshold` is ignored and a tighter dynamic threshold (20-30) is used instead
