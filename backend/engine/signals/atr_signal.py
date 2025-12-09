from ..signal import Signal
import pandas as pd
import numpy as np

class ATRSignal(Signal):
    def __init__(self, data: pd.DataFrame, parameters: dict = {}):
        super().__init__(data, parameters)
        self.name = "ATR"
        self.period = int(parameters.get('atr_period', 14))
        self._calculate_indicator()

    def _calculate_indicator(self):
        high = self.data['High']
        low = self.data['Low']
        close = self.data['Close']
        
        # Calculate True Range
        tr1 = high - low
        tr2 = abs(high - close.shift(1))
        tr3 = abs(low - close.shift(1))
        
        tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
        
        # Calculate ATR (Rolling Mean of TR)
        # Standard ATR uses Wilder's Smoothing, but SMA is often close enough for basic use.
        # Let's use Wilder's if possible, or simple rolling mean. 
        # Using simple rolling mean for simplicity and speed without extra deps.
        self.data['ATR'] = tr.rolling(window=self.period).mean()
        
        # Fill NaN
        self.data['ATR'] = self.data['ATR'].bfill()

    def generate(self, index, row) -> float:
        return self.data.loc[index, 'ATR']
