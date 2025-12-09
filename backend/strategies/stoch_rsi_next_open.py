from backend.strategies.stoch_rsi_mean_reversion import StochRSIMeanReversionStrategy

class StochRSINextOpen(StochRSIMeanReversionStrategy):
    def __init__(self, data, events, parameters, initial_cash=10000.0, broker=None):
        super().__init__(data, events, parameters, initial_cash, broker)
        self.pending_order = None

    def on_bar(self, row, i, df):
        if self.bar_index < 50: 
            return

        # 1. Execute Pending Orders at OPEN
        if self.pending_order:
            side, size = self.pending_order
            if side == 'buy':
                self.buy(price=row['Open'], size=size, timestamp=i)
                self.position = 'long' # Update state after fill
            elif side == 'sell':
                self.sell(price=row['Open'], size=size, timestamp=i)
                # Update state? 
                # If closing long: position becomes 0
                # If opening short: position becomes 'short'
                # Logic below handles state transitions, but we need to track it correctly.
                # Simplified: The base strategy updates self.position immediately.
                # We should probably defer state update too?
                # Actually, base strategy updates self.position in the signal block.
                # We need to override that.
            
            self.pending_order = None
            
            # If we just executed, do we check for new signals? 
            # Yes, but using the CLOSE of this bar.
            
        # 2. Signal Logic (Copy-Paste from Base but replace buy/sell with pending)
        current_k = row['k']
        prev_k = df.iloc[self.bar_index-1]['k']
        current_adx = row['adx']
        
        if current_adx > self.adx_threshold:
            return

        # Entry Logic
        if self.position == 0: 
            if prev_k < self.oversold:
                self.in_oversold_zone = True
            
            if self.in_oversold_zone and current_k > 50:
                # self.buy(...) -> Pending
                self.pending_order = ('buy', self.position_size)
                self.in_oversold_zone = False 
                # self.position = 'long'  <-- DON'T UPDATE YET
                # But wait, if we don't update, next bar will think we are flat and might signal again?
                # We need a 'pending_position' state?
                # Or just assume we are 'long' for logic purposes?
                self.position = 'long' # Assume filled for logic flow
                
            if current_k > 50:
                self.in_oversold_zone = False

            if prev_k > self.overbought:
                self.in_overbought_zone = True
                
            if self.in_overbought_zone and current_k < 50:
                self.pending_order = ('sell', self.position_size) # Short
                self.in_overbought_zone = False
                self.position = 'short'
                
            if current_k < 50:
                self.in_overbought_zone = False

        # Exit Logic
        elif self.position == 'long':
            if current_k > self.overbought:
                self.pending_order = ('sell', self.position_size) # Close
                self.position = 0
                
        elif self.position == 'short':
            if current_k < self.oversold:
                self.pending_order = ('buy', self.position_size) # Close
                self.position = 0
