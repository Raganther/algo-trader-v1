from ..signal import Signal
import pandas as pd

class TimeSignal(Signal):
    def __init__(self, data: pd.DataFrame, parameters: dict = {}):
        super().__init__(data, parameters)
        self.name = "Time"
        # No calculation needed, just extraction

    def generate(self, index, row) -> float:
        # Return the hour of the day (0-23)
        # print(f"DEBUG: TimeSignal Hour: {index.hour}")
        return float(index.hour)
