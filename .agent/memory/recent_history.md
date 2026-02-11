# Recent Git History

### 26989ff - feat: Phase 1 — Add sweep engine for parameter optimisation (2026-02-11)
New files:

backend/engine/data_utils.py — clean data loading with resampling
  - Extracts duplicated resampling logic from runner.py
  - Handles 5m/15m (fetch 1m, resample), 4h (fetch 1h, resample), direct TFs
  - Single function: load_backtest_data(symbol, timeframe, start, end)

backend/optimizer/scoring.py — Sharpe ratio + composite scoring
  - calc_sharpe() from equity curve with auto-detected periods/year
  - score_result() returns Sharpe as primary score, -999 for <10 trades

backend/optimizer/sweep.py — SweepEngine class
  - Fetches data once per symbol/timeframe, runs Backtester N times
  - Cartesian product of param grid, scores each result
  - Saves all results to experiments table via ExperimentTracker
  - run_multi_sweep() for batch across strategies/symbols/timeframes
  - Skip-tested dedup to avoid repeat work across runs
  - Hardcoded spread=0.0003, delay=0 (validated against live)

backend/optimizer/run_sweep.py — CLI entry point
  - python -m backend.optimizer.run_sweep --quick (smoke test)
  - python -m backend.optimizer.run_sweep --strategy X --symbol Y --timeframe Z
  - Default param grids for StochRSI, Donchian, MACDBollinger
  - Summary output with top 10 ranked results

Tested: 4 real backtests on SPY 1h via Alpaca, all saved to DB correctly.

Co-Authored-By: Claude Opus 4.6 <noreply@anthropic.com>

### 62d75f1 - feat: Phase 0 — Add experiments table + ExperimentTracker class (2026-02-11)
New experiments table in research.db (clean, separate from test_runs):
  - All rows guaranteed spread=0.0003, delay=0
  - Adds fields missing from test_runs: sharpe, score, annualised_return,
    trades_per_year, profit_factor, validation_status, strategy_source,
    parent_experiment_id (for LLM iteration lineage)

New ExperimentTracker class (backend/optimizer/experiment_tracker.py):
  - save() — write backtest results with auto-calculated annualised return
  - get_top_candidates() — rank by score, filter by min trades + validation
  - get_failures_for_strategy() — what didn't work (for LLM learning)
  - get_untested_combinations() — gap finder for search space coverage
  - has_been_tested() — dedup by params hash to avoid repeat work
  - get_summary_for_llm() — concise text summary replacing research_insights.md
  - update_validation() — update validation status after Phase 2 checks
  - count() — total experiments

All methods tested end-to-end, test data cleaned up.

Co-Authored-By: Claude Opus 4.6 <noreply@anthropic.com>

### 4fe11c6 - docs: Add extensibility & iterative build approach to discovery engine plan (2026-02-11)
- New section: Extensibility (adding indicators, economic data, event-driven trading)
  - Indicator library designed to grow (vectorized + stateful patterns)
  - 5 indicators to add before first sweep (OBV, VWAP, EMA, CCI, Williams %R)
  - Economic calendar slots in at any phase via existing on_event() wiring
  - Modularity/debugging properties per phase

- New section: Build Approach — assess each phase before proceeding
  - Phase-by-phase decision points with concrete criteria
  - No blind build of all 4 phases; results inform what to build next
  - New indicators/data added when results reveal the need

Co-Authored-By: Claude Opus 4.6 <noreply@anthropic.com>

### 5976bd2 - docs: Add Strategy Discovery Engine build plan + update session primer (2026-02-11)
New file: .agent/workflows/strategy_discovery_engine.md
- Full 4-phase build plan for automated strategy search system
- Phase 0: experiments table + ExperimentTracker class
- Phase 1: Sweep engine (parameter optimization across strategies/assets)
- Phase 2: Validation framework (walk-forward, holdout, multi-asset)
- Phase 3: Composable strategies (auto-generate indicator combinations)
- Phase 4: LLM agent loop (analyse results, generate code, iterate)
- Data strategy: separate experiments table (clean, not contaminated)
- ExperimentTracker replaces research_insights.md and analyze_results.py
- Detailed code references for all 9 indicators, strategy patterns, database
- Implementation order, file map, risk analysis

Updated: .claude/claude.md
- Phase 10: Strategy Discovery Engine (design complete, implementation next)
- Updated file references (strategy_discovery_engine.md = START HERE)
- Marked research_insights.md as RETIRED (contaminated with delay=1 results)
- New next steps: Phase 0-4 implementation tasks

Co-Authored-By: Claude Opus 4.6 <noreply@anthropic.com>

### d5d3896 - docs: Update memory files with live validation findings and strategy direction (2026-02-10)
Phase 9 documented: dual-bot conflict resolved (donchian-iwm-5m deleted),
live trading (100+ trades) confirms corrected backtest findings — indicator-only
strategies on liquid US ETFs produce ~zero returns after realistic costs.

CLAUDE.md: Updated to Phase 9, 3 bots, added strategy inventory,
backtest settings reference, decision point context for next session.

forward_testing_plan.md: Added Phase 9 section, updated bot status table,
marked Phase 4 complete, added Phase 5 pending tasks, updated expected outcome.

research.md: Added live validation section with sample trade P&L,
updated slippage data, documented delay=1 bug mechanism, added untested
indicator directions (less efficient assets, volume indicators, multi-TF,
crypto) with probability assessments alongside existing alternative tiers.

Co-Authored-By: Claude Opus 4.6 <noreply@anthropic.com>

### b60946a - docs: Add research on event-driven and macro strategy avenues (2026-02-06)
Comprehensive analysis of alternatives to indicator-only strategies:
- Economic announcement trading (NFP/CPI/FOMC) as top opportunity
- VIX term structure regime filter
- Sector rotation momentum, PEAD, credit spread overlay
- Ranked tiers, data sources, and phased build order

Co-Authored-By: Claude Opus 4.6 <noreply@anthropic.com>

### 3c34b5d - feat: Add SwingBreakout strategy + fix percentage-based spread model (2026-02-06)
Fixed PaperTrader spread from absolute price units to percentage-based:
  fill_price = base_price * (1 + spread/2) instead of base_price + spread/2
  --spread 0.0003 now means 0.03% of price ($0.075/side for SPY at $500)

New SwingBreakout strategy (daily timeframe, triple confirmation):
  - 55-day Donchian breakout + Bollinger width expanding + ADX rising
  - ATR trailing stop (3x) + Donchian 20-day exit
  - 2% equity risk, whole shares, 1x leverage cap

Backtest results (2020-2025, --spread 0.0003 --delay 0):
  SPY: -0.01%, QQQ: +1.39%, IWM: -2.24% (~3 trades/year)
  Cost impact negligible (0.19% over 5 years) as designed
  Strategy generates no meaningful alpha on liquid US ETFs

Preliminary finding: public indicators alone cannot generate alpha
on highly liquid ETFs after realistic transaction costs.

Co-Authored-By: Claude Opus 4.6 <noreply@anthropic.com>

### 0e05453 - fix: Make Donchian position key compatible with both live and backtest (2026-02-06)
Re-ran top 3 backtests with corrected cost model (--spread 0.0003 --delay 0):
- QQQ 5m StochRSI: +0.99% (was +44.9% with delay=1)
- IWM 15m StochRSI: -1.13% (was +19.8% with delay=1)
- QQQ 4h Donchian: -6.38% (was +22.6% with delay=1)

The delay=1 parameter was flattering mean reversion entries by giving
an extra bar of price continuation. With delay=0 (matching live fills),
all strategies are near breakeven or negative over 2020-2025.

Also fixed Donchian position dict key to use .get() fallback so it
works with both live_broker (key='price') and paper_trader (key='avg_price').

Co-Authored-By: Claude Opus 4.6 <noreply@anthropic.com>

### 7cb65b4 - docs: Correct slippage analysis and backtest cost model findings (2026-02-06)
Updated slippage data with 70+ trades (up from 20):
- SPY: 0.024% (39 trades), QQQ: 0.049% (7), IWM: 0.029% (24)
- Fill delay: avg 1.15 seconds (negligible for 5m/15m)

CRITICAL CORRECTION: Previous claim that backtest 0.01% spread was
"conservative" was wrong. The --delay 1 parameter actually HELPS
mean reversion entries (price continues in signal direction for 1
more bar). 3 of 4 "realistic" backtests outperform no-cost versions.

In live trading we fill in ~1 second (same bar), missing this benefit.
Corrected backtest params for after data collection: --spread 0.0003
--delay 0 to match actual live execution characteristics.

Updated next steps in claude.md with revised roadmap.

Co-Authored-By: Claude Opus 4.6 <noreply@anthropic.com>

### 16a8027 - fix: Fix KeyError in Donchian stop loss - use correct position dict key (2026-02-06)
Live broker stores entry price as position['price'] but Donchian strategy
was using position['avg_price'] (backtest format). Caused KeyError crash
on every bar when holding a position (204 PM2 restarts).

Fixed both long (line 150) and short (line 163) stop loss lookups.

Co-Authored-By: Claude Opus 4.6 <noreply@anthropic.com>

### 7ba8fad - feat: Implement memory system restructure for reliable context (2026-02-06)
Created new files:
- .claude/claude.md - Session primer (auto-read by Claude at startup)
- .claude/hooks/load-context.sh - SessionStart hook shows recent commits
- .claude/settings.json - Hook configuration

Updated files:
- system_manual.md - Added forward testing/live trading section
  - Cloud server management (PM2, deploy flow)
  - Platform constraints (crypto shorts, whole shares, etc.)
  - Critical bug fixes reference
  - Slippage analysis results
- git_save.md - Simplified workflow, removed non-existent curate_memory.py

Memory architecture:
- claude.md = Quick status + signposts (150 lines)
- system_manual.md = Permanent technical reference
- forward_testing_plan.md = Journey history (unchanged)
- recent_history.md = Auto-generated from commits

Benefits:
- Zero manual context loading on new sessions
- Hook auto-shows last 5 commits + file pointers
- Claude reads claude.md automatically
- Clear separation: status vs reference vs history

Co-Authored-By: Claude Opus 4.5 <noreply@anthropic.com>

### 1317cd7 - docs: Document Phase 8 multi-asset expansion and slippage analysis (2026-02-05)
Phase 8 additions:
- Fixed crypto short selling crash (Alpaca doesn't support crypto shorts)
- Added API error handling in live_broker.py (prevents loop crashes)
- Added IWM 5m bot (StochRSIMeanReversion)
- Added DonchianBreakout IWM 5m bot (trend-following comparison)

Slippage Analysis (20 trades):
- SPY: 0.032% avg slippage (13 trades)
- QQQ: 0.060% avg slippage (4 trades)
- IWM: 0.030% avg slippage (3 trades)

Key finding: Live slippage is within expected range, backtest
assumptions validated. IWM has tightest execution.

Current status: 4 bots active (SPY, QQQ, IWM StochRSI + IWM Donchian)

Co-Authored-By: Claude Opus 4.5 <noreply@anthropic.com>

### d5665f0 - fix: Disable short entries for crypto symbols (2026-02-05)
Alpaca doesn't support crypto short selling. Every short attempt was
crashing the live loop (40 crashes, 57 PM2 restarts). The bot appeared
to work because PM2 kept restarting it and position sync recovered.

Now skips the overbought zone flag for crypto symbols (containing '/')
so short entries are never attempted. Stocks retain full long/short.

Co-Authored-By: Claude Opus 4.5 <noreply@anthropic.com>

### 2df6fd6 - fix: Catch API errors in buy/sell to prevent live loop crashes (2026-02-05)
Alpaca APIError (insufficient balance, rejected orders) was unhandled
in LiveBroker.buy() and sell(). Exception propagated up and crashed
the entire live trading loop, causing PM2 restarts.

Now catches exceptions, logs the rejection, and returns None.
Strategy already guards with `if result is not None:` so position
state stays correct.

Co-Authored-By: Claude Opus 4.5 <noreply@anthropic.com>

### bd7738a - docs: Document Phase 7 bug fixes and multi-asset validation results (2026-02-05)
## Phase 7: Position Tracking Bug Fixes (2026-02-05)

7 critical bugs found and fixed during live BTC/SPY/QQQ testing:

1. Position state lost on restart (strategy.position=0 on init)
   - Fix: Sync with Alpaca after strategy init in runner.py
2. Zone flags re-trigger while holding (duplicate entries)
   - Fix: Move zone logic inside position==0 check
3. Symbol format mismatch BTCUSD vs BTC/USD (exits fail silently)
   - Fix: Store both formats in broker position cache
4. Exit qty lookup uses wrong method (returns None)
   - Fix: Use get_position() which handles both formats
5. Fractional stock orders need DAY TIF
   - Fix: Auto-detect and switch TimeInForce
6. No fractional short selling for stocks + residual positions
   - Fix: Round ALL stock orders to whole shares
7. Exit state not guarded on order failure (ghost flat state)
   - Fix: Only reset position if order returns non-None

## Validation Results
- BTC: 3+ clean round-trips (entry + exit filling correctly)
- SPY: 2 clean round-trips (35 whole shares, no residuals)
- QQQ: Running, waiting for 15m signals
- All trades verified against Alpaca order history

## Files Modified
- backend/runner.py (position sync on startup)
- backend/strategies/stoch_rsi_mean_reversion.py (zone guard, exit guard, get_position)
- backend/engine/live_broker.py (symbol normalization)
- backend/engine/alpaca_trader.py (whole shares, DAY TIF)

Co-Authored-By: Claude Opus 4.5 <noreply@anthropic.com>

### 3832ae6 - fix: Round all stock orders to whole shares + guard exit state (2026-02-05)
- Round both buy and sell for stocks (not just sells) to prevent
  fractional residuals (buy 35.6 → sell 35 → 0.6 orphan)
- Only reset position state if exit order actually succeeds
- Prevents ghost state where strategy thinks it exited but didn't

Co-Authored-By: Claude Opus 4.5 <noreply@anthropic.com>

### d8e4439 - fix: Round stock sell orders to whole shares (no fractional shorts) (2026-02-05)
Alpaca does not allow fractional short selling for stocks.
Round sell qty to int for non-crypto symbols.

Co-Authored-By: Claude Opus 4.5 <noreply@anthropic.com>

### 4a8ace5 - test: Default skip_adx_filter to True for forward testing validation (2026-02-05)
Avoids need for --parameters JSON via PM2 (which causes quoting
issues with wrapper scripts). Strategy defaults already have
EXTREME thresholds (50/50). Will revert after validation.

Co-Authored-By: Claude Opus 4.5 <noreply@anthropic.com>

### 7633a95 - fix: Use DAY time-in-force for fractional stock orders (2026-02-05)
Alpaca requires fractional stock orders to use DAY (not GTC).
Auto-detect fractional qty for non-crypto symbols and switch TIF.

Co-Authored-By: Claude Opus 4.5 <noreply@anthropic.com>

### 3af74ad - fix: Fix position tracking bugs for live crypto trading (2026-02-05)
- Sync position state with Alpaca on startup (prevents duplicate entries after restart)
- Normalize symbol keys in broker cache (BTCUSD + BTC/USD) so lookups don't silently fail
- Move zone flag logic inside position==0 check (prevents re-triggering while holding)
- Use get_position() for exit sizing (handles symbol format mismatch, returns actual qty)

Co-Authored-By: Claude Opus 4.5 <noreply@anthropic.com>
