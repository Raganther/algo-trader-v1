### 4269c04 - feat: Add Real/Raw cost tag to iteration history table (5 minutes ago)

Track spread and execution_delay per test run in the database,
and display a Costs column (Real/Raw) in the iteration history
so realistic results are easily distinguishable from raw backtests.

Co-Authored-By: Claude Opus 4.5 <noreply@anthropic.com>

---
### 5c2653d - docs: Update system manual with testing standards and workflow automation (35 minutes ago)

Detailed Changes:
- [Update] Core Architecture section: Added realistic cost modeling and automation components
- [Update] CLI Reference: Prioritized wrapper scripts over direct runner.py usage
  * Added realistic-test.sh documentation (auto-detects asset type, applies spread/delay)
  * Added test-and-sync.sh documentation (manual control with auto-sync)
  * Documented direct runner.py usage as 'low-level, not recommended'
- [New] Testing Standards & Realistic Costs section:
  * Documented 30% return difference (96% vs 65% on IWM)
  * Mandatory parameters: spread, delay, source
  * Asset-specific recommendations (stocks, crypto, forex)
  * Explained iteration system and version tracking
- [New] Workflow Automation section:
  * Complete testing workflow (automatic with wrappers)
  * Manual workflow steps (when using runner.py directly)
- [New] Quick Reference Card section:
  * Most common commands with examples
  * File locations reference
  * Important notes and warnings
- [Update] Recent System Updates: Added 2026-02-02 changes
- [Meta] Updated 'Last Updated' timestamp and system status

Key Improvements:
- System manual now reflects current best practices
- Clear guidance on using wrapper scripts vs direct runner
- Comprehensive testing standards documentation
- Quick reference for common operations
- Updated to 282 lines (from ~95 lines)

---
### ac5a713 - feat: Add realistic testing standards and wrapper script (39 minutes ago)

Detailed Changes:
- [Feat] Created scripts/realistic-test.sh wrapper that auto-applies realistic settings:
  * Detects asset type (Stock/Crypto/Forex)
  * Applies appropriate spread (0.0001 for stocks, 0.0002 for crypto/forex)
  * Forces execution delay of 1 bar (realistic order fill)
  * Uses Alpaca API for consistent data
- [Docs] Created docs/testing-standards.md comprehensive guide:
  * Explains why spread/delay matter (30% impact on returns!)
  * Provides recommended settings by asset class
  * Documents before/after comparison
  * Migration plan from old tests to realistic tests
- [Test] Validated realistic settings impact:
  * IWM: 96.29% (no costs) → 65.21% (realistic) = -31% difference
  * SPY: 54.36% (no costs) → 31.87% (realistic) = -22% difference
  * Spread/delay account for 5-7% per year on active strategies
- [Fix] Identified reproducibility issues:
  * Original tests likely used spread=0, delay=0 (unrealistic)
  * Data from Alpaca may have been revised/corrected over time
  * 2025 data was incomplete in Dec 2025 runs vs Feb 2026 reruns
- [System] Database now has 114 test runs (added iterations 11-13)

Key Findings:
- Strategies still profitable with realistic costs!
- IWM: 65% over 6 years (realistic) is excellent
- SPY: 32% over 6 years (realistic) is solid
- Testing standards now enforce robust, tradeable results

Recommendation: All future tests should use realistic-test.sh wrapper for accurate performance estimates.

---
### c5f0706 - feat: Add automatic test-and-sync wrapper + fix data_loader bug (4 hours ago)

Detailed Changes:
- [Fix] Resolved IndentationError in backend/engine/data_loader.py (duplicate else statement on line 26-27).
- [Feat] Created scripts/test-and-sync.sh wrapper that automates entire workflow:
  * Runs backtest via runner.py
  * Auto-updates research_insights.md via analyze_results.py --write
  * Auto-updates recent_history.md via update_memory.sh
  * Provides clear step-by-step output with success indicators
- [Test] Verified Alpaca API connectivity (SPY 1h data fetch successful).
- [Test] Ran StochRSIMeanReversion on SPY:
  * Iteration 9: 4.18% Return (Full 2024, 59 trades)
  * Iteration 10: 1.28% Return (Nov-Dec 2024, 6 trades)
- [Docs] Memory files updated: 100 total test runs now in database.

System Status:
- Database: research.db (100 runs total)
- Alpaca API: ✅ Working
- Memory Sync: ✅ Fully Automated

---
### e08a700 - [System] Critical Cleanup & GZIP Support (7 weeks ago)

Detailed Changes:
- [Fix] Solved Critical Disk Full Issue (Deleted 7GB of uncompressed data).
- [Feat] Added native GZIP support to DataLoader (.csv.gz).
- [Refactor] Organized project structure (moved scripts/logs/docs).
- [Feat] Verified QQQ (5m) Backtest frequency (1,275 trades/year).
- [Docs] Updated System Manual with new architecture.

---
### 6e453f8 - feat: implement market regime analysis (7 weeks ago)

Implemented a robust Market Regime Analysis engine to classify market conditions (Bull, Bear, Range, Volatile).

Key Changes:

- Created 'backend/analysis/regime_quantifier.py': Vectorized logic using ADX, SMA50/200, and ATR.

- Created 'backend/analysis/visualize_regimes.py': Generates interactive Plotly charts with regime-colored backgrounds.

- Updated 'backend/analyze_results.py': Automatically runs regime analysis for SPY and BTC/USD and appends findings to 'research_insights.md'.

- Updated 'research_insights.md': Added new section showing SPY is Ranging 66% of the time and BTC 80% of the time.

---
### 4c4622f - feat: Implement RapidFireTest Iteration 1 & 2 (7 weeks ago)

Detailed Findings:
- Iteration 1 (Shorting): 25.45% Return, 44k Trades. Promoted to Champion.
- Iteration 2 (Long-Only High Freq): 16.95% Return, 66k Trades. Created to bypass Alpaca Crypto shorting limits.
- Fix: Added retry logic to LiveBroker to handle Alpaca API 500 errors.
- Fix: Split 'Flip' logic in strategy to prevent insufficient balance errors.

---
### ab86fde - feat: Implement Strict Iteration Linking and Cumulative Forward Testing (7 weeks ago)

Detailed Changes:
- Database: Added 'iteration_index' column to 'live_trade_log'.
- Runner: Added '--iteration' CLI argument to 'trade' command.
- LiveBroker: Updated to track and log 'iteration_index'.
- Analysis: Updated 'analyze_results.py' to aggregate live sessions by iteration and display cumulative results.
- Report: Added 'Reality' column to Iteration History table.

---
### 2cfa72b - docs: Update task list with Cloud Deployment objective (7 weeks ago)

Detailed Changes:
- Added 'Cloud Deployment' section to task.md.
- Marked 'Forward Testing' verification as complete.

---
### ab4d36c - fix: Restore Reality Gap and Fix LiveBroker (7 weeks ago)

Detailed Changes:
- Fixed TypeError in LiveBroker.place_order (qty vs quantity mismatch).
- Re-implemented 'Reality Gap' logic in analyze_results.py (restored missing feature).
- Updated LiveBroker to match PaperTrader interface.

---
### e4d9a39 - feat: Hybrid Strategy Development (Failed) (7 weeks ago)

Detailed Changes:
- Implemented HybridRegimeV2 (StochRSI + Donchian + RegimeClassifier).
- Backtested on IWM (15m, 2020-2025).
- Result: -76% Return (Failed).
- Updated research_insights.md with results.
- Fixed bugs in RegimeClassifier and runner.py.

---
### 759473a - feat: Regime Switching Research and Analysis (7 weeks ago)

Detailed Changes:
- Implemented RegimeClassifier (ADX, ATR, SMA) in backend/analysis/regime_classifier.py.
- Created scan_regimes.py to map historical market conditions.
- Analyzed regimes for SPY, QQQ, IWM (2020-2025).
- Confirmed correlation between IWM Volatile Range and StochRSI performance.
- Updated research_insights.md with Market Regime Analysis.
- Fixed AlpacaDataLoader import and usage in scan_regimes.py.

---
### 1f902d1 - feat: Cross-Asset Validation and Trend Strategy Research (7 weeks ago)

Detailed Changes:
- Conducted Cross-Asset Validation for StochRSIMeanReversion on QQQ, IWM, DIA.
- Identified IWM (Russell 2000) as a top performer (96% Return).
- Conducted Trend Strategy Research on QQQ (DonchianBreakout, MACDBollinger).
- Fixed ImportError and syntax errors in MACDBollinger strategy.
- Added bollinger_bands function to backend/indicators/bollinger.py.
- Updated research_insights.md with new strategy profiles.

---
### c481d43 - feat: Refine Report with Full Configuration (7 weeks ago)

Detailed Changes:
- Updated runner.py to include default parameters for StochRSIMeanReversion.
- Updated analyze_results.py to merge default parameters with run parameters for display.
- Updated research_insights.md to show the full configuration for the Champion Strategy (Iteration 6).
- Marked 'Refine Report' as complete in task.md.

---
### 15b354f - feat: Timeframe Analysis for StochRSIMeanReversion (7 weeks ago)

Detailed Changes:
- Conducted Timeframe Analysis for StochRSIMeanReversion (SPY, 2020-2025).
- Identified 15m Timeframe (Iteration 6) as the new Champion with 54.36% Return.
- Updated analyze_results.py to correctly display Iteration History across different timeframes.
- Updated research_insights.md to reflect the new Champion and history.

---
### 126d26c - feat: Optimize StochRSIMeanReversion and Refine Report (7 weeks ago)

Detailed Changes:
- Fixed bug in StochRSI indicator where 'rsi_period' was ignored (decoupled from stoch_period).
- Ran Iterations 2-5 for StochRSIMeanReversion on SPY (2020-2025).
- Identified Iteration 5 (RSI Period 7) as the new Champion (17.15% Return).
- Updated research_insights.md to display 'Timeframe' in Strategy Profile.
- Verified automatic promotion of winning iterations in the report.

---
### 5f44a53 - feat: Implement Strategy Profile and Iteration Tagging (7 weeks ago)

Detailed Changes:
- Implemented 'Strategy Profile' view in research_insights.md with risk metrics (Time in DD, Stability).
- Added 'iteration_index' to test_runs table in research.db for better versioning.
- Updated runner.py to auto-increment iteration index for new runs.
- Refactored analyze_results.py to display 'Best Config' and 'Iteration History'.
- Ran Matrix Backtest for StochRSIMeanReversion (Iteration 1) on SPY (2020-2025).

---
### debdf95 - Refactor: System Cleanup and Redundancy Removal (7 weeks ago)

Detailed Findings:
- Deleted 'backend/paper_runner.py' (Redundant legacy script).
- Deleted 'backend/run_live_strategy.py' (Redundant legacy script).
- Deleted 'backend/database.sqlite' (Redundant old DB).
- Deleted 'results.db' (Redundant artifact).
- Verified 'runner.py' handles all Backtest/Matrix/Trade functions.
- Verified 'backend/engine/backtester.py' supports CSV backtesting independently of Alpaca.
- Confirmed system is ready for 'research.db' reset.

---
### 96f9815 - Refactor: Finalized Research Insights hybrid layout and Fixed Analysis Logic (7 weeks ago)

Detailed Findings:
- Implemented Hybrid Layout: Groups insights by Strategy/Symbol, shows Best Backtest (Theory) vs Reality Check (Forward Test).
- Fixed Win Rate Scaling: Corrected bug where win rates were displayed as 5000% (now 50.0%).
- Fixed Session Sorting: Live sessions are now sorted chronologically, ensuring the 'Latest' header matches the actual last session.
- Fixed Missing Metrics: Injected return/win_rate into insight parameters to prevent 0.00% display.
- Validated RapidFireTest: Confirmed correct 'Reality Gap' calculation (-16.0% gap for latest session).
- Prep: Ready for full database reset.

---
### 91110bc - fix: Improve Alpaca connection stability and refine analysis (8 weeks ago)

- Implemented exponential backoff retry logic in LiveBroker.refresh() to handle RemoteDisconnected errors.
- Updated analyze_results.py to compare Win Rate instead of Return for Reality Check.
- Fixed database persistence issue for Insight parameters (win_rate).
- Updated System Manual.

---