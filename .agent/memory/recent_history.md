### c380252 - docs: Update task list with Cloud Deployment objective (17 seconds ago)

Detailed Changes:
- Added 'Cloud Deployment' section to task.md.
- Marked 'Forward Testing' verification as complete.

---
### ab4d36c - fix: Restore Reality Gap and Fix LiveBroker (2 hours ago)

Detailed Changes:
- Fixed TypeError in LiveBroker.place_order (qty vs quantity mismatch).
- Re-implemented 'Reality Gap' logic in analyze_results.py (restored missing feature).
- Updated LiveBroker to match PaperTrader interface.

---
### e4d9a39 - feat: Hybrid Strategy Development (Failed) (10 hours ago)

Detailed Changes:
- Implemented HybridRegimeV2 (StochRSI + Donchian + RegimeClassifier).
- Backtested on IWM (15m, 2020-2025).
- Result: -76% Return (Failed).
- Updated research_insights.md with results.
- Fixed bugs in RegimeClassifier and runner.py.

---
### 759473a - feat: Regime Switching Research and Analysis (11 hours ago)

Detailed Changes:
- Implemented RegimeClassifier (ADX, ATR, SMA) in backend/analysis/regime_classifier.py.
- Created scan_regimes.py to map historical market conditions.
- Analyzed regimes for SPY, QQQ, IWM (2020-2025).
- Confirmed correlation between IWM Volatile Range and StochRSI performance.
- Updated research_insights.md with Market Regime Analysis.
- Fixed AlpacaDataLoader import and usage in scan_regimes.py.

---
### 1f902d1 - feat: Cross-Asset Validation and Trend Strategy Research (12 hours ago)

Detailed Changes:
- Conducted Cross-Asset Validation for StochRSIMeanReversion on QQQ, IWM, DIA.
- Identified IWM (Russell 2000) as a top performer (96% Return).
- Conducted Trend Strategy Research on QQQ (DonchianBreakout, MACDBollinger).
- Fixed ImportError and syntax errors in MACDBollinger strategy.
- Added bollinger_bands function to backend/indicators/bollinger.py.
- Updated research_insights.md with new strategy profiles.

---
### c481d43 - feat: Refine Report with Full Configuration (12 hours ago)

Detailed Changes:
- Updated runner.py to include default parameters for StochRSIMeanReversion.
- Updated analyze_results.py to merge default parameters with run parameters for display.
- Updated research_insights.md to show the full configuration for the Champion Strategy (Iteration 6).
- Marked 'Refine Report' as complete in task.md.

---
### 15b354f - feat: Timeframe Analysis for StochRSIMeanReversion (13 hours ago)

Detailed Changes:
- Conducted Timeframe Analysis for StochRSIMeanReversion (SPY, 2020-2025).
- Identified 15m Timeframe (Iteration 6) as the new Champion with 54.36% Return.
- Updated analyze_results.py to correctly display Iteration History across different timeframes.
- Updated research_insights.md to reflect the new Champion and history.

---
### 126d26c - feat: Optimize StochRSIMeanReversion and Refine Report (14 hours ago)

Detailed Changes:
- Fixed bug in StochRSI indicator where 'rsi_period' was ignored (decoupled from stoch_period).
- Ran Iterations 2-5 for StochRSIMeanReversion on SPY (2020-2025).
- Identified Iteration 5 (RSI Period 7) as the new Champion (17.15% Return).
- Updated research_insights.md to display 'Timeframe' in Strategy Profile.
- Verified automatic promotion of winning iterations in the report.

---
### 5f44a53 - feat: Implement Strategy Profile and Iteration Tagging (14 hours ago)

Detailed Changes:
- Implemented 'Strategy Profile' view in research_insights.md with risk metrics (Time in DD, Stability).
- Added 'iteration_index' to test_runs table in research.db for better versioning.
- Updated runner.py to auto-increment iteration index for new runs.
- Refactored analyze_results.py to display 'Best Config' and 'Iteration History'.
- Ran Matrix Backtest for StochRSIMeanReversion (Iteration 1) on SPY (2020-2025).

---
### debdf95 - Refactor: System Cleanup and Redundancy Removal (22 hours ago)

Detailed Findings:
- Deleted 'backend/paper_runner.py' (Redundant legacy script).
- Deleted 'backend/run_live_strategy.py' (Redundant legacy script).
- Deleted 'backend/database.sqlite' (Redundant old DB).
- Deleted 'results.db' (Redundant artifact).
- Verified 'runner.py' handles all Backtest/Matrix/Trade functions.
- Verified 'backend/engine/backtester.py' supports CSV backtesting independently of Alpaca.
- Confirmed system is ready for 'research.db' reset.

---
### 96f9815 - Refactor: Finalized Research Insights hybrid layout and Fixed Analysis Logic (24 hours ago)

Detailed Findings:
- Implemented Hybrid Layout: Groups insights by Strategy/Symbol, shows Best Backtest (Theory) vs Reality Check (Forward Test).
- Fixed Win Rate Scaling: Corrected bug where win rates were displayed as 5000% (now 50.0%).
- Fixed Session Sorting: Live sessions are now sorted chronologically, ensuring the 'Latest' header matches the actual last session.
- Fixed Missing Metrics: Injected return/win_rate into insight parameters to prevent 0.00% display.
- Validated RapidFireTest: Confirmed correct 'Reality Gap' calculation (-16.0% gap for latest session).
- Prep: Ready for full database reset.

---
### 91110bc - fix: Improve Alpaca connection stability and refine analysis (2 days ago)

- Implemented exponential backoff retry logic in LiveBroker.refresh() to handle RemoteDisconnected errors.
- Updated analyze_results.py to compare Win Rate instead of Return for Reality Check.
- Fixed database persistence issue for Insight parameters (win_rate).
- Updated System Manual.

---
### 3246ac9 - fix: Restore update_memory.sh and recent_history.md log format (2 days ago)

- Recreated .agent/scripts/update_memory.sh to maintain detailed git log history.
- Restored recent_history.md with last 20 commits including bodies.

---
### 137b87a - feat: Implement Reality Gap metric and fix PnL calculation (2 days ago)

- Implemented dynamic FIFO PnL calculation in analyze_results.py to fix 0.00% return issue.
- Added 'Reality Gap' (Delta) metric to research_insights.md to compare Theory vs Reality.
- Validated pipeline with RapidFireTest on BTC/USD (21-trade session recovered).
- Updated System Manual and Walkthrough.

---
### f32fec1 - feat: Implement Forward Test Analysis Pipeline (2 days ago)

Detailed Findings:
- Implemented 'Theory vs Reality' feedback loop in analyze_results.py.
- Added 'get_live_trades' to DatabaseManager to harvest live logs.
- Updated 'research_insights.md' to include 'Baseline Established' category.
- Verified pipeline with RapidFireTest on BTC/USD (Baseline: 0.5% Return).
- Fixed path mismatch for research_insights.md.

---
### a091eb1 - [Docs]: Update project memory and insights (3 days ago)


---
### ba2878e - [Fix]: Verified Live Trading & Logging Pipeline (3 days ago)

Detailed Findings:
- Fixed 'LiveBroker' to include 'spread' in trade logs.
- Updated 'RapidFireTest' to pass 'signal_price' for accurate slippage tracking.
- Verified end-to-end execution and logging with 'RapidFireTest' (Long-Only).
- Confirmed data alignment between Alpaca and internal DB.
- Added Pine Scripts for TradingView verification.

---
### a1721d9 - [Fix]: Enabled Live Trading Logger in CLI (3 days ago)

Detailed Findings:
- Updated 'backend/runner.py' to use 'LiveBroker' and 'DatabaseManager' for the 'trade' command.
- Fixed 'AttributeError' in 'LiveBroker' by adding 'get_position' method.
- Verified that 'RapidFireTest' runs via CLI and logs trades to 'research.db' with unique Session IDs.

---
### fbd37cb - [Feat]: Implemented Live Trading Logger (3 days ago)

Detailed Findings:
- Added 'live_trade_log' table to 'research.db' for persistent forward test verification.
- Updated 'LiveBroker' to poll Alpaca for exact fill prices and timestamps.
- Updated 'AlpacaTrader' to include 'get_order' method for retrieving execution details.
- Integrated 'DatabaseManager' into 'paper_runner.py' to auto-save all live trades.

---
### ed3db10 - [Refactor]: Optimized System Manual and Memory Logic (3 days ago)

Detailed Findings:
- Refactored 'system_manual.md' to 5 essential sections, removing 50% of bloat.
- Updated 'Critic' agent to cap 'Recent System Updates' to the last 5 items.
- Fixed duplicate section numbering and redundant process descriptions.
- Ensured memory remains concise and relevant for future sessions.

---