from ..signal import Signal
import pandas as pd
import numpy as np

class SupportResistanceSignal(Signal):
    def __init__(self, data: pd.DataFrame, parameters: dict):
        super().__init__(data, parameters)
        self.window = parameters.get('window', 20) # Lookback for pivots
        self.tolerance_pct = parameters.get('tolerance', 0.005) # 0.5% tolerance for "near" a level
        
        # Pre-calculate all levels once (OPTIMIZATION)
        print(f"Pre-calculating S/R levels with window={self.window}...")
        self.levels_df = self._calculate_all_levels()
        print(f"Found {len(self.levels_df)} support/resistance levels")
        
        # Initialize for debug
        self.last_supports = []
        self.last_resistances = []

    def _calculate_all_levels(self):
        """
        Pre-calculate all support and resistance levels once.
        Returns DataFrame with columns: date, level, type
        """
        levels = []
        
        # We need to scan through the data to find pivot points
        # A pivot is valid only if we have enough data around it
        for i in range(self.window, len(self.data) - self.window):
            window_slice = self.data.iloc[i-self.window : i+self.window+1]
            center_low = self.data.iloc[i]['Low']
            center_high = self.data.iloc[i]['High']
            center_date = self.data.index[i]
            
            # Check if this is a pivot low (support)
            if center_low == window_slice['Low'].min():
                levels.append({
                    'date': center_date,
                    'level': center_low,
                    'type': 'support'
                })
            
            # Check if this is a pivot high (resistance)
            if center_high == window_slice['High'].max():
                levels.append({
                    'date': center_date,
                    'level': center_high,
                    'type': 'resistance'
                })
        
        return pd.DataFrame(levels) if levels else pd.DataFrame(columns=['date', 'level', 'type'])

    def generate(self, index: pd.Timestamp, row: pd.Series) -> float:
        """
        Returns:
        1.0 if Price is near Support (Buy)
        -1.0 if Price is near Resistance (Sell)
        0.0 otherwise
        """
        current_price = row['Close']
        
        # Get recent levels (only look at levels that occurred before current candle)
        recent_levels = self.levels_df[self.levels_df['date'] <= index]
        
        if recent_levels.empty:
            return 0.0
        
        # Get the most recent levels (last 20 levels)
        recent_levels = recent_levels.tail(20)
        
        # Check if near support
        supports = recent_levels[recent_levels['type'] == 'support']['level'].values
        for level in supports:
            if abs(current_price - level) / current_price <= self.tolerance_pct:
                self.last_supports = supports.tolist()
                self.last_resistances = recent_levels[recent_levels['type'] == 'resistance']['level'].values.tolist()
                return 1.0
        
        # Check if near resistance
        resistances = recent_levels[recent_levels['type'] == 'resistance']['level'].values
        for level in resistances:
            if abs(current_price - level) / current_price <= self.tolerance_pct:
                self.last_supports = supports.tolist()
                self.last_resistances = resistances.tolist()
                return -1.0
        
        # Store for debug
        self.last_supports = supports.tolist()
        self.last_resistances = resistances.tolist()
        
        return 0.0

    def get_debug_data(self) -> dict:
        # We need to re-calculate or store the levels found in 'generate'.
        # Since 'generate' is called per step, we can store the last found levels in self.
        # However, 'generate' doesn't save them to self currently.
        # Let's update 'generate' to save them to self.last_supports/resistances
        return {
            "supports": getattr(self, 'last_supports', []),
            "resistances": getattr(self, 'last_resistances', [])
        }
