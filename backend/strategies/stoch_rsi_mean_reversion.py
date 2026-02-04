from backend.engine.strategy import Strategy
from backend.indicators.stoch_rsi import StochRSI
from backend.indicators.adx import adx
from backend.indicators.atr import atr
import pandas as pd

class StochRSIMeanReversionStrategy(Strategy):
    def __init__(self, data, events, parameters, initial_cash=10000.0, broker=None):
        super().__init__(data, events, parameters, initial_cash, broker)
        
        # Extract Parameters with Defaults
        self.rsi_period = int(parameters.get('rsi_period', 14))
        self.stoch_period = int(parameters.get('stoch_period', 14))
        self.k_period = int(parameters.get('k_period', 3))
        self.d_period = int(parameters.get('d_period', 3))
        self.overbought = float(parameters.get('overbought', 80))
        self.oversold = float(parameters.get('oversold', 20))
        self.adx_threshold = float(parameters.get('adx_threshold', 20))
        self.dynamic_adx = parameters.get('dynamic_adx', True) # Default to True for backward compatibility
        self.position_size = float(parameters.get('position_size', 100000.0))
        self.sl_atr = float(parameters.get('sl_atr', 3.0))
        
        self.skip_adx_filter = parameters.get('skip_adx_filter', False)
        self.atr_col = parameters.get('atr_col', 'atr')
        self.symbol = parameters.get('symbol', 'Unknown')
        
        # State
        self.in_oversold_zone = False
        self.in_overbought_zone = False
        self.bar_index = 0
        self.current_sl = None
        
        self.generate_signals(self.data)

    def generate_signals(self, df: pd.DataFrame):
        # 1. Calculate Indicators Iteratively
        stoch = StochRSI(self.rsi_period, self.stoch_period, self.k_period, self.d_period)
        k_values = []
        d_values = []
        
        for price in df['Close']:
            stoch.update(price)
            k_values.append(stoch.k if stoch.ready else None)
            d_values.append(stoch.d if stoch.ready else None)
            
        adx_series = adx(df['High'], df['Low'], df['Close'], 14)
        atr_series = atr(df['High'], df['Low'], df['Close'], 14)
        
        # Add to DataFrame
        df['k'] = k_values
        df['d'] = d_values
        df['adx'] = adx_series
        df[self.atr_col] = atr_series
        
        # Fill NaNs for safety
        df['k'] = df['k'].fillna(50)
        df['d'] = df['d'].fillna(50)
        
        return df

    def on_data(self, index, row):
        # Delegate to on_bar logic
        # We need the full dataframe for indicators, which is self.data
        # 'index' is the DataFrame TimeSeries index - use bar_index for integer position
        self.on_bar(row, self.bar_index, self.data)
        self.bar_index += 1

    def on_event(self, event):
        # No event handling logic for now
        pass

    def on_bar(self, row, i, df):
        # Skip if not enough data (use passed index, not self.bar_index for paper trading)
        if i < 50: return

        current_k = row['k']
        # Use .iloc for previous row access using passed integer position
        prev_k = df.iloc[i-1]['k']
        current_adx = row['adx']

        # Print every bar for monitoring (FORWARD TESTING VISIBILITY)
        print(f"[{row.name}] {self.symbol} ${row['Close']:.2f} | K: {current_k:.1f} (prev: {prev_k:.1f}) | ADX: {current_adx:.1f}")

        # Regime Filter: Only trade if Market is Ranging (ADX < Threshold)
        # Skip this check when called from HybridRegime (which already filtered by ADX)
        if not self.skip_adx_filter:
            # --- Adaptive Logic ---
            if self.dynamic_adx:
                # Calculate ATR % (Volatility)
                # atr_val is already calculated in generate_signals
                atr_val = row[self.atr_col]
                close_price = row['Close']
                
                if close_price > 0:
                    atr_pct = (atr_val / close_price) * 100
                else:
                    atr_pct = 0
                    
                # Determine Threshold based on Volatility
                # If Volatility is High (> 0.12%), be Defensive (Threshold 20)
                # If Volatility is Low (<= 0.12%), be Aggressive (Threshold 30)
                if atr_pct > 0.12:
                    dynamic_threshold = 20
                else:
                    dynamic_threshold = 30
                    
                # Use the dynamic threshold
                if current_adx > dynamic_threshold:
                    # Market is trending too strongly for the current regime
                    return
            else:
                # Static Threshold (Strict Filter)
                if current_adx > self.adx_threshold:
                    return

        # 0. Check Stop Loss (Priority)
        if self.position == 'long' and self.current_sl:
            if row['Low'] <= self.current_sl:
                # SL Hit
                pos = self.broker.get_positions().get(self.symbol)
                qty = pos['size'] if pos else 0
                self.sell(price=self.current_sl, size=qty, timestamp=i)
                self.position = 0
                self.current_sl = None
                return # Exit logic done

        elif self.position == 'short' and self.current_sl:
            if row['High'] >= self.current_sl:
                # SL Hit
                pos = self.broker.get_positions().get(self.symbol)
                qty = abs(pos['size']) if pos else 0
                self.buy(price=self.current_sl, size=qty, timestamp=i)
                self.position = 0
                self.current_sl = None
                return # Exit logic done

        # Entry Logic
        if self.position == 0: # 0 means flat
            # Long Setup
            if prev_k < self.oversold:
                self.in_oversold_zone = True
            
            if self.in_oversold_zone and current_k > 50:
                # Dynamic Sizing
                equity = self.broker.get_equity()
                risk_amt = equity * 0.02 # 2% Risk
                atr_val = row[self.atr_col]
                stop_dist = atr_val * self.sl_atr
                
                if stop_dist > 0:
                    size = risk_amt / stop_dist
                    
                    # Cap to 1x leverage (position value can't exceed equity)
                    max_size = equity / row['Close']
                    size = min(size, max_size)
                    size = round(size, 4)
                    
                    self.current_sl = row['Close'] - stop_dist
                    result = self.buy(price=row['Close'], size=size, timestamp=i, stop_loss=self.current_sl)
                    # Only update position state if order was actually executed
                    if result is not None:
                        self.in_oversold_zone = False 
                        self.position = 'long'
                
            if current_k > 50:
                self.in_oversold_zone = False
 
            # Short Setup
            if prev_k > self.overbought:
                self.in_overbought_zone = True
                
            if self.in_overbought_zone and current_k < 50:
                # Dynamic Sizing
                equity = self.broker.get_equity()
                risk_amt = equity * 0.02
                atr_val = row[self.atr_col]
                stop_dist = atr_val * self.sl_atr
                
                if stop_dist > 0:
                    size = risk_amt / stop_dist
                    
                    # Cap to 1x leverage (position value can't exceed equity)
                    max_size = equity / row['Close']
                    size = min(size, max_size)
                    size = round(size, 4)
                    
                    self.current_sl = row['Close'] + stop_dist
                    result = self.sell(price=row['Close'], size=size, timestamp=i, stop_loss=self.current_sl)
                    # Only update position state if order was actually executed
                    if result is not None:
                        self.in_overbought_zone = False
                        self.position = 'short'
                
            if current_k < 50:
                self.in_overbought_zone = False

        # Exit Logic (Signal Based)
        elif self.position == 'long':
            # Get current size to close
            pos = self.broker.get_positions().get(self.symbol)
            qty = pos['size'] if pos else 0
            
            if current_k > self.overbought:
                self.sell(price=row['Close'], size=qty, timestamp=i) 
                self.position = 0
                self.current_sl = None
                
        elif self.position == 'short':
            pos = self.broker.get_positions().get(self.symbol)
            qty = abs(pos['size']) if pos else 0
            
            if current_k < self.oversold:
                self.buy(price=row['Close'], size=qty, timestamp=i) 
                self.position = 0
                self.current_sl = None
