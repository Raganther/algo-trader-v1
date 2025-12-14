import pandas as pd
from backend.strategies.stoch_rsi_mean_reversion import StochRSIMeanReversionStrategy
from backend.analysis.regime_quantifier import RegimeQuantifier

class RegimeGatedStoch(StochRSIMeanReversionStrategy):
    """
    A 'Sniper' version of StochRSI that only trades when the market is in a RANGING regime.
    
    Logic:
    1. Calculate Regime (Bull, Bear, Range, Volatile).
    2. If RANGING: Execute standard StochRSI Mean Reversion logic.
    3. If TRENDING or VOLATILE: 
       - Do NOT open new positions.
       - Force CLOSE existing positions (Safety First).
    """
    
    def __init__(self, data: pd.DataFrame, events: pd.DataFrame = None, parameters: dict = {}, initial_cash: float = 10000.0, broker=None):
        super().__init__(data, events, parameters, initial_cash, broker)
        
        # 1. Quantify Regimes Upfront
        # We use the same parameters as the analysis (ADX 25, SMA 50/200)
        # We could make these parameters configurable if needed.
        self.quantifier = RegimeQuantifier(self.data)
        self.regime_df = self.quantifier.quantify()
        
        # Merge regime column into main data for easy access
        self.data['regime'] = self.regime_df['regime']
        
    def on_bar(self, bar, index, full_data):
        # 1. Check Regime
        # We need to look at the regime of the *current* bar (or previous to avoid lookahead?)
        # The Quantifier uses Close, so strictly speaking, at the moment of 'on_bar' (after close),
        # we know the regime of the bar that just closed.
        
        current_regime = bar['regime']
        
        # 2. Gating Logic
        if current_regime != RegimeQuantifier.RANGING:
            # --- KILL ZONE (Trend or Volatile) ---
            
            # If we have a position, CLOSE IT immediately.
            # We don't want to hold mean reversion trades during a trend or crash.
            current_position = self.broker.get_positions().get(self.symbol, {}).get('size', 0)
            
            if current_position != 0:
                # print(f"  [Regime Gate] Closing position due to {current_regime} regime.")
                if current_position > 0:
                    self.broker.place_order(self.symbol, 'sell', abs(current_position), price=bar['Close'], timestamp=bar.name)
                else:
                    self.broker.place_order(self.symbol, 'buy', abs(current_position), price=bar['Close'], timestamp=bar.name)
            
            # Do NOT proceed to StochRSI logic
            return

        # 3. Safe Zone (Ranging) -> Execute Parent Logic
        super().on_bar(bar, index, full_data)
