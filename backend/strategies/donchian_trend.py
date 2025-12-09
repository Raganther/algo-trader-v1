import pandas as pd
import numpy as np
from backend.engine.strategy import Strategy

class DonchianTrendStrategy(Strategy):
    def __init__(self, data: pd.DataFrame, events: pd.DataFrame = None, parameters: dict = {}, initial_cash: float = 10000.0, broker=None):
        super().__init__(data, events, parameters, initial_cash, broker)
        
        # Parameters
        self.entry_period = parameters.get('entry_period', 20)
        self.exit_period = parameters.get('exit_period', 10)
        self.stop_loss_atr = parameters.get('stop_loss_atr', 2.0)
        self.atr_period = parameters.get('atr_period', 20)
        self.adx_period = parameters.get('adx_period', 14)
        self.adx_threshold = parameters.get('adx_threshold', 25)
        self.sma_period = parameters.get('sma_period', 200)
        
        self.symbol = parameters.get('symbol', 'Unknown')
        self.atr_col = parameters.get('atr_col', 'atr')
        
        # Pre-calculate Indicators
        self._calculate_indicators()
        
    def _calculate_indicators(self):
        from backend.indicators.donchian import donchian_channels
        from backend.indicators.atr import atr
        from backend.indicators.adx import adx
        from backend.indicators.sma import sma

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
        self.data[self.atr_col] = atr(
            self.data['High'], 
            self.data['Low'], 
            self.data['Close'], 
            self.atr_period
        ).shift(1)
        
        # ADX Filter
        self.data['adx'] = adx(
            self.data['High'],
            self.data['Low'],
            self.data['Close'],
            self.adx_period
        ).shift(1) # Shift to avoid lookahead
        
        # SMA Filter
        self.data['sma_trend'] = sma(
            self.data['Close'],
            self.sma_period
        ).shift(1)

    def on_data(self, index, row):
        # Get current position
        positions = self.broker.get_positions()
        position = positions.get(self.symbol)
        
        current_qty = position['size'] if position else 0
        
        # Skip if indicators are NaN (warmup period)
        if pd.isna(row['entry_high']) or pd.isna(row[self.atr_col]) or pd.isna(row['adx']) or pd.isna(row['sma_trend']):
            return

        # Entry Logic
        if current_qty == 0:
            # Long Entry
            # Condition: Breakout + Strong Trend (ADX) + Bullish Trend (Price > SMA)
            if (row['Close'] > row['entry_high'] and 
                row['adx'] > self.adx_threshold and 
                row['Close'] > row['sma_trend']):
                
                equity = self.broker.get_equity()
                risk_amt = equity * 0.02 # 2% risk
                stop_loss_dist = row[self.atr_col] * self.stop_loss_atr
                if stop_loss_dist == 0: return
                
                size = risk_amt / stop_loss_dist
                size = round(size, 2)
                
                if size > 0:
                    self.broker.place_order(self.symbol, 'buy', size, price=row['Close'], timestamp=index)
            
            # Short Entry
            # Condition: Breakout + Strong Trend (ADX) + Bearish Trend (Price < SMA)
            elif (row['Close'] < row['entry_low'] and 
                  row['adx'] > self.adx_threshold and 
                  row['Close'] < row['sma_trend']):
                  
                equity = self.broker.get_equity()
                risk_amt = equity * 0.02
                stop_loss_dist = row[self.atr_col] * self.stop_loss_atr
                if stop_loss_dist == 0: return
                
                size = risk_amt / stop_loss_dist
                size = round(size, 2)
                
                if size > 0:
                    self.broker.place_order(self.symbol, 'sell', size, price=row['Close'], timestamp=index)

        # Exit Logic (Long)
        elif current_qty > 0:
            # Check Exit Rule (10-day Low)
            if row['Close'] < row['exit_low']:
                self.broker.place_order(self.symbol, 'sell', current_qty, price=row['Close'], timestamp=index) # Close position
            
            # Check Hard Stop Loss (ATR based)
            entry_price = position['avg_price']
            stop_price = entry_price - (row[self.atr_col] * self.stop_loss_atr)
            if row['Low'] < stop_price:
                 self.broker.place_order(self.symbol, 'sell', current_qty, price=stop_price, timestamp=index)

        # Exit Logic (Short)
        elif current_qty < 0:
            current_qty = abs(current_qty)
            # Check Exit Rule (10-day High)
            if row['Close'] > row['exit_high']:
                self.broker.place_order(self.symbol, 'buy', current_qty, price=row['Close'], timestamp=index) # Close position
            
            # Check Hard Stop Loss
            entry_price = position['avg_price']
            stop_price = entry_price + (row[self.atr_col] * self.stop_loss_atr)
            if row['High'] > stop_price:
                self.broker.place_order(self.symbol, 'buy', current_qty, price=stop_price, timestamp=index)

    def on_event(self, event):
        pass
