# Algo Trader V1 - Session Primer

> **Claude reads this automatically at session start. Keep it current.**

## Current Status

- **Phase:** Forward testing — verifying execution mechanics before real money
- **Active Bots:** 4 (gld-test + iau-test + slv-test + gdx-test — PAPER mode, aggressive params)
- **Server:** europe-west2-a (algotrader2026) — 958MB RAM + 1GB swap, 2 vCPUs
- **Validated Edges:** 4 precious metals strategies (GLD, SLV, GDX, IAU) all 15m StochRSI Enhanced
- **Fractional Shares:** ✅ Confirmed working in paper trading (Alpaca, min $1 order, DAY TIF)

## Where We Are (Mar 4)

**Testing execution mechanics with aggressive params on 4 bots.**

The backtested edge is validated. We're now verifying that the live trading infrastructure works correctly before committing real money. Specifically: order fills, trailing stops, min hold, position sync on restart.

**Test bots (aggressive params for more trades):**

| Bot | Symbol | OB/OS | Hold | Trail | Trades/yr |
|-----|--------|-------|------|-------|-----------|
| gld-test | GLD | 60/40 | 3 bars | after 3 bars | ~237 |
| iau-test | IAU | 60/40 | 3 bars | after 3 bars | ~237 |
| slv-test | SLV | 60/40 | 3 bars | after 3 bars | ~237 |
| gdx-test | GDX | 60/40 | 3 bars | after 3 bars | ~237 |

**Validated params (target — switch after mechanics verified):**

| Param | Value |
|-------|-------|
| OB/OS | 80/15 |
| Min hold | 10 bars |
| Trail after | 10 bars |
| ADX threshold | 20 |
| Skip days | Monday |
| Trades/yr | ~107 per symbol (~428 total across 4) |

**Bugs found & fixed:**
- Live fetch window was 2 days → only ~33 bars after weekends → `on_bar` guard (`i < 50`) silently skipped all signal evaluation. Fixed: 7-day window → 150+ bars.
- Removed `gld-15m-enhanced` (duplicate GLD bot, would conflict on same Alpaca position)
- Added 1GB swap to prevent OOM freezes when SSH + bots compete for RAM
- Zombie trades on pm2 restart — old process lingered after SIGTERM. Fixed: graceful shutdown handler.
- Wash trade rejection — server-side stop fires + bot also tries to sell → Alpaca rejects. Fixed: cancel ALL open orders for symbol before selling, not just tracked stop.
- Server-side stop orders rejected — fractional shares require DAY TIF, but stops used GTC. Fixed: DAY TIF for stock stops. Re-placed on first bar after market open if held overnight.
- Fill timeout too short (5s) — extended to 30s (15×2s) with warning log on timeout.
- Trailing stop gap — if update failed after cancelling old stop, position unprotected. Fixed: fallback re-places at old stop price.

**Reliability hardening (Mar 4 evening):**
- Order ID logged on all fills for Alpaca audit trail
- Heartbeat logging every ~15 min (`[HEARTBEAT]` — grep-friendly health check)
- 50-bar minimum data guard at runner level (clearer than silent skip in strategy)
- Cancel open orders on graceful shutdown (prevents orphaned stops on restart)
- pm2-logrotate installed (10MB max, 3 retained, compressed)

**Trade history (paper):**
- Feb 27: GLD BUY + SELL (49.6 shares). Quick cycle — trail didn't activate.
- Mar 4: GLD BUY $475.24 → SELL $471.98 (50.89 shares, -$166 paper)
- Mar 4: SLV BUY $76.79 → server stop fired → wash trade bug → manually closed at $76.25 (-$168 paper)
- Mar 4: GDX had orphaned stop order from previous session, cancelled on restart
- Mar 4 (evening): 4 positions opened — GLD $471.54, IAU $96.67, SLV $75.56, GDX $105.75. Server stops confirmed working after DAY TIF fix. Order IDs logging confirmed.
- Mar 4: SLV sold $75.52 (bot exit, trailing stop updated then signal exit, -$12.80). GDX sold $106.08 (bot exit, +$75.27). GLD + IAU held overnight.
- **Confirmed:** bot-initiated exits, trailing stop updates, order cancellation before exit, position sync
- **Not yet confirmed:** server-side stop firing (Alpaca auto-selling when price hits stop between candles)

**Backtest predictions for test params (Dec 2025 – Mar 2026):**
Used to validate backtest accuracy — compare live results over next 2-4 weeks.

| Symbol | Return | Max DD | Trades | Win Rate |
|--------|--------|--------|--------|----------|
| GLD | +0.16% | 0.77% | 58 | 48% |
| SLV | +14.25% | 1.15% | 44 | 57% |
| GDX | +2.45% | 0.94% | 69 | 59% |
| IAU | -0.50% | 0.99% | 54 | 37% |

If live results roughly match these patterns (GLD/IAU flat, SLV strongest), backtest engine is reliable.

## Validated Edges

| Strategy | Asset | TF | Sharpe | Return | Max DD | WF |
|---|---|---|---|---|---|---|
| **StochRSI Enhanced** | **GLD** | **15m** | **2.54** | **+44.7%** | **0.69%** | **Audited** |
| **StochRSI Enhanced** | **SLV** | **15m** | **2.54** | **+105.3%** | **2.00%** | **4/4** |
| **StochRSI Enhanced** | **GDX** | **15m** | **2.41** | **+114.1%** | **2.02%** | **4/4** |
| **StochRSI Enhanced** | **IAU** | **15m** | **~2.0** | **+32.6%** | **0.72%** | **4/4** |

**Thesis:** Precious metals mean-revert at 15m within trend. Same params work across all 4 without retuning.

## Other Strategies Tested

| Strategy | Asset | TF | Result | Status |
|---|---|---|---|---|
| EventSurprise (CPI) | GLD | 15m | +2.36%, 86% WR, 14 trades | Built |
| StochRSI | GLD | 1h | Sharpe 1.44 | Validated |
| StochRSI | IAU | 1h | Sharpe 1.22 | Validated |
| StochRSI | XLE | 1h | Sharpe 1.11 | Validated |
| StochRSI | SPY/QQQ/IWM | 5m-15m | No alpha | Dead end |

## Strategy Index

> **Read these when working on a specific strategy. DO NOT auto-read.**

| Strategy | File | Summary |
|---|---|---|
| StochRSI Enhanced GLD | `strategies/stochrsi_enhanced_gld.md` | Best edge. Full audit: param sensitivity, spread, B&H comparison. |
| StochRSI Enhanced SLV | `strategies/stochrsi_enhanced_slv.md` | Same params as GLD. Precious metals thesis confirmed. |
| StochRSI Enhanced GDX | `strategies/stochrsi_enhanced_gdx.md` | Gold miners. Leveraged gold proxy. |
| StochRSI Enhanced IAU | `strategies/stochrsi_enhanced_iau.md` | GLD proxy ETF. Most consistent year-by-year, lowest DD. |
| EventSurprise | `strategies/event_surprise.md` | CPI/NFP surprise trading. |
| Composable Results | `strategies/composable_results.md` | Phase 3 combo results. |

## Reference Files

1. `.claude/memory/system_manual.md` - Technical reference (CLI, backtesting, live trading, IG API docs)
2. `.claude/memory/recent_history.md` - Last 20 commits with full context (auto-generated)
3. `.claude/memory/ideas.md` - **DO NOT auto-read.** Future ideas log. Only reference when user explicitly asks.
4. `.claude/memory/strategies/` - **DO NOT auto-read.** Per-strategy research and params.
5. `.claude/archive/` - Historical plans (edge enhancement, discovery engine, forward testing)

## Quick Commands

```bash
# Check cloud bots
gcloud compute ssh algotrader2026 --zone=europe-west2-a --command="pm2 status"

# View bot logs (replace BOT_NAME)
gcloud compute ssh algotrader2026 --zone=europe-west2-a --command="pm2 logs BOT_NAME --lines 20 --nostream"

# Check latest signals across all bots
gcloud compute ssh algotrader2026 --zone=europe-west2-a --command="for bot in gld-test iau-test slv-test gdx-test; do echo \"=== \$bot ===\"; cat /home/alistairelliman/.pm2/logs/\${bot}-out.log | grep -E 'K:|BUY|SELL|FILLED' | tail -3; done"

# Deploy code changes
git push origin main
gcloud compute ssh algotrader2026 --zone=europe-west2-a --command="cd algo-trader-v1 && git pull && pm2 restart all"

# Backtest StochRSI Enhanced (validated params)
python3 -m backend.runner backtest --strategy StochRSIMeanReversion --symbol GLD --timeframe 15m --start 2020-01-01 --end 2025-12-31 --source alpaca --spread 0.0003 --delay 0 --parameters '{"rsi_period":7,"stoch_period":14,"overbought":80,"oversold":15,"adx_threshold":20,"skip_adx_filter":false,"sl_atr":2.0,"trailing_stop":true,"trail_atr":2.0,"trail_after_bars":10,"min_hold_bars":10,"skip_days":[0]}'
```

## Git Save Protocol

```bash
# 1. Update strategy memory if findings/params changed
# 2. Update claude.md if status/phase changed
# 3. Commit, then run ./scripts/update_memory.sh
# 4. git add .claude/memory/ && git commit --amend --no-edit
# 5. git push origin main
```

## Critical Context

### Deployment Flow
- Bots run on **cloud server**, not local machine
- Code changes: local edit → git push → cloud pull → pm2 restart
- Changes don't take effect until all steps complete

### Platform Constraints
- **Crypto shorts:** Disabled (Alpaca doesn't support)
- **Fractional shares:** ✅ Working. Uses `DAY` TIF (required by Alpaca), rounds to 4 decimals, min $1 order. **Stop orders also DAY** — expire at market close, re-placed on first bar after open.
- **Bracket orders:** Not supported for crypto
- **Market hours:** 2:30 PM - 9:00 PM Irish time (9:30 AM - 4:00 PM ET)
- **One position per symbol:** Multiple bots on same symbol WILL conflict. Use different symbols or separate accounts.

### Backtest Settings (validated against live)
```bash
--spread 0.0003 --delay 0
# spread 0.0003 = 0.03% of price
# delay 0 = fill at bar's Close (matches live execution)
```
**WARNING:** `--delay 1` is broken — fills at same bar's Open, not next bar's. Never use.

### Known Issues
- **Server RAM tight** (958MB + 1GB swap). Avoid heavy SSH commands while bots process bars.
- **Live fetch window:** Set to 7 days in runner.py. Must stay ≥7 to exceed `on_bar`'s `i < 50` guard, especially after weekends.

## Next Steps

- [x] Bot-initiated exits confirmed (signal-based sell with stop cancellation)
- [x] Trailing stop update confirmed (ratchets up on bar)
- [ ] Confirm server-side stop firing (Alpaca auto-sell when price hits stop between candles)
- [ ] Run test bots 2-4 weeks, compare live results to backtest predictions above
- [ ] Once mechanics verified + backtest accuracy confirmed: switch to validated params (OB 80/OS 15, trail 10, hold 10, skip Monday)
- [ ] Start real-money micro trading on Alpaca with €100-200 (fractional shares)
- [ ] Paper test EventSurprise (CPI-only) on cloud
- [ ] Scale up capital as live results match backtest expectations

## Discovery Engine (built, not currently running)

- **Experiments DB:** 5,300+ experiments, 90+ validated passes
- **Phases:** Sweep → Filter → Validate → Composable (all complete)
- **Overnight orchestrator:** `backend/optimizer/run_overnight.py` — chains all phases
- **CLI:** `python -m backend.optimizer.run_overnight [--scan|--quick|--medium] [--max-hours N] [--symbols X,Y]`

## Codebase Reference

**Strategies (21):** StochRSIMeanReversion, DonchianBreakout, SwingBreakout, MACDBollinger, EventSurprise, + variants
**Indicators:** StochRSI, RSI, MACD, ADX, Bollinger Bands, Donchian, ATR, SMA, CHOP
**Frontend:** Next.js dashboard at `frontend/` — DB-driven, auto-updates as engine validates edges

---

*Last updated: 2026-03-04. 4 test bots live (paper). Verifying execution mechanics before real money.*
