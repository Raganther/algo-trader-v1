from .stoch_rsi_mean_reversion import StochRSIMeanReversionStrategy
from datetime import time
import pandas as pd
from backend.indicators.adx import adx

class StochRSIQuantStrategy(StochRSIMeanReversionStrategy):
    """
    StochRSI Mean Reversion with Quant Optimization Filters:
    1. Time Filter: Avoid Opening Range (09:30-10:00) and Close (15:50-16:00).
    2. ADX Filter: Avoid Strong Trends (ADX > 30).
    """
    
    def __init__(self, *args, **kwargs):
        # Extract parameters before super().__init__ calls generate_signals
        params = {}
        if 'parameters' in kwargs:
            params = kwargs['parameters']
        elif len(args) > 2:
            params = args[2]
            
        self.adx_period = int(params.get('adx_period', 14))
        self.adx_threshold = float(params.get('adx_threshold', 30.0))
        self.use_time_filter = params.get('use_time_filter', True)
        
        super().__init__(*args, **kwargs)
        
    def generate_signals(self, df):
        # 1. Calculate Indicators (StochRSI is done in parent, we need ADX)
        # Calculate ADX using local indicator
        adx_series = adx(df['High'], df['Low'], df['Close'], period=self.adx_period)
        
        # Join ADX to main DF
        df['adx'] = adx_series
            
        # Call Parent to generate base signals (StochRSI)
        return super().generate_signals(df)

    def on_bar(self, row, i, df):
        """
        Override on_bar to apply filters before calling parent logic.
        """
        # 1. Time Filter
        if self.use_time_filter:
            # Assuming row.name is the datetime index
            current_time = row.name.time()
            
            # Blackout: 09:30 - 10:00 (Opening Drive)
            if time(9, 30) <= current_time < time(10, 0):
                return # SKIP
                
            # Blackout: 15:50 - 16:00 (MOC Imbalance)
            if time(15, 50) <= current_time <= time(16, 0):
                # Optional: Force Close here?
                # For now, just don't enter new trades.
                return # SKIP
            
        # 2. ADX Filter (Trend Day Killer)
        # If ADX > 30, Market is Trending. Mean Reversion will fail.
        if row.get('adx', 0) > self.adx_threshold:
            return # SKIP
            
        # 3. Call Parent Logic (StochRSI Entry/Exit)
        super().on_bar(row, i, df)
