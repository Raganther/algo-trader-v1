from ..strategy import Strategy
from ..signals.sma_signal import SMASignal
from ..signals.rsi_signal import RSISignal
from ..signals.macd_signal import MACDSignal
from ..signals.bollinger_signal import BollingerSignal
from ..signals.event_signal import EventSignal
from ..signals.support_resistance_signal import SupportResistanceSignal
from ..signals.trend_signal import TrendSignal
from ..signals.atr_signal import ATRSignal
from ..signals.time_signal import TimeSignal
from ..signals.time_range_signal import TimeRangeSignal
import pandas as pd

class CompositeStrategy(Strategy):
    def __init__(self, data: pd.DataFrame, events: pd.DataFrame = None, parameters: dict = {}, initial_cash: float = 10000.0, broker=None):
        super().__init__(data, events, parameters, initial_cash, broker)
        
        # Registry of available signal classes
        self.signal_registry = {
            "SMA": SMASignal,
            "RSI": RSISignal,
            "MACD": MACDSignal,
            "Bollinger": BollingerSignal,
            "Event": EventSignal,
            "SupportResistance": SupportResistanceSignal,
            "Trend": TrendSignal,
            "ATR": ATRSignal,
            "Time": TimeSignal,
            "TimeRange": TimeRangeSignal
        }
        
        self.signals = []
        self.conditions = parameters.get('conditions', [])
        self.exit_conditions = parameters.get('exit_conditions', [])
        self.short_conditions = parameters.get('short_conditions', [])
        self.cover_conditions = parameters.get('cover_conditions', [])
        
        # Risk Management
        self.stop_loss_pct = float(parameters.get('stop_loss', 0.0)) # 0.0 means disabled
        self.take_profit_pct = float(parameters.get('take_profit', 0.0))
        
        # ATR Risk Management
        self.atr_signal_id = parameters.get('atr_signal_id')
        self.sl_atr_mult = float(parameters.get('stop_loss_atr', 0.0))
        self.tp_atr_mult = float(parameters.get('take_profit_atr', 0.0))
        
        # Trailing Stop
        self.trailing_stop_params = parameters.get('trailing_stop', {})
        self.ts_activation = float(self.trailing_stop_params.get('activation_pct', 0.0))
        self.ts_trail = float(self.trailing_stop_params.get('trail_pct', 0.0))
        
        self.signal_instances = {}
        self.latest_signal_values = {} # Store latest values for all signals
        self.latest_debug_data = {}
        self.debug_history = []
        self.entry_price = 0.0
        self.entry_atr = 0.0 # Store ATR at entry
        self.highest_price = 0.0 # For Long Trailing Stop
        self.lowest_price = 0.0 # For Short Trailing Stop
        
        if 'signals' in parameters:
            for sig_config in parameters['signals']:
                sig_type = sig_config.get('type')
                sig_id = sig_config.get('id', sig_type)
                sig_params = sig_config.get('params', {})
                
                if sig_type in self.signal_registry:
                    instance = self.signal_registry[sig_type](data, sig_params)
                    self.signal_instances[sig_id] = instance
                    self.signals.append(instance)
                    self.latest_signal_values[sig_id] = 0.0 # Initialize

    def on_data(self, index, row):
        # Sync state from broker if available
        if self.broker:
            # We need to know the symbol to get position size.
            # Assuming single symbol strategy for now.
            symbol = self.parameters.get('symbol', 'Unknown')
            positions = self.broker.get_positions()
            if symbol in positions:
                self.position = positions[symbol]['size']
            else:
                self.position = 0
            
            self.cash = self.broker.get_balance()
            
        current_price = row['Close']
        
        # 1. Update Technical Signals
        self.latest_debug_data = {}
        for sig_id, instance in self.signal_instances.items():
            if hasattr(instance, 'generate') and not isinstance(instance, EventSignal):
                self.latest_signal_values[sig_id] = instance.generate(index, row)
                if hasattr(instance, 'get_debug_data'):
                    self.latest_debug_data[sig_id] = instance.get_debug_data()
        
        # 2. Risk Management (Stop Loss / Take Profit)
        if self.position != 0:
            pct_change = (current_price - self.entry_price) / self.entry_price
            
            # LONG POSITION RISK MANAGEMENT
            if self.position > 0:
                # Fixed % Stop Loss
                if self.stop_loss_pct > 0 and pct_change <= -self.stop_loss_pct:
                    self.sell(current_price, size=self.position, timestamp=index)
                    print(f"Stop Loss (Long) Hit at {current_price} ({pct_change*100:.2f}%)")
                    return # Exit early

                # ATR Stop Loss
                if self.sl_atr_mult > 0 and self.entry_atr > 0:
                    sl_price = self.entry_price - (self.entry_atr * self.sl_atr_mult)
                    if current_price <= sl_price:
                        self.sell(current_price, size=self.position, timestamp=index)
                        print(f"Stop Loss (ATR Long) Hit at {current_price}")
                        return

                # Fixed % Take Profit
                if self.take_profit_pct > 0 and pct_change >= self.take_profit_pct:
                    self.sell(current_price, size=self.position, timestamp=index)
                    print(f"Take Profit (Long) Hit at {current_price} ({pct_change*100:.2f}%)")
                    return # Exit early

                # ATR Take Profit
                if self.tp_atr_mult > 0 and self.entry_atr > 0:
                    tp_price = self.entry_price + (self.entry_atr * self.tp_atr_mult)
                    if current_price >= tp_price:
                        self.sell(current_price, size=self.position, timestamp=index)
                        print(f"Take Profit (ATR Long) Hit at {current_price}")
                        return

            # SHORT POSITION RISK MANAGEMENT
            elif self.position < 0:
                # For shorts, pct_change is inverted. 
                # If price goes DOWN (current < entry), pct_change is negative, but we are PROFITABLE.
                # If price goes UP (current > entry), pct_change is positive, but we are LOSING.
                
                # Fixed % Stop Loss (Price goes UP)
                if self.stop_loss_pct > 0 and pct_change >= self.stop_loss_pct:
                    self.buy(current_price, size=abs(self.position), timestamp=index)
                    print(f"Stop Loss (Short) Hit at {current_price} (+{pct_change*100:.2f}%)")
                    return

                # ATR Stop Loss (Price goes UP)
                if self.sl_atr_mult > 0 and self.entry_atr > 0:
                    sl_price = self.entry_price + (self.entry_atr * self.sl_atr_mult)
                    if current_price >= sl_price:
                        self.buy(current_price, size=abs(self.position), timestamp=index)
                        print(f"Stop Loss (ATR Short) Hit at {current_price}")
                        return

                # Fixed % Take Profit (Price goes DOWN)
                if self.take_profit_pct > 0 and pct_change <= -self.take_profit_pct:
                    self.buy(current_price, size=abs(self.position), timestamp=index)
                    print(f"Take Profit (Short) Hit at {current_price} ({pct_change*100:.2f}%)")
                    return

                # ATR Take Profit (Price goes DOWN)
                if self.tp_atr_mult > 0 and self.entry_atr > 0:
                    tp_price = self.entry_price - (self.entry_atr * self.tp_atr_mult)
                    if current_price <= tp_price:
                        self.buy(current_price, size=abs(self.position), timestamp=index)
                        print(f"Take Profit (ATR Short) Hit at {current_price}")
                        return

                if self.tp_atr_mult > 0 and self.entry_atr > 0:
                    tp_price = self.entry_price - (self.entry_atr * self.tp_atr_mult)
                    if current_price <= tp_price:
                        self.buy(current_price, size=abs(self.position), timestamp=index)
                        print(f"Take Profit (ATR Short) Hit at {current_price}")
                        return

            # TRAILING STOP LOGIC
            if self.ts_activation > 0 and self.ts_trail > 0:
                if self.position > 0: # Long
                    # Update Highest Price
                    if current_price > self.highest_price:
                        self.highest_price = current_price
                    
                    # Check Activation
                    if self.highest_price >= self.entry_price * (1 + self.ts_activation):
                        # Calculate Trailing Stop Price
                        ts_price = self.highest_price * (1 - self.ts_trail)
                        
                        if current_price <= ts_price:
                            self.sell(current_price, size=self.position, timestamp=index)
                            print(f"Trailing Stop (Long) Hit at {current_price} (High: {self.highest_price})")
                            return

                elif self.position < 0: # Short
                    # Update Lowest Price
                    if current_price < self.lowest_price:
                        self.lowest_price = current_price
                    
                    # Check Activation
                    if self.lowest_price <= self.entry_price * (1 - self.ts_activation):
                        # Calculate Trailing Stop Price
                        ts_price = self.lowest_price * (1 + self.ts_trail)
                        
                        if current_price >= ts_price:
                            self.buy(current_price, size=abs(self.position), timestamp=index)
                            print(f"Trailing Stop (Short) Hit at {current_price} (Low: {self.lowest_price})")
                            return

        # 3. Evaluate Entry Conditions (Buy/Short)
        buy_signal = True
        if not self.conditions:
            buy_signal = False
        else:
            for condition in self.conditions:
                if not self._evaluate_condition(condition, current_price):
                    buy_signal = False
                    break
        
        short_signal = True
        if not self.short_conditions:
            short_signal = False
        else:
            for condition in self.short_conditions:
                if not self._evaluate_condition(condition, current_price):
                    short_signal = False
                    break

        # 4. Evaluate Exit Conditions (Sell/Cover)
        sell_signal = True
        if not self.exit_conditions:
            sell_signal = False
        else:
            for condition in self.exit_conditions:
                if not self._evaluate_condition(condition, current_price):
                    sell_signal = False
                    break
                    
        cover_signal = True
        if not self.cover_conditions:
            cover_signal = False
        else:
            for condition in self.cover_conditions:
                if not self._evaluate_condition(condition, current_price):
                    cover_signal = False
                    break
        
        # Execute Logic
        if self.position == 0:
            if buy_signal:
                self.buy(current_price, size=1000, timestamp=index)
                self.entry_price = current_price
                self.highest_price = current_price # Initialize for TS
                self._capture_atr(index)
            elif short_signal:
                self.sell(current_price, size=1000, timestamp=index) # Sell to Open
                self.entry_price = current_price
                self.lowest_price = current_price # Initialize for TS
                self._capture_atr(index)
                
        elif self.position > 0: # Long
            if sell_signal:
                self.sell(current_price, size=self.position, timestamp=index) # Sell to Close

        elif self.position < 0: # Short
            if cover_signal:
                self.buy(current_price, size=abs(self.position), timestamp=index) # Buy to Cover

    def _capture_atr(self, index):
        if self.atr_signal_id and self.atr_signal_id in self.latest_signal_values:
            self.entry_atr = self.latest_signal_values[self.atr_signal_id]
        else:
            self.entry_atr = 0.0
        
        # Store debug history
        self.debug_history.append({
            "timestamp": index.isoformat(),
            "signals": self.latest_debug_data
        })
        
        # 5. Reset Event Signals
        for sig_id, instance in self.signal_instances.items():
            if isinstance(instance, EventSignal):
                self.latest_signal_values[sig_id] = 0.0

    def _evaluate_condition(self, condition, current_price=None):
        sig_id = condition.get('signal_id')
        operator = condition.get('operator')
        threshold = condition.get('value')
        
        if sig_id not in self.latest_signal_values:
            return False
            
        val = self.latest_signal_values[sig_id]
        
        # Handle dynamic threshold
        if isinstance(threshold, str):
            if threshold == 'Close' and current_price is not None:
                threshold = current_price
            elif threshold in self.latest_signal_values:
                threshold = self.latest_signal_values[threshold]
        
        try:
            # Attempt to convert threshold to float if it's not already
            # This handles cases where threshold might be a string representation of a number
            if not isinstance(threshold, (int, float)):
                threshold = float(threshold)
        except (ValueError, TypeError):
            # If conversion fails, keep original threshold or handle as error
            # For now, we'll let the comparison below potentially fail if types are incompatible
            pass 

        res = False
        try:
            if operator == '<':
                res = val < threshold
            elif operator == '>':
                res = val > threshold
            elif operator == '==':
                res = val == threshold
            elif operator == '>=':
                res = val >= threshold
            elif operator == '<=':
                res = val <= threshold
            else:
                res = False
        except Exception as e:
            print(f"ERROR in _evaluate_condition: {e}")
            print(f"Signal: {sig_id}, Value: {val} (Type: {type(val)})")
            print(f"Threshold: {threshold} (Type: {type(threshold)})")
            # Optionally re-raise the exception if you want it to halt execution
            # raise e
            return False # Return False on error to prevent unintended trades
            
        if res:
            pass
        else:
            # Debug print disabled after testing
            # if sig_id == 'RSI' and val > 40:
            #      print(f"DEBUG: Condition Failed: {sig_id} {operator} {threshold} (Val: {val})")
            pass
        
        return res

    def on_event(self, event):
        # Update Event Signals
        for sig_id, instance in self.signal_instances.items():
            if isinstance(instance, EventSignal):
                # Accumulate or set? Set is safer for single event per step.
                val = instance.on_event(event)
                if val != 0:
                    self.latest_signal_values[sig_id] = val
