import pandas as pd
import numpy as np
from backend.engine.strategy import Strategy

class BollingerBreakoutStrategy(Strategy):
    def __init__(self, data: pd.DataFrame, events: pd.DataFrame = None, parameters: dict = {}, initial_cash: float = 10000.0, broker=None):
        super().__init__(data, events, parameters, initial_cash, broker)
        
        # Parameters
        self.period = parameters.get('period', 20)
        self.std_dev = parameters.get('std_dev', 2.0)
        self.stop_loss_atr = parameters.get('stop_loss_atr', 2.0)
        self.atr_period = parameters.get('atr_period', 14)
        self.symbol = parameters.get('symbol', 'Unknown')
        
        # Pre-calculate Indicators
        self._calculate_indicators()
        
    def _calculate_indicators(self):
        from backend.indicators.bollinger import bollinger_bands
        from backend.indicators.atr import atr

        # Bollinger Bands
        # Shift by 1 to avoid lookahead bias
        bands = bollinger_bands(self.data['Close'], self.period, self.std_dev).shift(1)
        self.data['bb_upper'] = bands['upper']
        self.data['bb_middle'] = bands['middle']
        self.data['bb_lower'] = bands['lower']
        
        # ATR for Stop Loss
        self.data['atr'] = atr(
            self.data['High'], 
            self.data['Low'], 
            self.data['Close'], 
            self.atr_period
        ).shift(1)

    def on_data(self, index, row):
        # Get current position
        positions = self.broker.get_positions()
        position = positions.get(self.symbol)
        current_qty = position['size'] if position else 0
        
        # Warmup check
        if pd.isna(row['bb_upper']) or pd.isna(row['atr']):
            return

        # Entry Logic
        if current_qty == 0:
            # Long Breakout
            if row['Close'] > row['bb_upper']:
                self._enter_position('buy', row, index)
            
            # Short Breakout
            elif row['Close'] < row['bb_lower']:
                self._enter_position('sell', row, index)

        # Exit Logic (Long)
        elif current_qty > 0:
            # Exit if Price closes below Middle Band (Trend Reversal)
            if row['Close'] < row['bb_middle']:
                self.broker.place_order(self.symbol, 'sell', current_qty, row['Close'], timestamp=index)
            
            # Hard Stop Loss
            entry_price = position['avg_price']
            stop_price = entry_price - (row['atr'] * self.stop_loss_atr)
            if row['Low'] < stop_price:
                 self.broker.place_order(self.symbol, 'sell', current_qty, stop_price, timestamp=index)

        # Exit Logic (Short)
        elif current_qty < 0:
            current_qty = abs(current_qty)
            # Exit if Price closes above Middle Band
            if row['Close'] > row['bb_middle']:
                self.broker.place_order(self.symbol, 'buy', current_qty, row['Close'], timestamp=index)
            
            # Hard Stop Loss
            entry_price = position['avg_price']
            stop_price = entry_price + (row['atr'] * self.stop_loss_atr)
            if row['High'] > stop_price:
                self.broker.place_order(self.symbol, 'buy', current_qty, stop_price, timestamp=index)

    def _enter_position(self, side, row, index):
        equity = self.broker.get_equity()
        risk_amt = equity * 0.02 # 2% risk
        stop_loss_dist = row['atr'] * self.stop_loss_atr
        if stop_loss_dist == 0: return
        
        size = risk_amt / stop_loss_dist
        size = round(size, 2)
        
        if size > 0:
            self.broker.place_order(self.symbol, side, size, row['Close'], timestamp=index)

    def on_event(self, event):
        pass
