"""Validation functions for detecting overfitting.

Three checks:
1. Train/test holdout — does the strategy work on unseen data?
2. Walk-forward — does it work across multiple rolling windows?
3. Multi-asset consistency — does it work on related assets?
"""

import sys
import os
from contextlib import contextmanager

from backend.engine.backtester import Backtester
from backend.engine.data_utils import load_backtest_data
from backend.optimizer.scoring import calc_sharpe


@contextmanager
def _suppress():
    old = sys.stdout
    sys.stdout = open(os.devnull, "w")
    try:
        yield
    finally:
        sys.stdout.close()
        sys.stdout = old


def _run_backtest(strategy_class, params, data, timeframe):
    """Run a single backtest with stdout suppressed."""
    with _suppress():
        bt = Backtester(
            data=data,
            strategy_class=strategy_class,
            parameters=params,
            initial_capital=10000.0,
            spread=0.0003,
            execution_delay=0,
            interval=timeframe,
        )
        return bt.run()


def validate_holdout(strategy_class, params, symbol, timeframe,
                     train_start="2020-01-01", train_end="2023-12-31",
                     test_start="2024-01-01", test_end="2025-12-31"):
    """Train/test holdout validation.

    Runs the strategy on training period, then independently on test period.
    A strategy that returns +5% in training but -2% in testing is overfit.

    Returns:
        dict with train_result, test_result, degradation
    """
    params = {**params, "symbol": symbol}

    train_data = load_backtest_data(symbol, timeframe, train_start, train_end)
    test_data = load_backtest_data(symbol, timeframe, test_start, test_end)

    if train_data.empty or test_data.empty:
        return {"error": f"No data for {symbol} {timeframe}"}

    train_result = _run_backtest(strategy_class, params, train_data, timeframe)
    test_result = _run_backtest(strategy_class, params, test_data, timeframe)

    train_sharpe = calc_sharpe(train_result.get("equity_curve", []))
    test_sharpe = calc_sharpe(test_result.get("equity_curve", []))

    return {
        "train_return": train_result["return_pct"],
        "test_return": test_result["return_pct"],
        "train_sharpe": train_sharpe,
        "test_sharpe": test_sharpe,
        "train_trades": train_result["total_trades"],
        "test_trades": test_result["total_trades"],
        "train_win_rate": train_result["win_rate"],
        "test_win_rate": test_result["win_rate"],
        "degradation": train_result["return_pct"] - test_result["return_pct"],
    }


def walk_forward(strategy_class, params, symbol, timeframe,
                 train_years=2, test_years=1, start_year=2020, end_year=2025):
    """Rolling walk-forward validation.

    Tests the strategy on data it was never trained on, across
    multiple time windows.

    A robust strategy should show positive test returns in most windows.

    Returns:
        dict with windows list and pass_rate
    """
    params = {**params, "symbol": symbol}
    windows = []

    year = start_year
    while year + train_years + test_years - 1 <= end_year:
        train_start = f"{year}-01-01"
        train_end = f"{year + train_years - 1}-12-31"
        test_start = f"{year + train_years}-01-01"
        test_end = f"{year + train_years + test_years - 1}-12-31"

        train_data = load_backtest_data(symbol, timeframe, train_start, train_end)
        test_data = load_backtest_data(symbol, timeframe, test_start, test_end)

        if train_data.empty or test_data.empty:
            year += 1
            continue

        train_result = _run_backtest(strategy_class, params, train_data, timeframe)
        test_result = _run_backtest(strategy_class, params, test_data, timeframe)

        train_sharpe = calc_sharpe(train_result.get("equity_curve", []))
        test_sharpe = calc_sharpe(test_result.get("equity_curve", []))

        windows.append({
            "train_period": f"{train_start} to {train_end}",
            "test_period": f"{test_start} to {test_end}",
            "train_return": train_result["return_pct"],
            "test_return": test_result["return_pct"],
            "train_sharpe": train_sharpe,
            "test_sharpe": test_sharpe,
            "test_trades": test_result["total_trades"],
        })

        year += 1

    if not windows:
        return {"windows": [], "pass_rate": 0.0, "avg_test_return": 0.0}

    pass_count = sum(1 for w in windows if w["test_return"] > 0)
    avg_test_return = sum(w["test_return"] for w in windows) / len(windows)
    avg_test_sharpe = sum(w["test_sharpe"] for w in windows) / len(windows)

    return {
        "windows": windows,
        "pass_rate": pass_count / len(windows),
        "pass_count": pass_count,
        "total_windows": len(windows),
        "avg_test_return": avg_test_return,
        "avg_test_sharpe": avg_test_sharpe,
    }


# Related asset groups for multi-asset checks
RELATED_ASSETS = {
    "GLD": ["GLD", "SLV", "IAU"],
    "XLE": ["XLE", "XOP", "OIH"],
    "XBI": ["XBI", "IBB", "XLV"],
    "TLT": ["TLT", "IEF", "BND"],
    "SPY": ["SPY", "QQQ", "IWM", "DIA"],
    "QQQ": ["SPY", "QQQ", "IWM", "DIA"],
    "IWM": ["SPY", "QQQ", "IWM", "DIA"],
}


def get_related_symbols(symbol):
    """Get related assets for multi-asset consistency check."""
    return RELATED_ASSETS.get(symbol, [symbol])


def multi_asset_check(strategy_class, params, symbol, timeframe,
                      start="2020-01-01", end="2025-12-31"):
    """Test if the strategy works across related assets.

    A real edge should generalise to similar assets.
    If StochRSI works on GLD but fails on SLV and IAU,
    it's likely overfit to GLD-specific noise.

    Returns:
        dict with per-asset results and positive_rate
    """
    related = get_related_symbols(symbol)
    results = {}

    for sym in related:
        sym_params = {**params, "symbol": sym}
        data = load_backtest_data(sym, timeframe, start, end)

        if data.empty:
            results[sym] = {"error": "no data"}
            continue

        result = _run_backtest(strategy_class, sym_params, data, timeframe)
        sharpe = calc_sharpe(result.get("equity_curve", []))

        results[sym] = {
            "return_pct": result["return_pct"],
            "sharpe": sharpe,
            "total_trades": result["total_trades"],
            "win_rate": result["win_rate"],
            "max_drawdown": result["max_drawdown"],
        }

    # Count assets with positive returns (excluding errors)
    valid = {k: v for k, v in results.items() if "error" not in v}
    positive_count = sum(1 for v in valid.values() if v["return_pct"] > 0)
    total_valid = len(valid)

    return {
        "results": results,
        "positive_count": positive_count,
        "total_assets": total_valid,
        "positive_rate": positive_count / total_valid if total_valid > 0 else 0,
        "passes": positive_count >= total_valid * 0.6 if total_valid > 0 else False,
    }
