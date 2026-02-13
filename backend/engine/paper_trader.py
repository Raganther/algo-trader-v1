from .broker_adapter import BrokerAdapter
import pandas as pd
from datetime import datetime
import uuid

class PaperTrader(BrokerAdapter):
    def __init__(self, initial_capital=10000.0, spread=0.0, account_currency="USD"):
        self.initial_capital = initial_capital
        self.equity = initial_capital
        self.cash = initial_capital
        self.spread = spread
        self.account_currency = account_currency # Spread as fraction (e.g. 0.0003 = 0.03%)
        self.positions = {} # {symbol: {'size': float, 'avg_price': float}}
        self.orders = []
        self.trade_history = []
        self.override_price = None # For forcing execution price (e.g. Next Open)
        self.trades = [] # List of trade dictionaries
        self._entry_metadata = {} # {symbol: {...}} — stored at entry, merged into trade on close
        
        # Simulated Market Data (Updated via update_price)
        self.current_prices = {} 

    def set_execution_override(self, price):
        self.override_price = price

    def update_price(self, symbol: str, price: float):
        """Update the current market price for a symbol."""
        self.current_prices[symbol] = price

    def get_balance(self) -> float:
        return self.cash

    def get_equity(self) -> float:
        equity = self.cash
        for symbol, pos in self.positions.items():
            current_price = self.current_prices.get(symbol, pos['avg_price'])
            
            # Calculate PnL in Quote Currency
            # Long: (Current - Avg) * Size
            # Short: (Avg - Current) * Size (Size is negative for short in this logic? Or we track side?)
            # Let's use signed size: + for Long, - for Short
            
            raw_pnl = (current_price - pos['avg_price']) * pos['size']
            
            # Convert to Account Currency
            converted_pnl = self._convert_currency(raw_pnl, symbol)
            equity += converted_pnl
            
        return equity

    def get_positions(self) -> dict:
        """
        Get open positions with PnL.
        Returns dict: {symbol: {'size': float, 'avg_price': float, 'pnl': float}}
        """
        result = {}
        for symbol, pos in self.positions.items():
            market_price = self.current_prices.get(symbol, pos['avg_price'])
            
            # Calculate PnL based on Closing Price
            if pos['size'] > 0: # Long
                # Close by Selling at Bid (Market Price)
                close_price = market_price 
            else: # Short
                # Determine Base Price
                base_price = self.override_price if self.override_price is not None else market_price
                
                # Close by Buying at Ask (Base Price + Spread)
                close_price = base_price * (1 + self.spread)
            
            # PnL = (Close - Entry) * Size
            # Long: (Bid - Entry) * Size
            # Short: (Ask - Entry) * -Size = (Entry - Ask) * Size (Wait, size is negative)
            # Let's check Short math:
            # Entry: 1.1000. Ask: 1.09815. Size: -10000.
            
            raw_pnl = (close_price - pos['avg_price']) * pos['size']
            converted_pnl = self._convert_currency(raw_pnl, symbol)
            
            result[symbol] = {
                'size': pos['size'],
                'avg_price': pos['avg_price'],
                'pnl': converted_pnl
            }
        return result 

    def get_position(self, symbol: str) -> float:
        """Return the size of the position for a symbol."""
        if symbol in self.positions:
            return self.positions[symbol]['size']
        return 0.0

    def get_cash(self) -> float:
        """Return available cash."""
        return self.cash

    def get_average_entry_price(self, symbol: str) -> float:
        """Return average entry price for a symbol."""
        if symbol in self.positions:
            return self.positions[symbol]['avg_price']
        return 0.0

    # ... (omitted methods) ...

    def set_entry_metadata(self, symbol: str, metadata: dict):
        """Store metadata at trade entry (time, ATR, etc). Merged into trade_history on close."""
        self._entry_metadata[symbol] = metadata

    def place_order(self, symbol: str, side: str, quantity: float, order_type: str = "market", price: float = None, stop_loss: float = None, take_profit: float = None, timestamp=None, exit_reason: str = None) -> dict:
        """
        Execute a simulated order.
        For MVP, we assume immediate fill at current price (Market).
        """
        # Defensive Type Casting
        try:
            quantity = float(quantity)
            if price is not None:
                price = float(price)
        except ValueError:
            print(f"Error: Invalid quantity or price for {symbol}. Qty: {quantity} ({type(quantity)}), Price: {price} ({type(price)})")
            return None

        if symbol not in self.current_prices:
            print(f"Error: No price data for {symbol}")
            return None

        market_price = self.current_prices[symbol]
        
        # Apply Spread
        # Buy at Ask (Market + Spread)
        # Sell at Bid (Market - Spread)
        # We assume 'market_price' is the Mid Price or Bid, so we adjust accordingly.
        # Determine Execution Price
        # If override is set (e.g. Next Open), use it. 
        # Otherwise use the requested price.
        # If requested price is None, use Market Price.
        if self.override_price is not None:
            base_price = self.override_price
        elif price is not None:
            base_price = price
        else:
            base_price = market_price
        
        if side == 'buy':
            fill_price = base_price * (1 + self.spread / 2)
        else:
            fill_price = base_price * (1 - self.spread / 2)

        if price and order_type == 'limit':
            fill_price = price # Limit orders might ignore spread logic in simple backtest, but let's keep it simple.
            
        # Update Position
        current_pos = self.positions.get(symbol, {'size': 0.0, 'avg_price': 0.0})
        old_size = current_pos['size']
        
        # LEVERAGE CAP: Prevent position value from exceeding equity (1x max leverage)
        # This protects against unrealistic backtesting results
        equity = self.get_equity()
        max_affordable_qty = equity / fill_price if fill_price > 0 else quantity
        capped_quantity = min(quantity, max_affordable_qty)
        
        if capped_quantity < quantity:
            # Silently cap (could add logging if desired)
            quantity = capped_quantity
        
        signed_qty = quantity if side == 'buy' else -quantity
        new_size = old_size + signed_qty
        
        # Calculate Realized PnL if reducing/closing
        realized_pnl = 0.0
        if (old_size > 0 and signed_qty < 0) or (old_size < 0 and signed_qty > 0):
            # Closing portion
            closed_qty = abs(signed_qty) if abs(signed_qty) <= abs(old_size) else abs(old_size)
            
            # PnL per unit
            price_diff = fill_price - current_pos['avg_price']
            if old_size < 0: # Short closing
                price_diff = current_pos['avg_price'] - fill_price
                
            raw_pnl = price_diff * closed_qty
            realized_pnl = self._convert_currency(raw_pnl, symbol)
            
            self.cash += realized_pnl
            
            # Record Trade (with entry metadata if available)
            trade_record = {
                'symbol': symbol,
                'side': side,
                'qty': closed_qty,
                'entry': current_pos['avg_price'],
                'exit': fill_price,
                'pnl': realized_pnl,
                'timestamp': timestamp,
                'exit_reason': exit_reason,
            }
            # Merge entry metadata (entry_time, atr_at_entry, etc)
            entry_meta = self._entry_metadata.pop(symbol, {})
            trade_record.update(entry_meta)
            self.trade_history.append(trade_record)

        # Update Avg Price (Weighted Average)
        if new_size != 0:
            if (old_size >= 0 and signed_qty > 0) or (old_size <= 0 and signed_qty < 0):
                # Increasing position
                total_value = (abs(old_size) * current_pos['avg_price']) + (abs(signed_qty) * fill_price)
                new_avg = total_value / abs(new_size)
                self.positions[symbol] = {'size': new_size, 'avg_price': new_avg}
            else:
                # Decreasing position (Avg price stays same until flip)
                if abs(signed_qty) > abs(old_size):
                    # Flipped position
                    remaining_flip = abs(new_size)
                    self.positions[symbol] = {'size': new_size, 'avg_price': fill_price}
                else:
                    # Just reduced
                    self.positions[symbol]['size'] = new_size
        else:
            if symbol in self.positions:
                del self.positions[symbol]

        order_record = {
            'id': str(uuid.uuid4()),
            'symbol': symbol,
            'side': side,
            'qty': quantity,
            'price': fill_price,
            'status': 'filled',
            'timestamp': timestamp
        }
        self.orders.append(order_record)
        return order_record

    def close_position(self, symbol: str, quantity: float = None) -> dict:
        if symbol not in self.positions:
            return None
        
        pos = self.positions[symbol]
        side = 'sell' if pos['size'] > 0 else 'buy'
        qty = quantity if quantity else abs(pos['size'])
        
        return self.place_order(symbol, side, qty)

    def _convert_currency(self, amount: float, symbol: str) -> float:
        """
        Convert amount from Quote Currency of 'symbol' to Account Currency.
        Example: 
        - Account: USD
        - Symbol: USDJPY (Quote: JPY)
        - Amount: 1000 JPY
        - Result: 1000 / USDJPY_Price = $6.66 USD
        """
        base = symbol[:3]
        quote = symbol[3:6]
        
        if quote == self.account_currency:
            return amount
            
        if base == self.account_currency:
            # e.g. USDJPY, Account USD. Quote JPY.
            # We have JPY amount. Need USD.
            # Rate USD/JPY = X.  1 USD = X JPY.  1 JPY = 1/X USD.
            # Amount (JPY) / Rate = Amount (USD)
            rate = self.current_prices.get(symbol)
            if rate:
                return amount / rate
                
        # Handle JPY Crosses (e.g. GBPJPY -> USD)
        if quote == 'JPY' and self.account_currency == 'USD':
            # Use a conservative static rate for verification
            # 1 USD = ~150 JPY.  1 JPY = 1/150 USD.
            # Amount (JPY) / 150 = Amount (USD)
            # TODO: Implement dynamic rate fetching for crosses
            return amount / 150.0
            
        # Fallback (Mock/Error)
        return amount 
