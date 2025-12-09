import pandas as pd
import numpy as np
from ..signal import Signal

class TimeRangeSignal(Signal):
    """
    Signal that identifies the High/Low range during a specific time window (e.g., Asian Session)
    and generates signals when price breaks out of this range in a subsequent window.
    """
    def __init__(self, data: pd.DataFrame, parameters: dict):
        super().__init__(data, parameters)
        self.range_start = parameters.get('range_start', "00:00") # Start of range calculation (GMT)
        self.range_end = parameters.get('range_end', "08:00")     # End of range calculation (GMT)
        self.trade_window_end = parameters.get('trade_window_end', "12:00") # Stop taking new trades after this
        self.buffer_pips = parameters.get('buffer_pips', 2)       # Buffer for breakout (in pips)
        self.pip_size = parameters.get('pip_size', 0.0001)        # Pip size (0.0001 for major pairs)
        
        # Pre-calculate ranges
        self.ranges = self._calculate_ranges()

    def _calculate_ranges(self):
        """
        Pre-calculate the High/Low for the specified time window for each day.
        Returns a DataFrame indexed by date with 'range_high' and 'range_low'.
        """
        df = self.data.copy()
        df['time'] = df.index.time
        
        # Convert string times to objects for comparison
        start_time = pd.to_datetime(self.range_start).time()
        end_time = pd.to_datetime(self.range_end).time()
        
        # Filter data within the range window
        if start_time < end_time:
            mask = (df['time'] >= start_time) & (df['time'] < end_time)
        else: # Range crosses midnight
            mask = (df['time'] >= start_time) | (df['time'] < end_time)
            
        range_data = df[mask]
        
        # Group by date to find daily high/low
        # Note: For ranges crossing midnight, we'd need more complex grouping by "session day"
        # For simple Asian session (00:00-08:00), grouping by date is fine.
        daily_ranges = range_data.groupby(range_data.index.date).agg({
            'High': 'max',
            'Low': 'min'
        })
        
        daily_ranges.columns = ['range_high', 'range_low']
        return daily_ranges

    def generate(self, index: pd.Timestamp, row: pd.Series) -> float:
        """
        Generate signal for a single candle.
        Returns:
        1.0 if Bullish Breakout
        -1.0 if Bearish Breakout
        0.0 otherwise
        """
        # 1. Check Time Window
        current_time = index.time()
        start_time = pd.to_datetime(self.range_end).time()
        stop_time = pd.to_datetime(self.trade_window_end).time()
        
        if not (start_time <= current_time < stop_time):
            return 0.0
            
        # 2. Get Range for Today
        current_date = index.date()
        if current_date not in self.ranges.index:
            return 0.0
            
        day_range = self.ranges.loc[current_date]
        range_high = day_range['range_high']
        range_low = day_range['range_low']
        
        buffer = self.buffer_pips * self.pip_size
        
        # 3. Check Breakout
        # Note: We check High/Low for breakout, but usually execute on Close or next Open.
        # If High broke the level, it's a signal.
        
        if row['High'] > (range_high + buffer):
            return 1.0
        elif row['Low'] < (range_low - buffer):
            return -1.0
            
        return 0.0

    def get_debug_data(self) -> dict:
        return {}
