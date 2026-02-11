# Algo Trader V1 - Session Primer

> **Claude reads this automatically at session start. Keep it current.**

## Current Status

- **Phase:** 10 - Strategy Discovery Engine (Phases 0-3 complete, GLD forward testing)
- **Active Bots:** 1 (GLD 1h StochRSI — PAPER mode, validated params)
- **Server:** europe-west2-a (algotrader2026)
- **Discovery Engine:** Phase 0 (DB) ✓, Phase 1 (sweeps) ✓, Phase 2 (validation) ✓, Phase 3 (composable) ✓
- **Key Finding:** GLD 1h StochRSI — Sharpe 1.44, + new composable combos (MACD+ATR Sharpe 1.14)
- **Experiments DB:** 1,800 experiments (1,332 parameter sweeps + 458 composable combos)

## Where We Left Off (Feb 10)

**Phases 0-3 complete. GLD forward test deployed. Composable sweep found new combos.**

### What's been built:
1. **Phase 0 — Experiments DB:** `experiments` table + `ExperimentTracker` class
2. **Phase 1 — Sweep Engine:** 1,332 param sweeps across GLD/XLE/XBI/TLT
3. **Phase 2 — Validation:** holdout, walk-forward, multi-asset — 18/18 passed
4. **Phase 3 — Composable Strategies:** 458 indicator combos tested on GLD 1h

### GLD forward test (deployed):
- **Bot:** gld-1h on cloud, PAPER mode, StochRSI with validated params
- **Params:** RSI 21, Stoch 7, OB 80, OS 15, ADX threshold 25, ATR stop 3x
- **Script:** `scripts/run_gld.sh` — old EXTREME bots stopped

### Phase 3 composable results (top combos on GLD 1h):
| Sharpe | Return | Trades | Entry | Exit | Filter |
|--------|--------|--------|-------|------|--------|
| 1.137 | +34.0% | 12 | MACD cross | ATR stop 3x | none |
| 1.113 | +33.3% | 14 | Bollinger bounce | ATR stop 3x | none |
| 0.797 | +7.3% | 263 | RSI extreme | Opposite zone | none |
| 0.661 | +8.8% | 176 | MACD cross | Donchian exit | SMA uptrend |

### What to decide next:
- Run Phase 2 validation on top composable candidates
- Monitor GLD forward test for live confirmation
- Phase 4 (LLM agent) — optional given current results

## Read These Files for Details

1. `.agent/workflows/strategy_discovery_engine.md` - **START HERE** — full build plan for automated strategy search
2. `.agent/memory/recent_history.md` - Last 20 commits with full context
3. `.agent/workflows/forward_testing_plan.md` - Complete forward test journey (Phases 1-9)
4. `.agent/memory/system_manual.md` - Technical reference (backtesting + live)
5. `.agent/memory/research.md` - Alternative strategy research + live validation findings
6. `.agent/memory/research_insights.md` - RETIRED (contaminated with delay=1 results, replaced by ExperimentTracker)

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

**GLD Forward Test (active):**
- RSI period: 21, Stoch period: 7
- Oversold: 15, Overbought: 80
- ADX threshold: 25 (filter ON)
- ATR stop: 3x
- Mode: PAPER

## Next Steps

- [x] Fix IWM dual-bot conflict (stopped donchian-iwm-5m, keeping iwm-5m only)
- [x] Validate live trading confirms corrected backtest findings (confirmed: trades net ~zero)
- [x] Decide direction → Build automated Strategy Discovery Engine
- [x] Design build plan (4 phases, data strategy, file map) → `strategy_discovery_engine.md`
- [x] **Phase 0:** Add `experiments` table + `ExperimentTracker` class
- [x] **Phase 1:** Build sweep engine + run 1,332 experiments across GLD/XLE/XBI/TLT
- [x] **Phase 2:** Build validation framework — 18/18 top candidates passed all checks
- [x] **Phase 3:** Build composable framework — 458 combos on GLD, new edges found
- [x] Deploy GLD 1h StochRSI to cloud (PAPER mode, validated params)
- [x] Stop old EXTREME bots (SPY/QQQ/IWM)
- [ ] Run Phase 2 validation on top composable candidates
- [ ] Monitor GLD forward test (paper trading)
- [ ] **Phase 4:** Build LLM agent loop (optional — may not be needed)

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
| **StochRSI** | **GLD** | **1h** | **+18.3% ann, Sharpe 1.44** | **VALIDATED** |
| StochRSI | XLE | 1h | +11.1% ann, Sharpe 1.11 | Validated |
| StochRSI | XBI | 1h | +9.0% ann, Sharpe 0.90 | Sweep positive |
| StochRSI | TLT | 1h | +8.5% ann, Sharpe 0.85 | Sweep positive |

**Live trading (EXTREME mode, 100+ trades):** Confirms ~zero net returns on SPY/QQQ/IWM.
**Discovery Engine (1,800 experiments):** GLD/XLE edges validated. Composable sweep found MACD+ATR and Bollinger+ATR combos.

## Available Indicators (in codebase)

StochRSI, RSI, MACD, ADX, Bollinger Bands, Donchian Channels, ATR, SMA, CHOP
**Now used in composable strategies:** CHOP (as filter), all indicators composable via building_blocks.py
**Not yet implemented:** OBV, VWAP, volume-based indicators

## Existing Strategy Code (20 strategies in backend/strategies/)

Core: StochRSIMeanReversion, DonchianBreakout, SwingBreakout, MACDBollinger
Variants: StochRSILimit, StochRSINextOpen, StochRSIQuant, StochRSISniper
Regime: HybridRegime, HybridRegimeV2, RegimeGatedStoch
Donchian variants: DonchianADX, DonchianReversal, DonchianTrend
Other: SimpleSMA, BollingerBreakout, GoldenCross, NFPBreakout (skeleton), GammaScalping (skeleton), RapidFireTest

---

*Last updated: 2026-02-11 (Phase 3 composable sweep complete, GLD forward test deployed, 1,800 experiments)*
*Update this file when phase changes or major milestones reached*
