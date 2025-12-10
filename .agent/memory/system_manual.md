# System Manual: AI Forex Research Platform

> [!IMPORTANT]
> **Purpose & Scope**
> This document is a **Technical Reference** for the system's architecture, frameworks, and usage.
> *   **INCLUDE:** How-to guides, CLI commands, dependency lists, directory structure, architectural patterns (e.g., "How the Hybrid Broker works").
> *   **EXCLUDE:** Strategy performance results, backtest logs, research insights, "lessons learned", or historical narrative.
> *   **Research Insights:** All findings and results must be documented in **Git Commit Messages**, which are automatically aggregated into `recent_history.md`.

## 1. Infrastructure Overview
**Goal**: A standardized, modular platform for algorithmic trading research and execution.

### Core Components
- **Backend**: Python (FastAPI).
    - **Engine**: Custom event-driven backtester (`backend/engine/`).
    - **Database**: SQLite (`backend/research.db`) for storing all test results and series data.
- **Frontend**: Next.js (React).
    - **Strategy Lab**: Dashboard for visualizing Matrix and Edge results.
    - **Detail View**: Granular analysis of individual test runs.

## 2. The Master Algorithm (`runner.py`)
The `runner.py` script is the **Universal Runner** that enforces consistency across all research. It ensures that every strategy, regardless of logic, is executed under identical conditions.

### Key Mechanisms
1.  **Unified Data Loading**:
    - Uses `DataLoader` to fetch and resample data.
    - **Rule**: Always aligns data to the target timeframe (e.g., resampling 1m to 4h if 4h is missing) to ensure data integrity.
2.  **Parameter Injection**:
    - Dynamically configures strategy instances based on the `strategy_name`.
    - Allows for strategy-specific parameters (e.g., `HybridRegime` vs `MACDBollinger`) while keeping the execution loop identical.
3.  **Continuous Execution**:
    - Runs a single, continuous backtest over the entire requested range (e.g., 2002-2024).
    - **Purpose**: Guarantees trade validity across year boundaries (avoids "New Year's Eve" gaps where trades might be artificially closed).
4.  **Standardized Reporting**:
    - Calculates Return, Drawdown, and Win Rate using the exact same mathematical formulas for every test.
    - Splits the continuous run into yearly segments for granular storage in `research.db`.
5.  **1x Leverage Cap (Broker Level)**:
    - The `PaperTrader` enforces a maximum position size equal to account equity.
    - Prevents unrealistic backtest results from excessive leverage.
    - Applies to ALL strategies automatically.

## 3. CLI Commands & Workflows
All research is triggered via the `runner.py` CLI.

### Single Backtest
- **Paper Trading**: `python3 -m backend.paper_runner` (Runs live paper trading loop)
- **Backtest**: `python3 -m backend.runner backtest --strategy [Name] --symbol [Sym] --timeframe [TF] --tag [Tag] --start [Date] --end [Date]`
    - *Strategies*: `StochRSIMeanReversion`, `StochRSIQuant`, `DonchianTrend`, `HybridRegime`, `GammaScalping`
    - *Tag*: Optional label for the run (e.g., `Safe`, `Aggressive`)

### Matrix Research
Run a grid of tests across multiple pairs and years.
```bash
python3 -m backend.runner matrix --strategy [Name] --pairs [all/list] --years [range] --source [csv/alpaca]
```

### Analysis
Process raw results to generate insights (saved to `research.db`).
```bash
python3 backend/analyze_results.py
```

### Paper Trading (Live)
Run the live paper trading loop for a specific strategy (currently hardcoded to SPY 5m StochRSI).
```bash
python3 -m backend.paper_runner
```

### Researcher Agent (The Planner)
Run the autonomous agent to find or optimize strategies.
```bash
python3 -m backend.agent.researcher --goal "Find a high return strategy" --symbol [Sym] --timeframe [TF]
```

#### Modular Architecture
The Agent follows the **Chapter 11 Design Pattern** (`Goal -> Plan -> Execute -> Monitor`):
1.  **Planner** (`backend/agent/planner.py`):
    *   **RuleBasedPlanner**: (Default) Uses logic/regex to map Goals to Strategies. Deterministic and fast.
    *   **LLMPlanner**: (Future) Can be plugged in to use OpenAI/LangChain for complex reasoning.
2.  **Researcher** (`backend/agent/researcher.py`):
    *   The "Orchestrator" that runs the loop. It asks the Planner for a strategy, executes it via `ToolBox`, and sends results to the Critic.
3.  **Critic** (`backend/agent/critic.py`):
    *   Evaluates results and curates `research_insights.md`.


## 4. Strategy Engine
- **Base Class**: `backend.engine.strategy.Strategy`
- **Execution**:
    - `runner.py` initializes the strategy with data and parameters.
    - `on_data(index, row)` is called for every bar.
    - `place_order(symbol, qty, side)`: **NEW** Standard method for executing trades (Paper or Live).
    - `broker.place_order()` handles execution (Paper or Live).
- **Hybrid Architecture**:
    - `HybridRegimeStrategy` uses a **MockBroker** system.
    - Sub-strategies (`StochRSI`, `Donchian`) run on virtual brokers.
    - The Parent Strategy filters and routes orders to the Real Broker based on the active regime.
    - **Advanced Filters**:
        - **Seasonality**: No-Trade Zones (09:30-10:00, 15:50-16:00).
        - **VIX**: Volatility Regime Filter.
        - **Sector TICK**: Market Breadth Filter (requires fetching 10 Sector ETFs).
    - **GammaScalping**:
        - **Logic**: Uses Bollinger Band Width to detect low volatility regimes ("Long Gamma"). Scalps Mean Reversion when Volatility is low.
        - **Optimization**: Tunable `vol_threshold` and `rsi_period`.
    - **HybridRegime Updates**:
        - **TICK Filter**: Automatically bypassed if `sector_tick` data is missing (e.g., for Forex CSVs).
        - **CSV Support**: `ToolBox` auto-detects Forex symbols and switches source to `csv`.

## 5. Strategy Factory (Agent Capability)
The Agent can autonomously create, register, and verify new strategies.

- **Generator**: `backend.agent.strategy_generator.StrategyGenerator`
    - Uses a robust template based on the verified `RapidFireTest` bot.
    - Handles imports, class structure, and standard indicators (RSI).
- **Registrar**: `backend.agent.registrar.StrategyRegistrar`
    - Automatically injects the new strategy class into `backend/runner.py`.
- **Workflow**:
    1.  **Create**: Agent generates `backend/strategies/new_strategy.py`.
    2.  **Register**: Agent updates `runner.py` imports and `STRATEGY_MAP`.
    3.  **Verify**: Agent runs a backtest on `BTC/USD` (or other supported asset) to confirm syntax and logic.


## 5. Data Pipeline
- **Sources**: Alpaca (Live/Paper), CSV (Backtest).
    - **Auto-Detection**: `ToolBox` automatically selects `source="csv"` for Forex pairs (containing "USD", "EUR", "JPY", "GBP", "=").
- **Loader**: `backend.engine.alpaca_loader.AlpacaDataLoader`.
- **Advanced Data**:
    - `runner.py` automatically fetches `VIXY` (Volatility) and `XLK, XLF...` (Sectors) if the strategy requires them.
    - **Sector TICK**: Calculated in `runner.py` as the net count of sectors UP vs DOWN (-10 to +10).

## 6. The Research Loop
1.  **Implement**: Modify strategy logic in `backend/strategies/`.
2.  **Execute**: Run `runner.py` (Backtest or Matrix).
3.  **Analyze**: Run `analyze_results.py` to generate insights in `research.db`.
4.  **Verify**: Check `research_insights.md` (auto-generated) for findings.
5.  **Save**: Run `/git_save` to commit and update memory.

## 7. API Structure
The Backend exposes results via a REST API for the Frontend.

- `GET /api/runs`: List all test runs (metrics only).
- `GET /api/runs/{test_id}`: Get full details (including equity curve) for a specific run. Supports downsampling for large datasets.
- `GET /api/edges`: Get aggregated "Edge" stats with best timeframe selection.
- `GET /api/results/composite`: Get the stitched "Full History" equity curve for a Strategy/Symbol/Timeframe combo. Supports downsampling.
- `GET /api/insights`: Get generated research insights.

## 5. Frontend Architecture
- **Matrix View**: Heatmap of performance (Year vs Pair).
- **Edge View**: Filtered list of strategies meeting the "Consistency Champion" criteria (>65% win rate).
- **Strategy Overview**: Visualizes the Composite Equity Curve (2002-2024).

## 8. Forward Testing (Paper Trading)
To verify the execution pipeline and measure slippage, we use a high-frequency test strategy.

### RapidFireTest Strategy
- **Logic**: RSI(2) on 1m timeframe. Buy < 10, Sell > 90.
- **Goal**: Generate 10-20 trades/day to verify Alpaca connectivity and execution speed.

**Command:**
```bash
# Standard Run
python3 -m backend.runner trade --strategy RapidFireTest --symbol BTC/USD --timeframe 1m --paper

# Long-Running (Prevent Sleep)
caffeinate -i python3 -m backend.runner trade --strategy RapidFireTest --symbol BTC/USD --timeframe 1m --paper
```

**Verification Steps:**
1.  Run the command.
2.  Wait for "Entering Live Loop...".
3.  Monitor the terminal for "SIGNAL: BUY/SELL".
4.  Check Alpaca Dashboard to confirm the trade appeared.
5.  Compare the "Price" in the terminal log vs the "Fill Price" in Alpaca to measure slippage.


## Recent System Updates
- [Feat]: Verified Strategy Factory & Fixed Execution Pipeline (2025-12-09)
- [Feat]: Implemented Strategy Factory (Agent Upgrade) (2025-12-09)
- [Feat]: Verified Live Trading Pipeline (RapidFireTest) (2025-12-09)
- [Feat]: Implemented Unified Memory System (2025-12-10)
