"""Hard disqualification filters for backtest results.

Fast checks that reject candidates before expensive validation.
"""

DISQUALIFICATION_RULES = {
    "min_trades": 30,
    "min_trades_per_year": 6,
    "max_drawdown": 25.0,
    "min_profit_factor": 1.05,
    "min_win_rate": 0.35,
    "max_win_rate": 0.85,
}


def passes_disqualification(result, years=None, rules=None):
    """Check if a backtest result passes hard filters.

    Args:
        result: dict from Backtester.run()
        years: number of years in the backtest period (for trades/year calc)
        rules: optional override of DISQUALIFICATION_RULES

    Returns:
        (bool, str): (passes, reason) — reason is None if passes
    """
    r = rules or DISQUALIFICATION_RULES

    total_trades = result.get("total_trades", 0)
    if total_trades < r["min_trades"]:
        return False, f"too_few_trades ({total_trades} < {r['min_trades']})"

    if years and years > 0:
        trades_per_year = total_trades / years
        if trades_per_year < r["min_trades_per_year"]:
            return False, f"too_few_trades_per_year ({trades_per_year:.1f} < {r['min_trades_per_year']})"

    max_dd = result.get("max_drawdown", 0)
    if max_dd > r["max_drawdown"]:
        return False, f"drawdown_too_high ({max_dd:.1f}% > {r['max_drawdown']}%)"

    pf = result.get("profit_factor", 0)
    if pf < r["min_profit_factor"]:
        return False, f"profit_factor_too_low ({pf:.2f} < {r['min_profit_factor']})"

    wr = result.get("win_rate", 0)
    if wr < r["min_win_rate"]:
        return False, f"win_rate_too_low ({wr:.2f} < {r['min_win_rate']})"
    if wr > r["max_win_rate"]:
        return False, f"win_rate_too_high ({wr:.2f} > {r['max_win_rate']})"

    return True, None
