# Algo Trader V1 - Session Primer

> **Claude reads this automatically at session start. Keep it current.**

## Current Status

- **Phase:** 10 - Strategy Discovery Engine (Phases 0-2 complete, GLD edge validated)
- **Active Bots:** 3 (SPY 5m, QQQ 15m, IWM 5m) — all StochRSI EXTREME mode
- **Server:** europe-west2-a (algotrader2026)
- **Discovery Engine:** Phase 0 (DB) ✓, Phase 1 (sweeps) ✓, Phase 2 (validation) ✓
- **Key Finding:** GLD 1h StochRSI — 18.3% ann, Sharpe 1.44, passed all validation checks
- **Experiments DB:** 1,332 experiments across GLD/XLE/XBI/TLT

## Where We Left Off (Feb 10)

**Phases 0-2 of Strategy Discovery Engine complete. GLD edge validated.**

### What's been built:
1. **Phase 0 — Experiments DB:** `experiments` table + `ExperimentTracker` class (save, query, dedup, LLM summaries)
2. **Phase 1 — Sweep Engine:** `sweep.py`, `scoring.py`, `data_utils.py`, `run_sweep.py` — ran 1,332 experiments across GLD/XLE/XBI/TLT
3. **Phase 2 — Validation Framework:** `disqualify.py`, `validation.py`, `pipeline.py` — holdout, walk-forward, multi-asset checks

### Key discovery results:
- **GLD 1h StochRSI:** 92% of 324 param combos profitable. Best: Sharpe 1.44, 18.3% ann return
- **XLE 1h StochRSI:** 88% profitable. Best: Sharpe 1.11
- **XBI 1h StochRSI:** 62% profitable. Best: Sharpe 0.90
- **TLT 1h StochRSI:** 55% profitable. Best: Sharpe 0.85

### Phase 2 validation results (18/18 passed):
- 17 GLD + 1 XLE candidates validated
- **100% walk-forward pass rate** across all candidates (positive in every rolling test window)
- **100% multi-asset consistency** (GLD edge generalises to SLV and IAU)
- Best out-of-sample return: **10.5%** on 2024-2025 holdout data
- Best params: RSI 21, Stoch 7, OB 80, OS 15, ATR stop 3x, ADX filter on

### What to decide next:
- **Option A:** Forward-test best GLD strategy live (deploy to cloud, monitor)
- **Option B:** Phase 3 — composable strategies to refine/combine indicators
- **Option C:** Both in parallel

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
- [x] Decide direction → Build automated Strategy Discovery Engine
- [x] Design build plan (4 phases, data strategy, file map) → `strategy_discovery_engine.md`
- [x] **Phase 0:** Add `experiments` table + `ExperimentTracker` class
- [x] **Phase 1:** Build sweep engine + run 1,332 experiments across GLD/XLE/XBI/TLT
- [x] **Phase 2:** Build validation framework — 18/18 top candidates passed all checks
- [ ] **Decide:** Forward-test GLD live vs Phase 3 composable strategies vs both
- [ ] **Phase 3:** Build composable strategy framework (building blocks + generator)
- [ ] **Phase 4:** Build LLM agent loop (prompt builder, code validator, iteration loop)
- [ ] Run EXTREME mode through Feb 13 to finish slippage data collection
- [ ] Deploy validated GLD strategy to cloud for live forward testing

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
**Discovery Engine (1,332 experiments):** GLD/XLE edges validated through holdout, walk-forward, multi-asset checks.

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

*Last updated: 2026-02-10 (Discovery Engine Phases 0-2 complete, GLD edge validated, 18/18 passed)*
*Update this file when phase changes or major milestones reached*
