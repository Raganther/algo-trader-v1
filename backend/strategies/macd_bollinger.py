import pandas as pd
import numpy as np
from backend.engine.strategy import Strategy

class MACDBollingerStrategy(Strategy):
    def __init__(self, data: pd.DataFrame, events: pd.DataFrame = None, parameters: dict = {}, initial_cash: float = 10000.0, broker=None):
        super().__init__(data, events, parameters, initial_cash, broker)
        
        # Parameters
        self.bb_period = parameters.get('bb_period', 20)
        self.bb_std = parameters.get('bb_std', 2.0)
        self.macd_fast = parameters.get('macd_fast', 12)
        self.macd_slow = parameters.get('macd_slow', 26)
        self.macd_signal = parameters.get('macd_signal', 9)
        self.sl_atr = parameters.get('sl_atr', 2.0)
        self.atr_period = parameters.get('atr_period', 14)
        
        # New Parameters
        self.use_trailing_stop = parameters.get('use_trailing_stop', False)
        self.trailing_atr_dist = parameters.get('trailing_atr_dist', 3.0)
        self.use_adx_filter = parameters.get('use_adx_filter', False)
        self.adx_threshold = parameters.get('adx_threshold', 25)
        
        self.symbol = parameters.get('symbol', 'Unknown')
        
        # State for Trailing Stop
        self.highest_high = 0.0
        self.lowest_low = float('inf')
        
        # Pre-calculate Indicators
        self._calculate_indicators()
        
    def _calculate_indicators(self):
        from backend.indicators.bollinger import bollinger_bands
        from backend.indicators.macd import macd
        from backend.indicators.atr import atr
        from backend.indicators.adx import adx

        # Bollinger Bands
        bb_results = bollinger_bands(self.data['Close'], self.bb_period, self.bb_std)
        self.data['bb_upper'] = bb_results['upper']
        self.data['bb_lower'] = bb_results['lower']
        self.data['bb_middle'] = bb_results['middle']
        
        # MACD
        macd_results = macd(self.data['Close'], self.macd_fast, self.macd_slow, self.macd_signal)
        self.data['macd'] = macd_results['macd']
        self.data['macd_signal'] = macd_results['signal']
        
        # ATR for Stop Loss
        self.data['atr'] = atr(
            self.data['High'], 
            self.data['Low'], 
            self.data['Close'], 
            self.atr_period
        )
        
        # ADX Filter
        if self.use_adx_filter:
            self.data['adx'] = adx(
                self.data['High'], 
                self.data['Low'], 
                self.data['Close'], 
                self.adx_period
            )

    def on_data(self, index, row):
        # Get current position
        positions = self.broker.get_positions()
        position = positions.get(self.symbol)
        
        current_qty = position['size'] if position else 0
        
        # Skip if indicators are NaN
        if pd.isna(row['bb_upper']) or pd.isna(row['macd']) or pd.isna(row['atr']):
            return
            
        # ADX Check
        adx_ok = True
        if self.use_adx_filter:
            if pd.isna(row['adx']) or row['adx'] < self.adx_threshold:
                adx_ok = False

        # Entry Logic
        if current_qty == 0:
            # Reset Trailing State
            self.highest_high = 0.0
            self.lowest_low = float('inf')
            
            if not adx_ok: return

            # Long Entry: Close > Upper BB AND MACD > Signal (Momentum Confirmation)
            if row['Close'] > row['bb_upper'] and row['macd'] > row['macd_signal']:
                equity = self.broker.get_equity()
                risk_amt = equity * 0.02 # 2% risk
                stop_loss_dist = row['atr'] * self.sl_atr
                if stop_loss_dist == 0: return
                
                size = risk_amt / stop_loss_dist
                size = round(size, 2)
                
                if size > 0:
                    self.broker.place_order(self.symbol, 'buy', size, row['Close'], timestamp=index)
                    self.highest_high = row['High'] # Init High Water Mark
            
            # Short Entry: Close < Lower BB AND MACD < Signal
            elif row['Close'] < row['bb_lower'] and row['macd'] < row['macd_signal']:
                equity = self.broker.get_equity()
                risk_amt = equity * 0.02
                stop_loss_dist = row['atr'] * self.sl_atr
                if stop_loss_dist == 0: return
                
                size = risk_amt / stop_loss_dist
                size = round(size, 2)
                
                if size > 0:
                    self.broker.place_order(self.symbol, 'sell', size, row['Close'], timestamp=index)
                    self.lowest_low = row['Low'] # Init Low Water Mark

        # Exit Logic (Long)
        elif current_qty > 0:
            # Update High Water Mark
            if row['High'] > self.highest_high:
                self.highest_high = row['High']
                
            # Trailing Stop Exit
            if self.use_trailing_stop:
                trail_stop_price = self.highest_high - (row['atr'] * self.trailing_atr_dist)
                if row['Low'] < trail_stop_price:
                    self.broker.place_order(self.symbol, 'sell', current_qty, trail_stop_price, timestamp=index)
                    return

            # Standard Exit Rule: Close < Middle Band (Trend Reversal)
            if row['Close'] < row['bb_middle']:
                self.broker.place_order(self.symbol, 'sell', current_qty, row['Close'], timestamp=index)
                return
            
            # Hard Stop Loss
            entry_price = position['avg_price']
            stop_price = entry_price - (row['atr'] * self.sl_atr)
            if row['Low'] < stop_price:
                 self.broker.place_order(self.symbol, 'sell', current_qty, stop_price, timestamp=index)

        # Exit Logic (Short)
        elif current_qty < 0:
            current_qty = abs(current_qty)
            
            # Update Low Water Mark
            if row['Low'] < self.lowest_low:
                self.lowest_low = row['Low']
                
            # Trailing Stop Exit
            if self.use_trailing_stop:
                trail_stop_price = self.lowest_low + (row['atr'] * self.trailing_atr_dist)
                if row['High'] > trail_stop_price:
                    self.broker.place_order(self.symbol, 'buy', current_qty, trail_stop_price, timestamp=index)
                    return

            # Standard Exit Rule: Close > Middle Band
            if row['Close'] > row['bb_middle']:
                self.broker.place_order(self.symbol, 'buy', current_qty, row['Close'], timestamp=index)
                return
            
            # Hard Stop Loss
            entry_price = position['avg_price']
            stop_price = entry_price + (row['atr'] * self.sl_atr)
            if row['High'] > stop_price:
                self.broker.place_order(self.symbol, 'buy', current_qty, stop_price, timestamp=index)

    def on_event(self, event):
        pass
