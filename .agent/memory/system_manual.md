# System Manual: AI Trading Research Platform

> [!IMPORTANT]
> **Purpose & Scope**
> This document is a **Technical Reference** for the system's architecture, frameworks, and usage.
> *   **INCLUDE:** How-to guides, CLI commands, dependency lists, directory structure, architectural patterns.
> *   **EXCLUDE:** Strategy performance results, backtest logs, research insights, or historical narrative.
> *   **Research Insights:** Documented in **Git Commit Messages** and aggregated in `recent_history.md`.

## 1. Core Architecture
**Goal**: A standardized, modular platform for algorithmic trading research and execution with realistic cost modeling.

### Components
- **Backend**: Python (FastAPI).
    - **Engine**: Custom event-driven backtester (`backend/engine/`).
    - **Database**: SQLite (`backend/research.db`) for storing test results and live trade logs.
    - **Analysis**: `analyze_results.py` correlates Backtests (Theory) with Live Logs (Reality) and calculates the **Reality Gap (Delta)**.
    - **Automation**: Wrapper scripts for streamlined testing and memory synchronization.
- **Frontend**: Next.js (React).
    - **Strategy Lab**: Dashboard for visualizing Matrix and Edge results.

### The Master Algorithm (`runner.py`)
The `runner.py` script is the **Universal Runner** that enforces consistency.
1.  **Unified Data Loading**: Always aligns data to the target timeframe using `DataLoader`.
2.  **Continuous Execution**: Runs a single backtest over the entire range (e.g., 2020-2025) to ensure validity.
3.  **Standardized Reporting**: Calculates Return, Drawdown, and Win Rate using identical formulas.
4.  **1x Leverage Cap**: Enforced by `PaperTrader` to prevent unrealistic results.
5.  **Realistic Cost Modeling**: Supports spread and execution delay for accurate performance estimates.

## 2. CLI Reference
All research is triggered via CLI commands. **IMPORTANT: Always use wrapper scripts for production testing.**

### Recommended: Automated Workflow Scripts

#### Realistic Testing (Recommended for All Tests)
```bash
# Automatic realistic settings (spread, delay, data source)
bash scripts/realistic-test.sh backtest \
  --strategy [Name] \
  --symbol [Sym] \
  --timeframe [TF] \
  --start [Date] \
  --end [Date]

# Matrix research with realistic settings
bash scripts/realistic-test.sh matrix \
  --strategy [Name] \
  --pairs [list] \
  --years [range] \
  --timeframes [list]
```

**What it does:**
- Auto-detects asset type (Stock/Crypto/Forex)
- Applies appropriate spread (0.0001 stocks, 0.0002 crypto/forex)
- Forces execution delay = 1 bar (realistic)
- Uses Alpaca API for consistency
- Auto-updates research_insights.md and recent_history.md

#### Manual Test-and-Sync (Advanced)
```bash
# Run test with full control, auto-sync memory
bash scripts/test-and-sync.sh backtest \
  --strategy [Name] \
  --symbol [Sym] \
  --timeframe [TF] \
  --start [Date] \
  --end [Date] \
  --spread [value] \
  --delay [bars] \
  --source [alpaca/csv]
```

### Direct Runner (Low-Level, Not Recommended)
```bash
# Single Backtest (manual - no auto-sync)
python3 -m backend.runner backtest \
  --strategy [Name] \
  --symbol [Sym] \
  --timeframe [TF] \
  --start [Date] \
  --end [Date] \
  --spread [value] \
  --delay [bars] \
  --source [alpaca/csv]

# Matrix Research (manual - no auto-sync)
python3 -m backend.runner matrix \
  --strategy [Name] \
  --pairs [all/list] \
  --years [range] \
  --source [csv/alpaca]

# Note: When using direct runner, must manually run:
# python3 -m backend.analyze_results --write
# bash .agent/scripts/update_memory.sh
```

### Live / Paper Trading
```bash
# Run Live Loop (Paper Default)
python3 -m backend.runner trade \
  --strategy [Name] \
  --symbol [Sym] \
  --timeframe [TF] \
  --paper
```

### AI Agent
```bash
# Autonomous Researcher
python3 -m backend.agent.researcher \
  --goal "Find a high return strategy" \
  --symbol [Sym] \
  --timeframe [TF]
```

## 3. Strategy Development
Strategies reside in `backend/strategies/` and inherit from `backend.engine.strategy.Strategy`.

### Base Class Methods
- `on_data(index, row)`: Called for every bar. Main logic goes here.
- `place_order(symbol, qty, side)`: Standard method for executing trades.
- `broker.get_position(symbol)`: Returns current position size.

### Strategy Factory (Agent Capability)
The Agent can autonomously create and register new strategies.
- **Generator**: `backend.agent.strategy_generator.StrategyGenerator` (Uses `RapidFireTest` template).
- **Registrar**: `backend.agent.registrar.StrategyRegistrar` (Injects into `runner.py`).
- **Workflow**: Create -> Register -> Verify (Backtest on BTC/USD).

### Hybrid Architecture
- **HybridRegimeStrategy**: Uses a **MockBroker** to filter sub-strategies (`StochRSI`, `Donchian`) based on regimes (VIX, Seasonality).
- **GammaScalping**: Uses Bollinger Band Width to detect low volatility.

## 4. Data & API
- **Sources**: Alpaca (Live/Paper), CSV (Backtest).
    - **Auto-Detection**: `ToolBox` automatically selects `source="csv"` for Forex pairs.
- **Advanced Data**: `runner.py` fetches `VIXY` (Volatility) and Sector ETFs if required.

### API Endpoints
- `GET /api/runs`: List all test runs.
- `GET /api/runs/{test_id}`: Get full details (equity curve).
- `GET /api/edges`: Get aggregated "Edge" stats.
- `GET /api/insights`: Get generated research insights.

## 5. Testing Standards & Realistic Costs

### Critical Discovery (2026-02-02)
Original tests significantly overstated returns by not including trading costs:
- **Without costs:** 96% return (IWM, 6 years)
- **With costs:** 65% return (IWM, 6 years)
- **Impact:** 30% of profits lost to spread/delay!

### Mandatory Parameters for All Tests
```bash
--spread [value]   # Trading cost (bid-ask spread)
--delay [bars]     # Execution delay (0=instant, 1=next bar)
--source [name]    # Data source (alpaca recommended)
```

**Recommended Values:**
- **Stocks (SPY, QQQ, IWM):** `--spread 0.0001 --delay 1 --source alpaca`
- **Crypto (BTC/USD, ETH/USD):** `--spread 0.0002 --delay 1 --source alpaca`
- **Forex (GBPJPY, EURUSD):** `--spread 0.0002 --delay 1 --source csv`

**Why These Matter:**
- Spread: Cost difference between buy (ask) and sell (bid) prices
- Delay: Real orders take time to execute (1 bar = realistic)
- Over 1,000+ trades, these costs compound to 5-7% per year!

### Iteration System
Tests are versioned (v1, v2, v3...) per strategy/symbol combination:
- Reruns create NEW iterations (doesn't overwrite old results)
- Database preserves all iterations for comparison
- Useful for tracking data changes and parameter optimization

**Example:**
```
StochRSIMeanReversion_IWM_15m_2020_v1 → 21.05% (no costs)
StochRSIMeanReversion_IWM_15m_2020_v2 → 13.12% (with costs)
```

Both results saved! Compare to understand cost impact.

## 6. Workflow Automation

### Complete Testing Workflow (Automatic)
When using `realistic-test.sh` or `test-and-sync.sh`:

1. **Backtest runs** → Data fetched, strategy executed
2. **Results saved** → Database updated (research.db)
3. **Insights generated** → research_insights.md auto-updated
4. **Git history synced** → recent_history.md refreshed
5. **Ready to commit** → All memory files synchronized

No manual steps required!

### Manual Workflow (When using runner.py directly)
```bash
# Step 1: Run test
python3 -m backend.runner backtest [args...]

# Step 2: Update insights
python3 -m backend.analyze_results --write

# Step 3: Update git history
bash .agent/scripts/update_memory.sh

# Step 4: Commit
git add .
git commit -m "test: [description]"
```

## 7. Quick Reference Card

### Most Common Commands

**Run Realistic Test (Recommended):**
```bash
bash scripts/realistic-test.sh backtest \
  --strategy StochRSIMeanReversion \
  --symbol SPY \
  --timeframe 15m \
  --start 2020-01-01 \
  --end 2025-12-31
```

**Matrix Research (Multiple Symbols):**
```bash
bash scripts/realistic-test.sh matrix \
  --strategy StochRSIMeanReversion \
  --pairs SPY,QQQ,IWM \
  --years 2020-2025 \
  --timeframes 15m
```

**Check Test Results:**
```bash
# View latest insights
cat .agent/memory/research_insights.md

# Check database
sqlite3 backend/research.db "SELECT strategy, symbol, AVG(return_pct) FROM test_runs GROUP BY strategy, symbol;"
```

**Update Memory After Manual Tests:**
```bash
python3 -m backend.analyze_results --write
bash .agent/scripts/update_memory.sh
```

### File Locations
- **Test Results:** `backend/research.db` (SQLite database)
- **Research Insights:** `.agent/memory/research_insights.md` (auto-generated)
- **Git History:** `.agent/memory/recent_history.md` (auto-generated)
- **Testing Standards:** `docs/testing-standards.md`
- **Strategies:** `backend/strategies/*.py`
- **Wrapper Scripts:** `scripts/*.sh`

### Important Notes
- ✅ Always use realistic settings (spread/delay) for production tests
- ✅ Wrapper scripts auto-sync all memory files
- ✅ Database keeps all iterations (never overwrites)
- ⚠️ Original tests (v1-v10) likely overstated by ~30% (no costs)
- ⚠️ API keys exposed in .env (CRITICAL: needs fixing)

## 8. Recent System Updates
- [Feat]: Realistic Testing Standards & Wrapper Script (2026-02-02)
- [Feat]: Automated Test-and-Sync Workflow (2026-02-02)
- [Fix]: Resolved data_loader.py IndentationError (2026-02-02)
- [Validation]: Confirmed 30% cost impact on returns (2026-02-02)
- [Fix]: Implemented Auto-Retry Logic for Alpaca Connection (2025-12-11)
- [Feat]: Implemented Forward Test Analysis (Theory vs Reality) (2025-12-11)
- [Feat]: Implemented Live Trading Logger (2025-12-10)
- [Feat]: Implemented Unified Memory System (2025-12-10)
- [Feat]: Verified Strategy Factory & Fixed Execution Pipeline (2025-12-09)

---

**Last Updated:** 2026-02-02
**System Status:** ✅ Operational | 114 Test Runs | Alpaca API Connected
