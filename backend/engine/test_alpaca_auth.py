from alpaca.trading.client import TradingClient
# from alpaca.trading.requests import GetAccountRequest
import os
from dotenv import load_dotenv

load_dotenv()

api_key = os.getenv('ALPACA_API_KEY')
secret_key = os.getenv('ALPACA_SECRET_KEY')
paper = True

print(f"Testing Auth with Key: {api_key}")

try:
    trading_client = TradingClient(api_key, secret_key, paper=paper)
    account = trading_client.get_account()
    print("Authentication Successful!")
    print(f"Account Status: {account.status}")
    print(f"Buying Power: {account.buying_power}")
    
except Exception as e:
    print(f"Authentication Failed: {e}")
