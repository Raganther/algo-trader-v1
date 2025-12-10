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
        """Fetch latest account info from Alpaca."""
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

    def get_equity(self):
        return self.equity

    def get_positions(self):
        return self.positions
        
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
                'slippage': filled_order['filled_avg_price'] - price,
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
                'timestamp': filled_order['filled_at']
            })
            print(f"✅ FILLED SELL: {filled_order['filled_avg_price']}")
        else:
            print(f"⚠️ Order {res['id']} not filled yet.")
            
        return res
