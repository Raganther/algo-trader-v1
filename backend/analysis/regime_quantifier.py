import pandas as pd
import numpy as np
from backend.indicators.adx import adx
from backend.indicators.atr import atr
from backend.indicators.sma import sma

class RegimeQuantifier:
    """
    Quantifies Market Regimes based on Trend Strength (ADX), 
    Trend Direction (SMA Alignment), and Volatility (ATR).
    """
    
    # Enum Constants
    BULL_TREND = "BULL_TREND"
    BEAR_TREND = "BEAR_TREND"
    RANGING = "RANGING"
    VOLATILE = "VOLATILE"
    
    def __init__(self, data: pd.DataFrame):
        self.data = data.copy()
        
    def quantify(self, adx_period=14, adx_threshold=25, sma_fast=50, sma_slow=200, atr_period=14, vol_multiplier=1.5):
        """
        Classifies each bar into a Regime.
        
        Logic:
        1. VOLATILE: Current ATR > (Average ATR * vol_multiplier)
        2. BULL_TREND: Price > SMA_Fast > SMA_Slow AND ADX > Threshold
        3. BEAR_TREND: Price < SMA_Fast < SMA_Slow AND ADX > Threshold
        4. RANGING: Everything else
        """
        # 1. Calculate Indicators
        # ADX
        self.data['adx'] = adx(self.data['High'], self.data['Low'], self.data['Close'], adx_period)
        
        # SMAs
        self.data['sma_fast'] = sma(self.data['Close'], sma_fast)
        self.data['sma_slow'] = sma(self.data['Close'], sma_slow)
        
        # ATR & Volatility Baseline
        self.data['atr'] = atr(self.data['High'], self.data['Low'], self.data['Close'], atr_period)
        # We use a longer rolling average of ATR to establish "Normal Volatility"
        self.data['atr_avg'] = self.data['atr'].rolling(window=100).mean()
        
        # 2. Vectorized Classification
        # Initialize with RANGING (Default)
        self.data['regime'] = self.RANGING
        
        # Conditions
        c_bull = (
            (self.data['Close'] > self.data['sma_fast']) & 
            (self.data['sma_fast'] > self.data['sma_slow']) & 
            (self.data['adx'] > adx_threshold)
        )
        
        c_bear = (
            (self.data['Close'] < self.data['sma_fast']) & 
            (self.data['sma_fast'] < self.data['sma_slow']) & 
            (self.data['adx'] > adx_threshold)
        )
        
        c_volatile = (
            self.data['atr'] > (self.data['atr_avg'] * vol_multiplier)
        )
        
        # Apply Logic (Order matters: Volatile overrides Trend? Or Trend overrides Volatile?)
        # Plan says: Volatile overrides Trend.
        # Let's apply Trend first, then overwrite with Volatile.
        
        self.data.loc[c_bull, 'regime'] = self.BULL_TREND
        self.data.loc[c_bear, 'regime'] = self.BEAR_TREND
        
        # Overwrite with Volatile (Safety First)
        self.data.loc[c_volatile, 'regime'] = self.VOLATILE
        
        return self.data[['Close', 'adx', 'sma_fast', 'sma_slow', 'atr', 'regime']]
