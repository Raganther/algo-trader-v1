import os
from alpaca.trading.client import TradingClient
from alpaca.trading.requests import MarketOrderRequest, GetOrdersRequest
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

    def place_order(self, symbol, qty, side, order_type='market', time_in_force='gtc', stop_loss=None, take_profit=None):
        """
        Place an order with optional Bracket (Stop Loss / Take Profit).
        side: 'buy' or 'sell'
        stop_loss: float price
        take_profit: float price
        """
        alpaca_side = OrderSide.BUY if side.lower() == 'buy' else OrderSide.SELL
        alpaca_tif = TimeInForce.GTC # Default
        
        # Clean symbol (BTC/USD -> BTCUSD)
        clean_symbol = symbol.replace('/', '')

        if time_in_force.lower() == 'day':
            alpaca_tif = TimeInForce.DAY
            
        # Construct Order Request
        req_params = {
            "symbol": clean_symbol,
            "qty": qty,
            "side": alpaca_side,
            "time_in_force": alpaca_tif
        }
        
        # Add Bracket Logic
        if stop_loss or take_profit:
            # Bracket orders must be GTC usually, but Alpaca handles it.
            # We use the 'order_class' parameter for brackets if using the advanced API,
            # but the python SDK has specific helpers.
            # Actually, MarketOrderRequest has stop_loss and take_profit dicts.
            
            if stop_loss:
                req_params["stop_loss"] = {"stop_price": stop_loss}
            
            if take_profit:
                req_params["take_profit"] = {"limit_price": take_profit}
                
        req = MarketOrderRequest(**req_params)
        
        order = self.client.submit_order(order_data=req)
        return {
            'id': str(order.id),
            'status': order.status,
            'symbol': order.symbol,
            'qty': float(order.qty) if order.qty else 0.0
        }

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
