from backend.engine.strategy import Strategy
from backend.indicators.bollinger import BollingerBands
from backend.indicators.rsi import RSI

class GammaScalping(Strategy):
    """
    Gamma Scalping Strategy (Proxy Implementation)
    
    Thesis: Market Makers (Dealers) dampen volatility when they are 'Long Gamma' (Stable Market).
    We assume a 'Long Gamma' regime when volatility is compressed (Low BB Width).
    In this regime, we aggressively fade moves to the Bollinger Bands (Mean Reversion).
    
    When volatility expands (High BB Width), we assume 'Short Gamma' (Instability) and stop trading.
    """
    def __init__(self, data, events, parameters, initial_cash=10000.0, broker=None):
        super().__init__(data, events, parameters, initial_cash, broker)
        self.symbol = parameters.get("symbol", "Unknown")
        self.bb_period = int(parameters.get("bb_period", 20))
        self.bb_std = float(parameters.get("bb_std", 2.0))
        self.rsi_period = int(parameters.get("rsi_period", 14))
        self.vol_threshold = float(parameters.get("vol_threshold", 0.02)) # Max BB Width % for "Stable" regime
        
        self.bb = BollingerBands(self.bb_period, self.bb_std)
        self.rsi = RSI(self.rsi_period)

    def on_data(self, index, row):
        # Update Indicators
        self.bb.update(row['Close'])
        self.rsi.update(row['Close'])
        
        if not self.bb.ready or not self.rsi.ready:
            return

        # Calculate Metrics
        upper = self.bb.upper
        lower = self.bb.lower
        mid = self.bb.middle
        rsi_val = self.rsi.value
        
        # Volatility Proxy: Band Width relative to price
        # (Upper - Lower) / Mid
        bb_width = (upper - lower) / mid
        
        # Regime Filter: Only trade in "Long Gamma" (Low Vol) environments
        is_stable_regime = bb_width < self.vol_threshold
        
        positions = self.broker.get_positions()
        pos_data = positions.get(self.symbol)
        current_pos = pos_data['size'] if pos_data else 0
        
        # Entry Logic (Mean Reversion)
        if is_stable_regime:
            # Long: Price hits Lower Band + Oversold
            if row['Close'] < lower and rsi_val < 30:
                if current_pos <= 0:
                    self.broker.close_position(self.symbol)
                    self.broker.place_order(self.symbol, "buy", 1, price=row['Close'])
            
            # Short: Price hits Upper Band + Overbought
            elif row['Close'] > upper and rsi_val > 70:
                if current_pos >= 0:
                    self.broker.close_position(self.symbol)
                    self.broker.place_order(self.symbol, "sell", 1, price=row['Close'])
        
        # Exit Logic (Revert to Mean)
        # If we are in a trade, exit at the Middle Band
        if current_pos > 0 and row['Close'] > mid:
            self.broker.close_position(self.symbol)
        elif current_pos < 0 and row['Close'] < mid:
            self.broker.close_position(self.symbol)

    def on_event(self, event):
        pass
