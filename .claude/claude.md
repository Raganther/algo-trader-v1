# Algo Trader V1 - Session Primer

> **Claude reads this automatically at session start. Keep it current.**

## Current Status

- **Phase:** 10 - Strategy Discovery Engine (Phases 0-3 complete, overnight orchestrator built)
- **Active Bots:** 1 (GLD 15m StochRSI — PAPER mode, validated params)
- **Server:** europe-west2-a (algotrader2026)
- **Discovery Engine:** Phase 0 (DB) ✓, Phase 1 (sweeps) ✓, Phase 2 (validation) ✓, Phase 3 (composable) ✓, Overnight orchestrator ✓
- **Key Finding:** GLD 15m StochRSI Enhanced — Sharpe 2.42, VALIDATED. Trailing stop + min hold + skip Monday.
- **Experiments DB:** 5,300+ experiments, 90+ validated passes (growing via overnight runs)

## Where We Left Off (Feb 13)

**Edge enhancements validated. Trailing stop + min hold took GLD 15m from Sharpe 1.57 to 2.42. All 4 variants passed full validation (holdout + walk-forward + multi-asset). Bot running baseline params on paper — enhanced version ready to deploy.**

### What's been built:
1. **Phase 0 — Experiments DB:** `experiments` table + `ExperimentTracker` class
2. **Phase 1 — Sweep Engine:** 5,300+ param sweeps across 21 symbol/TF combos
3. **Phase 2 — Validation:** holdout, walk-forward, multi-asset — 90 passed
4. **Phase 3 — Composable Strategies:** 458 indicator combos tested on GLD 1h
5. **Overnight Orchestrator:** `run_overnight.py` — chains all phases for unattended runs

### Overnight orchestrator (`backend/optimizer/run_overnight.py`):
- **4 passes:** Broad sweep → Filter → Validate → Expand winners
- **CLI:** `python -m backend.optimizer.run_overnight [--scan|--quick|--medium] [--max-hours N] [--skip-composable] [--skip-sweep] [--skip-validation] [--symbols X,Y] [--timeframes 15m,1h]`
- **Grid tiers:** scan (11 combos), quick (32), medium (972), full (3,456) per target
- **Time budget:** Global timer, graceful stop at each pass when expired
- **Crash recovery:** `skip_tested=True` everywhere, re-run picks up where left off
- **Priority targets:** GLD other TFs, gold-correlated (SLV/IAU/GDX), XLE/XBI/TLT, broad market

### GLD forward test (deployed):
- **Bot:** gld-15m on cloud, PAPER mode, StochRSI with validated params (switched from 1h on Feb 13)
- **Params:** RSI 7, Stoch 14, OB 80, OS 15, ADX threshold 20, ATR stop 2x
- **Script:** `scripts/run_gld.sh` — old EXTREME bots stopped

### Phase 3 composable results (458 combos → 3 validated):
- 7 of top 10 **REJECTED** — high-Sharpe/low-trade combos were overfit noise
- 3 **PASSED** full validation (holdout + walk-forward + multi-asset):

| Combo | Test Return | WF Pass | Multi-Asset | Trades |
|-------|-----------|---------|-------------|--------|
| RSI extreme + Opposite zone | +0.3% | 75% | 100% (3/3) | 263 |
| MACD cross + Donchian exit + SMA uptrend | +10.9% | 75% | 67% (2/3) | 176 |
| RSI extreme + Trailing ATR 3x | +4.9% | 75% | 67% (2/3) | 252 |

### Best validated edge — GLD 15m StochRSI Enhanced (Sharpe 2.42):
- **Base params:** RSI 7, Stoch 14, OB 80, OS 15, ADX threshold 20, ATR stop 2x
- **Enhancements:** skip Monday, trailing stop (2x ATR after 10 bars), min hold 10 bars
- **Full-period return:** 38.1%, **Max drawdown:** 0.7%, **Trades:** 465 over 5 years
- **Holdout test:** Train +18.6% (Sharpe 2.27), Test +16.4% (Sharpe 2.69) — minimal degradation
- **Walk-forward:** 4/4 windows positive (100%), all years profitable
- **Multi-asset:** GLD +38%, SLV +92%, IAU +31% — generalises strongly
- **Previous baseline:** Sharpe 1.57, 664 trades, 1.2% DD — enhancements nearly doubled Sharpe

### Edge Enhancement Results (Feb 13):
**Diagnostic analysis found three key leaks:**
1. Stop losses were 100% losers (199 trades, -$1,219) → fixed with trailing stop
2. Short-duration trades (1-5 bars) were breakeven noise (72% of trades) → fixed with min hold
3. Monday trades were near-zero edge (128 trades, +$23 total) → fixed with day filter

**All 4 tested variants passed full validation:**

| Variant | Sharpe | Holdout Ret | WF Pass | Multi-Asset | DD |
|---|---|---|---|---|---|
| Baseline (no enhancements) | 1.44 | +9.4% | 4/4 | 3/3 | 1.2% |
| Trail 2x/5bar + Hold 5 | 2.19 | +15.3% | 4/4 | 3/3 | 0.7% |
| **Skip Mon + Trail 2x/10bar + Hold 10** | **2.42** | **+16.4%** | **4/4** | **3/3** | **0.7%** |
| Trail 3x ATR after 5 bars | 1.85 | +14.6% | 4/4 | 3/3 | 1.3% |

**Key insight:** Enhancements performed *better* on unseen data than in-sample. The trailing stop is a structural improvement (not curve-fitting) — it also improved SLV (+92%) and IAU (+31%).

### What to decide next:
- Deploy enhanced params to paper bot (replace current baseline params)
- Apply trailing stop enhancement to other validated strategies (GLD 1h, IAU 1h, XLE 1h)
- Run next iteration: fine-tune trail/hold params, test exit-focused enhancements
- Explore spread betting / IG API for small-account trading (ideas.md #11)
- Position sizing / Kelly with improved Sharpe 2.42 and DD 0.7% (ideas.md #7)

## Read These Files for Details

1. `.agent/workflows/edge_enhancement_plan.md` - **ACTIVE** — plan to improve validated edges (time filters, exits, vol scaling)
2. `.agent/workflows/strategy_discovery_engine.md` - Full build plan for automated strategy search (Phases 0-3 complete)
3. `.agent/memory/recent_history.md` - Last 20 commits with full context
4. `.agent/workflows/forward_testing_plan.md` - Complete forward test journey (Phases 1-9)
5. `.agent/memory/system_manual.md` - Technical reference (backtesting + live)
6. `.agent/memory/research.md` - Alternative strategy research + live validation findings
7. `.agent/memory/research_insights.md` - RETIRED (contaminated with delay=1 results, replaced by ExperimentTracker)
8. `.agent/memory/ideas.md` - **DO NOT auto-read.** Future ideas log (#1-17: hedging, pairs trading, regime detection, time filters, exits, etc). Only reference when user explicitly asks.

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

**GLD Forward Test (active — switched to 15m on Feb 13):**
- RSI period: 7, Stoch period: 14
- Oversold: 15, Overbought: 80
- ADX threshold: 20 (filter ON)
- ATR stop: 2x
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
- [x] Run Phase 2 validation on top composable candidates — 3/10 passed, 7 rejected
- [x] Build overnight orchestrator — `run_overnight.py` chains all phases unattended
- [x] Run scan + medium grid sweeps across 21 symbol/TF combos (5,300+ experiments)
- [x] Validate top candidates — 90 passed, GLD 15m Sharpe 1.66 is best
- [x] Deploy GLD 15m bot on paper (replaced GLD 1h on Feb 13)
- [x] **Edge Enhancement:** Trade analysis → trailing stop + min hold + Monday filter → Sharpe 1.57 → 2.42
- [x] Validate enhancements — all 4 variants passed holdout + walk-forward + multi-asset
- [ ] Deploy enhanced params to paper bot (skip Mon, trail 2x/10bar, hold 10)
- [ ] Apply trailing stop to other validated strategies (GLD 1h, IAU, XLE, SLV)
- [ ] Review validation run results (150 candidates, ran Feb 13)
- [ ] Explore spread betting / IG API for small-account trading (ideas.md #11)
- [ ] Position sizing with improved risk profile (Sharpe 2.42, DD 0.7%)
- [ ] Monitor GLD 15m forward test (paper trading)

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
| **StochRSI** | **GLD** | **15m** | **Sharpe 1.57 base → 2.42 enhanced** | **VALIDATED (best edge)** |
| **StochRSI+Enhanced** | **GLD** | **15m** | **Sharpe 2.42, +38%, DD 0.7%, 465 trades** | **VALIDATED** |
| **StochRSI** | **GLD** | **1h** | **+18.3% ann, Sharpe 1.44** | **VALIDATED** |
| StochRSI | IAU | 1h | +11.6% ann, Sharpe 1.22 | Validated |
| StochRSI | XLE | 1h | +11.1% ann, Sharpe 1.11 | Validated |
| StochRSI | XBI | 1h | +9.0% ann, Sharpe 0.90 | Sweep positive |
| StochRSI | TLT | 1h | +8.5% ann, Sharpe 0.85 | Sweep positive |

**Live trading (EXTREME mode, 100+ trades):** Confirms ~zero net returns on SPY/QQQ/IWM.
**Discovery Engine (5,300+ experiments, 90+ validated):** GLD 15m enhanced (Sharpe 2.42) is best edge. Trailing stop + min hold validated across GLD/SLV/IAU. GLD/IAU/XLE 1h also validated.

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

*Last updated: 2026-02-13 (Edge enhancements validated — Sharpe 1.57→2.42, trailing stop + min hold + skip Mon)*
*Update this file when phase changes or major milestones reached*
