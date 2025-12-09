
import pandas as pd
import numpy as np
from backend.engine.strategy import Strategy
from backend.indicators.rsi import RSI

class AGoldenCrossStrategy(Strategy):
    """
    Create a Golden Cross strategy
    """
    
    def __init__(self, data: pd.DataFrame, events: pd.DataFrame = None, parameters: dict = {}, initial_cash: float = 10000.0, broker=None):
        super().__init__(data, events, parameters, initial_cash, broker)
        self.symbol = parameters.get('symbol', 'Unknown')
        
        # Parameters
        self.rsi_period = int(parameters.get('rsi_period', 14))
        self.buy_threshold = float(parameters.get('buy_threshold', 30))
        self.sell_threshold = float(parameters.get('sell_threshold', 70))
        self.stop_loss_pct = float(parameters.get('stop_loss_pct', 0.02))
        
        # Indicators
        self.rsi = RSI(self.rsi_period)
        
        # Pre-calculate indicators
        self.generate_signals(self.data)

    def generate_signals(self, data):
        """
        Calculate indicators for the entire dataset.
        """
        # Calculate RSI
        # We use the vectorized rsi function if available, or loop
        # For simplicity in this template, we'll assume vectorized or simple calculation
        # But our RSI class is iterative. Let's use the vectorized helper if imported, 
        # or just rely on on_bar for live. For backtest speed, vectorized is better.
        
        # Simple Vectorized RSI for Backtesting Speed
        close = data['Close']
        delta = close.diff()
        gain = (delta.where(delta > 0, 0)).fillna(0)
        loss = (-delta.where(delta < 0, 0)).fillna(0)
        avg_gain = gain.rolling(window=self.rsi_period).mean()
        avg_loss = loss.rolling(window=self.rsi_period).mean()
        rs = avg_gain / avg_loss
        self.data['rsi'] = 100 - (100 / (1 + rs))
        
        # Logic Placeholder (Vectorized)
        # self.data['signal'] = 0
        # self.data.loc[self.data['rsi'] < self.buy_threshold, 'signal'] = 1
        # self.data.loc[self.data['rsi'] > self.sell_threshold, 'signal'] = -1

    def on_data(self, index, row):
        """
        Called on every new data point.
        """
        self.on_bar(row, index, self.data)

    def on_event(self, event):
        """
        Called when an economic event occurs.
        """
        pass

    def on_bar(self, row, i, full_data):
        """
        Executed on every bar.
        """
        # Update Indicators (Live)
        # In live mode, 'row' is the latest bar. 
        # We might need to recalculate RSI based on recent history in full_data.
        
        current_price = row['Close']
        current_rsi = row.get('rsi')
        
        # Fallback if RSI not in row (e.g. live calculation needed)
        if pd.isna(current_rsi):
             # Calculate on fly using last N bars
             if len(full_data) > self.rsi_period + 1:
                 # Simple RSI calc
                 delta = full_data['Close'].diff()
                 gain = (delta.where(delta > 0, 0)).fillna(0)
                 loss = (-delta.where(delta < 0, 0)).fillna(0)
                 avg_gain = gain.rolling(window=self.rsi_period).mean().iloc[-1]
                 avg_loss = loss.rolling(window=self.rsi_period).mean().iloc[-1]
                 if avg_loss == 0:
                     current_rsi = 100
                 else:
                     rs = avg_gain / avg_loss
                     current_rsi = 100 - (100 / (1 + rs))
             else:
                 current_rsi = 50 # Neutral
        
        # Trading Logic
        current_position = self.broker.get_position(self.symbol)
        
        # ENTRY
        if current_position == 0:
            if current_rsi < self.buy_threshold:
                qty = self.calculate_position_size(current_price)
                self.place_order(self.symbol, qty, 'buy')
                print(f">>> SIGNAL: BUY {self.symbol} at {current_price} (RSI: {current_rsi:.2f})")
                
        # EXIT
        elif current_position > 0:
            # Stop Loss
            avg_entry = self.broker.get_average_entry_price(self.symbol)
            if avg_entry > 0 and current_price < avg_entry * (1 - self.stop_loss_pct):
                self.place_order(self.symbol, current_position, 'sell')
                print(f">>> SIGNAL: STOP LOSS {self.symbol} at {current_price}")
                
            # Take Profit / Exit Signal
            elif current_rsi > self.sell_threshold:
                self.place_order(self.symbol, current_position, 'sell')
                print(f">>> SIGNAL: SELL {self.symbol} at {current_price} (RSI: {current_rsi:.2f})")

    def calculate_position_size(self, price):
        # Simple 95% equity usage for now
        cash = self.broker.get_cash()
        if cash < 10: return 0
        return (cash * 0.95) / price
