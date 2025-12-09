from alpaca.trading.client import TradingClient
from alpaca.trading.requests import MarketOrderRequest
from alpaca.trading.enums import OrderSide, TimeInForce
import os
from dotenv import load_dotenv

load_dotenv()

api_key = os.getenv('ALPACA_API_KEY')
secret_key = os.getenv('ALPACA_SECRET_KEY')
paper = True

print(f"Testing Trade with Key: {api_key}")

try:
    trading_client = TradingClient(api_key, secret_key, paper=paper)
    
    # Check Buying Power
    account = trading_client.get_account()
    print(f"Buying Power: {account.buying_power}")
    
    # Place Market Order for BTC/USD
    symbol = "BTC/USD" 
    
    print(f"Placing Market Buy for {symbol}...")
    
    market_order_data = MarketOrderRequest(
        symbol=symbol,
        qty=0.01, # 0.01 BTC (~$900)
        side=OrderSide.BUY,
        time_in_force=TimeInForce.GTC
    )

    market_order = trading_client.submit_order(
        order_data=market_order_data
    )
    
    print("Order Submitted Successfully!")
    print(f"Order ID: {market_order.id}")
    print(f"Status: {market_order.status}")
    
except Exception as e:
    print(f"Trade Failed: {e}")
