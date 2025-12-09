from ..signal import Signal
import pandas as pd

class TrendSignal(Signal):
    def __init__(self, data: pd.DataFrame, parameters: dict):
        super().__init__(data, parameters)
        self.fast_period = parameters.get('fast_period', 20)
        self.slow_period = parameters.get('slow_period', 50)
        self.adx_period = parameters.get('adx_period', 14)
        self.adx_threshold = parameters.get('adx_threshold', 25) # ADX > 25 usually indicates strong trend
        
        # Pre-calculate indicators for speed
        self.data['SMA_Fast'] = self.data['Close'].rolling(window=self.fast_period).mean()
        self.data['SMA_Slow'] = self.data['Close'].rolling(window=self.slow_period).mean()
        
        # ADX Calculation (Simplified TR and DX)
        # 1. True Range
        self.data['H-L'] = self.data['High'] - self.data['Low']
        self.data['H-PC'] = abs(self.data['High'] - self.data['Close'].shift(1))
        self.data['L-PC'] = abs(self.data['Low'] - self.data['Close'].shift(1))
        self.data['TR'] = self.data[['H-L', 'H-PC', 'L-PC']].max(axis=1)
        
        # 2. Directional Movement
        self.data['UpMove'] = self.data['High'] - self.data['High'].shift(1)
        self.data['DownMove'] = self.data['Low'].shift(1) - self.data['Low']
        
        self.data['+DM'] = 0.0
        self.data.loc[(self.data['UpMove'] > self.data['DownMove']) & (self.data['UpMove'] > 0), '+DM'] = self.data['UpMove']
        
        self.data['-DM'] = 0.0
        self.data.loc[(self.data['DownMove'] > self.data['UpMove']) & (self.data['DownMove'] > 0), '-DM'] = self.data['DownMove']
        
        # 3. Smoothed
        self.data['TR14'] = self.data['TR'].rolling(window=self.adx_period).sum()
        self.data['+DM14'] = self.data['+DM'].rolling(window=self.adx_period).sum()
        self.data['-DM14'] = self.data['-DM'].rolling(window=self.adx_period).sum()
        
        # 4. DI
        self.data['+DI'] = 100 * (self.data['+DM14'] / self.data['TR14'])
        self.data['-DI'] = 100 * (self.data['-DM14'] / self.data['TR14'])
        
        # 5. DX and ADX
        self.data['DX'] = 100 * abs(self.data['+DI'] - self.data['-DI']) / (self.data['+DI'] + self.data['-DI'])
        self.data['ADX'] = self.data['DX'].rolling(window=self.adx_period).mean()

    def generate(self, index: pd.Timestamp, row: pd.Series) -> float:
        """
        Returns:
        1.0 if Strong Uptrend (ADX > Threshold AND Fast > Slow)
        -1.0 if Strong Downtrend (ADX > Threshold AND Fast < Slow)
        0.0 if Weak Trend / Ranging
        """
        try:
            current_adx = self.data.loc[index, 'ADX']
            fast_sma = self.data.loc[index, 'SMA_Fast']
            slow_sma = self.data.loc[index, 'SMA_Slow']
        except KeyError:
            return 0.0
            
        if pd.isna(current_adx) or pd.isna(fast_sma) or pd.isna(slow_sma):
            return 0.0
            
        if current_adx < self.adx_threshold:
            return 0.0 # Weak trend
            
        if fast_sma > slow_sma:
            return 1.0 # Strong Uptrend
        elif fast_sma < slow_sma:
            return -1.0 # Strong Downtrend
            
        return 0.0
