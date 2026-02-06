# Algo Trader V1 - Session Primer

> **Claude reads this automatically at session start. Keep it current.**

## Current Status

- **Phase:** 8 - Multi-Asset Expansion & Slippage Analysis
- **Active Bots:** 4 (SPY 5m, QQQ 15m, IWM 5m, Donchian IWM 5m)
- **Server:** europe-west2-a (algotrader2026)
- **Mode:** EXTREME testing (50/50 thresholds, ADX disabled)

## Latest Achievement

- Slippage analysis complete: SPY 0.032%, QQQ 0.060%, IWM 0.030%
- 9 critical bugs fixed (position tracking, crypto shorts, API errors, whole shares)
- 20+ validated trades across SPY/QQQ/IWM
- Backtest assumptions validated against live execution

## Open Positions / Pending

- Check Alpaca dashboard for current positions
- IWM may have pending market order (fills at market open 2:30 PM Irish)

## Read These Files for Details

1. `.agent/memory/recent_history.md` - Last 20 commits with full context
2. `.agent/workflows/forward_testing_plan.md` - Complete forward test journey
3. `.agent/memory/system_manual.md` - Technical reference (backtesting + live)
4. `.agent/memory/research_insights.md` - Strategy backtest performance

## Quick Commands

```bash
# Check cloud bots
gcloud compute ssh algotrader2026 --zone=europe-west2-a --command="pm2 status"

# View bot logs
gcloud compute ssh algotrader2026 --zone=europe-west2-a --command="pm2 logs spy-5m --lines 20 --nostream"

# Deploy code changes
git push origin main
gcloud compute ssh algotrader2026 --zone=europe-west2-a --command="cd algo-trader-v1 && git pull && pm2 restart all"
```

## Git Save Protocol

```bash
# 1. Commit with detailed message
git add [files]
git commit -m "type: description" -m "detailed body..."

# 2. Auto-generate recent_history.md
./scripts/update_memory.sh

# 3. Amend to include history
git add .agent/memory/recent_history.md
git commit --amend --no-edit

# 4. Push
git push origin main
```

## Critical Context (Always Remember)

### Deployment Flow
- Bots run on **cloud server**, not local machine
- Code changes need: local edit → git push → cloud pull → pm2 restart
- Changes don't take effect until all steps complete

### Platform Constraints
- **Crypto shorts:** Disabled (Alpaca doesn't support)
- **Stock orders:** Whole shares only (no fractional)
- **Bracket orders:** Not supported for crypto
- **Market hours:** 2:30 PM - 9:00 PM Irish time (9:30 AM - 4:00 PM ET)

### What Works
- Position sync on restart (recovers state from Alpaca)
- Exit state guarding (only resets if order succeeds)
- API error handling (returns None, doesn't crash)
- Symbol normalization (BTCUSD + BTC/USD both work)

## Current Testing Settings

**EXTREME Mode (for infrastructure validation):**
- Oversold: 50 (trades at midpoint)
- Overbought: 50 (trades every reversal)
- ADX filter: DISABLED (`skip_adx_filter=True`)

**Production Mode (after validation):**
- Oversold: 20
- Overbought: 80
- ADX filter: ENABLED

## Next Steps

- [x] Monitor Donchian IWM 5m for first trades (trading as of Feb 6)
- [x] Check if IWM pending order filled at market open (confirmed)
- [x] Fix Donchian KeyError bug (`position['avg_price']` → `position['price']`)
- [ ] Fix IWM dual-bot conflict (both iwm-5m and donchian-iwm-5m sell combined position)
- [ ] Run EXTREME mode for 1 week (target: Feb 13) to collect slippage data
- [ ] Re-run backtests with corrected params: `--spread 0.0003 --delay 0`
- [ ] After backtests: revert to conservative 20/80 thresholds
- [ ] Forward test most promising strategies for 2+ months

## Critical Finding: Backtest Cost Model

Previous `--spread 0.0001 --delay 1` is misleading for mean reversion:
- `delay=1` HELPS entries (price continues in signal direction), making backtests optimistic
- Live fills in ~1 second (same bar), so we miss this delay benefit
- Corrected params: `--spread 0.0003 --delay 0` (after 1 week of data)

---

*Last updated: 2026-02-06*
*Update this file when phase changes or major milestones reached*
