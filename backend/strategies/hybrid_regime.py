import pandas as pd
import numpy as np
from backend.engine.strategy import Strategy
from backend.indicators.adx import adx
from backend.indicators.sma import sma
from backend.strategies.stoch_rsi_mean_reversion import StochRSIMeanReversionStrategy
from backend.strategies.donchian_breakout import DonchianBreakoutStrategy

class MockBroker:
    """
    A dummy broker that captures orders from sub-strategies but doesn't execute them.
    The parent strategy inspects these orders to decide whether to execute real trades.
    """
    def __init__(self):
        self.orders = []
        self.positions = {} # symbol -> {'size': 0, 'avg_price': 0}
        self.equity = 100000.0 # Dummy equity

    def place_order(self, symbol, side, qty=None, quantity=None, **kwargs):
        if qty is None: qty = quantity
        if qty is None: return None
        
        # Record the order request
        order = {
            'symbol': symbol,
            'side': side,
            'qty': qty,
            'kwargs': kwargs
        }
        self.orders.append(order)
        return True # Pretend success

    def get_positions(self):
        return self.positions

    def get_equity(self):
        return self.equity
        
    def get_balance(self):
        return self.equity

    def clear_orders(self):
        self.orders = []
        
    def set_position(self, symbol, size, price):
        """Allow parent to sync mock position with real position"""
        self.positions[symbol] = {'size': size, 'avg_price': price}


class HybridRegimeStrategy(Strategy):
    def __init__(self, data: pd.DataFrame, events: pd.DataFrame = None, parameters: dict = {}, initial_cash: float = 10000.0, broker=None):
        super().__init__(data, events, parameters, initial_cash, broker)
        
        # Parameters
        self.adx_period = int(parameters.get('adx_period', 14))
        self.adx_threshold = float(parameters.get('adx_threshold', 30))
        self.symbol = parameters.get('symbol', 'Unknown')
        
        # Calculate Regime Indicator (ADX)
        # Note: We calculate on the full dataset upfront
        self.data['regime_adx'] = adx(self.data['High'], self.data['Low'], self.data['Close'], self.adx_period)
        
        # Initialize Mock Brokers for Sub-Strategies
        self.stoch_broker = MockBroker()
        self.donch_broker = MockBroker()
        
        # Initialize Sub-Strategies
        # We pass parameters.copy() to avoid side effects
        
        # StochRSI Setup
        stoch_params = parameters.copy()
        stoch_params['atr_col'] = 'atr_stoch'
        stoch_params['skip_adx_filter'] = True # We handle regime filtering
        self.mean_reversion = StochRSIMeanReversionStrategy(data, events, stoch_params, initial_cash, self.stoch_broker)
        
        # Donchian Setup
        donch_params = parameters.copy()
        donch_params['atr_col'] = 'atr_donch'
        self.trend_following = DonchianBreakoutStrategy(data, events, donch_params, initial_cash, self.donch_broker)
        
        # State
        self.bar_counter = 0
        self.current_regime = None # 'stoch' or 'donchian'
        
    def on_data(self, index, row):
        if self.bar_counter >= len(self.data):
            return

        # 1. Get Enriched Data
        enriched_row = self.data.iloc[self.bar_counter]
        current_adx = enriched_row['regime_adx']
        bar_idx = self.bar_counter
        self.bar_counter += 1
        
        if pd.isna(current_adx):
            return

        # 2. Determine Regime
        is_trending = current_adx > self.adx_threshold
        new_regime = 'donchian' if is_trending else 'stoch'
        
        # --- Advanced Filters (Phase 1) ---
        
        # A. Seasonality (Time-Based)
        # We need the timestamp of the current bar
        current_time = enriched_row.name # Assuming index is DatetimeIndex
        if not isinstance(current_time, pd.Timestamp):
            # Try to get from column if index is int
            if 'Date' in enriched_row:
                current_time = enriched_row['Date']
            else:
                # Fallback: Can't filter by time if we don't have it
                current_time = None
                
        allowed_to_trade = True
        force_close = False
        
        if current_time:
            # 1. No-Trade Zone: Open (09:30 - 10:00)
            # We want to avoid the first 30 mins of the session
            # Assuming data is in ET or market time. 
            # If using Alpaca data, it's usually UTC. We need to be careful.
            # Runner converts to market time? Let's assume the index is correct for now.
            # Actually, let's check the hour/minute directly.
            
            # Convert to ET if it's UTC (Alpaca default)
            # For simplicity in this iteration, we'll assume the backtester handles TZ or we check relative time.
            # But wait, 'enriched_row.name' from backtester is usually the index.
            
            # Let's define market open as 9:30.
            # If we just check time:
            t = current_time.time()
            
            # 09:30 - 10:00 ET
            if (t.hour == 9 and t.minute >= 30) or (t.hour == 10 and t.minute < 0): 
                # Wait, 9:30-10:00 is hour 9, min >= 30.
                allowed_to_trade = False
                
            # 2. Hard Close: 15:50 - 16:00 ET
            if t.hour == 15 and t.minute >= 50:
                allowed_to_trade = False
                force_close = True
                
        # B. VIX Filter
        # If VIX is too low (< 12), volatility is too compressed for mean reversion.
        if 'vix_close' in enriched_row:
            vix = enriched_row['vix_close']
            if vix < 12:
                allowed_to_trade = False
                
        # ----------------------------------
            
        # ----------------------------------
        
        # 3. Handle Regime Transition (Close positions if regime changes OR Force Close)
        # We only hold one position at a time for the symbol
        real_positions = self.broker.get_positions()
        real_pos = real_positions.get(self.symbol)
        real_size = real_pos['size'] if real_pos else 0
        
        # Force Close Logic (Seasonality)
        if force_close and real_size != 0:
             if real_size > 0:
                 self.broker.place_order(self.symbol, 'sell', abs(real_size), price=enriched_row['Close'])
             else:
                 self.broker.place_order(self.symbol, 'buy', abs(real_size), price=enriched_row['Close'])
             real_size = 0
             
        # Regime Change Logic
        elif self.current_regime and self.current_regime != new_regime:
            if real_size != 0:
                # Close existing position because regime changed
                if real_size > 0:
                    self.broker.place_order(self.symbol, 'sell', abs(real_size), price=enriched_row['Close'])
                else:
                    self.broker.place_order(self.symbol, 'buy', abs(real_size), price=enriched_row['Close'])
                real_size = 0 # We are now flat
        
        self.current_regime = new_regime
        
        # 4. Sync Mock Brokers with Real State
        # Both strategies need to know the current position to manage it or open new ones
        # But crucially, we only want the ACTIVE strategy to "see" the position if it owns it.
        # If we are flat, both see 0.
        
        if new_regime == 'stoch':
            self.stoch_broker.set_position(self.symbol, real_size, enriched_row['Close']) # Approx price
            self.donch_broker.set_position(self.symbol, 0, 0) # Donchian thinks it's flat
        else:
            self.donch_broker.set_position(self.symbol, real_size, enriched_row['Close'])
            self.stoch_broker.set_position(self.symbol, 0, 0) # Stoch thinks it's flat
            
        # Clear previous mock orders
        self.stoch_broker.clear_orders()
        self.donch_broker.clear_orders()
        
        # 5. Step Sub-Strategies (Generate Signals)
        # We pass the sub-strategy's OWN data row to ensure it has its specific indicators
        
        # Step StochRSI
        stoch_row = self.mean_reversion.data.iloc[bar_idx]
        self.mean_reversion.on_bar(stoch_row, bar_idx, self.mean_reversion.data)
        
        # Step Donchian
        donch_row = self.trend_following.data.iloc[bar_idx]
        self.trend_following.on_bar(donch_row, bar_idx, self.trend_following.data)
        
        # 6. Execute Signals from ACTIVE Regime
        # Only if allowed by filters
        if allowed_to_trade:
            if new_regime == 'stoch':
                self._process_orders(self.stoch_broker.orders)
            else:
                self._process_orders(self.donch_broker.orders)
            
    def _process_orders(self, orders):
        """Execute orders from the active sub-strategy"""
        for order in orders:
            # --------------------------------
            
            # --------------------------------
            
            # Pass through to real broker
            self.broker.place_order(
                order['symbol'], 
                order['side'], 
                order['qty'], 
                **order['kwargs']
            )

    def on_event(self, event):
        pass
