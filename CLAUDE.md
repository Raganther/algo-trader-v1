# Algo Trader V1

## What it is
Algorithmic trading research and live execution platform. Python backend, Next.js frontend.
Modular strategy engine — strategies register in `runner.py` STRATEGY_MAP, run via CLI.
Phase: Forward testing — verifying live execution mechanics on 4 paper bots before real money.

## Session Start
Read in order on every cold start:
1. `memory/MEMORY.md` — recent git saves
2. `memory/plan.md` — active steps
3. `memory/observations.md` — running insights from current testing phase

Read on demand only:
- `docs/dev.md` — ideas backlog
- `.claude/memory/strategies/` — per-strategy research and params

## Run Commands

```bash
# Backtest (validated params)
python3 -m backend.runner backtest --strategy StochRSIMeanReversion --symbol GLD --timeframe 15m --start 2020-01-01 --end 2025-12-31 --source alpaca --spread 0.0003 --delay 0 --parameters '{"rsi_period":7,"stoch_period":14,"overbought":80,"oversold":15,"adx_threshold":20,"skip_adx_filter":false,"sl_atr":2.0,"trailing_stop":true,"trail_atr":2.0,"trail_after_bars":10,"min_hold_bars":10,"skip_days":[0]}'

# Get current server time (always run this first when checking bots — establishes UTC anchor)
gcloud compute ssh algotrader2026 --zone=europe-west2-a --command="date -u"

# Check cloud bots
gcloud compute ssh algotrader2026 --zone=europe-west2-a --command="pm2 status"

# Check recent trades across all bots (today + yesterday shown separately — never add HEARTBEAT to this grep)
gcloud compute ssh algotrader2026 --zone=europe-west2-a --command="for bot in gld-test iau-test slv-test gdx-test; do echo \"=== \$bot ===\"; logs=\$(ls -t /home/alistairelliman/.pm2/logs/\${bot}-out*.log | head -2); today=\$(echo \"\$logs\" | head -1); yesterday=\$(echo \"\$logs\" | tail -1); echo \"-- today --\"; grep -E 'LIVE BUY|LIVE SELL|FILLED|TRAILING STOP|SERVER STOP|Starting Live|⚠️|❌|⏳' \"\$today\" 2>/dev/null; echo \"-- yesterday --\"; grep -E 'LIVE BUY|LIVE SELL|FILLED|TRAILING STOP|SERVER STOP|Starting Live|⚠️|❌|⏳' \"\$yesterday\" 2>/dev/null; done"

# Deploy code changes to cloud
git push origin main
gcloud compute ssh algotrader2026 --zone=europe-west2-a --command="cd algo-trader-v1 && git pull && pm2 restart all"

# Git save
./scripts/git-save.sh "message"

# Discovery engine
python -m backend.optimizer.run_overnight [--scan|--quick|--medium] [--max-hours N] [--symbols X,Y]

# Fetch historical price data (run once, then as needed to sync)
python3 scripts/fetch_price_data.py --symbols GLD,IAU,SLV,GDX --start 2020-01-01
```

## Architecture
- **Runner:** `backend/runner.py` — STRATEGY_MAP registers all strategies, CLI entry point for all backtests
- **Registry:** `STRATEGY_MAP` in `runner.py` — add strategy here to make it available
- **Engine:** `backend/engine/` — backtester, data loaders, live broker, paper trader
- **Strategies:** `backend/strategies/` — 21 strategies
- **Indicators:** `backend/indicators/` — StochRSI, RSI, MACD, ADX, Bollinger, ATR, SMA, CHOP
- **DB:** `backend/research.db` — experiments, live trades
- **Frontend:** `frontend/` — Next.js dashboard, DB-driven
- **Reference:** `.claude/memory/system_manual.md` — full CLI and architecture docs
- **Strategy notes:** `.claude/memory/strategies/` — per-strategy research and params

## Current Status
Phase: Forward testing + charting. 4 paper bots running on cloud (gld-test, iau-test, slv-test, gdx-test).
Price action chart live at `/chart` — Stage 1 complete (candlestick chart, symbol/range selector).
UI redesigned: Inter font, shared sidebar nav, max-width constraints, consistent page structure.
Stage 2 next: trade overlays on chart.
Aggressive test params (OB 60/OS 40, 3-bar hold/trail) to generate more trades for mechanics verification.
~3 weeks of live testing complete (started late Feb). All bots active: GDX started trading Mar 16 after zero trades previously.
Mar 16: full Alpaca order audit — all records match perfectly. 6 complete trades across 4 bots, 2 server stops fired, trailing stops ratcheted.
Pre-market signal bug found and fixed Mar 16 (market hours gate, runner.py).
Infrastructure assessment: core is sound. 13 bugs found and fixed. Data integrity 100% from Mar 5 onwards.
Remaining before real money: (1) confirm trailing stop firing in profit, (2) fix short entry guard + verify short mechanics end-to-end.
Estimated timeline: ~2 more weeks paper testing minimum.

**Test bots:**

| Bot | Symbol | OB/OS | ADX thresh | Hold | Trail | Trades/yr |
|-----|--------|-------|------------|------|-------|-----------|
| gld-test | GLD | 60/40 | 50 | 3 bars | after 3 bars | ~237 |
| iau-test | IAU | 60/40 | 50 | 3 bars | after 3 bars | ~237 |
| slv-test | SLV | 60/40 | 50 | 3 bars | after 3 bars | ~237 |
| gdx-test | GDX | 60/40 | 50 | 3 bars | after 3 bars | ~237 |

**Validated params (switch after mechanics verified):**

| Param | Value |
|-------|-------|
| OB/OS | 80/15 |
| Min hold | 10 bars |
| Trail after | 10 bars |
| ADX threshold | 20 |
| Skip days | Monday |
| Trades/yr | ~107 per symbol |

**Confirmed working:** bot-initiated exits, trailing stop updates (ratchets up), order cancellation before exit, position sync on restart, heartbeat logging, DAY TIF stops, DB reconciliation on startup, server-side stop FIRING (confirmed Mar 10 — SLV stop at $80.49 auto-filled at $80.43). GDX started trading Mar 16 — resolves zero-trade open question.

**Not yet confirmed:** trailing stop FIRING in profit (same Alpaca server-side mechanism — needs trail ratcheted above entry before firing). Mar 16: trailing stop ratcheted on both SLV and GDX but both closed via K-signal, not server stop.

**Long-only baseline established (Mar 14):** Bots currently run long-only. Full vs long-only Sharpe: GLD 2.54→~1.91, IAU ~2.0→~1.33, SLV 2.54→~3.29 (better!), GDX 2.41→~1.54. SLV viable long-only; GLD/IAU/GDX meaningfully weaker. See strategy cards for full breakdown.

**Two exit mechanics (not three):** (1) bot K-signal exit at candle close, (2) Alpaca server-side stop auto-execution intrabar — covers both stop loss and trailing stop exits.

**Backtest predictions for test params (Dec 2025 – Mar 2026):**

| Symbol | Return | Max DD | Trades | Win Rate |
|--------|--------|--------|--------|----------|
| GLD | +0.16% | 0.77% | 58 | 48% |
| SLV | +14.25% | 1.15% | 44 | 57% |
| GDX | +2.45% | 0.94% | 69 | 59% |
| IAU | -0.50% | 0.99% | 54 | 37% |

**Known issues (not yet fixed):**
- Fractional short selling not supported — Alpaca rejects short (sell-to-open) orders for fractional shares. Short trading disabled until whole-share quantity sizing is implemented.

## Validated Edges

| Strategy | Asset | TF | Sharpe | Return | Max DD | WF |
|---|---|---|---|---|---|---|
| StochRSI Enhanced | GLD | 15m | 2.54 | +44.7% | 0.69% | Audited |
| StochRSI Enhanced | SLV | 15m | 2.54 | +105.3% | 2.00% | 4/4 |
| StochRSI Enhanced | GDX | 15m | 2.41 | +114.1% | 2.02% | 4/4 |
| StochRSI Enhanced | IAU | 15m | ~2.0 | +32.6% | 0.72% | 4/4 |

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
- Fractional short selling rejected by Alpaca — bots are long-only until whole-share qty sizing added
- Alpaca timestamps are UTC, not ET — confirmed Mar 14
