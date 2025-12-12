import pandas as pd
import numpy as np
from backend.indicators.adx import adx
from backend.indicators.atr import atr

class RegimeClassifier:
    def __init__(self, data: pd.DataFrame):
        self.data = data.copy()
        
    def calculate_indicators(self, adx_period=14, sma_period=200, atr_period=14):
        """Calculates indicators needed for classification."""
        # ADX
        self.data['adx'] = adx(self.data['High'], self.data['Low'], self.data['Close'], adx_period)
        
        # SMA 200 (Trend Direction)
        self.data['sma_200'] = self.data['Close'].rolling(window=sma_period).mean()
        
        # ATR (Volatility)
        self.data['atr'] = atr(self.data['High'], self.data['Low'], self.data['Close'], atr_period)
        self.data['atr_pct'] = self.data['atr'] / self.data['Close']
        
        return self.data
        
    def classify(self, adx_threshold=25, volatility_threshold=0.015):
        """
        Classifies each bar into a Regime.
        
        Regimes:
        - TRENDING_UP: ADX > Threshold AND Price > SMA 200
        - TRENDING_DOWN: ADX > Threshold AND Price < SMA 200
        - RANGING: ADX < Threshold
        - VOLATILE: ATR % > Volatility Threshold (Overrides others if extreme)
        """
        if 'adx' not in self.data.columns or 'atr_pct' not in self.data.columns:
            self.calculate_indicators()
            
        def get_regime(row):
            # 1. Check Volatility (Optional override, or just a tag)
            is_volatile = row['atr_pct'] > volatility_threshold
            
            # 2. Check Trend Strength
            if row['adx'] > adx_threshold:
                if row['Close'] > row['sma_200']:
                    return "TRENDING_UP"
                else:
                    return "TRENDING_DOWN"
            else:
                if is_volatile:
                    return "VOLATILE_RANGE"
                else:
                    return "QUIET_RANGE"
                    
        self.data['regime'] = self.data.apply(get_regime, axis=1)
        return self.data[['Close', 'adx', 'sma_200', 'atr_pct', 'regime']]
