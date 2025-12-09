from backend.engine.strategy import Strategy
import pandas as pd

class SimpleSMAStrategy(Strategy):
    def __init__(self, data: pd.DataFrame, events: pd.DataFrame = None, parameters: dict = {}, initial_cash: float = 10000.0, broker=None):
        super().__init__(data, events, parameters, initial_cash, broker)
        
        # Parameters
        self.fast_period = int(parameters.get('fast_period', 10))
        self.slow_period = int(parameters.get('slow_period', 50))
        self.qty = float(parameters.get('qty', 10000.0)) # Fixed quantity for simplicity
        
        # Calculate Indicators
        self.data['sma_fast'] = self.data['Close'].rolling(window=self.fast_period).mean()
        self.data['sma_slow'] = self.data['Close'].rolling(window=self.slow_period).mean()
        
    def on_data(self, index, row):
        # Wait for warmup
        if pd.isna(row['sma_slow']):
            return
            
        # Get current position
        positions = self.broker.get_positions()
        symbol = self.parameters.get('symbol', 'Unknown')
        current_pos = positions.get(symbol)
        current_size = current_pos['size'] if current_pos else 0
        
        # Crossover Logic
        # We need previous values to detect crossover
        # Using integer index to access previous row
        if index == 0: return
        
        prev_row = self.data.iloc[index - 1]
        
        # Golden Cross (Fast crosses above Slow)
        if prev_row['sma_fast'] <= prev_row['sma_slow'] and row['sma_fast'] > row['sma_slow']:
            # Go Long
            if current_size <= 0:
                # Close Short if any
                if current_size < 0:
                    self.broker.place_order(symbol, 'buy', abs(current_size), price=row['Close'], timestamp=index)
                
                # Open Long
                self.broker.place_order(symbol, 'buy', self.qty, price=row['Close'], timestamp=index)
                
        # Death Cross (Fast crosses below Slow)
        elif prev_row['sma_fast'] >= prev_row['sma_slow'] and row['sma_fast'] < row['sma_slow']:
            # Go Short
            if current_size >= 0:
                # Close Long if any
                if current_size > 0:
                    self.broker.place_order(symbol, 'sell', abs(current_size), price=row['Close'], timestamp=index)
                
                # Open Short
                self.broker.place_order(symbol, 'sell', self.qty, price=row['Close'], timestamp=index)

    def on_event(self, event):
        pass
