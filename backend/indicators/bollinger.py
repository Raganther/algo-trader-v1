import pandas as pd
import numpy as np

class BollingerBands:
    def __init__(self, period: int = 20, std_dev: float = 2.0):
        self.period = period
        self.std_dev = std_dev
        self.prices = []
        self.upper = 0.0
        self.middle = 0.0
        self.lower = 0.0
        self.ready = False

    def update(self, price: float):
        self.prices.append(price)
        if len(self.prices) > self.period:
            self.prices.pop(0)
            
        if len(self.prices) == self.period:
            self.ready = True
            series = pd.Series(self.prices)
            mean = series.mean()
            std = series.std()
            
            self.middle = mean
            self.upper = mean + (std * self.std_dev)
            self.lower = mean - (std * self.std_dev)
        else:
            self.ready = False
