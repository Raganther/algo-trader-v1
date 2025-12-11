from backend.engine.alpaca_trader import AlpacaTrader

class LiveBroker:
    """
    Adapts AlpacaTrader to match the BacktestBroker interface expected by Strategies.
    """
    def __init__(self, symbol, paper=True):
        self.trader = AlpacaTrader(paper=paper)
        self.symbol = symbol
        self.positions = {} # Cache positions
        self.equity = 100000.0 # Default fallback
        self.new_trades = [] # Queue for new trades
        self.refresh()

    def refresh(self):
        """Fetch latest account info from Alpaca with retry logic."""
        import time
        max_retries = 3
        retry_delay = 1
        
        for attempt in range(max_retries):
            try:
                summary = self.trader.get_account_summary()
                self.equity = summary['equity']
                
                # Convert Alpaca positions to simple dict format
                # {'SPY': {'size': 10, 'price': 500}}
                raw_pos = self.trader.get_open_trades()
                self.positions = {}
                for p in raw_pos:
                    self.positions[p['symbol']] = {
                        'size': p['qty'],
                        'price': p['entry_price']
                    }
                return # Success
            except Exception as e:
                print(f"⚠️ Connection Error in refresh (Attempt {attempt+1}/{max_retries}): {e}")
                if attempt < max_retries - 1:
                    time.sleep(retry_delay)
                    retry_delay *= 2 # Exponential backoff
                else:
                    print("❌ Max retries reached. Skipping refresh.")
                    # We don't raise here to prevent crashing the main loop, 
                    # but we might be trading on stale data.
                    pass

    def get_equity(self):
        return self.equity

    def get_positions(self):
        return self.positions
        
    def get_position(self, symbol):
        """Return position size for a specific symbol."""
        # Clean symbol if needed, but dictionary keys should match
        # AlpacaTrader returns 'BTCUSD' usually, but we might use 'BTC/USD'
        # Let's handle both or just check.
        # The refresh() method uses p['symbol'] from Alpaca.
        
        # Try exact match
        if symbol in self.positions:
            return self.positions[symbol]['size']
            
        # Try stripped match
        clean = symbol.replace('/', '')
        if clean in self.positions:
            return self.positions[clean]['size']
            
        return 0.0
        
    def get_new_trades(self):
        """Return and clear new trades list."""
        trades = self.new_trades[:]
        self.new_trades = []
        return trades

    def _wait_for_fill(self, order_id, retries=5):
        """Polls Alpaca for order fill."""
        import time
        for _ in range(retries):
            order = self.trader.get_order(order_id)
            if order and order['status'] == 'filled':
                return order
            time.sleep(1)
        return None

    def buy(self, price, size, timestamp=None, stop_loss=None, take_profit=None):
        """
        Execute Buy Order.
        Note: 'price' is ignored for Market Orders, but kept for interface compatibility.
        """
        # Strategy passes size as amount of shares (float)
        # Strategy might pass stop_loss (if we update strategy to use it)
        # Currently strategy manages SL manually, but we can override.
        
        # For now, just execute market buy
        # If strategy passes stop_loss (which it doesn't yet in current code), we'd use it.
        # But wait, I just updated AlpacaTrader to support bracket orders.
        # I should update the Strategy to pass SL to broker.buy()!
        
        print(f"LIVE BUY: {size} shares of {self.symbol}")
        res = self.trader.place_order(
            symbol=self.symbol,
            qty=size,
            side='buy',
            stop_loss=stop_loss,
            take_profit=take_profit
        )
        
        # Poll for fill to get exact price
        filled_order = self._wait_for_fill(res['id'])
        if filled_order:
            self.new_trades.append({
                'symbol': self.symbol,
                'side': 'buy',
                'qty': size,
                'signal_price': price, # Expected price from Strategy
                'fill_price': filled_order['filled_avg_price'],
                'slippage': filled_order['filled_avg_price'] - price, # Slippage is bad if Buy Price > Signal Price
                'spread': 0.0, # Placeholder
                'timestamp': filled_order['filled_at']
            })
            print(f"✅ FILLED BUY: {filled_order['filled_avg_price']}")
        else:
            print(f"⚠️ Order {res['id']} not filled yet.")
            
        return res

    def sell(self, price, size, timestamp=None, stop_loss=None, take_profit=None):
        print(f"LIVE SELL: {size} shares of {self.symbol}")
        res = self.trader.place_order(
            symbol=self.symbol, 
            qty=size,
            side='sell',
            stop_loss=stop_loss,
            take_profit=take_profit
        )
        
        # Poll for fill
        filled_order = self._wait_for_fill(res['id'])
        if filled_order:
            self.new_trades.append({
                'symbol': self.symbol,
                'side': 'sell',
                'qty': size,
                'signal_price': price,
                'fill_price': filled_order['filled_avg_price'],
                'slippage': price - filled_order['filled_avg_price'], # Slippage is bad if Sell Price < Signal Price
                'spread': 0.0, # Placeholder, requires Bid/Ask snapshot
                'timestamp': filled_order['filled_at']
            })
            print(f"✅ FILLED SELL: {filled_order['filled_avg_price']}")
        else:
            print(f"⚠️ Order {res['id']} not filled yet.")
            
        return res

    def place_order(self, symbol, qty, side, order_type='market', price=None, stop_loss=None, take_profit=None, **kwargs):
        """
        Unified interface for placing orders.
        Delegates to buy/sell to ensure logging logic is used.
        """
        # Ignore symbol argument if it matches self.symbol (LiveBroker is single-symbol usually)
        # But if it differs, we might warn.
        
        if side.lower() == 'buy':
            return self.buy(price=price if price else 0.0, size=qty, stop_loss=stop_loss, take_profit=take_profit)
        elif side.lower() == 'sell':
            return self.sell(price=price if price else 0.0, size=qty, stop_loss=stop_loss, take_profit=take_profit)
        else:
            print(f"Error: Unknown side {side}")
            return None
