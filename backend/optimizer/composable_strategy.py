"""Generic composable strategy that wires building blocks together.

Instead of writing a new Strategy subclass for each idea, you pass
entry/exit/filter/sizer functions as parameters. The ComposableStrategy
handles all the plumbing: indicator calculation, position tracking,
stop loss management, and order execution.

Works with both the Backtester (via BrokerAdapter) and live trading.
"""

import pandas as pd
from backend.engine.strategy import Strategy
from backend.optimizer.indicator_calculator import compute_indicators


class ComposableStrategy(Strategy):
    def __init__(self, data, events, parameters, initial_cash=10000.0, broker=None):
        super().__init__(data, events, parameters, initial_cash, broker)

        self.symbol = parameters.get("symbol", "Unknown")

        # Building blocks (callables)
        self.entry_fn = parameters["entry_fn"]
        self.exit_fn = parameters["exit_fn"]
        self.filter_fn = parameters.get("filter_fn")
        self.sizer_fn = parameters.get("sizer_fn")

        # State for zone-based entries and trailing exits
        self.state = {}
        self.position_side = None  # 'long' | 'short' | None
        self.entry_price = None
        self.bar_index = 0

        # Pre-compute indicators
        compute_indicators(self.data, parameters)

    def on_data(self, index, row):
        self.on_bar(row, self.bar_index, self.data)
        self.bar_index += 1

    def on_event(self, event):
        pass

    def on_bar(self, row, i, df):
        # Need at least 200 bars for SMA 200
        if i < 200:
            return

        prev_row = df.iloc[i - 1]

        # 1. Check regime filter
        if self.filter_fn and not self.filter_fn(row):
            # Filter says don't trade — close any open position
            if self.position_side:
                self._close_position(row, i)
            return

        # 2. If in position, check exit
        if self.position_side:
            should_exit = self.exit_fn(
                row, self.position_side, self.entry_price, self.state
            )
            if should_exit:
                self._close_position(row, i)
            return

        # 3. If flat, check entry
        signal = self.entry_fn(row, prev_row, self.state)
        if signal in ("long", "short"):
            self._open_position(signal, row, i)

    def _open_position(self, side, row, i):
        equity = self.broker.get_equity() if self.broker else self.cash
        price = row["Close"]
        atr_val = row["atr"]

        # Calculate size
        if self.sizer_fn:
            size = self.sizer_fn(equity, price, atr_val)
        else:
            size = (equity * 0.25) / price

        size = round(size, 4)
        if size <= 0:
            return

        # Record ATR at entry for stop loss calculations
        self.state["entry_atr"] = atr_val
        self.state["best_price"] = price

        if side == "long":
            result = self.buy(price=price, size=size, timestamp=i)
        else:
            result = self.sell(price=price, size=size, timestamp=i)

        if result is not None:
            self.position_side = side
            self.entry_price = price

    def _close_position(self, row, i):
        price = row["Close"]
        qty = abs(self.broker.get_position(self.symbol)) if self.broker else 0

        if qty <= 0:
            # Position already closed (e.g., by stop loss)
            self.position_side = None
            self.entry_price = None
            self.state.pop("entry_atr", None)
            self.state.pop("best_price", None)
            return

        if self.position_side == "long":
            result = self.sell(price=price, size=qty, timestamp=i)
        else:
            result = self.buy(price=price, size=qty, timestamp=i)

        if result is not None:
            self.position_side = None
            self.entry_price = None
            self.state.pop("entry_atr", None)
            self.state.pop("best_price", None)
