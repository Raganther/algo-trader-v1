
from backend.engine.alpaca_trader import AlpacaTrader

class LiveBroker:
    """
    Adapts AlpacaTrader to match the BacktestBroker interface expected by Strategies.
    """
    def __init__(self, symbol, paper=True, iteration_index=None):
        self.symbol = symbol
        self.paper = paper
        self.iteration_index = iteration_index
        self.trader = AlpacaTrader(paper=paper)
        
        # Retry logic for initial connection
        import time
        max_retries = 5
        retry_delay = 2
        
        for attempt in range(max_retries):
            try:
                self.initial_balance = self.trader.get_cash()
                break
            except Exception as e:
                print(f"⚠️ Connection Error in init (Attempt {attempt+1}/{max_retries}): {e}")
                if attempt < max_retries - 1:
                    time.sleep(retry_delay)
                    retry_delay *= 2
                else:
                    print("❌ Failed to connect to Alpaca after retries. Defaulting balance to 100k.")
                    self.initial_balance = 100000.0 # Fallback to avoid crash
        
        self.trades = [] # Local log of trades in this session
        self.last_trade_time = None
        self.positions = {} # Cache positions
        self.equity = self.initial_balance # Default fallback
        self.new_trades = [] # Queue for new trades
        self.pending_stop_order_id = None  # Server-side stop order ID
        self.pending_stop_qty = None  # Qty tracked alongside stop order ID for pending_fills fallback
        self.pending_stop_side = None  # 'sell' for long positions, 'buy' for short positions
        self._last_stop_price = None  # Track last stop price for fallback on update failure
        self.pending_fills = []  # Timed-out orders that may still be in-flight
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
                    sym = p['symbol']
                    pos_data = {
                        'size': p['qty'],
                        'price': p['entry_price']
                    }
                    self.positions[sym] = pos_data
                    # Also store with slash for crypto (BTCUSD → BTC/USD)
                    if len(sym) == 6 and sym.endswith('USD'):
                        slash_sym = sym[:-3] + '/' + sym[-3:]
                        self.positions[slash_sym] = pos_data
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
        """Return and clear new trades list. Also retries timed-out pending fills."""
        # Retry any timed-out orders that may now be filled
        still_pending = []
        for pf in self.pending_fills:
            order = self.trader.get_order(pf['order_id'])
            if order and order['status'] == 'filled':
                fill_price = order['filled_avg_price']
                slippage = pf['signal_price'] - fill_price if pf['side'] == 'sell' else fill_price - pf['signal_price']
                self.new_trades.append({
                    'symbol': self.symbol,
                    'side': pf['side'],
                    'qty': pf['qty'],
                    'signal_price': pf['signal_price'],
                    'fill_price': fill_price,
                    'slippage': slippage,
                    'spread': 0.0,
                    'timestamp': order['filled_at'],
                    'order_id': pf['order_id']
                })
                print(f"✅ PENDING FILL resolved: {pf['side']} @ {fill_price} (order {pf['order_id'][:8]}...)")
            else:
                still_pending.append(pf)
        self.pending_fills = still_pending

        trades_to_return = []
        for t in self.new_trades:
            t['iteration_index'] = self.iteration_index
            trades_to_return.append(t)
        self.new_trades = []
        return trades_to_return

    def set_entry_metadata(self, symbol, metadata):
        """
        Updates the last trade for the symbol with metadata.
        This is called by strategies to attach analysis data (e.g. regime, atr) to the trade.
        """
        # Find partial trade in new_trades
        if self.new_trades:
            # Assuming the last trade is the one we just made
            # We could filter by symbol if needed, but usually execution is sequential.
            self.new_trades[-1].update(metadata)
        else:
            # This might happen if order failed or wasn't tracked
            print(f"⚠️ Warning: set_entry_metadata called but no new trades found for {symbol}")

    def _wait_for_fill(self, order_id, retries=15):
        """Polls Alpaca for order fill. 15 retries × 2s = 30s timeout."""
        import time
        for attempt in range(retries):
            order = self.trader.get_order(order_id)
            if order and order['status'] == 'filled':
                return order
            time.sleep(2)
        print(f"⚠️ ORDER NOT FILLED after {retries * 2}s — order_id: {order_id}. Check manually.")
        return None

    def buy(self, price, size, timestamp=None, stop_loss=None, take_profit=None):
        """
        Execute Buy Order.
        Two cases:
          - stop_loss provided + position == 0: opening a long position
          - no stop_loss + position < 0: closing a short position
        """
        import time
        is_crypto = '/' in self.symbol
        current_position = self.get_position(self.symbol)

        if current_position < 0:
            # Closing a short position — cancel pending buy stop first
            cancelled = self.trader.cancel_all_orders_for_symbol(self.symbol)
            if cancelled > 0:
                print(f"🛡️ Cancelled {cancelled} open order(s) for {self.symbol} before short exit")
                time.sleep(0.5)
            self.pending_stop_order_id = None
            self.pending_stop_qty = None
            self.pending_stop_side = None
            print(f"LIVE BUY (close short): {size} shares of {self.symbol}")
        else:
            # Opening a long position
            print(f"LIVE BUY: {size} shares of {self.symbol}")

        try:
            res = self.trader.place_order(
                symbol=self.symbol,
                qty=size,
                side='buy'
            )
        except Exception as e:
            print(f"❌ BUY order rejected: {e}")
            return None

        filled_order = self._wait_for_fill(res['id'])
        if filled_order:
            self.new_trades.append({
                'symbol': self.symbol,
                'side': 'buy',
                'qty': size,
                'signal_price': price,
                'fill_price': filled_order['filled_avg_price'],
                'slippage': filled_order['filled_avg_price'] - price,
                'spread': 0.0,
                'timestamp': filled_order['filled_at'],
                'order_id': res['id']
            })
            print(f"✅ FILLED BUY: {filled_order['filled_avg_price']} (order {res['id'][:8]}...)")

            # Place server-side sell stop for long entry (not for short close)
            if stop_loss and not is_crypto:
                try:
                    stop_res = self.trader.place_stop_order(
                        symbol=self.symbol,
                        qty=size,
                        side='sell',
                        stop_price=stop_loss
                    )
                    self.pending_stop_order_id = stop_res['id']
                    self.pending_stop_qty = size
                    self.pending_stop_side = 'sell'
                    self._last_stop_price = stop_loss
                    print(f"🛡️ SERVER STOP placed at ${stop_loss:.2f} (order {stop_res['id'][:8]}...)")
                except Exception as e:
                    print(f"⚠️ Server stop order failed: {e} — bot will manage stop locally")
                    self.pending_stop_order_id = None
                    self.pending_stop_qty = None
                    self.pending_stop_side = None
        else:
            self.pending_fills.append({'order_id': res['id'], 'signal_price': price, 'side': 'buy', 'qty': size})
            print(f"⏳ Buy order {res['id'][:8]}... queued in pending_fills for retry")

        return res

    def sell(self, price, size, timestamp=None, stop_loss=None, take_profit=None):
        """
        Execute Sell Order.
        Three cases:
          - position > 0: closing a long position (exit)
          - position == 0 + stop_loss provided: opening a short position (entry)
          - position == 0 + no stop_loss: duplicate exit signal — skip
        """
        import time
        is_crypto = '/' in self.symbol
        current_position = self.get_position(self.symbol)

        if current_position > 0:
            # Closing a long position — cancel pending sell stop first
            cancelled = self.trader.cancel_all_orders_for_symbol(self.symbol)
            if cancelled > 0:
                print(f"🛡️ Cancelled {cancelled} open order(s) for {self.symbol} before long exit")
                time.sleep(0.5)
            self.pending_stop_order_id = None
            self.pending_stop_qty = None
            self.pending_stop_side = None
            print(f"LIVE SELL: {size} shares of {self.symbol}")

        else:
            # No position — block all sells (Alpaca rejects fractional short selling)
            # Short trading requires whole-share qty; re-enable once position sizing is updated
            print(f"⚠️ SELL skipped: no open position for {self.symbol} — ignoring duplicate exit signal")
            return None

        try:
            res = self.trader.place_order(
                symbol=self.symbol,
                qty=size,
                side='sell'
            )
        except Exception as e:
            print(f"❌ SELL order rejected: {e}")
            return None

        filled_order = self._wait_for_fill(res['id'])
        if filled_order:
            self.new_trades.append({
                'symbol': self.symbol,
                'side': 'sell',
                'qty': size,
                'signal_price': price,
                'fill_price': filled_order['filled_avg_price'],
                'slippage': price - filled_order['filled_avg_price'],
                'spread': 0.0,
                'timestamp': filled_order['filled_at'],
                'order_id': res['id']
            })
            print(f"✅ FILLED SELL: {filled_order['filled_avg_price']} (order {res['id'][:8]}...)")

            # Short entry stop placement removed — fractional short selling not supported by Alpaca
        else:
            self.pending_fills.append({'order_id': res['id'], 'signal_price': price, 'side': 'sell', 'qty': size})
            print(f"⏳ Sell order {res['id'][:8]}... queued in pending_fills for retry")

        return res

    def update_stop_order(self, new_stop_price, qty):
        """Update the server-side stop order to a new price (for trailing stops)."""
        if not self.pending_stop_order_id:
            return
        old_stop_price = self._last_stop_price
        # Cancel old, place new
        self.trader.cancel_order(self.pending_stop_order_id)
        stop_side = self.pending_stop_side or 'sell'  # 'sell' for longs, 'buy' for shorts
        try:
            stop_res = self.trader.place_stop_order(
                symbol=self.symbol,
                qty=qty,
                side=stop_side,
                stop_price=new_stop_price
            )
            self.pending_stop_order_id = stop_res['id']
            self.pending_stop_qty = qty
            self._last_stop_price = new_stop_price
            print(f"🛡️ TRAILING STOP updated to ${new_stop_price:.2f} (order {stop_res['id'][:8]}...)")
        except Exception as e:
            print(f"⚠️ Trailing stop update to ${new_stop_price:.2f} failed: {e}")
            # Re-place at OLD stop price as fallback to keep position protected
            fallback_price = old_stop_price if old_stop_price else new_stop_price
            try:
                fallback_res = self.trader.place_stop_order(
                    symbol=self.symbol,
                    qty=qty,
                    side=stop_side,
                    stop_price=fallback_price
                )
                self.pending_stop_order_id = fallback_res['id']
                self.pending_stop_qty = qty
                self._last_stop_price = fallback_price
                print(f"🛡️ FALLBACK STOP re-placed at ${fallback_price:.2f} (order {fallback_res['id'][:8]}...)")
            except Exception as e2:
                print(f"❌ FALLBACK STOP also failed: {e2} — POSITION UNPROTECTED! Check manually.")
                self.pending_stop_order_id = None

    def place_order(self, symbol, side, quantity, order_type='market', price=None, stop_loss=None, take_profit=None, **kwargs):
        """
        Unified interface for placing orders.
        Delegates to buy/sell to ensure logging logic is used.
        Matches PaperTrader signature: (symbol, side, quantity, ...)
        """
        # Ignore symbol argument if it matches self.symbol (LiveBroker is single-symbol usually)
        # But if it differs, we might warn.
        
        if side.lower() == 'buy':
            return self.buy(price=price if price else 0.0, size=quantity, stop_loss=stop_loss, take_profit=take_profit)
        elif side.lower() == 'sell':
            return self.sell(price=price if price else 0.0, size=quantity, stop_loss=stop_loss, take_profit=take_profit)
        else:
            print(f"Error: Unknown side {side}")
            return None
