# Recent Git History

### 600a5a4 - [System] Critical Cleanup & GZIP Support (2025-12-14)
Detailed Changes:
- [Fix] Solved Critical Disk Full Issue (Deleted 7GB of uncompressed data).
- [Feat] Added native GZIP support to DataLoader (.csv.gz).
- [Refactor] Organized project structure (moved scripts/logs/docs).
- [Feat] Verified QQQ (5m) Backtest frequency (1,275 trades/year).
- [Docs] Updated System Manual with new architecture.

### 6e453f8 - feat: implement market regime analysis (2025-12-13)
Implemented a robust Market Regime Analysis engine to classify market conditions (Bull, Bear, Range, Volatile).

Key Changes:

- Created 'backend/analysis/regime_quantifier.py': Vectorized logic using ADX, SMA50/200, and ATR.

- Created 'backend/analysis/visualize_regimes.py': Generates interactive Plotly charts with regime-colored backgrounds.

- Updated 'backend/analyze_results.py': Automatically runs regime analysis for SPY and BTC/USD and appends findings to 'research_insights.md'.

- Updated 'research_insights.md': Added new section showing SPY is Ranging 66% of the time and BTC 80% of the time.

### 4c4622f - feat: Implement RapidFireTest Iteration 1 & 2 (2025-12-13)
Detailed Findings:
- Iteration 1 (Shorting): 25.45% Return, 44k Trades. Promoted to Champion.
- Iteration 2 (Long-Only High Freq): 16.95% Return, 66k Trades. Created to bypass Alpaca Crypto shorting limits.
- Fix: Added retry logic to LiveBroker to handle Alpaca API 500 errors.
- Fix: Split 'Flip' logic in strategy to prevent insufficient balance errors.

### ab86fde - feat: Implement Strict Iteration Linking and Cumulative Forward Testing (2025-12-13)
Detailed Changes:
- Database: Added 'iteration_index' column to 'live_trade_log'.
- Runner: Added '--iteration' CLI argument to 'trade' command.
- LiveBroker: Updated to track and log 'iteration_index'.
- Analysis: Updated 'analyze_results.py' to aggregate live sessions by iteration and display cumulative results.
- Report: Added 'Reality' column to Iteration History table.

### 2cfa72b - docs: Update task list with Cloud Deployment objective (2025-12-13)
Detailed Changes:
- Added 'Cloud Deployment' section to task.md.
- Marked 'Forward Testing' verification as complete.

### ab4d36c - fix: Restore Reality Gap and Fix LiveBroker (2025-12-13)
Detailed Changes:
- Fixed TypeError in LiveBroker.place_order (qty vs quantity mismatch).
- Re-implemented 'Reality Gap' logic in analyze_results.py (restored missing feature).
- Updated LiveBroker to match PaperTrader interface.

### e4d9a39 - feat: Hybrid Strategy Development (Failed) (2025-12-12)
Detailed Changes:
- Implemented HybridRegimeV2 (StochRSI + Donchian + RegimeClassifier).
- Backtested on IWM (15m, 2020-2025).
- Result: -76% Return (Failed).
- Updated research_insights.md with results.
- Fixed bugs in RegimeClassifier and runner.py.

### 759473a - feat: Regime Switching Research and Analysis (2025-12-12)
Detailed Changes:
- Implemented RegimeClassifier (ADX, ATR, SMA) in backend/analysis/regime_classifier.py.
- Created scan_regimes.py to map historical market conditions.
- Analyzed regimes for SPY, QQQ, IWM (2020-2025).
- Confirmed correlation between IWM Volatile Range and StochRSI performance.
- Updated research_insights.md with Market Regime Analysis.
- Fixed AlpacaDataLoader import and usage in scan_regimes.py.

### 1f902d1 - feat: Cross-Asset Validation and Trend Strategy Research (2025-12-12)
Detailed Changes:
- Conducted Cross-Asset Validation for StochRSIMeanReversion on QQQ, IWM, DIA.
- Identified IWM (Russell 2000) as a top performer (96% Return).
- Conducted Trend Strategy Research on QQQ (DonchianBreakout, MACDBollinger).
- Fixed ImportError and syntax errors in MACDBollinger strategy.
- Added bollinger_bands function to backend/indicators/bollinger.py.
- Updated research_insights.md with new strategy profiles.

### c481d43 - feat: Refine Report with Full Configuration (2025-12-12)
Detailed Changes:
- Updated runner.py to include default parameters for StochRSIMeanReversion.
- Updated analyze_results.py to merge default parameters with run parameters for display.
- Updated research_insights.md to show the full configuration for the Champion Strategy (Iteration 6).
- Marked 'Refine Report' as complete in task.md.

### 15b354f - feat: Timeframe Analysis for StochRSIMeanReversion (2025-12-12)
Detailed Changes:
- Conducted Timeframe Analysis for StochRSIMeanReversion (SPY, 2020-2025).
- Identified 15m Timeframe (Iteration 6) as the new Champion with 54.36% Return.
- Updated analyze_results.py to correctly display Iteration History across different timeframes.
- Updated research_insights.md to reflect the new Champion and history.

### 126d26c - feat: Optimize StochRSIMeanReversion and Refine Report (2025-12-12)
Detailed Changes:
- Fixed bug in StochRSI indicator where 'rsi_period' was ignored (decoupled from stoch_period).
- Ran Iterations 2-5 for StochRSIMeanReversion on SPY (2020-2025).
- Identified Iteration 5 (RSI Period 7) as the new Champion (17.15% Return).
- Updated research_insights.md to display 'Timeframe' in Strategy Profile.
- Verified automatic promotion of winning iterations in the report.

### 5f44a53 - feat: Implement Strategy Profile and Iteration Tagging (2025-12-12)
Detailed Changes:
- Implemented 'Strategy Profile' view in research_insights.md with risk metrics (Time in DD, Stability).
- Added 'iteration_index' to test_runs table in research.db for better versioning.
- Updated runner.py to auto-increment iteration index for new runs.
- Refactored analyze_results.py to display 'Best Config' and 'Iteration History'.
- Ran Matrix Backtest for StochRSIMeanReversion (Iteration 1) on SPY (2020-2025).

### debdf95 - Refactor: System Cleanup and Redundancy Removal (2025-12-12)
Detailed Findings:
- Deleted 'backend/paper_runner.py' (Redundant legacy script).
- Deleted 'backend/run_live_strategy.py' (Redundant legacy script).
- Deleted 'backend/database.sqlite' (Redundant old DB).
- Deleted 'results.db' (Redundant artifact).
- Verified 'runner.py' handles all Backtest/Matrix/Trade functions.
- Verified 'backend/engine/backtester.py' supports CSV backtesting independently of Alpaca.
- Confirmed system is ready for 'research.db' reset.

### 96f9815 - Refactor: Finalized Research Insights hybrid layout and Fixed Analysis Logic (2025-12-12)
Detailed Findings:
- Implemented Hybrid Layout: Groups insights by Strategy/Symbol, shows Best Backtest (Theory) vs Reality Check (Forward Test).
- Fixed Win Rate Scaling: Corrected bug where win rates were displayed as 5000% (now 50.0%).
- Fixed Session Sorting: Live sessions are now sorted chronologically, ensuring the 'Latest' header matches the actual last session.
- Fixed Missing Metrics: Injected return/win_rate into insight parameters to prevent 0.00% display.
- Validated RapidFireTest: Confirmed correct 'Reality Gap' calculation (-16.0% gap for latest session).
- Prep: Ready for full database reset.

### 91110bc - fix: Improve Alpaca connection stability and refine analysis (2025-12-11)
- Implemented exponential backoff retry logic in LiveBroker.refresh() to handle RemoteDisconnected errors.
- Updated analyze_results.py to compare Win Rate instead of Return for Reality Check.
- Fixed database persistence issue for Insight parameters (win_rate).
- Updated System Manual.

### 3246ac9 - fix: Restore update_memory.sh and recent_history.md log format (2025-12-11)
- Recreated .agent/scripts/update_memory.sh to maintain detailed git log history.
- Restored recent_history.md with last 20 commits including bodies.

### 137b87a - feat: Implement Reality Gap metric and fix PnL calculation (2025-12-11)
- Implemented dynamic FIFO PnL calculation in analyze_results.py to fix 0.00% return issue.
- Added 'Reality Gap' (Delta) metric to research_insights.md to compare Theory vs Reality.
- Validated pipeline with RapidFireTest on BTC/USD (21-trade session recovered).
- Updated System Manual and Walkthrough.

### f32fec1 - feat: Implement Forward Test Analysis Pipeline (2025-12-11)
Detailed Findings:
- Implemented 'Theory vs Reality' feedback loop in analyze_results.py.
- Added 'get_live_trades' to DatabaseManager to harvest live logs.
- Updated 'research_insights.md' to include 'Baseline Established' category.
- Verified pipeline with RapidFireTest on BTC/USD (Baseline: 0.5% Return).
- Fixed path mismatch for research_insights.md.

### a091eb1 - [Docs]: Update project memory and insights (2025-12-10)
