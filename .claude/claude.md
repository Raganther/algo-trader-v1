# Algo Trader V1 - Session Primer

> **Claude reads this automatically at session start. Keep it current.**

## Current Status

- **Phase:** 10 - Strategy Discovery Engine (Phases 0-3 complete, overnight orchestrator built)
- **Active Bots:** 2 (gld-test + iau-test — PAPER mode, aggressive params to verify enhancement mechanics)
- **Server:** europe-west2-a (algotrader2026)
- **Discovery Engine:** Phase 0 (DB) ✓, Phase 1 (sweeps) ✓, Phase 2 (validation) ✓, Phase 3 (composable) ✓, Overnight orchestrator ✓
- **Key Finding:** GLD 15m StochRSI Enhanced — Sharpe 2.54 (audited Feb 27), VALIDATED. Trailing stop + min hold + skip Monday.
- **Experiments DB:** 5,300+ experiments, 90+ validated passes (growing via overnight runs)
- **IG Integration:** ✅ Phase 1-2 done (data loader + IGBroker). IG best used for execution only.
- **Fractional Shares:** ✅ Alpaca fractional orders enabled — can trade GLD with €100 (min $1 order).

## Where We Left Off (Feb 27)

**Built Strategy Reference Dashboard (frontend rebuild) + ran full GLD 15m audit.**

**Dashboard:** Replaced old experiment matrix browser with curated personal reference dashboard. Fully DB-driven — strategy cards auto-generate from `experiments` table when `validation_status='passed'` AND Sharpe ≥ 1.0. Detail pages show year-by-year table, equity curve, drawdown chart, and research notes (live from `.claude/memory/strategies/*.md`).

**GLD 15m Audit (Feb 27):**
- Data quality: 36,075 bars, resampled 1m→15m via Alpaca IEX. Clean.
- Full period (2020–Feb 2026): 44.7%, DD 0.69%, 710 trades, Sharpe 2.54
- Parameter sensitivity: robust. `min_hold_bars=10` is critical — dropping to 5 kills returns. `trail_atr=1.5` shows +47.5% vs +43% baseline (worth investigating).
- Spread sensitivity: profitable up to 0.22% spread — 7-20× headroom vs real GLD spreads.
- Buy & Hold honest: B&H returned 117.5% vs 44.7% (gold bull run). Strategy wins on risk-adjusted: Sharpe 2.54 vs 0.98, DD 0.69% vs 22%.
- Key risk: strategy underperforms in trending markets. Works in all conditions but absolute return lags B&H in strong trends.

**Key fixes during session:**
- Inserted enhanced GLD 15m experiment as `passed` with Sharpe 2.54.
- Ran GLD 1h year-by-year backtests (2020–2025), stored in test_runs.
- Fixed iteration_index query logic for per-year runs.
- Fixed markdown map to exact `Strategy|SYMBOL|TF` keys.

### Frontend architecture:
- **`frontend/src/lib/db.ts`** — server-only SQLite reader (better-sqlite3), reads research.db directly
- **`frontend/src/lib/registry.ts`** — markdown file map + status thresholds (Sharpe ≥ 1.3 = validated)
- **`frontend/src/app/page.tsx`** — index: DB-driven card grid, auto-sorted by Sharpe
- **`frontend/src/app/strategy/[slug]/page.tsx`** — detail: stats panel, year table, equity curve, notes
- **No FastAPI needed** — Next.js API routes read DB/files directly
- **`next.config.ts`** — `serverExternalPackages: ['better-sqlite3']`

### What's been built:
1. **Phase 0 — Experiments DB:** `experiments` table + `ExperimentTracker` class
2. **Phase 1 — Sweep Engine:** 5,300+ param sweeps across 21 symbol/TF combos
3. **Phase 2 — Validation:** holdout, walk-forward, multi-asset — 90 passed
4. **Phase 3 — Composable Strategies:** 458 indicator combos tested on GLD 1h
5. **Overnight Orchestrator:** `run_overnight.py` — chains all phases for unattended runs
6. **Economic Calendar Integration:** event blackout filter + EventSurprise strategy
7. **EventSurprise Strategy:** `backend/strategies/event_surprise.py` — CPI/NFP surprise trading
8. **Strategy Dashboard:** `frontend/` — DB-driven reference UI, auto-updates as engine validates edges

### Overnight orchestrator (`backend/optimizer/run_overnight.py`):
- **4 passes:** Broad sweep → Filter → Validate → Expand winners
- **CLI:** `python -m backend.optimizer.run_overnight [--scan|--quick|--medium] [--max-hours N] [--skip-composable] [--skip-sweep] [--skip-validation] [--symbols X,Y] [--timeframes 15m,1h]`
- **Grid tiers:** scan (11 combos), quick (32), medium (972), full (3,456) per target
- **Crash recovery:** `skip_tested=True` everywhere, re-run picks up where left off

## Strategy Index

> **Read these when working on a specific strategy. DO NOT auto-read.**

| Strategy | File | Status | Summary |
|---|---|---|---|
| **StochRSI Enhanced GLD** | `strategies/stochrsi_enhanced_gld.md` | VALIDATED (Sharpe 2.54, audited Feb 27) | Best edge. 44.7% / 0.69% DD / all years positive. Full audit done: param sensitivity, spread sensitivity, B&H comparison. |
| **EventSurprise** | `strategies/event_surprise.md` | BUILT (backtest positive) | CPI/NFP surprise trading. Research findings, direction mappings, results |
| **Composable Results** | `strategies/composable_results.md` | Complete (3 validated) | Phase 3 combo results, building blocks reference |

## Strategies Tested (summary)

| Strategy | Asset | TF | Result | Status |
|---|---|---|---|---|
| **StochRSI Enhanced** | **GLD** | **15m** | **Sharpe 2.54 (audited), +44.7%, DD 0.69%** | **VALIDATED (best)** |
| **EventSurprise (CPI)** | **GLD** | **15m** | **+2.36%, 86% WR, 14 trades** | **Built** |
| StochRSI | GLD | 1h | Sharpe 1.44 | Validated |
| StochRSI | IAU | 1h | Sharpe 1.22 | Validated |
| StochRSI | XLE | 1h | Sharpe 1.11 | Validated |
| StochRSI | XBI/TLT | 1h | Sharpe 0.85-0.90 | Sweep positive |
| StochRSI | SPY/QQQ/IWM | 5m-15m | No alpha | Confirmed live |
| EventSurprise (all) | GLD | 15m | +2.95%, 48% WR, 58 trades | Built |

## Reference Files

1. `.claude/memory/system_manual.md` - Technical reference (CLI, backtesting, live trading, IG API docs)
2. `.claude/memory/recent_history.md` - Last 20 commits with full context (auto-generated)
3. `.claude/memory/ideas.md` - **DO NOT auto-read.** Future ideas log (#1-18). Only reference when user explicitly asks.
4. `.claude/memory/strategies/` - **DO NOT auto-read.** Per-strategy research, findings, and params. Read when working on that strategy.
5. `.claude/archive/edge_enhancement_plan.md` - Plan to improve validated edges
6. `.claude/archive/strategy_discovery_engine.md` - Full build plan for automated strategy search
7. `.claude/archive/forward_testing_plan.md` - Complete forward test journey (Phases 1-9)

## Quick Commands

```bash
# Check cloud bots
gcloud compute ssh algotrader2026 --zone=europe-west2-a --command="pm2 status"

# View bot logs
gcloud compute ssh algotrader2026 --zone=europe-west2-a --command="pm2 logs spy-5m --lines 20 --nostream"

# Deploy code changes
git push origin main
gcloud compute ssh algotrader2026 --zone=europe-west2-a --command="cd algo-trader-v1 && git pull && pm2 restart all"

# Backtest StochRSI Enhanced (CORRECT param names — verified Feb 26)
python3 -m backend.runner backtest --strategy StochRSIMeanReversion --symbol GLD --timeframe 15m --start 2020-01-01 --end 2025-12-31 --source alpaca --spread 0.0003 --delay 0 --parameters '{"rsi_period":7,"stoch_period":14,"overbought":80,"oversold":15,"adx_threshold":20,"skip_adx_filter":false,"sl_atr":2.0,"trailing_stop":true,"trail_atr":2.0,"trail_after_bars":10,"min_hold_bars":10,"skip_days":[0]}'

# Backtest EventSurprise (CPI-only)
python3 -m backend.runner backtest --strategy EventSurprise --symbol GLD --timeframe 15m --start 2020-01-01 --end 2025-12-31 --source alpaca --spread 0.0003 --delay 0 --parameters '{"event_types":["CPI m/m","CPI y/y"],"hold_bars":4,"stop_pct":0.5,"entry_delay":1}'
```

## Git Save Protocol

```bash
# 1. Update strategy memory (if this session changed findings/params/results for a strategy)
#    Edit the relevant .claude/memory/strategies/<strategy>.md file
#    Also update claude.md if status/summary changed (e.g. new strategy, phase change)

# 2. Commit with detailed message
git add [files]
git commit -m "type: description" -m "detailed body..."

# 3. Auto-generate recent_history.md
./scripts/update_memory.sh

# 4. Amend to include history + memory updates
git add .claude/memory/
git commit --amend --no-edit

# 5. Push
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
- **One position per symbol:** Alpaca has one shared position per symbol per account. Multiple bots on same symbol WILL conflict. Use different symbols (e.g. GLD + IAU) or separate accounts.

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

**Enhancement Verification (active — 2 bots, aggressive params for more trades):**
- RSI period: 7, Stoch period: 14
- Oversold: 40, Overbought: 60 (wide — triggers more signals)
- ADX threshold: 50
- ATR stop: 2x, trailing stop: 2x ATR after 3 bars, min hold: 3 bars
- Skip days: Monday
- Symbols: GLD (gld-test) + IAU (iau-test)
- Mode: PAPER

## Next Steps

- [ ] Monitor gld-test + iau-test for trades (DAY TIF fix deployed Feb 26)
- [ ] Once enhancement mechanics verified: switch to validated params (OB 80/OS 15, trail 10 bars, hold 10)
- [ ] Start real-money micro trading on Alpaca with €100-200 (fractional GLD)
- [ ] Apply trailing stop to other validated strategies (GLD 1h, IAU, XLE, SLV) — run year backtests + insert into experiments
- [ ] Paper test EventSurprise (CPI-only) on cloud
- [ ] Run overnight orchestrator — new validated edges will auto-appear in dashboard
- [ ] Add research notes `.md` files for GLD 1h, IAU 1h, XLE 1h strategies
- [ ] To add notes for a strategy: create `.claude/memory/strategies/<name>.md` + add key to `frontend/src/lib/registry.ts` MARKDOWN_MAP

## Existing Strategy Code (21 strategies in backend/strategies/)

Core: StochRSIMeanReversion, DonchianBreakout, SwingBreakout, MACDBollinger, **EventSurprise**
Variants: StochRSILimit, StochRSINextOpen, StochRSIQuant, StochRSISniper
Regime: HybridRegime, HybridRegimeV2, RegimeGatedStoch
Donchian variants: DonchianADX, DonchianReversal, DonchianTrend
Other: SimpleSMA, BollingerBreakout, GoldenCross, NFPBreakout (skeleton), GammaScalping (skeleton), RapidFireTest

## Available Indicators (in codebase)

StochRSI, RSI, MACD, ADX, Bollinger Bands, Donchian Channels, ATR, SMA, CHOP
**Composable via:** `building_blocks.py`
**Not yet implemented:** OBV, VWAP, volume-based indicators

---

*Last updated: 2026-02-27 (Strategy reference dashboard built. GLD 15m full audit complete — Sharpe 2.54, trail_atr=1.5 lead to investigate)*
*Update this file when phase changes or major milestones reached*
