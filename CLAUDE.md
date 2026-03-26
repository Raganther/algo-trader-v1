# Algo Trader V1

## What it is
Algorithmic trading research and live execution platform. Python backend, Next.js frontend.
Modular strategy engine — strategies register in `runner.py` STRATEGY_MAP, run via CLI.
Phase: Forward testing — verifying live execution mechanics on 4 paper bots before real money.

## Session Start
Read in order on every cold start:
1. `.claude/memory/gitlog.md` — recent git saves
2. `.claude/memory/plan.md` — active steps
3. `.claude/memory/observations.md` — running insights from current testing phase

Read on demand only:
- `.claude/procedures/_index.md` — index of extracted procedures; scan at plan creation for relevant how-to patterns
- `.claude/strategies/stochrsi_enhanced_gld.md` — GLD 15m validated params, full audit data, bear market test, long-only baseline
- `.claude/strategies/stochrsi_enhanced_iau.md` — IAU 15m validated params and performance summary
- `.claude/strategies/stochrsi_enhanced_slv.md` — SLV 15m validated params and performance summary
- `.claude/strategies/stochrsi_enhanced_gdx.md` — GDX 15m validated params and performance summary
- `.claude/strategies/composable_results.md` — Phase 3 composable strategy results (3 validated combos, not yet deployed)
- `.claude/strategies/event_surprise.md` — EventSurprise strategy: CPI/NFP research, backtest results, parked
- `.claude/calibration/calibration_notes.md` — calibration methodology, Apr 20 commands, Mar 5–16 snapshot

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
- **Strategy notes:** `.claude/strategies/` — 6 domain files, individually listed in Session Start above
- **Calibration notes:** `.claude/calibration/calibration_notes.md` — methodology, Apr 20 commands, snapshots
- **OpenBrain category:** `.claude/openbrain-category` — `algo-trader`
- **Hooks:** SessionStart (load-context.sh), PreToolUse guard (git-save-guard.sh), PostToolUse OpenBrain audit (openbrain-audit-reminder.sh), PostToolUse plan domain reminder (plan-domain-reminder.sh)

## Current Status
Phase: Forward testing + charting. 4 paper bots running on cloud (gld-test, iau-test, slv-test, gdx-test).
Price action chart live at `/chart` — Stage 1 complete (candlestick chart, symbol/range selector).
UI redesigned: Inter font, shared sidebar nav, max-width constraints, consistent page structure.
Stage 2 next: trade overlays on chart.
Aggressive test params (OB 60/OS 40, 3-bar hold/trail) to generate more trades for mechanics verification.
~3 weeks of live testing complete (started late Feb). All bots active: GDX started trading Mar 16 after zero trades previously.
Mar 16: full Alpaca order audit — all records match perfectly. 6 complete trades across 4 bots, 2 server stops fired, trailing stops ratcheted.
Pre-market signal bug found and fixed Mar 16 (market hours gate, runner.py).
Mar 17: 4 trades across all bots. Full Alpaca audit — all records matched. GDX server stop fired intrabar (19:06 UTC) — confirmed again. Trailing stop firing in profit still unconfirmed. Trail params tightened (trail_atr 2.0→0.5, trail_after_bars 3→1) to provoke trail fire.
Mar 18: 4 trades across all 4 bots, all flat EOD. SLV server stop fired (stop loss). IAU trail ratcheted but exited via K-signal. Per-trade diagnostic run: with OLD params (2.0 ATR), backtest predicts ZERO profitable trail fires in Jan-Mar 2026 — matches live exactly, no bug. With new params (0.5 ATR), backtest predicts ~5 per symbol. 2 days on new params so far — still waiting.
Mar 19: 4 trades, all flat ~18:46 UTC. Full Alpaca audit — all 12 orders matched. GDX trail update failed (race condition in update_stop_order — cancel async, new stop placed before shares freed). Fixed with 1s sleep after cancel. Bug existed since Mar 4 fallback was added, exposed by tighter trail_after_bars=1. Deployed fix.
Infrastructure assessment: core is sound. 13 bugs found and fixed. Data integrity 100% from Mar 5 onwards.
**Calibration target: Apr 20.** Running current aggressive params until then, then backtest same window with identical params to validate the backtest engine. Aggressive params kept deliberately — they generate ~2x more trades than validated params, making the calibration comparison statistically meaningful. Clean data window: Mar 20 – Apr 20 (Mar 20 = first fully confirmed clean day with current params and all fixes deployed).
Remaining before real money: (1) confirm trailing stop firing in profit, (2) fix short entry guard + verify short mechanics end-to-end, (3) calibration comparison on Apr 20.

**Test bots:**

| Bot | Symbol | OB/OS | ADX thresh | Hold | Trail | Trades/yr |
|-----|--------|-------|------------|------|-------|-----------|
| gld-test | GLD | 60/40 | 50 | 3 bars | after 1 bar (0.5 ATR) | ~237 |
| iau-test | IAU | 60/40 | 50 | 3 bars | after 1 bar (0.5 ATR) | ~237 |
| slv-test | SLV | 60/40 | 50 | 3 bars | after 1 bar (0.5 ATR) | ~237 |
| gdx-test | GDX | 60/40 | 50 | 3 bars | after 1 bar (0.5 ATR) | ~237 |

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

**Trailing stop FIRING in profit — confirmed Mar 23.** GDX: entry $80.05 (Mar 20), trail ratcheted to $83.35 over 3-day hold, server stop fired intrabar @ $83.317 (+$958 paper). Both server-side exit mechanics now fully confirmed.

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
- `dynamic_adx` defaults to True in strategy — always pass `"dynamic_adx": false` in backtest params, otherwise `adx_threshold` is ignored and a tighter dynamic threshold (20-30) is used instead
