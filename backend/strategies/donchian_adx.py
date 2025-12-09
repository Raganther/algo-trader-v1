from backend.strategies.donchian_breakout import DonchianBreakoutStrategy
from backend.indicators.adx import adx
import pandas as pd

class DonchianADXStrategy(DonchianBreakoutStrategy):
    """
    Donchian Breakout Strategy with ADX Regime Filter.
    Only enters trades when ADX is above a threshold (trending market).
    """
    
    def __init__(self, data: pd.DataFrame, events: pd.DataFrame = None, parameters: dict = {}, initial_cash: float = 10000.0, broker=None):
        # Initialize parameters before calling super because super calls _calculate_indicators
        self.adx_threshold = parameters.get("adx_threshold", 25)
        self.adx_period = parameters.get("adx_period", 14)
        
        super().__init__(data, events, parameters, initial_cash, broker)

    def _calculate_indicators(self):
        # Call base class to calculate Donchian channels and ATR
        super()._calculate_indicators()
        
        # Calculate ADX
        # We need to shift it by 1 to avoid lookahead bias (using yesterday's ADX to decide today)
        self.data['adx'] = adx(
            self.data['High'], 
            self.data['Low'], 
            self.data['Close'], 
            self.adx_period
        ).shift(1)

    def on_data(self, index, row):
        # Get current position
        positions = self.broker.get_positions()
        position = positions.get(self.symbol)
        
        current_qty = position['size'] if position else 0
        
        # Skip if indicators are NaN
        if pd.isna(row['entry_high']) or pd.isna(row['atr']) or pd.isna(row['adx']):
            return

        # REGIME FILTER: Only enter if ADX > Threshold
        # We allow EXITS regardless of ADX (to get out of bad trades), but block ENTRIES.
        is_trending = row['adx'] > self.adx_threshold

        # Entry Logic
        if current_qty == 0:
            if not is_trending:
                return # Skip entry if market is choppy

            # Long Entry
            if row['Close'] > row['entry_high']:
                equity = self.broker.get_equity()
                risk_amt = equity * 0.02 
                stop_loss_dist = row['atr'] * self.stop_loss_atr
                if stop_loss_dist == 0: return
                
                size = risk_amt / stop_loss_dist
                size = round(size, 2)
                
                if size > 0:
                    self.broker.place_order(self.symbol, 'buy', size, row['Close'], timestamp=index)
            
            # Short Entry
            elif row['Close'] < row['entry_low']:
                equity = self.broker.get_equity()
                risk_amt = equity * 0.02
                stop_loss_dist = row['atr'] * self.stop_loss_atr
                if stop_loss_dist == 0: return
                
                size = risk_amt / stop_loss_dist
                size = round(size, 2)
                
                if size > 0:
                    self.broker.place_order(self.symbol, 'sell', size, row['Close'], timestamp=index)

        # Exit Logic (Same as Base Class)
        elif current_qty > 0:
            # Check Exit Rule (10-day Low)
            if row['Close'] < row['exit_low']:
                self.broker.place_order(self.symbol, 'sell', current_qty, row['Close'], timestamp=index) 
            
            # Check Hard Stop Loss
            entry_price = position['avg_price']
            stop_price = entry_price - (row['atr'] * self.stop_loss_atr)
            if row['Low'] < stop_price:
                 self.broker.place_order(self.symbol, 'sell', current_qty, stop_price, timestamp=index)

        elif current_qty < 0:
            current_qty = abs(current_qty)
            # Check Exit Rule (10-day High)
            if row['Close'] > row['exit_high']:
                self.broker.place_order(self.symbol, 'buy', current_qty, row['Close'], timestamp=index) 
            
            # Check Hard Stop Loss
            entry_price = position['avg_price']
            stop_price = entry_price + (row['atr'] * self.stop_loss_atr)
            if row['High'] > stop_price:
                self.broker.place_order(self.symbol, 'buy', current_qty, stop_price, timestamp=index)
