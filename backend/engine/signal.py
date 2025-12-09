from abc import ABC, abstractmethod
import pandas as pd

class Signal(ABC):
    def __init__(self, data: pd.DataFrame, parameters: dict = {}):
        self.data = data
        self.parameters = parameters
        self.name = "BaseSignal"

    @abstractmethod
    def generate(self, index: pd.Timestamp, row: pd.Series) -> float:
        """
        Calculate the signal value for a given row.
        Returns a float value (e.g., 1.0 for buy, -1.0 for sell, 0.0 for neutral, or a raw indicator value).
        """
        raise NotImplementedError("Subclasses must implement generate()")

    def get_debug_data(self) -> dict:
        """
        Returns dictionary of debug information (e.g. computed levels, internal state)
        to be visualized on the frontend.
        """
        return {}
