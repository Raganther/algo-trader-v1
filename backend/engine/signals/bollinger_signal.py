from ..signal import Signal
import pandas as pd

class BollingerSignal(Signal):
    def __init__(self, data: pd.DataFrame, parameters: dict = {}):
        super().__init__(data, parameters)
        self.name = "Bollinger"
        self.period = int(parameters.get('bb_period', 20))
        self.std_dev = float(parameters.get('bb_std', 2.0))
        self._calculate_indicator()

    def _calculate_indicator(self):
        # Pre-calculate Bollinger Bands
        close = self.data['Close']
        self.data['BB_Middle'] = close.rolling(window=self.period).mean()
        std = close.rolling(window=self.period).std()
        self.data['BB_Upper'] = self.data['BB_Middle'] + (std * self.std_dev)
        self.data['BB_Lower'] = self.data['BB_Middle'] - (std * self.std_dev)

    def generate(self, index, row) -> float:
        # Get integer location
        try:
            i = self.data.index.get_loc(index)
        except KeyError:
            return 0.0

        if i < self.period:
            return 0.0

        # Use iloc for safe scalar access
        price = row['Close']
        upper = self.data['BB_Upper'].iloc[i]
        lower = self.data['BB_Lower'].iloc[i]
        
        # Mean Reversion Logic
        # Buy when price touches/crosses below Lower Band (Oversold)
        if price < lower:
            return 1.0
            
        # Sell when price touches/crosses above Upper Band (Overbought)
        elif price > upper:
            return -1.0
            
        return 0.0
