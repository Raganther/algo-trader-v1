import pandas as pd
import numpy as np
from backend.engine.strategy import Strategy
from backend.analysis.regime_classifier import RegimeClassifier
from backend.strategies.stoch_rsi_mean_reversion import StochRSIMeanReversionStrategy
from backend.strategies.donchian_breakout import DonchianBreakoutStrategy

class MockBroker:
    """Captures orders from sub-strategies."""
    def __init__(self):
        self.orders = []
        self.positions = {} 
        self.equity = 100000.0

    def place_order(self, symbol, side, qty=None, quantity=None, **kwargs):
        if qty is None: qty = quantity
        if qty is None: return None
        self.orders.append({'symbol': symbol, 'side': side, 'qty': qty, 'kwargs': kwargs})
        return True

    def get_positions(self): return self.positions
    def get_equity(self): return self.equity
    def clear_orders(self): self.orders = []
    def set_position(self, symbol, size, price):
        self.positions[symbol] = {'size': size, 'avg_price': price}

class HybridRegimeV2(Strategy):
    def __init__(self, data: pd.DataFrame, events: pd.DataFrame = None, parameters: dict = {}, initial_cash: float = 10000.0, broker=None):
        super().__init__(data, events, parameters, initial_cash, broker)
        
        self.symbol = parameters.get('symbol', 'Unknown')
        
        # 1. Classify Regimes Upfront
        classifier = RegimeClassifier(self.data)
        # Use default thresholds (ADX 25)
        self.regime_data = classifier.classify(adx_threshold=25)
        self.data['regime'] = self.regime_data['regime']
        
        # 2. Initialize Sub-Strategies
        self.stoch_broker = MockBroker()
        self.donch_broker = MockBroker()
        
        # StochRSI (Range)
        stoch_params = parameters.copy()
        stoch_params['rsi_period'] = 7 # Champion Config
        self.range_strategy = StochRSIMeanReversionStrategy(data, events, stoch_params, initial_cash, self.stoch_broker)
        
        # Donchian (Trend)
        donch_params = parameters.copy()
        donch_params['entry_period'] = 20
        donch_params['exit_period'] = 10
        self.trend_strategy = DonchianBreakoutStrategy(data, events, donch_params, initial_cash, self.donch_broker)
        
        self.bar_counter = 0
        self.current_regime = None

    def on_data(self, index, row):
        if self.bar_counter >= len(self.data): return
        
        # Get Current Regime
        # Note: We must use the PREVIOUS bar's regime to avoid lookahead bias?
        # Actually, ADX/SMA are calculated on Close. So we know the regime at the Close of the bar.
        # But we trade at the Close (or next Open). 
        # For simplicity, we use the current bar's regime to decide logic for *this* bar.
        
        regime = row['regime'] # Calculated by Classifier
        
        # Map Regime to Strategy
        # TRENDING_UP / TRENDING_DOWN -> Trend Strategy
        # RANGING / VOLATILE -> Range Strategy
        
        if 'TRENDING' in regime:
            active_strategy = self.trend_strategy
            active_broker = self.donch_broker
            inactive_broker = self.stoch_broker
            regime_type = 'trend'
        else:
            active_strategy = self.range_strategy
            active_broker = self.stoch_broker
            inactive_broker = self.donch_broker
            regime_type = 'range'
            
        # Handle Regime Switch (Close Positions)
        real_positions = self.broker.get_positions()
        real_pos = real_positions.get(self.symbol)
        real_size = real_pos['size'] if real_pos else 0
        
        if self.current_regime and self.current_regime != regime_type:
            # Regime Changed! Close everything to start fresh.
            if real_size != 0:
                side = 'sell' if real_size > 0 else 'buy'
                self.broker.place_order(self.symbol, side, abs(real_size), price=row['Close'])
                real_size = 0
                
        self.current_regime = regime_type
        
        # Sync Mock Brokers
        active_broker.set_position(self.symbol, real_size, row['Close'])
        inactive_broker.set_position(self.symbol, 0, 0)
        
        active_broker.clear_orders()
        inactive_broker.clear_orders()
        
        # Step Active Strategy
        # We need to call on_data (or on_bar depending on implementation)
        # StochRSI uses on_data(index, row)
        # Donchian uses on_data(index, row)
        
        # IMPORTANT: We must update the internal state of BOTH strategies so indicators/logic track correctly,
        # even if we ignore the signals from the inactive one.
        # But for efficiency and logic isolation, usually we only step the active one.
        # However, indicators like "Highest High" (Donchian) need to track history.
        # Since indicators are pre-calculated in __init__, we are safe on that front.
        # But state variables (like trailing stops) might need care.
        # For now, we step ONLY the active strategy.
        
        active_strategy.on_data(index, row)
        
        # Execute Orders
        for order in active_broker.orders:
            self.broker.place_order(
                order['symbol'], 
                order['side'], 
                order['qty'], 
                **order['kwargs']
            )
            
        self.bar_counter += 1

    def on_event(self, event): pass
