"""Shared-timeline portfolio runner.

Runs N strategy instances on N symbols against a SINGLE shared PaperTrader
on a unified time grid. Unlike `backtester.py` (one strategy / one symbol /
$10k pool), this runner answers portfolio-level questions:

- Aggregate Sharpe / DD with shared capital and 4-position cap binding
- Whether the Apr 29 correlation-aware sizing discount actually fires
  (single-symbol backtest is N=1 always, so the discount is a no-op there)
- Per-symbol contribution to portfolio P&L
- Max concurrent positions / cluster co-occupancy

Timeline policy: UNION of per-symbol timestamps. A symbol with no bar at
time T does not get on_data, but its position still marks-to-market via
the broker's last known price for that symbol.
"""
from __future__ import annotations

from collections import Counter
from itertools import groupby
from typing import Iterable

import pandas as pd

from .paper_trader import PaperTrader
from . import correlation_sizing


class PortfolioRunner:
    def __init__(
        self,
        symbol_data: dict[str, pd.DataFrame],
        strategy_class,
        parameters: dict,
        initial_capital: float = 94000.0,
        spread: float = 0.0,
        rotation=None,
    ):
        self.symbol_data = {sym: df for sym, df in symbol_data.items() if df is not None and not df.empty}
        if not self.symbol_data:
            raise ValueError("No symbol data provided.")

        self.strategy_class = strategy_class
        self.parameters_template = dict(parameters)
        self.initial_capital = initial_capital
        self.spread = spread

        self.broker = PaperTrader(initial_capital=initial_capital, spread=spread)

        self.strategies: dict[str, object] = {}
        for sym, df in self.symbol_data.items():
            params = dict(parameters)
            params["symbol"] = sym
            # V2 — each bot sizes off initial_capital (mirrors live: 7 bots on one Alpaca
            # account each see the same equity number when sizing). No compounding artefact.
            params["equity_mode"] = "fixed"
            self.strategies[sym] = strategy_class(df, None, params, initial_capital, self.broker)
            # Rotation flag — runner toggles at W-FRI boundary. Default False so
            # no-rotation runs are bit-identical to baseline.
            self.strategies[sym].rotation_paused = False

        self.rotation = rotation
        self._last_rotation_week = None

        self.equity_history: list[dict] = []
        self.concurrent_history: list[dict] = []   # per-timestamp count of open positions
        self.cluster_cooccupancy: Counter = Counter()  # {N_held_in_cluster: count of bars with that state}

    def _build_event_stream(self) -> list[tuple[pd.Timestamp, str, pd.Series]]:
        events = []
        for sym, df in self.symbol_data.items():
            for ts, row in df.iterrows():
                events.append((ts, sym, row))
        events.sort(key=lambda e: (e[0], e[1]))
        return events

    def _open_position_count(self) -> int:
        return sum(1 for p in self.broker.positions.values() if abs(p.get("size", 0)) > 0)

    def _sample_cluster_cooccupancy(self) -> None:
        """For each cluster, count how many of its members currently hold a position."""
        positions = self.broker.positions
        for cluster_name, members in correlation_sizing.CLUSTERS.items():
            n = sum(1 for sym in members if abs(positions.get(sym, {}).get("size", 0)) > 0)
            self.cluster_cooccupancy[(cluster_name, n)] += 1

    def run(self) -> dict:
        events = self._build_event_stream()
        if not events:
            return self._empty_results()

        for ts, group in groupby(events, key=lambda e: e[0]):
            group_list = list(group)
            for _, sym, row in group_list:
                self.broker.update_price(sym, row["Close"])

            # Rotation rebalance: at the W-FRI boundary, refresh each strategy's
            # rotation_paused flag from the active set. period_start of W-FRI is
            # Saturday → strictly increases at the Saturday→Friday boundary, so
            # this fires once per week regardless of the bar's intra-week time.
            if self.rotation is not None:
                current_week = pd.Timestamp(ts).to_period("W-FRI").start_time
                if current_week != self._last_rotation_week:
                    active = self.rotation.active_set_for(ts)
                    for sym, strat in self.strategies.items():
                        strat.rotation_paused = (sym not in active)
                    self.rotation.record_rebalance(ts, active)
                    print(f"[ROTATION] {ts} active={len(active)}/{len(self.strategies)}: {sorted(active)}")
                    self._last_rotation_week = current_week

            for _, sym, row in group_list:
                self.strategies[sym].on_data(ts, row)

            # Record state after all symbols at this timestamp have processed
            equity = self.broker.get_equity()
            self.equity_history.append({"time": int(pd.Timestamp(ts).timestamp()), "equity": round(equity, 2)})
            self.concurrent_history.append({
                "time": int(pd.Timestamp(ts).timestamp()),
                "n_open": self._open_position_count(),
            })
            self._sample_cluster_cooccupancy()

        return self._compute_results()

    def _empty_results(self) -> dict:
        return {
            "initial_capital": self.initial_capital,
            "final_equity": self.initial_capital,
            "return_pct": 0.0,
            "max_drawdown": 0.0,
            "sharpe": 0.0,
            "total_trades": 0,
            "per_symbol": {},
            "max_concurrent": 0,
            "cluster_cooccupancy": {},
            "equity_history": [],
        }

    def _compute_results(self) -> dict:
        final_equity = self.broker.get_equity()
        return_pct = ((final_equity - self.initial_capital) / self.initial_capital) * 100.0

        # Aggregate Sharpe — daily-resampled equity × √252 (matches backtester.py logic)
        sharpe = 0.0
        max_drawdown_pct = 0.0
        if len(self.equity_history) > 1:
            df_eq = pd.DataFrame(self.equity_history)
            df_eq["ts"] = pd.to_datetime(df_eq["time"], unit="s")
            df_eq = df_eq.set_index("ts").sort_index()
            daily = df_eq["equity"].resample("1D").last().dropna()
            daily_ret = daily.pct_change().dropna()
            if len(daily_ret) > 1 and daily_ret.std() > 0:
                sharpe = (daily_ret.mean() / daily_ret.std()) * (252 ** 0.5)
            # Max DD on daily equity
            running_peak = daily.cummax()
            dd = (running_peak - daily) / running_peak
            max_drawdown_pct = float(dd.max() * 100.0) if len(dd) else 0.0

        # Per-symbol P&L from broker.trade_history
        per_symbol: dict[str, dict] = {}
        for trade in self.broker.trade_history:
            sym = trade.get("symbol", "Unknown")
            entry = per_symbol.setdefault(sym, {"trades": 0, "pnl": 0.0, "wins": 0, "losses": 0})
            entry["trades"] += 1
            pnl = float(trade.get("pnl", 0.0))
            entry["pnl"] += pnl
            if pnl > 0:
                entry["wins"] += 1
            else:
                entry["losses"] += 1
        for sym, e in per_symbol.items():
            e["pnl"] = round(e["pnl"], 2)
            e["win_rate"] = round(e["wins"] / e["trades"], 3) if e["trades"] else 0.0

        # Max concurrent positions
        max_concurrent = 0
        if self.concurrent_history:
            max_concurrent = max(r["n_open"] for r in self.concurrent_history)

        # Cluster co-occupancy distribution
        cooccupancy_summary: dict[str, dict[int, int]] = {}
        for (cluster, n), count in self.cluster_cooccupancy.items():
            cooccupancy_summary.setdefault(cluster, {})[n] = count

        return {
            "initial_capital": self.initial_capital,
            "final_equity": round(final_equity, 2),
            "return_pct": round(return_pct, 2),
            "max_drawdown": round(max_drawdown_pct, 2),
            "sharpe": round(float(sharpe), 2),
            "total_trades": len(self.broker.trade_history),
            "per_symbol": per_symbol,
            "max_concurrent": max_concurrent,
            "cluster_cooccupancy": cooccupancy_summary,
            "equity_history": self.equity_history,
            "trade_history": self.broker.trade_history,
            "rotation_log": (self.rotation.rebalance_log() if self.rotation is not None else []),
        }
