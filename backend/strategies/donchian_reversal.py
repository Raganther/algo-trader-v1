import pandas as pd
import numpy as np
from backend.engine.strategy import Strategy

class DonchianReversalStrategy(Strategy):
    """
    The "Anti-Strategy".
    Fades the breakout:
    - Buy when Price < Lower Channel (Betting on Reversal)
    - Sell when Price > Upper Channel (Betting on Reversal)
    
    In a strong trend (like JPY), this should lose money consistently.
    """
    def __init__(self, data: pd.DataFrame, events: pd.DataFrame = None, parameters: dict = {}, initial_cash: float = 10000.0, broker=None):
        super().__init__(data, events, parameters, initial_cash, broker)
        
        # Parameters
        self.entry_period = parameters.get('entry_period', 20)
        self.exit_period = parameters.get('exit_period', 10)
        self.stop_loss_atr = parameters.get('stop_loss_atr', 2.0)
        self.atr_period = parameters.get('atr_period', 20)
        self.symbol = parameters.get('symbol', 'Unknown')
        
        # Pre-calculate Indicators
        self._calculate_indicators()
        
    def _calculate_indicators(self):
        from backend.indicators.donchian import donchian_channels
        from backend.indicators.atr import atr

        # Donchian Channels
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
        
        # Skip if indicators are NaN (warmup period)
        if pd.isna(row['entry_high']) or pd.isna(row['atr']):
            return

        # Entry Logic (INVERTED)
        if current_qty == 0:
            # Long Entry (Fade the Breakdown)
            if row['Close'] < row['entry_low']:
                equity = self.broker.get_equity()
                risk_amt = equity * 0.02 
                stop_loss_dist = row['atr'] * self.stop_loss_atr
                if stop_loss_dist == 0: return
                
                size = risk_amt / stop_loss_dist
                size = round(size, 2)
                
                if size > 0:
                    self.broker.place_order(self.symbol, 'buy', size, row['Close'], timestamp=index)
            
            # Short Entry (Fade the Breakout)
            elif row['Close'] > row['entry_high']:
                equity = self.broker.get_equity()
                risk_amt = equity * 0.02
                stop_loss_dist = row['atr'] * self.stop_loss_atr
                if stop_loss_dist == 0: return
                
                size = risk_amt / stop_loss_dist
                size = round(size, 2)
                
                if size > 0:
                    self.broker.place_order(self.symbol, 'sell', size, row['Close'], timestamp=index)

        # Exit Logic (Long)
        elif current_qty > 0:
            # Exit Rule (Reverted to Mean/High)
            if row['Close'] > row['exit_high']: # Inverted Exit
                self.broker.place_order(self.symbol, 'sell', current_qty, row['Close'], timestamp=index) 
            
            # Stop Loss
            entry_price = position['avg_price']
            stop_price = entry_price - (row['atr'] * self.stop_loss_atr)
            if row['Low'] < stop_price:
                 self.broker.place_order(self.symbol, 'sell', current_qty, stop_price, timestamp=index)

        # Exit Logic (Short)
        elif current_qty < 0:
            current_qty = abs(current_qty)
            # Exit Rule (Reverted to Mean/Low)
            if row['Close'] < row['exit_low']: # Inverted Exit
                self.broker.place_order(self.symbol, 'buy', current_qty, row['Close'], timestamp=index) 
            
            # Stop Loss
            entry_price = position['avg_price']
            stop_price = entry_price + (row['atr'] * self.stop_loss_atr)
            if row['High'] > stop_price:
                self.broker.place_order(self.symbol, 'buy', current_qty, stop_price, timestamp=index)

    def on_event(self, event):
        pass
