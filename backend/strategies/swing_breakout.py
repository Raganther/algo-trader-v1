import pandas as pd
import numpy as np
from backend.engine.strategy import Strategy

class SwingBreakoutStrategy(Strategy):
    """
    Daily-timeframe swing breakout strategy with triple confirmation.

    Entry (ALL must be true):
      1. Donchian 55-day breakout (Close > upper_55 for long)
      2. Bollinger width expanding (bb_width > 50-day avg of bb_width)
      3. ADX(14) > 20 AND ADX rising

    Exit (whichever triggers first):
      1. ATR trailing stop: 3x ATR(20) from highest high (longs) / lowest low (shorts)
      2. Donchian 20-day exit: Close < lower_20 (longs) / Close > upper_20 (shorts)

    Position sizing: 2% equity risk, stop = 3x ATR(20), capped at 1x leverage.
    """

    def __init__(self, data: pd.DataFrame, events: pd.DataFrame = None, parameters: dict = {}, initial_cash: float = 10000.0, broker=None):
        super().__init__(data, events, parameters, initial_cash, broker)

        # Parameters
        self.entry_period = parameters.get('entry_period', 55)
        self.exit_period = parameters.get('exit_period', 20)
        self.atr_period = parameters.get('atr_period', 20)
        self.atr_stop_mult = parameters.get('atr_stop_mult', 3.0)
        self.adx_period = parameters.get('adx_period', 14)
        self.adx_threshold = parameters.get('adx_threshold', 20)
        self.bb_period = parameters.get('bb_period', 20)
        self.bb_std = parameters.get('bb_std', 2.0)
        self.bb_avg_period = parameters.get('bb_avg_period', 50)
        self.risk_pct = parameters.get('risk_pct', 0.02)

        self.symbol = parameters.get('symbol', 'Unknown')
        self.atr_col = parameters.get('atr_col', 'atr')

        # Trailing stop state
        self.highest_since_entry = None
        self.lowest_since_entry = None

        # Pre-calculate indicators
        self._calculate_indicators()

    def _calculate_indicators(self):
        from backend.indicators.donchian import donchian_channels
        from backend.indicators.atr import atr
        from backend.indicators.adx import adx
        from backend.indicators.bollinger import bollinger_bands

        # Donchian Channels - 55-day entry, 20-day exit
        channels = donchian_channels(
            self.data['High'],
            self.data['Low'],
            self.entry_period,
            self.exit_period
        )
        self.data['entry_high'] = channels['upper_entry']
        self.data['entry_low'] = channels['lower_entry']
        self.data['exit_high'] = channels['upper_exit']
        self.data['exit_low'] = channels['lower_exit']

        # ATR for position sizing and trailing stop
        self.data[self.atr_col] = atr(
            self.data['High'],
            self.data['Low'],
            self.data['Close'],
            self.atr_period
        ).shift(1)

        # ADX for trend confirmation
        self.data['adx'] = adx(
            self.data['High'],
            self.data['Low'],
            self.data['Close'],
            self.adx_period
        ).shift(1)

        # Previous ADX for "rising" check
        self.data['adx_prev'] = self.data['adx'].shift(1)

        # Bollinger Bands for volatility expansion
        bb = bollinger_bands(self.data['Close'], self.bb_period, self.bb_std)
        # Shift to avoid lookahead - use previous bar's BB width
        self.data['bb_width'] = (bb['upper'] - bb['lower']).shift(1)
        self.data['bb_width_avg'] = self.data['bb_width'].rolling(window=self.bb_avg_period).mean()

    def on_data(self, index, row):
        positions = self.broker.get_positions()
        position = positions.get(self.symbol)

        current_qty = position['size'] if position else 0

        # Skip if indicators not ready
        if pd.isna(row['entry_high']) or pd.isna(row[self.atr_col]) or pd.isna(row['adx']) or pd.isna(row['adx_prev']) or pd.isna(row['bb_width_avg']):
            return

        # Entry Logic
        if current_qty == 0:
            # Reset trailing stop state
            self.highest_since_entry = None
            self.lowest_since_entry = None

            # Shared confirmation checks
            adx_confirms = row['adx'] > self.adx_threshold and row['adx'] > row['adx_prev']
            vol_expanding = row['bb_width'] > row['bb_width_avg']

            # Long Entry
            if (row['Close'] > row['entry_high'] and adx_confirms and vol_expanding):
                equity = self.broker.get_equity()
                stop_dist = row[self.atr_col] * self.atr_stop_mult
                if stop_dist <= 0:
                    return

                risk_amt = equity * self.risk_pct
                size = risk_amt / stop_dist
                # Cap at 1x leverage
                max_size = equity / row['Close']
                size = min(size, max_size)
                size = int(size)  # Whole shares only

                if size > 0:
                    self.broker.place_order(self.symbol, 'buy', size, price=row['Close'], timestamp=index)
                    self.highest_since_entry = row['High']

            # Short Entry
            elif (row['Close'] < row['entry_low'] and adx_confirms and vol_expanding):
                equity = self.broker.get_equity()
                stop_dist = row[self.atr_col] * self.atr_stop_mult
                if stop_dist <= 0:
                    return

                risk_amt = equity * self.risk_pct
                size = risk_amt / stop_dist
                max_size = equity / row['Close']
                size = min(size, max_size)
                size = int(size)

                if size > 0:
                    self.broker.place_order(self.symbol, 'sell', size, price=row['Close'], timestamp=index)
                    self.lowest_since_entry = row['Low']

        # Exit Logic (Long)
        elif current_qty > 0:
            # Update trailing high
            if self.highest_since_entry is None:
                self.highest_since_entry = row['High']
            else:
                self.highest_since_entry = max(self.highest_since_entry, row['High'])

            stop_dist = row[self.atr_col] * self.atr_stop_mult
            trailing_stop = self.highest_since_entry - stop_dist

            # Exit 1: ATR trailing stop
            if row['Low'] < trailing_stop:
                self.broker.place_order(self.symbol, 'sell', current_qty, price=trailing_stop, timestamp=index)
                self.highest_since_entry = None
            # Exit 2: Donchian 20-day exit
            elif row['Close'] < row['exit_low']:
                self.broker.place_order(self.symbol, 'sell', current_qty, price=row['Close'], timestamp=index)
                self.highest_since_entry = None

        # Exit Logic (Short)
        elif current_qty < 0:
            abs_qty = abs(current_qty)

            # Update trailing low
            if self.lowest_since_entry is None:
                self.lowest_since_entry = row['Low']
            else:
                self.lowest_since_entry = min(self.lowest_since_entry, row['Low'])

            stop_dist = row[self.atr_col] * self.atr_stop_mult
            trailing_stop = self.lowest_since_entry + stop_dist

            # Exit 1: ATR trailing stop
            if row['High'] > trailing_stop:
                self.broker.place_order(self.symbol, 'buy', abs_qty, price=trailing_stop, timestamp=index)
                self.lowest_since_entry = None
            # Exit 2: Donchian 20-day exit
            elif row['Close'] > row['exit_high']:
                self.broker.place_order(self.symbol, 'buy', abs_qty, price=row['Close'], timestamp=index)
                self.lowest_since_entry = None

    def on_event(self, event):
        pass

    def generate_signals(self, data):
        """Live trading signal generation - recalculate indicators on fresh data."""
        from backend.indicators.donchian import donchian_channels
        from backend.indicators.atr import atr
        from backend.indicators.adx import adx
        from backend.indicators.bollinger import bollinger_bands

        channels = donchian_channels(data['High'], data['Low'], self.entry_period, self.exit_period)
        data['entry_high'] = channels['upper_entry']
        data['entry_low'] = channels['lower_entry']
        data['exit_high'] = channels['upper_exit']
        data['exit_low'] = channels['lower_exit']

        data[self.atr_col] = atr(data['High'], data['Low'], data['Close'], self.atr_period).shift(1)
        data['adx'] = adx(data['High'], data['Low'], data['Close'], self.adx_period).shift(1)
        data['adx_prev'] = data['adx'].shift(1)

        bb = bollinger_bands(data['Close'], self.bb_period, self.bb_std)
        data['bb_width'] = (bb['upper'] - bb['lower']).shift(1)
        data['bb_width_avg'] = data['bb_width'].rolling(window=self.bb_avg_period).mean()

        self.data = data

    def on_bar(self, row, index, data):
        """Live trading entry point."""
        self.on_data(index, row)
