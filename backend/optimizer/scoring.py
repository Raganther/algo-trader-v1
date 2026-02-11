"""Scoring functions for backtest results.

Provides Sharpe ratio calculation and a composite scoring function
used by the sweep engine to rank experiment results.
"""

import math


def calc_sharpe(equity_curve, risk_free_rate=0.0):
    """Calculate annualised Sharpe ratio from an equity curve.

    Args:
        equity_curve: list of dicts with 'equity' key (as produced by Backtester)
        risk_free_rate: annual risk-free rate (default 0)

    Returns:
        float: annualised Sharpe ratio, or 0.0 if insufficient data
    """
    if not equity_curve or len(equity_curve) < 2:
        return 0.0

    equities = [p["equity"] for p in equity_curve]

    # Calculate period returns
    returns = []
    for i in range(1, len(equities)):
        prev = equities[i - 1]
        if prev == 0:
            continue
        returns.append((equities[i] - prev) / prev)

    if len(returns) < 2:
        return 0.0

    mean_ret = sum(returns) / len(returns)
    variance = sum((r - mean_ret) ** 2 for r in returns) / (len(returns) - 1)
    std_ret = math.sqrt(variance) if variance > 0 else 0.0

    if std_ret == 0:
        return 0.0

    # Estimate periods per year from the equity curve timestamps
    periods_per_year = _estimate_periods_per_year(equity_curve)

    # Annualise
    excess_return = mean_ret - (risk_free_rate / periods_per_year)
    sharpe = (excess_return / std_ret) * math.sqrt(periods_per_year)

    return round(sharpe, 4)


def score_result(results, equity_curve):
    """Composite score for ranking backtest results.

    Returns -999 for disqualified results (too few trades).
    Otherwise returns the Sharpe ratio as the primary score.

    Args:
        results: dict from Backtester.run()
        equity_curve: list of dicts with 'equity' key

    Returns:
        float: composite score
    """
    total_trades = results.get("total_trades", 0)

    if total_trades < 10:
        return -999.0

    sharpe = calc_sharpe(equity_curve)
    return sharpe


def _estimate_periods_per_year(equity_curve):
    """Estimate trading periods per year from equity curve timestamps."""
    if len(equity_curve) < 2:
        return 252  # default to daily

    try:
        from datetime import datetime

        first = equity_curve[0].get("time")
        last = equity_curve[-1].get("time")

        if first is None or last is None:
            return 252

        # Handle both string dates and unix timestamps
        if isinstance(first, str):
            t0 = datetime.fromisoformat(first)
            t1 = datetime.fromisoformat(last)
        elif isinstance(first, (int, float)):
            t0 = datetime.fromtimestamp(first)
            t1 = datetime.fromtimestamp(last)
        else:
            return 252

        total_seconds = (t1 - t0).total_seconds()
        if total_seconds <= 0:
            return 252

        n_periods = len(equity_curve) - 1
        seconds_per_period = total_seconds / n_periods
        seconds_per_year = 365.25 * 24 * 3600

        periods_per_year = seconds_per_year / seconds_per_period
        return max(1, periods_per_year)

    except (ValueError, TypeError, OverflowError):
        return 252
