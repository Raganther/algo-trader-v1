from ..signal import Signal
import pandas as pd

class SMASignal(Signal):
    def __init__(self, data: pd.DataFrame, parameters: dict = {}):
        super().__init__(data, parameters)
        self.name = "SMA"
        self.fast_period = int(parameters.get('fast_period', 10))
        self.slow_period = int(parameters.get('slow_period', 30))
        self._calculate_indicator()

    def _calculate_indicator(self):
        # Pre-calculate indicators using pandas
        self.sma_fast = self.data['Close'].rolling(window=self.fast_period).mean()
        self.sma_slow = self.data['Close'].rolling(window=self.slow_period).mean()

    def generate(self, index, row) -> float:
        # Get integer location
        try:
            i = self.data.index.get_loc(index)
        except KeyError:
            return 0.0

        # We need enough data
        if i < self.slow_period:
            return 0.0

        # Use iloc for safe scalar access
        current_fast = self.sma_fast.iloc[i]
        current_slow = self.sma_slow.iloc[i]
        
        if isinstance(current_fast, pd.Series):
            current_fast = current_fast.iloc[-1]
        if isinstance(current_slow, pd.Series):
            current_slow = current_slow.iloc[-1]
            
        # Store for debug
        self.last_fast = current_fast
        self.last_slow = current_slow
        self.last_value = current_slow # Default value is slow SMA
        
        # Check mode
        mode = self.parameters.get('mode', 'crossover')
        
        if mode == 'value':
            # Return the Slow SMA value (usually the trend baseline)
            return float(current_slow)
        
        # Default: Crossover Logic
        prev_fast = self.sma_fast.iloc[i - 1]
        prev_slow = self.sma_slow.iloc[i - 1]

        if prev_fast < prev_slow and current_fast > current_slow:
            return 1.0 # Bullish Crossover (Buy)
        elif prev_fast > prev_slow and current_fast < current_slow:
            return -1.0 # Bearish Crossover (Sell)
            
        return 0.0 # Neutral

    def get_debug_data(self):
        # Return the values used for the last calculation
        # We need to access the *last accessed* index, but generate() doesn't store state.
        # However, CompositeStrategy calls generate() right before get_debug_data().
        # So we can store the last calculated values in self.
        return {
            "type": "SMA",
            "fast": float(self.last_fast) if hasattr(self, 'last_fast') else 0.0,
            "slow": float(self.last_slow) if hasattr(self, 'last_slow') else 0.0,
            "value": float(self.last_value) if hasattr(self, 'last_value') else 0.0
        }
