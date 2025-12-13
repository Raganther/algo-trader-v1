from backend.engine.strategy import Strategy
from backend.indicators.rsi import rsi
import pandas as pd

class RapidFireTestStrategy(Strategy):
    """
    Rapid Fire Test Strategy
    Goal: Generate frequent trades to test execution speed and slippage.
    Logic: RSI(2) on 1m timeframe.
    - Buy: RSI < 10
    - Sell: RSI > 90
    """
    def __init__(self, data: pd.DataFrame, events: pd.DataFrame = None, parameters: dict = {}, initial_cash: float = 10000.0, broker=None):
        super().__init__(data, events, parameters, initial_cash, broker)
        self.rsi_period = int(parameters.get('rsi_period', 2))
        self.buy_threshold = float(parameters.get('buy_threshold', 30))
        self.sell_threshold = float(parameters.get('sell_threshold', 70))
        self.symbol = parameters.get('symbol', 'Unknown')
        
        self.bar_index = 0
        
        # Calculate Indicators
        self.generate_signals(self.data)

    def on_data(self, index, row):
        """Required by Abstract Base Class"""
        self.on_bar(row, self.bar_index, self.data)
        self.bar_index += 1

    def on_event(self, event):
        """Required by Abstract Base Class"""
        pass

    def generate_signals(self, data):
        """Recalculate indicators on new data"""
        if len(data) > self.rsi_period:
            data['rsi'] = rsi(data['Close'], self.rsi_period)
        else:
            data['rsi'] = 50.0 # Default neutral

    def on_bar(self, bar, i, data):
        """
        Executed on every new bar.
        """
        # Ensure we have enough data
        if i < self.rsi_period:
            return

        current_rsi = data['rsi'].iloc[i]
        
        # Log for visibility
        print(f"[{bar.name}] Price: {bar['Close']:.2f} | RSI({self.rsi_period}): {current_rsi:.2f}")

        # Check for Open Positions
        current_position = self.broker.get_position(self.symbol)
        
        # Logic: Long-Only High Frequency (Iteration 2)
        # RSI < Buy Threshold (e.g. 30) -> Buy
        # RSI > Sell Threshold (e.g. 70) -> Sell (Close)
        
        if current_rsi < self.buy_threshold:
            # Signal: BUY
            if current_position == 0:
                print(f"  >>> SIGNAL: BUY (RSI {current_rsi:.2f} < {self.buy_threshold})")
                self.broker.place_order(
                    symbol=self.symbol,
                    quantity=0.01,
                    side='buy',
                    order_type='market',
                    price=bar['Close'],
                    timestamp=bar.name
                )

        elif current_rsi > self.sell_threshold:
            # Signal: SELL (Exit Only)
            if current_position > 0:
                print(f"  >>> SIGNAL: SELL (RSI {current_rsi:.2f} > {self.sell_threshold})")
                self.broker.place_order(
                    symbol=self.symbol,
                    quantity=current_position,
                    side='sell',
                    order_type='market',
                    price=bar['Close'],
                    timestamp=bar.name
                )
