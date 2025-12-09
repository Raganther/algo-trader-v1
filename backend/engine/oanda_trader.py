import requests
import json
import time
from datetime import datetime
from backend.engine.broker_adapter import BrokerAdapter

class OandaTrader(BrokerAdapter):
    def __init__(self, api_key: str, account_id: str, environment: str = "practice"):
        """
        Initialize OandaTrader.
        environment: "practice" (Demo) or "live" (Real)
        """
        self.api_key = api_key
        self.account_id = account_id
        self.environment = environment
        
        if environment == "practice":
            self.base_url = "https://api-fxpractice.oanda.com/v3"
        else:
            self.base_url = "https://api-fxtrade.oanda.com/v3"
            
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        # Cache for positions to avoid spamming API
        self.positions_cache = {}
        self.last_update = 0

    def _request(self, method, endpoint, data=None):
        url = f"{self.base_url}{endpoint}"
        try:
            if method == "GET":
                response = requests.get(url, headers=self.headers)
            elif method == "POST":
                response = requests.post(url, headers=self.headers, json=data)
            elif method == "PUT":
                response = requests.put(url, headers=self.headers, json=data)
            else:
                raise ValueError(f"Unsupported method: {method}")
                
            response.raise_for_status()
            return response.json()
        except requests.exceptions.HTTPError as e:
            print(f"Oanda API Error: {e}")
            if e.response is not None:
                print(f"Response: {e.response.text}")
            return None
        except Exception as e:
            print(f"Request Error: {e}")
            return None

    def get_balance(self) -> float:
        """Get current account balance."""
        endpoint = f"/accounts/{self.account_id}/summary"
        data = self._request("GET", endpoint)
        if data and 'account' in data:
            return float(data['account']['balance'])
        return 0.0

    def get_equity(self) -> float:
        """Get current account equity (Balance + Unrealized PnL)."""
        endpoint = f"/accounts/{self.account_id}/summary"
        data = self._request("GET", endpoint)
        if data and 'account' in data:
            return float(data['account']['NAV']) # Net Asset Value
        return 0.0

    def get_positions(self) -> dict:
        """
        Get open positions.
        Returns dict: {symbol: {'size': float, 'avg_price': float, 'pnl': float}}
        """
        endpoint = f"/accounts/{self.account_id}/openPositions"
        data = self._request("GET", endpoint)
        
        positions = {}
        if data and 'positions' in data:
            for pos in data['positions']:
                symbol = pos['instrument'].replace("_", "") # Oanda uses EUR_USD, we use EURUSD
                
                # Net position (Long + Short)
                long_units = float(pos['long']['units'])
                short_units = float(pos['short']['units'])
                net_units = long_units + short_units
                
                if net_units != 0:
                    avg_price = 0.0
                    pnl = 0.0
                    
                    if long_units > 0:
                        avg_price = float(pos['long']['averagePrice'])
                        pnl += float(pos['long']['unrealizedPL'])
                    if short_units < 0:
                        avg_price = float(pos['short']['averagePrice'])
                        pnl += float(pos['short']['unrealizedPL'])
                        
                    positions[symbol] = {
                        'size': net_units,
                        'avg_price': avg_price,
                        'pnl': pnl
                    }
        return positions

    def place_order(self, symbol: str, side: str, size: float, order_type: str = "market", price: float = None, stop_loss: float = None, take_profit: float = None):
        """
        Place an order.
        symbol: e.g. "EURUSD" (will be converted to "EUR_USD")
        side: "buy" or "sell"
        size: quantity (e.g. 1000)
        """
        # Format symbol for Oanda (EURUSD -> EUR_USD)
        if "_" not in symbol and len(symbol) == 6:
             oanda_symbol = f"{symbol[:3]}_{symbol[3:]}"
        else:
            oanda_symbol = symbol
            
        units = int(size) if side.lower() == "buy" else -int(size)
        
        order_body = {
            "order": {
                "instrument": oanda_symbol,
                "units": str(units),
                "type": "MARKET", # Default to Market for now
                "positionFill": "DEFAULT"
            }
        }
        
        # Add SL/TP if provided
        if stop_loss:
            order_body["order"]["stopLossOnFill"] = {"price": f"{stop_loss:.5f}"}
        if take_profit:
            order_body["order"]["takeProfitOnFill"] = {"price": f"{take_profit:.5f}"}
            
        print(f"Sending Order to Oanda: {json.dumps(order_body, indent=2)}")
        
        endpoint = f"/accounts/{self.account_id}/orders"
        response = self._request("POST", endpoint, data=order_body)
        
        if response and 'orderFillTransaction' in response:
            fill = response['orderFillTransaction']
            print(f"Order Filled: {fill['id']} @ {fill['price']}")
            return True
        elif response and 'orderCreateTransaction' in response:
             print(f"Order Created (Pending): {response['orderCreateTransaction']['id']}")
             return True
        else:
            print("Order Failed.")
            return False

    def cancel_order(self, order_id: str):
        endpoint = f"/accounts/{self.account_id}/orders/{order_id}/cancel"
        self._request("PUT", endpoint)

    def update_price(self, symbol: str, price: float):
        # Oanda doesn't need manual price updates, it fetches live.
        pass
