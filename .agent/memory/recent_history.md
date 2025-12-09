# Recent Git History

### 55cb4e3 - feat: Implement Adaptive Regime Switching and Stress Test (2025-12-08)
Detailed Findings:
- Implemented Adaptive StochRSIMeanReversion (ATR% > 0.12% -> Defensive ADX 20, else Aggressive ADX 30).
- Verified Adaptive Strategy on 10-year history.
  - 2021 (Bull): +11.1% (Improved from +6.8%)
  - 2018 (Bear): +11.6% (Profitable)
- Ran Stress Test on Optimized Strategy (Static 20) with /bin/zsh.02 Spread.
  - 2022: Collapsed to +6.3%
  - 2016: Collapsed to -11.0%
  - Conclusion: High friction costs due to high trade frequency (~3500/year) make the strategy unviable in its current form.
- Planned Pivot: Reduce trade frequency via higher timeframe or stricter filters.

### 7c00ad5 - feat: Remove Sector TICK and verify StochRSI on SPY (10-Year) (2025-12-08)
Detailed Findings:
- Removed inactive Sector TICK logic from hybrid_regime.py and runner.py.
- Verified StochRSIMeanReversion on SPY (5m) for 2016-2025.
- Results:
  - 2016: +4.98%
  - 2017: +11.14%
  - 2018: -3.31%
  - 2019: +2.69%
  - 2020: +14.23%
  - 2021: +14.28%
  - 2022: +24.74%
  - 2023: +11.02%
  - 2024: +5.30%
  - 2025: +12.86% (Jan-Nov)
- Conclusion: Strategy is robust and consistent (90% profitable years).
- Updated research_insights.md and walkthrough.md.

### d985c49 - docs: Update System Manual with GammaScalping and HybridRegime details (2025-12-08)

### 7db1871 - fix: GammaScalping bug and HybridRegime optimization (2025-12-08)
Detailed Findings:
- Fixed GammaScalping Argument Order and NoneType Price bug.
- Verified GammaScalping on SPY (2024): -0.32% Return (Flat).
- Optimized GammaScalping: Tested Volatility Threshold (1.5%) and RSI (7). Both failed to improve baseline.
- Restored GBPJPY HybridRegime history (2002-2024) from SQLite.
- Fixed HybridRegime CSV Data Source detection and TICK Filter bug.
- Optimized HybridRegime on GBPJPY: Tested ADX (30, 20) and RSI (9). All failed to beat baseline (+3.45%).
- Conclusion: Default parameters are robust. Simple is better.

### f07273c - chore: Sync recent_history.md with latest refactor (2025-12-08)

### 0dcbe4c - refactor: Implement Modular Rule-Based Agent Architecture (2025-12-08)
Detailed Changes:
- Reverted LangChain dependencies to avoid API key requirement.
- Created 'backend/agent/planner.py' with 'RuleBasedPlanner'.
- Refactored 'Researcher' to use the 'Goal -> Plan -> Execute -> Monitor' loop (Chapter 11 Pattern).
- Updated 'system_manual.md' to document the new Modular Architecture.
- Validated with 'DonchianTrend' on SPY (Success).
- Note: GammaScalping bug identified (pending fix).

### 8aaa126 - docs: Update plans for Agent Refactor (LangChain) (2025-12-08)
Detailed Findings:
- Updated task.md and implementation_plan.md (Artifacts) to reflect the new direction.
- Plan: Refactor Researcher and Critic to use LangChain and OpenAI.
- Goal: Align with 'Agentic Design Patterns' (Chapter 11) methodology.
- Dependencies: langchain_openai, openai, python-dotenv.
- This commit prepares the codebase for the major refactor.

### 7ef3b00 - fix: Refine Agent Optimization Logic (2025-12-07)
Detailed Findings:
- Updated MemorySystem.has_run_before to accept a 'symbol' argument.
- Updated Researcher to pass the current symbol to the memory check.
- This ensures the Agent runs a Baseline test for new symbols instead of prematurely optimizing based on other symbols' results.
- Verified fix with GBPUSD=X test.

### 779dca6 - feat: Implement GammaScalping and Verify Agent (2025-12-07)
Detailed Findings:
- Implemented GammaScalping strategy (Bollinger Band Width + RSI Mean Reversion).
- Refactored Indicators (RSI, Bollinger, StochRSI) to be class-based for consistency.
- Verified Agent capabilities with DonchianTrend on AAPL (Success).
- Identified data type bug in GammaScalping (pending fix).
- Updated Researcher to capture specific error messages.

### d985abf - docs: Update research insights with accurate 5-year data (2025-12-07)
Detailed Changes:
- Updated research_insights.md to reflect the full 5-year performance of the Aggressive StochRSI strategy (+88.5% Total Return).
- Clarified that while 2024 was weaker, the strategy significantly outperformed in 2022.
- Verified database records confirm no data overwriting.

### 5bf5130 - feat: Researcher Agent Optimization and CLI (2025-12-07)
Detailed Changes:
- Implemented Parameter Optimization (Level 2 Agent):
  - Updated Researcher Agent to detect previous runs and trigger optimization.
  - Implemented 'Safe' (RSI 21) and 'Aggressive' (RSI 7) optimization heuristics.
  - Verified agent successfully iterates through variations.

- Documentation:
  - Updated system_manual.md with Researcher Agent CLI commands.
  - Cleaned up research_insights.md with concise result summaries.

- Research Findings (SPY 5m):
  - Baseline (RSI 14): +32.95% Return, 6.88% DD.
  - Safe (RSI 21): +2.95% Return (Too slow).
  - Aggressive (RSI 7): +24.74% Return (Winner for 2024 Bull Market).

### cb9a63d - feat: Implement Researcher Agent and Memory System (2025-12-07)
Detailed Changes:
- Implemented Memory System:
  - Created .agent/memory/research_insights.md for semantic memory.
  - Created scripts/curate_memory.py to auto-extract insights from git history.
  - Updated git_save workflow to include curation step.

- Implemented Researcher Agent:
  - Created backend/agent/researcher.py (The Brain/Planner).
  - Created backend/agent/toolbox.py (The Hands/Runner Wrapper).
  - Created backend/agent/memory_system.py (The Hippocampus).

- Verification:
  - Verified curation script extracts insights correctly.
  - Verified Researcher Agent can plan, execute runner.py, and save results.
  - Validated 'Conflict Resolution' workflow for unlearning incorrect data.

### ff8247a - docs: Verify StochRSIQuant results and refine System Manual (2025-12-06)
Detailed Findings:
- Verified StochRSIQuant (Safe) performance for 2020-2025.
- Result: +71.0% Total Return, 5.94% Max Drawdown.
- Addressed discrepancy: Previous high returns (e.g., +97% in 2022) were due to the now-fixed leverage bug.
- Current results reflect realistic 1x leverage.
- Updated System Manual with 'Purpose & Scope' section to separate technical docs from research insights.

### 1989492 - feat: Implement StochRSISniper and document negative results (2025-12-06)
Detailed Findings:
- Implemented StochRSISniper (Combining StochRSIQuant + Sector TICK).
- Result: FAILED (-26.06% Return over 5 Years).
- Crucial Insight: Fundamental conflict between ADX < 30 (Range) and TICK > 1.5 (Momentum).
- When Breadth surges (High TICK) in a Quiet Market (Low ADX), it signals a Breakout.
- Fading this breakout leads to losses.
- Recommendation: Stick to StochRSIQuant (Safe) separately.

### 0aef7c6 - docs: Restore detailed findings for Sector TICK filter in history (2025-12-05)

### cbf68b7 - chore: Update git_save workflow to enforce detailed history (2025-12-05)
Detailed Explanation:
- Updated .agent/workflows/git_save.md to require multi-line commit messages.
- This ensures that research findings and analysis are automatically captured in recent_history.md by the update_memory.sh script.
- Previous commits often missed context because only the subject line was provided.

### 47553f1 - feat: Implement HybridRegime MockBroker and Sector TICK filters (2025-12-05)

### 98afc6d - WIP: HybridRegime strategy bug - only 1 trade despite fixes (2025-12-05)
PROBLEM:
- HybridRegime produces only 1 trade over 5 years when run through runner.py
- Works partially when tested directly (2 trades in 500 bars)

ROOT CAUSES IDENTIFIED BUT NOT FULLY RESOLVED:
1. bar_index desync: StochRSI's bar_index only increments when called
   by HybridRegime (not every bar), so it misaligns with actual data position
2. Row data mismatch: Backtester passes rows without indicator columns,
   sub-strategies need to use HybridRegime's enriched data
3. Warmup issue: on_bar checks 'if i < 50: return' but bar_index may be 0
   even when actual data position is > 50

FIXES ATTEMPTED:
- Added bar_counter to HybridRegime
- Pass enriched_row from self.data to sub-strategies
- Sync mean_reversion.bar_index = bar_counter - 1 before calls
- Fixed on_bar to use passed i instead of self.bar_index

WHAT WORKS:
- StochRSIMeanReversion standalone: 32.95% return, 5055 trades over 5yr
- Direct Alpaca test: 2 trades in 500 bars
- Paper trading: Fixed and working

NEEDS INVESTIGATION:
- Why runner.py flow produces different results than direct test
- Full bar_index synchronization between HybridRegime and sub-strategies

OTHER CHANGES IN THIS COMMIT:
- 1x leverage cap in PaperTrader (working correctly)
- Fixed paper_runner bar_index bug
- Cleaned unrealistic backtest results from database

### 008c359 - fix: Add 1x leverage cap to prevent unrealistic backtest results (2025-12-05)
Key changes:
- Fixed paper_runner bar_index bug that prevented live trading from executing
- Added 5m/15m/30m/4h timeframe mappings to alpaca_loader
- Added broker-level 1x leverage cap in PaperTrader to prevent overleveraging
- Added strategy-level leverage caps in stoch_rsi_mean_reversion and donchian_breakout
- Fixed frontend year display for multi-year backtests
- Re-ran backtests with realistic leverage (StochRSIQuant now shows ~58% 5yr vs 1600%)
- Cleaned up old unrealistic test results from database
- Updated system_manual.md with leverage cap documentation

Paper trading now properly executes trades when conditions are met.
HybridRegime returns now realistic after leverage fix.

### 6bfd781 - feat: revert VIX filter and fix multi-year test labels (2025-12-05)
