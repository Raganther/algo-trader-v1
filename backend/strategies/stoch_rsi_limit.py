from backend.strategies.stoch_rsi_mean_reversion import StochRSIMeanReversionStrategy

class StochRSILimit(StochRSIMeanReversionStrategy):
    def __init__(self, data, events, parameters, initial_cash=10000.0, broker=None):
        super().__init__(data, events, parameters, initial_cash, broker)
        self.pending_order = None

    def on_bar(self, row, i, df):
        if self.bar_index < 50: 
            return

        # 1. Execute Pending Orders (Limit Logic)
        if self.pending_order:
            side, size, limit_price = self.pending_order
            
            filled = False
            
            # Market Order (limit_price is None)
            if limit_price is None:
                self.broker.place_order(symbol=self.parameters.get('symbol', 'Unknown'), side=side, quantity=size, price=row['Open'], timestamp=i)
                # Note: We use broker.place_order directly or self.buy/sell?
                # self.buy/sell calls broker.place_order.
                # Let's use self.buy/sell for consistency.
                if side == 'buy':
                    self.buy(price=row['Open'], size=size, timestamp=i)
                    self.position = 'long'
                elif side == 'sell':
                    self.sell(price=row['Open'], size=size, timestamp=i)
                    self.position = 'short'
                filled = True
            
            # Limit Order
            else:
                if side == 'buy':
                    if row['Low'] <= limit_price:
                        # Filled
                        actual_fill = min(row['Open'], limit_price) if row['Open'] < limit_price else limit_price
                        self.buy(price=actual_fill, size=size, timestamp=i)
                        self.position = 'long'
                        filled = True
                elif side == 'sell':
                    if row['High'] >= limit_price:
                        # Filled
                        actual_fill = max(row['Open'], limit_price) if row['Open'] > limit_price else limit_price
                        self.sell(price=actual_fill, size=size, timestamp=i)
                        self.position = 'short'
                        filled = True
            
            # If filled or expired (1 bar expiry for now), clear pending
            self.pending_order = None
            
            # If we just filled, we don't look for new signals on this bar (simplify)
            if filled:
                return

        # 2. Signal Logic
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
                # Signal: Buy
                # Place Limit at CURRENT CLOSE (which becomes Prev Close next bar)
                self.pending_order = ('buy', self.position_size, row['Close'])
                self.in_oversold_zone = False 
                # Do NOT update self.position yet
                
            if current_k > 50:
                self.in_oversold_zone = False

            if prev_k > self.overbought:
                self.in_overbought_zone = True
                
            if self.in_overbought_zone and current_k < 50:
                # Signal: Sell
                self.pending_order = ('sell', self.position_size, row['Close'])
                self.in_overbought_zone = False
                
            if current_k < 50:
                self.in_overbought_zone = False

        # Exit Logic
        elif self.position == 'long':
            if current_k > self.overbought:
                # Market Exit at Next Open
                # We can simulate this by setting a pending 'market' order
                # Or just use the 'next_open' logic if we had it.
                # Since we are in 'on_bar' for the *current* bar, we want to exit at *next* bar's Open.
                # We can set a pending order with a special flag or just use the Limit logic with a very aggressive limit?
                # No, let's add a 'market' type to pending_order tuple: (side, size, price, type)
                # But to keep it simple: A Market Sell is just a Sell Limit at 0 (or -infinity)? No, Sell Limit is High >= Limit.
                # A Market Sell fills at Open.
                # Let's use a special marker price=None for Market.
                self.pending_order = ('sell', self.position_size, None) 
                self.position = 0 # Update state immediately (assuming fill)
                
        elif self.position == 'short':
            if current_k < self.oversold:
                self.pending_order = ('buy', self.position_size, None) # Market Exit
                self.position = 0


