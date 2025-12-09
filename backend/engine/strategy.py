from abc import ABC, abstractmethod
import pandas as pd

class Strategy(ABC):
    def __init__(self, data: pd.DataFrame, events: pd.DataFrame = None, parameters: dict = {}, initial_cash: float = 10000.0, broker=None):
        self.data = data
        self.events = events
        self.parameters = parameters
        self.broker = broker # BrokerAdapter instance
        
        # If no broker provided, we might default to None or a dummy for backward compatibility,
        # but ideally we enforce it. For now, we'll handle None.
        
        self.cash = initial_cash # Legacy, should use broker.get_balance()
        self.position = 0 # Legacy, should use broker.get_positions()
        
        self.orders = [] # Keep for log/debug, but execution goes to broker
        self.trades = [] 
        self.equity_curve = []

    @abstractmethod
    def on_data(self, index, row):
        """
        Called on every new data point (candle).
        """
        pass

    @abstractmethod
    def on_event(self, event):
        """
        Called when an economic event occurs.
        """
        pass

    def buy(self, price, size=1.0, timestamp=None, stop_loss=None, take_profit=None):
        if self.broker:
            return self.broker.place_order(symbol=self.parameters.get('symbol', 'Unknown'), side='buy', quantity=size, price=price, timestamp=timestamp, stop_loss=stop_loss, take_profit=take_profit)
        else:
            # Legacy fallback
            self._place_order('buy', price, size, timestamp)
            return True

    def sell(self, price, size=1.0, timestamp=None, stop_loss=None, take_profit=None):
        if self.broker:
            return self.broker.place_order(symbol=self.parameters.get('symbol', 'Unknown'), side='sell', quantity=size, price=price, timestamp=timestamp, stop_loss=stop_loss, take_profit=take_profit)
        else:
            # Legacy fallback
            self._place_order('sell', price, size, timestamp)
            return True

    def _place_order(self, side, price, size, timestamp):
        self.orders.append({
            'side': side,
            'price': price,
            'size': size,
            'timestamp': timestamp,
            'status': 'pending' 
        })
