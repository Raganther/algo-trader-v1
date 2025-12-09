from abc import ABC, abstractmethod
import pandas as pd

class BrokerAdapter(ABC):
    """
    Abstract base class for broker interactions.
    Standardizes how strategies interact with execution engines (Paper or Live).
    """
    
    @abstractmethod
    def get_balance(self) -> float:
        """Return current account balance (cash)."""
        pass

    @abstractmethod
    def get_equity(self) -> float:
        """Return current account equity (cash + unrealized pnl)."""
        pass

    @abstractmethod
    def get_positions(self) -> dict:
        """Return dict of open positions."""
        pass

    @abstractmethod
    def place_order(self, symbol: str, side: str, quantity: float, order_type: str = "market", price: float = None, stop_loss: float = None, take_profit: float = None) -> dict:
        """
        Place an order.
        side: 'buy' or 'sell'
        order_type: 'market', 'limit', 'stop'
        """
        pass

    @abstractmethod
    def close_position(self, symbol: str, quantity: float = None) -> dict:
        """Close an existing position."""
        pass
