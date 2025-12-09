from ..signal import Signal
import pandas as pd

class EventSignal(Signal):
    def __init__(self, data: pd.DataFrame, parameters: dict = {}):
        super().__init__(data, parameters)
        self.name = "Event"
        self.target_event = parameters.get('event_name', "Non-Farm Payrolls")
        self.impact_filter = parameters.get('impact', "High")

    def generate(self, index, row) -> float:
        # EventSignal is unique: it doesn't usually trigger on price data (on_data),
        # but rather on specific event timestamps.
        # However, for consistency, we can check if the current index matches an event.
        return 0.0

    def on_event(self, event) -> float:
        """
        Special method for EventSignal to process event objects directly.
        """
        # Check if event matches target (or if target is 'All')
        if self.target_event != 'All' and self.target_event not in event['event']:
            return 0.0
            
        actual = event.get('actual_val')
        forecast = event.get('forecast_val')
        currency = event.get('currency')
        
        if actual is None or forecast is None:
            return 0.0
            
        deviation = actual - forecast
        
        # Logic: 
        # Positive Deviation (Actual > Forecast) -> Good for Currency
        # Negative Deviation (Actual < Forecast) -> Bad for Currency
        
        signal = 0.0
        
        if currency == 'USD':
            if deviation > 0:
                # USD Strong -> EURUSD Down -> Sell
                signal = -1.0
            elif deviation < 0:
                # USD Weak -> EURUSD Up -> Buy
                signal = 1.0
                
        elif currency == 'EUR':
            if deviation > 0:
                # EUR Strong -> EURUSD Up -> Buy
                signal = 1.0
            elif deviation < 0:
                # EUR Weak -> EURUSD Down -> Sell
                signal = -1.0
                
        return signal
