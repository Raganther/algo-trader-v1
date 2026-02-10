# Algo Trader V1 - Session Primer

> **Claude reads this automatically at session start. Keep it current.**

## Current Status

- **Phase:** 9 - Strategy Direction Decision
- **Active Bots:** 3 (SPY 5m, QQQ 15m, IWM 5m) — all StochRSI EXTREME mode
- **Server:** europe-west2-a (algotrader2026)
- **Mode:** EXTREME testing (50/50 thresholds, ADX disabled)
- **Infrastructure:** Fully validated. Bots stable 5+ days, 100+ trades executed, no crashes.

## Where We Left Off (Feb 10)

**Decision point reached:** Should we continue iterating on indicator-based strategies, or pivot to alternative approaches?

### What's been proven:
1. **Infrastructure works perfectly** — bots run for days, orders fill reliably, position sync works
2. **Backtester is now trustworthy** — `--spread 0.0003 --delay 0` matches live execution
3. **Live trading confirms backtest findings** — trades net roughly zero, consistent with corrected backtests
4. **Indicator-only strategies on SPY/QQQ/IWM produce no alpha** after realistic costs

### What hasn't been tried (indicator-based):
- Less efficient assets (small-cap ETFs, sector ETFs like XLE/XBI, emerging markets)
- Volume-based indicators (OBV, VWAP — everything tested so far is price-only)
- Multi-timeframe confluence (e.g. 5m signals only when daily trend aligns)
- Crypto markets (RegimeGatedStoch on BTC showed small positive: +1.74% ann.)

### Alternative approaches documented in research.md:
- **Tier 1:** Economic announcement events (FOMC/NFP/CPI), VIX term structure regime filter
- **Tier 2:** Sector rotation momentum, post-earnings drift (PEAD), credit spread overlay
- NFPBreakoutStrategy skeleton exists but untested

### Owner's position:
Interested in continuing indicator experimentation now that backtester is accurate, before giving up entirely. The corrected backtester is a reliable tool — any strategy showing profit with `delay=0` has a real chance of working live.

## Read These Files for Details

1. `.agent/memory/recent_history.md` - Last 20 commits with full context
2. `.agent/workflows/forward_testing_plan.md` - Complete forward test journey (Phases 1-9)
3. `.agent/memory/system_manual.md` - Technical reference (backtesting + live)
4. `.agent/memory/research_insights.md` - Strategy backtest performance (auto-generated)
5. `.agent/memory/research.md` - Alternative strategy research + live validation findings

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

## Backtest Settings (CORRECT — validated against live)

```bash
# These settings match live execution characteristics
--spread 0.0003 --delay 0

# spread 0.0003 = 0.03% of price (~$0.21 on $700 stock)
# delay 0 = fill at bar's Close (matches live: bot sees close, places market order immediately)
```

**WARNING:** `--delay 1` is broken — it fills at same bar's Open (not next bar's Open), creating phantom profit for mean reversion. Never use delay=1.

## Current Testing Settings

**EXTREME Mode (active — for slippage data collection):**
- Oversold: 50 (trades at midpoint)
- Overbought: 50 (trades every reversal)
- ADX filter: DISABLED (`skip_adx_filter=True`)

**Production Mode (if reverting):**
- Oversold: 20
- Overbought: 80
- ADX filter: ENABLED

## Next Steps

- [x] Fix IWM dual-bot conflict (stopped donchian-iwm-5m, keeping iwm-5m only)
- [x] Validate live trading confirms corrected backtest findings (confirmed: trades net ~zero)
- [ ] Decide direction: more indicator experiments vs alternative data approaches
- [ ] If indicators: test on less efficient assets, add volume indicators, try multi-TF confluence
- [ ] If alternative: build economic calendar integration (NFP/CPI/FOMC event trading)
- [ ] Run EXTREME mode through Feb 13 to finish slippage data collection
- [ ] After direction chosen: revert to conservative 20/80 thresholds or deploy new strategy

## Strategies Tested (with corrected costs)

| Strategy | Asset | TF | Result | Status |
|---|---|---|---|---|
| StochRSI | QQQ | 5m | 0.99% | No alpha |
| StochRSI | IWM | 15m | -1.13% | No alpha |
| StochRSI | SPY | 15m | -8.61% | No alpha |
| Donchian | QQQ | 4h | -6.38% | No alpha |
| SwingBreakout | SPY/QQQ/IWM | Daily | -0.01% to +1.39% | No alpha |
| MACD+Bollinger | QQQ | 1h | +1.03% ann. | Marginal |
| RegimeGatedStoch | SPY | 1h | +2.01% ann. | Marginal |
| RegimeGatedStoch | BTC | 1h | +1.74% ann. | Small positive |

**Live trading (EXTREME mode, 100+ trades):** Confirms ~zero net returns on SPY/QQQ/IWM.

## Available Indicators (in codebase)

StochRSI, RSI, MACD, ADX, Bollinger Bands, Donchian Channels, ATR, SMA, CHOP
**Not yet used in strategies:** CHOP (Choppiness Index)
**Not yet implemented:** OBV, VWAP, volume-based indicators

## Existing Strategy Code (20 strategies in backend/strategies/)

Core: StochRSIMeanReversion, DonchianBreakout, SwingBreakout, MACDBollinger
Variants: StochRSILimit, StochRSINextOpen, StochRSIQuant, StochRSISniper
Regime: HybridRegime, HybridRegimeV2, RegimeGatedStoch
Donchian variants: DonchianADX, DonchianReversal, DonchianTrend
Other: SimpleSMA, BollingerBreakout, GoldenCross, NFPBreakout (skeleton), GammaScalping (skeleton), RapidFireTest

---

*Last updated: 2026-02-10 (dual-bot fix, live validation complete, strategy direction decision point)*
*Update this file when phase changes or major milestones reached*
