import pandas as pd
import numpy as np
from backend.indicators.rsi import RSI

class StochRSI:
    def __init__(self, period: int = 14, smooth_k: int = 3, smooth_d: int = 3):
        self.period = period
        self.smooth_k = smooth_k
        self.smooth_d = smooth_d
        
        self.rsi = RSI(period)
        self.rsi_history = [] # Need history for Min/Max
        self.stoch_rsi_raw = [] # Need history for K
        self.k_values = [] # Need history for D
        
        self.k = 0.0
        self.d = 0.0
        self.ready = False

    def update(self, price: float):
        self.rsi.update(price)
        
        if not self.rsi.ready:
            return

        self.rsi_history.append(self.rsi.value)
        if len(self.rsi_history) > self.period:
            self.rsi_history.pop(0)
            
        if len(self.rsi_history) == self.period:
            min_rsi = min(self.rsi_history)
            max_rsi = max(self.rsi_history)
            
            if max_rsi == min_rsi:
                raw = 0.0 # Avoid div by zero
            else:
                raw = (self.rsi.value - min_rsi) / (max_rsi - min_rsi)
            
            self.stoch_rsi_raw.append(raw)
            if len(self.stoch_rsi_raw) > self.smooth_k:
                self.stoch_rsi_raw.pop(0)
                
            if len(self.stoch_rsi_raw) == self.smooth_k:
                k_val = (sum(self.stoch_rsi_raw) / self.smooth_k) * 100
                self.k = k_val
                
                self.k_values.append(k_val)
                if len(self.k_values) > self.smooth_d:
                    self.k_values.pop(0)
                    
                if len(self.k_values) == self.smooth_d:
                    self.d = sum(self.k_values) / self.smooth_d
                    self.ready = True
