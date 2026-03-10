# Algo Trader V1

## What it is
Algorithmic trading research and live execution platform. Python backend, Next.js frontend.
Modular strategy engine — strategies register in `runner.py` STRATEGY_MAP, run via CLI.
Phase: Forward testing — verifying live execution mechanics on 4 paper bots before real money.

## Session Start
Read in order on every cold start:
1. `memory/MEMORY.md` — recent git saves
2. `memory/plan.md` — current active plan

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

# Check today's trades across all bots (correct command — logs rotate at midnight)
gcloud compute ssh algotrader2026 --zone=europe-west2-a --command="for bot in gld-test iau-test slv-test gdx-test; do echo \"=== \$bot ===\"; cat \$(ls -t /home/alistairelliman/.pm2/logs/\${bot}-out*.log | head -2) 2>/dev/null | grep -E 'LIVE BUY|LIVE SELL|FILLED|TRAILING STOP|SERVER STOP|Starting Live|⚠️'; done"

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
Week 1 complete — all bots flat into weekend. DB reconciliation deployed Mar 9.
Waiting to confirm: server-side stop firing, trailing stop profit lock-in.
Next: run 2-4 more weeks, compare live results to backtest predictions, then switch to validated params.

**Test bots:**

| Bot | Symbol | OB/OS | Hold | Trail | Trades/yr |
|-----|--------|-------|------|-------|-----------|
| gld-test | GLD | 60/40 | 3 bars | after 3 bars | ~237 |
| iau-test | IAU | 60/40 | 3 bars | after 3 bars | ~237 |
| slv-test | SLV | 60/40 | 3 bars | after 3 bars | ~237 |
| gdx-test | GDX | 60/40 | 3 bars | after 3 bars | ~237 |

**Validated params (switch after mechanics verified):**

| Param | Value |
|-------|-------|
| OB/OS | 80/15 |
| Min hold | 10 bars |
| Trail after | 10 bars |
| ADX threshold | 20 |
| Skip days | Monday |
| Trades/yr | ~107 per symbol |

**Confirmed working:** bot-initiated exits, trailing stop updates (ratchets up), order cancellation before exit, position sync on restart, heartbeat logging, DAY TIF stops, DB reconciliation on startup.

**Not yet confirmed:** server-side stop firing (Alpaca auto-executing between candles), trailing stop FIRING (locking in profit).

**Backtest predictions for test params (Dec 2025 – Mar 2026):**

| Symbol | Return | Max DD | Trades | Win Rate |
|--------|--------|--------|--------|----------|
| GLD | +0.16% | 0.77% | 58 | 48% |
| SLV | +14.25% | 1.15% | 44 | 57% |
| GDX | +2.45% | 0.94% | 69 | 59% |
| IAU | -0.50% | 0.99% | 54 | 37% |

**Bugs found & fixed:**
- Live fetch window 2 days → ~33 bars after weekends → silent skip. Fixed: 7-day window.
- Duplicate GLD bot conflict. Fixed: removed gld-15m-enhanced.
- OOM freezes under load. Fixed: 1GB swap added to server.
- Zombie trades on pm2 restart. Fixed: graceful SIGTERM handler.
- Wash trade rejection when server stop fires + bot also tries to sell. Fixed: cancel ALL open orders before exit.
- Server-side stop orders rejected (GTC not allowed for fractional shares). Fixed: DAY TIF, re-placed after market open.
- Fill timeout too short (5s). Fixed: 30s (15×2s).
- Trailing stop gap — position unprotected if update fails. Fixed: fallback re-places at old price.
- DB reconciliation gap — server stops and overnight fills not logged. Fixed: server stop logger, pending_fills retry, startup reconciliation.
- Timed-out buy orders never logged — pending_fills only tracked sells. Fixed: buys now queued in pending_fills on timeout.
- Reconcile lookback too short — 3-day window missed pre-market DAY orders filled at open. Fixed: extended to 7 days.

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
