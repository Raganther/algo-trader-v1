import pandas as pd
import numpy as np
from backend.engine.strategy import Strategy

class DonchianBreakoutStrategy(Strategy):
    def __init__(self, data: pd.DataFrame, events: pd.DataFrame = None, parameters: dict = {}, initial_cash: float = 10000.0, broker=None):
        super().__init__(data, events, parameters, initial_cash, broker)
        
        # Parameters
        self.entry_period = parameters.get('entry_period', 20)
        self.exit_period = parameters.get('exit_period', 10)
        self.stop_loss_atr = parameters.get('stop_loss_atr', 2.0)
        self.atr_period = parameters.get('atr_period', 20)
        self.symbol = parameters.get('symbol', 'Unknown')
        self.atr_col = parameters.get('atr_col', 'atr')
        
        # State
        self.bar_index = 0
        
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
        # Note: Our modular ATR uses rolling mean. The original code used rolling mean of True Range.
        # The logic matches.
        # Original: 
        # high_low = self.data['High'] - self.data['Low']
        # ... true_range = np.max(ranges, axis=1)
        # self.data['atr'] = true_range.rolling(window=self.atr_period).mean().shift(1)
        
        # Modular ATR returns the rolling mean. We just need to shift it by 1 for usage (to avoid lookahead)
        self.data[self.atr_col] = atr(
            self.data['High'], 
            self.data['Low'], 
            self.data['Close'], 
            self.atr_period
        ).shift(1)

    def on_data(self, index, row):
        # Delegate to on_bar with internal bar position and data
        self.on_bar(row, self.bar_index, self.data)
        self.bar_index += 1

    def on_bar(self, row, i, df):
        # Skip warmup period
        if i < 50:
            return
            
        # Get current position
        positions = self.broker.get_positions()
        position = positions.get(self.symbol)
        
        current_qty = position['size'] if position else 0
        
        # Skip if indicators are NaN (warmup period)
        if pd.isna(row['entry_high']) or pd.isna(row[self.atr_col]):
            return

        # Entry Logic
        if current_qty == 0:
            # Long Entry
            if row['Close'] > row['entry_high']:
                # Calculate Size (Risk Based? For now fixed 1 unit or based on cash)
                # Let's use a simple 10% of equity for now to simulate "units"
                equity = self.broker.get_equity()
                risk_amt = equity * 0.02 # 2% risk
                stop_loss_dist = row[self.atr_col] * self.stop_loss_atr
                if stop_loss_dist == 0: return
                
                size = risk_amt / stop_loss_dist
                
                # Cap to 1x leverage (position value can't exceed equity)
                max_size = equity / row['Close']
                size = min(size, max_size)
                size = round(size, 2)
                
                if size > 0:
                    self.broker.place_order(self.symbol, 'buy', size, price=row['Close'], timestamp=i)
                    # We rely on the broker to track the position, but we could set a hard SL order here if the broker supported it.
                    # For this simple engine, we'll check SL in on_data.
            
            # Short Entry
            elif row['Close'] < row['entry_low']:
                equity = self.broker.get_equity()
                risk_amt = equity * 0.02
                stop_loss_dist = row[self.atr_col] * self.stop_loss_atr
                if stop_loss_dist == 0: return
                
                size = risk_amt / stop_loss_dist
                
                # Cap to 1x leverage (position value can't exceed equity)
                max_size = equity / row['Close']
                size = min(size, max_size)
                size = round(size, 2)
                
                if size > 0:
                    self.broker.place_order(self.symbol, 'sell', size, price=row['Close'], timestamp=i)

        # Exit Logic (Long)
        elif current_qty > 0:
            # Check Exit Rule (10-day Low)
            if row['Close'] < row['exit_low']:
                self.broker.place_order(self.symbol, 'sell', current_qty, price=row['Close'], timestamp=i) # Close position
            
            # Check Hard Stop Loss (ATR based) - Optional, Turtle usually just reversed or exited
            # But let's implement the 2N stop
            entry_price = position['avg_price']
            stop_price = entry_price - (row[self.atr_col] * self.stop_loss_atr)
            if row['Low'] < stop_price:
                 self.broker.place_order(self.symbol, 'sell', current_qty, price=stop_price, timestamp=i)

        # Exit Logic (Short)
        elif current_qty < 0:
            current_qty = abs(current_qty)
            # Check Exit Rule (10-day High)
            if row['Close'] > row['exit_high']:
                self.broker.place_order(self.symbol, 'buy', current_qty, price=row['Close'], timestamp=i) # Close position
            
            # Check Hard Stop Loss
            entry_price = position['avg_price']
            stop_price = entry_price + (row[self.atr_col] * self.stop_loss_atr)
            if row['High'] > stop_price:
                self.broker.place_order(self.symbol, 'buy', current_qty, price=stop_price, timestamp=i)

    def on_event(self, event):
        pass

