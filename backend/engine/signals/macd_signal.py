from ..signal import Signal
import pandas as pd

class MACDSignal(Signal):
    def __init__(self, data: pd.DataFrame, parameters: dict = {}):
        super().__init__(data, parameters)
        self.name = "MACD"
        self.fast_period = int(parameters.get('macd_fast', 12))
        self.slow_period = int(parameters.get('macd_slow', 26))
        self.signal_period = int(parameters.get('macd_signal', 9))
        self.mode = parameters.get('mode', 'crossover') # 'crossover' or 'trend'
        self._calculate_indicator()

    def _calculate_indicator(self):
        # Calculate MACD using pandas_ta or manual calculation
        # Manual for now to avoid extra dependencies if not installed
        close = self.data['Close']
        ema_fast = close.ewm(span=self.fast_period, adjust=False).mean()
        ema_slow = close.ewm(span=self.slow_period, adjust=False).mean()
        
        self.data['MACD'] = ema_fast - ema_slow
        self.data['MACD_Signal'] = self.data['MACD'].ewm(span=self.signal_period, adjust=False).mean()
        self.data['MACD_Hist'] = self.data['MACD'] - self.data['MACD_Signal']

    def generate(self, index, row) -> float:
        # Get integer location
        try:
            i = self.data.index.get_loc(index)
        except KeyError:
            return 0.0

        if i < self.slow_period:
            return 0.0

        # Use iloc for safe scalar access
        macd_current = self.data['MACD'].iloc[i]
        signal_current = self.data['MACD_Signal'].iloc[i]
        
        # Trend Mode: Return 1.0 if Bullish, -1.0 if Bearish (Sustained)
        if self.mode == 'trend':
            if macd_current > signal_current:
                # print(f"DEBUG: MACD Trend Bullish. MACD: {macd_current}, Sig: {signal_current}")
                return 1.0
            elif macd_current < signal_current:
                return -1.0
            return 0.0

        # Crossover Mode (Default): Return 1.0 only on Cross Up
        macd_prev = self.data['MACD'].iloc[i-1]
        signal_prev = self.data['MACD_Signal'].iloc[i-1]

        # Bullish: MACD crosses ABOVE Signal line
        if macd_prev < signal_prev and macd_current > signal_current:
            return 1.0
            
        # Bearish: MACD crosses BELOW Signal line
        elif macd_prev > signal_prev and macd_current < signal_current:
            return -1.0
            
        return 0.0
