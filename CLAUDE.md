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
- `.claude/memory/system_manual.md` — full technical CLI reference
- `.claude/memory/strategies/` — per-strategy research and params

## Run Commands

```bash
# Backtest (validated params)
python3 -m backend.runner backtest --strategy StochRSIMeanReversion --symbol GLD --timeframe 15m --start 2020-01-01 --end 2025-12-31 --source alpaca --spread 0.0003 --delay 0 --parameters '{"rsi_period":7,"stoch_period":14,"overbought":80,"oversold":15,"adx_threshold":20,"skip_adx_filter":false,"sl_atr":2.0,"trailing_stop":true,"trail_atr":2.0,"trail_after_bars":10,"min_hold_bars":10,"skip_days":[0]}'

# Check cloud bots
gcloud compute ssh algotrader2026 --zone=europe-west2-a --command="pm2 status"

# View bot logs
gcloud compute ssh algotrader2026 --zone=europe-west2-a --command="pm2 logs BOT_NAME --lines 20 --nostream"

# Check latest signals across all bots
gcloud compute ssh algotrader2026 --zone=europe-west2-a --command="for bot in gld-test iau-test slv-test gdx-test; do echo \"=== \$bot ===\"; cat /home/alistairelliman/.pm2/logs/\${bot}-out.log | grep -E 'K:|BUY|SELL|FILLED' | tail -3; done"

# Deploy code changes to cloud
git push origin main
gcloud compute ssh algotrader2026 --zone=europe-west2-a --command="cd algo-trader-v1 && git pull && pm2 restart all"

# Git save
./scripts/git-save.sh "message"

# Discovery engine
python -m backend.optimizer.run_overnight [--scan|--quick|--medium] [--max-hours N] [--symbols X,Y]
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

## Current Status
Phase: Forward testing — 4 paper bots running on cloud (gld-test, iau-test, slv-test, gdx-test).
Aggressive test params (OB 60/OS 40, 3-bar hold/trail) to generate more trades for mechanics verification.
Week 1 complete — all bots flat into weekend.
Waiting to confirm: server-side stop firing, trailing stop profit lock-in.
Next: run 2-4 more weeks, compare live results to backtest predictions, then switch to validated params.

## Constraints
- `--delay 1` is broken — never use. Always use `--delay 0`
- `--spread 0.0003 --delay 0` are the validated backtest settings — do not change
- Never run two bots on the same symbol — Alpaca position conflicts
- Stop orders must use DAY TIF for fractional shares (GTC rejected by Alpaca)
- Live fetch window must stay ≥7 days in runner.py (weekends need 150+ bars)
- Server RAM tight — avoid heavy SSH commands while bots are processing bars
- Deploy to cloud only when bot code changes — docs/memory changes don't need deploy
