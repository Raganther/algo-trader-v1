import os
from alpaca.trading.client import TradingClient
from alpaca.trading.requests import MarketOrderRequest, StopOrderRequest, GetOrdersRequest
from alpaca.trading.enums import OrderSide, TimeInForce, OrderStatus
from dotenv import load_dotenv

load_dotenv()

class AlpacaTrader:
    def __init__(self, paper=True):
        self.api_key = os.getenv('ALPACA_API_KEY')
        self.secret_key = os.getenv('ALPACA_SECRET_KEY')
        self.paper = paper
        
        if not self.api_key or not self.secret_key:
            raise ValueError("Alpaca API keys not found in .env")
            
        self.client = TradingClient(self.api_key, self.secret_key, paper=self.paper)

    def get_account_summary(self):
        """
        Returns a dictionary with account details:
        {
            'balance': float,
            'equity': float,
            'buying_power': float,
            'currency': str
        }
        """
        account = self.client.get_account()
        return {
            'balance': float(account.cash),
            'equity': float(account.equity),
            'buying_power': float(account.buying_power),
            'currency': account.currency
        }

    def get_open_trades(self):
        """
        Returns a list of open positions.
        """
        positions = self.client.get_all_positions()
        trades = []
        for pos in positions:
            trades.append({
                'symbol': pos.symbol,
                'qty': float(pos.qty),
                'entry_price': float(pos.avg_entry_price),
                'current_price': float(pos.current_price),
                'pnl': float(pos.unrealized_pl),
                'side': 'buy' if float(pos.qty) > 0 else 'sell' # Alpaca uses positive/negative qty for long/short? 
                                                                # Actually, Alpaca has 'side' in orders, but positions just have qty.
                                                                # Usually long is positive, short is negative.
            })
        return trades

    def get_position(self, symbol):
        """
        Returns the quantity of the position for a specific symbol.
        Returns 0 if no position exists.
        """
        try:
            # Clean symbol (BTC/USD -> BTCUSD)
            clean_symbol = symbol.replace('/', '')
            pos = self.client.get_open_position(clean_symbol)
            return float(pos.qty)
        except Exception as e:
            # Alpaca raises an error if no position exists
            # print(f"DEBUG: get_position error: {e}") 
            return 0.0

    def get_cash(self):
        """Return available cash."""
        return self.get_account_summary()['balance']

    def get_average_entry_price(self, symbol):
        """
        Returns the average entry price for a specific symbol.
        Returns 0.0 if no position exists.
        """
        try:
            clean_symbol = symbol.replace('/', '')
            pos = self.client.get_open_position(clean_symbol)
            return float(pos.avg_entry_price)
        except Exception:
            return 0.0

    def place_order(self, symbol, qty, side, order_type='market', time_in_force='gtc', stop_loss=None, take_profit=None):
        """
        Place a simple market order.
        stop_loss/take_profit params are ignored here — use place_stop_order() separately
        (Alpaca doesn't support bracket orders with fractional shares).
        """
        alpaca_side = OrderSide.BUY if side.lower() == 'buy' else OrderSide.SELL
        clean_symbol = symbol.replace('/', '')

        is_crypto = '/' in symbol
        if not is_crypto:
            qty = round(qty, 4)
            alpaca_tif = TimeInForce.DAY
        else:
            alpaca_tif = TimeInForce.GTC

        req = MarketOrderRequest(
            symbol=clean_symbol,
            qty=qty,
            side=alpaca_side,
            time_in_force=alpaca_tif
        )

        order = self.client.submit_order(order_data=req)
        return {
            'id': str(order.id),
            'status': order.status,
            'symbol': order.symbol,
            'qty': float(order.qty) if order.qty else 0.0
        }

    def place_stop_order(self, symbol, qty, side, stop_price):
        """Place a standalone stop order (for server-side stop losses with fractional shares)."""
        clean_symbol = symbol.replace('/', '')
        alpaca_side = OrderSide.BUY if side.lower() == 'buy' else OrderSide.SELL
        is_crypto = '/' in symbol
        qty = round(qty, 4) if not is_crypto else qty
        # GTC so stop orders persist overnight (DAY expires at market close)
        alpaca_tif = TimeInForce.GTC

        req = StopOrderRequest(
            symbol=clean_symbol,
            qty=qty,
            side=alpaca_side,
            time_in_force=alpaca_tif,
            stop_price=round(stop_price, 2)
        )
        order = self.client.submit_order(order_data=req)
        return {
            'id': str(order.id),
            'status': order.status,
            'symbol': order.symbol,
            'qty': float(order.qty) if order.qty else 0.0
        }

    def cancel_order(self, order_id):
        """Cancel an order by ID. Returns True on success."""
        try:
            self.client.cancel_order_by_id(order_id)
            return True
        except Exception as e:
            print(f"⚠️ Cancel order {order_id} failed: {e}")
            return False

    def cancel_all_orders_for_symbol(self, symbol):
        """Cancel all open orders for a specific symbol. Returns count cancelled."""
        try:
            request = GetOrdersRequest(status='open', symbols=[symbol])
            orders = self.client.get_orders(filter=request)
            cancelled = 0
            for order in orders:
                try:
                    self.client.cancel_order_by_id(order.id)
                    cancelled += 1
                except Exception:
                    pass  # Order may have already filled/cancelled
            return cancelled
        except Exception as e:
            print(f"⚠️ Cancel all orders for {symbol} failed: {e}")
            return 0

    def close_trade(self, symbol):
        """
        Close all positions for a symbol.
        """
        self.client.close_position(symbol)
        return True

    def close_all_trades(self):
        """
        Close all open positions.
        """
        self.client.close_all_positions(cancel_orders=True)
        return True

    def get_order(self, order_id):
        """
        Get order details by ID.
        """
        try:
            order = self.client.get_order_by_id(order_id)
            return {
                'id': str(order.id),
                'status': order.status,
                'filled_avg_price': float(order.filled_avg_price) if order.filled_avg_price else None,
                'filled_qty': float(order.filled_qty) if order.filled_qty else 0.0,
                'created_at': order.created_at.isoformat() if order.created_at else None,
                'filled_at': order.filled_at.isoformat() if order.filled_at else None
            }
        except Exception as e:
            print(f"Error fetching order {order_id}: {e}")
            return None
