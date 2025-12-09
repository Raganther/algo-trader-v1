from .stoch_rsi_quant import StochRSIQuantStrategy

class StochRSISniperStrategy(StochRSIQuantStrategy):
    """
    StochRSI Sniper Strategy:
    Combines the best of 'Quant' (Time + ADX Filters) with 'Sector TICK' (Market Breadth).
    
    Filters:
    1. Time: No trade 09:30-10:00, 15:50-16:00 (Inherited from Quant)
    2. ADX: No trade if ADX > 30 (Inherited from Quant)
    3. Sector TICK: 
       - Longs: Require TICK <= -1.5 (Oversold Breadth)
       - Shorts: Require TICK >= 1.5 (Overbought Breadth)
    """
    
    def __init__(self, *args, **kwargs):
        # Extract parameters
        params = {}
        if 'parameters' in kwargs:
            params = kwargs['parameters']
        elif len(args) > 2:
            params = args[2]
            
        self.tick_threshold = float(params.get('tick_threshold', 1.5))
        
        super().__init__(*args, **kwargs)
        
    def on_bar(self, row, i, df):
        """
        Override on_bar to apply Sector TICK filter before calling parent (Quant) logic.
        """
        # 1. Sector TICK Filter
        # We need to check the 'sector_tick' column in the row
        # Note: runner.py adds this column if strategy is StochRSISniper
        
        tick = row.get('sector_tick', 0)
        
        # Determine intent (Long or Short)
        # Wait, we don't know the intent yet because the signal is generated in the parent.
        # But we can filter based on general market condition.
        
        # If we are in a "Long Setup" (StochRSI Oversold), we need TICK <= -1.5
        # If we are in a "Short Setup" (StochRSI Overbought), we need TICK >= 1.5
        
        # Access Parent State (StochRSI) to know if we are in a setup?
        # The parent logic is:
        # if prev_k < oversold: in_oversold_zone = True
        # if in_oversold_zone and current_k > 50: BUY
        
        # Problem: The parent logic handles state updates AND execution in one go.
        # If we just call super().on_bar(), it will execute the trade.
        # We need to intercept the execution OR pre-filter based on what *might* happen.
        
        # Approach:
        # We can't easily know if the parent *will* trade without duplicating logic.
        # BUT, we can use the TICK to block *directions*.
        
        # If TICK is Neutral (-1.5 to 1.5), we block ALL entries.
        # If TICK is Negative (<= -1.5), we allow LONGS only.
        # If TICK is Positive (>= 1.5), we allow SHORTS only.
        
        # How to enforce "Longs Only" or "Shorts Only" when calling super()?
        # We can temporarily modify the 'oversold' or 'overbought' thresholds? No, messy.
        
        # Cleaner Approach:
        # Re-implement the entry logic here? No, violates DRY.
        
        # Best Approach:
        # Check the TICK.
        # If TICK is Neutral: Return (No trades allowed).
        # If TICK is Negative: 
        #    - We want Longs. 
        #    - Can we prevent Shorts? 
        #    - Yes, we can check `self.in_overbought_zone`. If True, we are looking for a short.
        #    - If we are looking for a short but TICK is Negative, we should BLOCK.
        
        # Let's try this:
        
        # 1. Check TICK
        is_oversold_breadth = tick <= -self.tick_threshold
        is_overbought_breadth = tick >= self.tick_threshold
        
        # 2. Check Potential Setups (Peek at Parent State)
        # Note: 'in_oversold_zone' means we are waiting for a Long trigger.
        # Note: 'in_overbought_zone' means we are waiting for a Short trigger.
        
        # If we are flat (position == 0):
        if self.position == 0:
            # If we are potentially going LONG (in zone OR entering zone)
            # We can't easily peek "entering zone" without duplicated logic.
            
            # SIMPLIFICATION:
            # If TICK is Neutral, return immediately. (Sniper waits for extreme breadth).
            if not is_oversold_breadth and not is_overbought_breadth:
                return # SKIP (No Breadth Edge)
                
            # If TICK is Oversold (Long Bias), but we are setting up for a Short...
            # The parent logic will handle the trigger.
            # If we call parent, and it triggers a Short while TICK is Oversold... that's a bad trade (Counter-Breadth).
            # We need to block it.
            
            # We can use a flag?
            # Or just check the StochRSI values ourselves?
            
            # Let's duplicate the StochRSI check just for the *direction* filter.
            # It's safer than trying to hack the parent.
            
            current_k = row['k']
            
            # If we are about to buy (Long):
            # Requires: in_oversold_zone AND k > 50
            # We can't stop the parent from updating state, but we can stop execution.
            
            # Actually, if we return here, we stop the parent from updating state (in_oversold_zone).
            # This is DANGEROUS. If we skip on_bar, the state machine breaks.
            
            # SOLUTION:
            # We must allow the state machine to update, but block the *order*.
            # But `buy()` is called inside `on_bar`.
            
            # We can override `buy` and `sell`?
            # Yes! This is the cleanest way.
            
            pass # Proceed to call parent
            
        # Call Parent (Updates State, Generates Signals)
        super().on_bar(row, i, df)

    def buy(self, price, size, timestamp, stop_loss=None):
        # Intercept Buy Order
        # Only allow if TICK indicates Oversold Breadth
        # We need access to the current row's TICK.
        # 'on_bar' has the row, but 'buy' doesn't.
        # We can store 'current_tick' in 'on_bar'.
        
        current_tick = getattr(self, 'current_tick', 0)
        if current_tick <= -self.tick_threshold:
            return super().buy(price, size, timestamp, stop_loss)
        else:
            return None # Blocked by TICK

    def sell(self, price, size, timestamp, stop_loss=None):
        # Intercept Sell Order (Short Entry OR Long Exit)
        
        # Wait, 'sell' is used for BOTH Short Entry and Long Exit.
        # We must NOT block Exits!
        
        if self.position == 'long':
            # This is an Exit. Always allow.
            return super().sell(price, size, timestamp, stop_loss)
            
        elif self.position == 0:
            # This is a Short Entry.
            # Only allow if TICK indicates Overbought Breadth
            current_tick = getattr(self, 'current_tick', 0)
            if current_tick >= self.tick_threshold:
                return super().sell(price, size, timestamp, stop_loss)
            else:
                return None # Blocked by TICK
                
        return super().sell(price, size, timestamp, stop_loss)

    def on_bar(self, row, i, df):
        # Store current tick for the buy/sell interceptors
        self.current_tick = row.get('sector_tick', 0)
        
        # Call Parent (Quant -> MeanReversion)
        super().on_bar(row, i, df)
