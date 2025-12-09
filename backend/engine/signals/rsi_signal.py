from ..signal import Signal
import pandas as pd

class RSISignal(Signal):
    def __init__(self, data: pd.DataFrame, parameters: dict = {}):
        super().__init__(data, parameters)
        self.name = "RSI"
        self.period = int(parameters.get('rsi_period', 14))
        self.overbought = int(parameters.get('rsi_overbought', 70))
        self.oversold = int(parameters.get('rsi_oversold', 30))
        self.mode = parameters.get('mode', 'signal')  # 'signal' or 'value'
        self._calculate_indicator()

    def _calculate_indicator(self):
        # Pre-calculate RSI for the entire dataset
        close = self.data['Close']
        delta = close.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=self.period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=self.period).mean()
        rs = gain / loss
        self.data['RSI'] = 100 - (100 / (1 + rs))
        self.data['RSI'] = self.data['RSI'].fillna(50)

    def generate(self, index, row) -> float:
        val = self.data.loc[index, 'RSI']
        if isinstance(val, pd.Series):
            val = val.iloc[-1]
        current_rsi = float(val)
        self.last_rsi = current_rsi
        
        # Value Mode: Return raw RSI value (0-100)
        if self.mode == 'value':
            return current_rsi
        
        # Signal Mode (Default): Return -1/0/1 based on overbought/oversold
        if current_rsi < self.oversold:
            return 1.0 # Buy
        elif current_rsi > self.overbought:
            return -1.0 # Sell
        
        return 0.0 # Neutral

    def get_debug_data(self):
        return {
            "type": "RSI",
            "value": float(self.last_rsi) if hasattr(self, 'last_rsi') else 0.0
        }
