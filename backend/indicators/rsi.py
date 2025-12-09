import pandas as pd
import numpy as np

class RSI:
    def __init__(self, period: int = 14):
        self.period = period
        self.gains = []
        self.losses = []
        self.avg_gain = 0.0
        self.avg_loss = 0.0
        self.value = 50.0 # Default neutral
        self.ready = False
        self.prev_price = None

    def update(self, price: float):
        if self.prev_price is None:
            self.prev_price = price
            return

        change = price - self.prev_price
        self.prev_price = price
        
        gain = max(change, 0)
        loss = max(-change, 0)
        
        if not self.ready:
            self.gains.append(gain)
            self.losses.append(loss)
            
            if len(self.gains) == self.period:
                self.avg_gain = sum(self.gains) / self.period
                self.avg_loss = sum(self.losses) / self.period
                self.ready = True
                self._calculate()
        else:
            # Wilder's Smoothing
            self.avg_gain = ((self.avg_gain * (self.period - 1)) + gain) / self.period
            self.avg_loss = ((self.avg_loss * (self.period - 1)) + loss) / self.period
            self._calculate()

    def _calculate(self):
        if self.avg_loss == 0:
            self.value = 100.0
        else:
            rs = self.avg_gain / self.avg_loss
            self.value = 100 - (100 / (1 + rs))

def rsi(series: pd.Series, period: int = 14) -> pd.Series:
    """
    Vectorized RSI Calculation (Wilder's Smoothing)
    """
    delta = series.diff()
    gain = (delta.where(delta > 0, 0)).fillna(0)
    loss = (-delta.where(delta < 0, 0)).fillna(0)
    
    avg_gain = gain.ewm(alpha=1/period, min_periods=period, adjust=False).mean()
    avg_loss = loss.ewm(alpha=1/period, min_periods=period, adjust=False).mean()
    
    rs = avg_gain / avg_loss
    rsi_val = 100 - (100 / (1 + rs))
    return rsi_val
