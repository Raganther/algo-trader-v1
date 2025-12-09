from backend.engine.paper_trader import PaperTrader

def test_paper_trader():
    print("--- Testing Paper Trader ---")
    
    # 1. Initialize
    trader = PaperTrader(initial_balance=10000.0, account_currency="USD")
    print(f"Initial Balance: ${trader.get_balance()}")
    
    # 2. Test USDJPY Trade (Currency Mismatch)
    symbol = "USDJPY=X"
    current_price = 150.00
    trader.update_price(symbol, current_price)
    
    print(f"\n--- Buying 1000 {symbol} @ {current_price} ---")
    trader.place_order(symbol, 'buy', 1000, price=current_price)
    
    pos = trader.get_positions()[symbol]
    print(f"Position: {pos}")
    
    # 3. Simulate Price Move (Profit)
    # Price moves to 151.00 (+1.00 JPY per unit)
    # Total PnL (JPY) = 1.00 * 1000 = 1000 JPY
    # Expected PnL (USD) = 1000 JPY / 151.00 = $6.62 USD
    new_price = 151.00
    trader.update_price(symbol, new_price)
    
    equity = trader.get_equity()
    unrealized_pnl = equity - 10000.0
    print(f"\nPrice moved to {new_price}")
    print(f"Equity: ${equity:.2f}")
    print(f"Unrealized PnL (USD): ${unrealized_pnl:.2f}")
    
    expected_pnl = (1000) / 151.00
    print(f"Expected PnL (USD): ${expected_pnl:.2f}")
    
    if abs(unrealized_pnl - expected_pnl) < 0.01:
        print("PASS: Currency Conversion Logic Verified")
    else:
        print("FAIL: Currency Conversion Mismatch")

    # 4. Close Position
    print(f"\n--- Closing Position @ {new_price} ---")
    trader.close_position(symbol)
    
    final_balance = trader.get_balance()
    print(f"Final Balance: ${final_balance:.2f}")
    
    if abs(final_balance - (10000.0 + expected_pnl)) < 0.01:
        print("PASS: Realized PnL Verified")
    else:
        print("FAIL: Realized PnL Mismatch")

if __name__ == "__main__":
    test_paper_trader()
