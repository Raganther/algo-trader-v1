# Recent Git History

### 1ac1676 - chore: Clean up memory files, update claude.md with IG integration (2026-02-14)
Deleted:
- .agent/memory/research_insights.md (RETIRED, contaminated with delay=1 results)
- .agent/memory/research.md (outdated, findings already in claude.md)

Updated claude.md:
- Added IG integration status line
- Updated 'Where We Left Off' to Feb 14 (IG Phase 1 complete)
- Added IG backtest command to Quick Commands
- Cleaned Read These Files section (3 memory + 3 workflow files)
- Updated Next Steps with IG milestones (3 checked, 2 remaining)
- Removed references to deleted files

### ea83500 - feat: Add --source ig to runner.py for IG data backtesting (2026-02-14)
Phase 1 of IG integration:
- Added 'ig' as third data source option (alongside csv/alpaca) in backtest, matrix, and trade commands
- Added IG data loading branches in run_backtest() and worker_task()
- Added GLD/SLV/IAU ETF ticker → IG Gold/Silver CFD epic mappings
- Updated Gold epic from DFB (CS.D.USCGC.TODAY.IP) to CFD (CS.D.CFDGOLD.CFDGC.IP) which works on demo

Verification: Ran 'backtest --source ig --symbol GLD --timeframe 15m' with Enhanced StochRSI params.
Result: -1.85% return, 148 trades, 60% win rate, 2.42% max DD over 6 weeks of IG demo Gold data.
Strategy executes correctly on IG data — no changes needed to strategy code.

### 4f9e37d - fix: Patch IGDataLoader date format and epic resolution (2026-02-14)
Fixes for IG Demo API interaction:
- Reverted date format to ISO 8601 (YYYY-MM-DDTHH:MM:SS) which prevents error.malformed.date
- Added datetime object passing to trading-ig for robustness
- Updated _process_df to prioritize 'bid'/'ask' mid-price calculation over 'last' (which was NaN for CFDs/Gold)
- Updated test script to use dynamically discovered epic from search
- Updated memory files (ideas.md, system_manual.md) to reflect working status

Verification:
- Successfully fetched 93 rows of Gold 15m data on Demo account

### ea719c6 - feat: Add IG spread betting data loader (2026-02-14)
New files:
- backend/engine/ig_loader.py: IGDataLoader class mirroring AlpacaDataLoader interface
  for fetching historical OHLCV data from IG REST API (gold, forex, indices)
- backend/engine/test_ig_loader.py: Quick test script for IG API connection

Changes:
- .env: Added IG_API_KEY, IG_USERNAME, IG_PASSWORD, IG_ACC_TYPE (demo)
- ideas.md: Added idea #18 documenting IG spread betting integration
  motivation (Kelly sizing on small accounts, tax-free in Ireland)
- system_manual.md: Added IG loader usage docs and API reference

Status: IGDataLoader built and tested. Authentication works on demo
but IG demo environment has no instruments/price data provisioned
(search returns 0, price history returns 500 error). Emailed IG support.
Code will work once IG resolves demo provisioning or live KYC approved.

Key technical details:
- Uses trading-ig Python library (pip install trading-ig)
- Epics: CS.D.USCGC.TODAY.IP (Gold), CS.D.EURUSD.MINI.IP (EUR/USD)
- Resolutions: 1Min, 5Min, 15Min, 1H, 4H, D
- REST API for history/orders, Streaming (Lightstreamer) for live prices

Co-Authored-By: Claude Opus 4.5 <noreply@anthropic.com>

### 0700679 - fix(broker): add set_entry_metadata to LiveBroker to prevent crash on trade (2026-02-13)

### 8e0dac0 - test: Add temporary aggressive-params test bot for piping verification (2026-02-13)
OB 60/OS 40, ADX 50, trail after 3 bars, min hold 3 bars.
Generates high trade frequency to verify trailing stop, min hold,
and skip_days mechanics are working in live paper trading.
Delete after verification.

Co-Authored-By: Claude Opus 4.6 <noreply@anthropic.com>

### d44665c - feat: Deploy enhanced GLD 15m strategy (Sharpe 2.42) (2026-02-13)
Skip Monday + trailing stop (2x ATR after 10 bars) + min hold 10 bars.
Replaces baseline params (Sharpe 1.57) with validated enhanced version.

Co-Authored-By: Claude Opus 4.6 <noreply@anthropic.com>

### 0558c89 - feat: Edge enhancements — trailing stop + min hold take Sharpe from 1.57 to 2.42 (2026-02-13)
Trade analysis revealed three key leaks in GLD 15m StochRSI:
- Stop losses were 100% losers (199 trades, -$1,219 total)
- Short-duration trades (1-5 bars, 72% of trades) were breakeven noise
- Monday trades had near-zero edge (128 trades, +$23 total)

Enhancements added to StochRSIMeanReversion (all optional, off by default):
- skip_days: filter entries on specified days (e.g. [0] for Monday)
- trailing_stop + trail_after_bars + trail_atr: move stop to lock in profits
- min_hold_bars: prevent signal exits before N bars held

Enriched trade records (entry_time, exit_reason, atr_at_entry, direction,
entry_hour, entry_dow) for diagnostic analysis. Added set_entry_metadata()
to PaperTrader, exit_reason passthrough in Strategy base class.

A/B sweep results (18 variants vs baseline):
- Skip Monday: Sharpe +0.12 (removes dead trades)
- Trail 2x ATR after 20 bars: Sharpe +0.41 (best single enhancement)
- Trail 2x/5bar + Hold 5: Sharpe 2.30 (+0.73, best combo)
- Skip Mon + Trail 2x/10bar + Hold 10: Sharpe 2.42 (+0.72)

Full validation — ALL 4 variants PASSED (holdout + walk-forward + multi-asset):
- Best: Skip Mon + Trail 2x/10bar + Hold 10 → Sharpe 2.42
- Holdout: +16.4% (train +18.6%, only 2.2% degradation)
- Walk-forward: 4/4 windows positive (100%)
- Multi-asset: GLD +38%, SLV +92%, IAU +31%

Key insight: Enhancements performed BETTER on unseen data. Trailing stop
is structural (not curve-fitting) — generalises across gold assets.

New files:
- backend/optimizer/trade_analysis.py — diagnostic backtest + trade slicing
- backend/optimizer/enhancement_sweep.py — A/B sweep framework

Co-Authored-By: Claude Opus 4.6 <noreply@anthropic.com>

### b065f82 - docs: Add edge enhancement plan and update session context (2026-02-13)
New file: .agent/workflows/edge_enhancement_plan.md
- 5-phase plan to improve validated edges (GLD 15m Sharpe 1.66)
- Phase 1: Enrich trade records (entry time, exit reason, ATR at entry)
- Phase 2: Diagnostic analysis (time-of-day, vol regime, exit patterns)
- Phase 3: Build targeted filters based on analysis findings
- Phase 4: A/B sweep (~50 variants vs baseline)
- Phase 5: Stack winners + validate through walk-forward

Key finding: backtester doesn't store entry timestamps or exit reasons,
needs enrichment before analysis can begin.

Updated ideas.md with 5 new ideas (#13-17): time-of-day filtering,
exit optimisation, limit order entries, vol-scaled sizing, news blackout.

Updated claude.md: GLD 15m bot deployed (replaced 1h), validation run
in progress (150 candidates), edge enhancement as next priority.

Raised validation candidate limit from 50 to 150 in run_overnight.py
to cover all unvalidated symbol/TF combos in a single run.

Co-Authored-By: Claude Opus 4.6 <noreply@anthropic.com>

### 29d2cfc - feat: Switch GLD bot from 1h to 15m (Sharpe 1.66, best validated edge) (2026-02-13)
GLD 15m params: RSI 7, Stoch 14, OB 80, OS 15, ADX 20, ATR stop 2x
Replaces GLD 1h (Sharpe 1.44) with higher-edge 15m strategy.

Co-Authored-By: Claude Opus 4.6 <noreply@anthropic.com>

### b63e070 - docs: Update with GLD 15m validation results and new strategy ideas (2026-02-13)
- GLD 15m StochRSI (Sharpe 1.66) validated as best edge — yearly returns 2-7%
- 5,300+ experiments, 90 validated passes across GLD/IAU/XLE
- Added ideas #7-12: position sizing, GDX amplification, multi-TF confirmation,
  cross-asset signals, spread betting/IG API for small accounts, forex discovery
- Updated next steps: explore IG API for €100 starting capital

Co-Authored-By: Claude Opus 4.6 <noreply@anthropic.com>

### a91cf41 - feat: Add scan/medium grid modes, symbol filtering, and ideas log (2026-02-12)
- Added --scan (11 combos), --medium (972 combos) grid tiers for faster iteration
- Added --symbols and --timeframes CLI filters to focus runs on promising targets
- Added --skip-sweep and --skip-validation flags for independent pass execution
- Fixed --quick not respecting explicit --max-hours override
- Pass 4 now loads winners from DB when skipping validation
- Enabled verbose output during sweeps for progress visibility
- Created .agent/memory/ideas.md for future strategy concepts (drawdown analysis,
  regime rotation, pairs trading, beta hedging, portfolio diversification, dashboard)
- Updated claude.md with ideas.md reference (DO NOT auto-read)

Co-Authored-By: Claude Opus 4.6 <noreply@anthropic.com>

### de52b94 - feat: Add overnight strategy discovery orchestrator (2026-02-11)
Single script (run_overnight.py) chains all discovery phases for
unattended overnight runs. 4 passes: broad sweep across priority-
ordered asset/TF combos → filter promising candidates from DB →
validate via holdout/walk-forward/multi-asset → expand winners to
adjacent timeframes and related assets.

Features:
- TimeBudget class with global time limit (default 10h)
- --quick mode for smoke testing (reduced grids, <1h)
- --skip-composable to skip slow composable sweeps
- skip_tested=True everywhere for crash recovery
- Per-sweep error handling (logs and continues)
- Priority targets: GLD other TFs, gold-correlated (SLV/IAU/GDX),
  XLE/XBI/TLT, broad market (SPY/QQQ/IWM/DIA)
- Final report with timing, new experiments, validation results,
  and top 10 all-time performers

No existing files modified — wires existing Phase 0-3 APIs together.

Co-Authored-By: Claude Opus 4.6 <noreply@anthropic.com>

### 8c4de0d - feat: Validate composable strategies — 3/10 passed, 7 rejected (2026-02-11)
Added validate_composable.py to bridge composable building blocks
with the Phase 2 validation pipeline. Maps stored block names back
to callables and runs full validation chain.

Results on top 10 composable candidates (GLD 1h):
- 7 REJECTED: high-Sharpe combos had too few trades (<30) or low
  profit factor — overfit noise caught by disqualification filters
- 3 PASSED full validation:
  1. RSI extreme + opposite zone: 263 trades, 75% WF, 100% multi-asset
  2. MACD cross + Donchian exit + SMA uptrend: +10.9% OOS, 75% WF
  3. RSI extreme + trailing ATR 3x: +4.9% OOS, no degradation, 252 trades

Key insight: validation correctly filtered overfit combos. The low-trade
high-Sharpe strategies (MACD+ATR, Bollinger+ATR) were statistical noise.
Original StochRSI strategy (Sharpe 1.44) remains the strongest edge.

Co-Authored-By: Claude Opus 4.6 <noreply@anthropic.com>

### a371af6 - feat: Phase 3 — Composable strategy framework + GLD forward test (2026-02-11)
Built composable strategy system with pluggable building blocks:
- indicator_calculator.py: Pre-computes all 9 indicators in one pass
- building_blocks.py: 7 entries, 7 exits, 6 filters, 3 sizers
- composable_strategy.py: Generic Strategy class wiring blocks together
- combination_generator.py: Cartesian product with compatibility rules
- run_composable.py: CLI sweep runner with experiment tracking

Ran 458 compatible combinations on GLD 1h (31.5 minutes):
- 156 positive (34%), best Sharpe 1.137 (MACD cross + ATR stop 3x)
- New combos found: Bollinger bounce + ATR stop (Sharpe 1.113),
  RSI extreme + opposite zone (263 trades, 2% DD)
- Top composable candidates need Phase 2 validation next

Deployed GLD 1h StochRSI forward test to cloud (PAPER mode):
- Stopped all old EXTREME bots (SPY/QQQ/IWM)
- Validated params: RSI 21, Stoch 7, OB 80, OS 15, ADX 25, ATR 3x
- scripts/run_gld.sh for PM2 management

Co-Authored-By: Claude Opus 4.6 <noreply@anthropic.com>

### ad05fb0 - feat: Phase 2 — Add validation framework + validate GLD edge (2026-02-11)
Built three-stage validation pipeline:
- disqualify.py: Hard filters (min trades, drawdown, profit factor, win rate)
- validation.py: Holdout (2020-23 train, 2024-25 test), walk-forward
  (rolling 2yr/1yr), multi-asset consistency (GLD→SLV,IAU)
- pipeline.py: Chains all checks, updates experiments DB with results

Validated top 20 candidates from Phase 1 sweeps:
- 18/18 passed (17 GLD + 1 XLE), 0 rejected
- 100% walk-forward pass rate across all candidates
- 100% multi-asset consistency (edge generalises to SLV and IAU)
- Best: GLD 1h StochRSI, Sharpe 1.44, 10.5% out-of-sample return

Updated claude.md with Phase 2 results and discovery engine findings.

Co-Authored-By: Claude Opus 4.6 <noreply@anthropic.com>

### 1c72e44 - fix: Suppress strategy debug prints during sweep backtests (2026-02-11)
Strategies print per-bar debug output (e.g. StochRSI prints K/D/ADX
every bar). With 8000+ bars × 324 combos = millions of print lines,
this was making sweeps extremely slow and output unmanageable.

Added suppress_stdout() context manager around bt.run() calls.
Sweep progress/summary still prints normally.

Co-Authored-By: Claude Opus 4.6 <noreply@anthropic.com>

### 0b0b53f - feat: Phase 1 — Add sweep engine for parameter optimisation (2026-02-11)
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
