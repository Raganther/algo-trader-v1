# System Manual: AI Forex Research Platform

> [!IMPORTANT]
> **Purpose & Scope**
> This document is a **Technical Reference** for the system's architecture, frameworks, and usage.
> *   **INCLUDE:** How-to guides, CLI commands, dependency lists, directory structure, architectural patterns.
> *   **EXCLUDE:** Strategy performance results, backtest logs, research insights, or historical narrative.
> *   **Research Insights:** Documented in **Git Commit Messages** and aggregated in `recent_history.md`.

## 1. Core Architecture
**Goal**: A standardized, modular platform for algorithmic trading research and execution.

### Components
- **Backend**: Python (FastAPI).
    - **Engine**: Custom event-driven backtester (`backend/engine/`).
    - **Database**: SQLite (`backend/research.db`) for storing test results.
- **Frontend**: Next.js (React).
    - **Strategy Lab**: Dashboard for visualizing Matrix and Edge results.

### The Master Algorithm (`runner.py`)
The `runner.py` script is the **Universal Runner** that enforces consistency.
1.  **Unified Data Loading**: Always aligns data to the target timeframe using `DataLoader`.
2.  **Continuous Execution**: Runs a single backtest over the entire range (e.g., 2002-2024) to ensure validity.
3.  **Standardized Reporting**: Calculates Return, Drawdown, and Win Rate using identical formulas.
4.  **1x Leverage Cap**: Enforced by `PaperTrader` to prevent unrealistic results.

## 2. CLI Reference
All research is triggered via the `runner.py` CLI.

### Backtesting
```bash
# Single Backtest
python3 -m backend.runner backtest --strategy [Name] --symbol [Sym] --timeframe [TF] --start [Date] --end [Date]

# Matrix Research (Grid Search)
python3 -m backend.runner matrix --strategy [Name] --pairs [all/list] --years [range] --source [csv/alpaca]
```

### Live / Paper Trading
```bash
# Run Live Loop (Paper Default)
python3 -m backend.runner trade --strategy [Name] --symbol [Sym] --timeframe [TF] --paper
```

### AI Agent
```bash
# Autonomous Researcher
python3 -m backend.agent.researcher --goal "Find a high return strategy" --symbol [Sym] --timeframe [TF]
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

## 5. Recent System Updates
- [Feat]: Implemented Unified Memory System (2025-12-10)
- [Feat]: Verified Strategy Factory & Fixed Execution Pipeline (2025-12-09)
- [Feat]: Implemented Strategy Factory (Agent Upgrade) (2025-12-09)
- [Feat]: Verified Live Trading Pipeline (RapidFireTest) (2025-12-09)
