import unittest
from backend.engine.paper_trader import PaperTrader

class TestPaperTraderLogic(unittest.TestCase):
    def setUp(self):
        # Initialize with $10,000 and 1.5 pip spread (0.00015)
        self.spread = 0.00015
        self.broker = PaperTrader(initial_balance=10000.0, spread=self.spread)
        self.symbol = "EURUSD"

    def test_spread_application_buy(self):
        """Test that buying applies the spread (Buy at Ask = Price + Spread)"""
        market_price = 1.10000
        self.broker.update_price(self.symbol, market_price) # Set market price first
        
        # Buy 10,000 units
        self.broker.place_order(self.symbol, "buy", 10000, price=market_price)
        
        position = self.broker.get_positions()[self.symbol]
        expected_price = market_price + self.spread # 1.10015
        
        self.assertAlmostEqual(position['avg_price'], expected_price, places=5, 
                               msg=f"Buy price should include spread. Got {position['avg_price']}, expected {expected_price}")

    def test_spread_application_sell(self):
        """Test that selling applies the spread (Sell at Bid = Price)"""
        market_price = 1.10000
        self.broker.update_price(self.symbol, market_price)
        
        self.broker.place_order(self.symbol, "sell", 10000, price=market_price)
        
        position = self.broker.get_positions()[self.symbol]
        expected_price = market_price # 1.10000 (Selling at Bid)
        
        self.assertAlmostEqual(position['avg_price'], expected_price, places=5,
                               msg=f"Sell price should be at Bid (Market Price). Got {position['avg_price']}, expected {expected_price}")

    def test_pnl_calculation_long(self):
        """Test PnL for a Long position"""
        entry_price = 1.10000
        self.broker.update_price(self.symbol, entry_price)
        
        # Buy executes at 1.10015 (with spread)
        self.broker.place_order(self.symbol, "buy", 10000, price=entry_price)
        
        # Price moves up to 1.10215 (20 pips above entry cost)
        current_price = 1.10215 
        self.broker.update_price(self.symbol, current_price)
        
        position = self.broker.get_positions()[self.symbol]
        # Entry Cost: 1.10015
        # Current Value (Bid): 1.10215
        # Diff: +0.00200 (20 pips)
        # Value: 20 pips * 10,000 units = $20
        
        expected_pnl = (current_price - (entry_price + self.spread)) * 10000
        
        self.assertAlmostEqual(position['pnl'], expected_pnl, places=2,
                               msg=f"Long PnL incorrect. Got {position['pnl']}, expected {expected_pnl}")

    def test_pnl_calculation_short(self):
        """Test PnL for a Short position"""
        entry_price = 1.10000
        self.broker.update_price(self.symbol, entry_price)
        
        # Sell executes at 1.10000 (Bid)
        self.broker.place_order(self.symbol, "sell", 10000, price=entry_price)
        
        # Price drops to 1.09800 (20 pips profit)
        current_price = 1.09800
        self.broker.update_price(self.symbol, current_price)
        
        position = self.broker.get_positions()[self.symbol]
        
        # Entry: 1.10000
        # Exit Cost (Ask): 1.09800 + 0.00015 = 1.09815
        # Diff: 1.10000 - 1.09815 = 0.00185 (18.5 pips)
        # Profit: 0.00185 * 10,000 = $18.50
        
        expected_pnl = (entry_price - (current_price + self.spread)) * 10000
        
        self.assertAlmostEqual(position['pnl'], expected_pnl, places=2,
                               msg=f"Short PnL incorrect. Got {position['pnl']}, expected {expected_pnl}")

    def test_equity_update(self):
        """Test that Equity = Balance + Unrealized PnL"""
        self.broker.update_price(self.symbol, 1.10000)
        self.broker.place_order(self.symbol, "buy", 10000, price=1.10000)
        # Entry at 1.10015.
        # Immediate PnL at 1.10000 (Bid) = 1.10000 - 1.10015 = -0.00015 (-1.5 pips spread cost)
        # Loss = $1.50
        
        self.broker.update_price(self.symbol, 1.10000)
        
        equity = self.broker.get_equity()
        balance = self.broker.get_balance() # 10000
        
        expected_equity = 10000.0 - 1.50
        
        self.assertAlmostEqual(equity, expected_equity, places=2,
                               msg=f"Equity should reflect spread cost immediately. Got {equity}, expected {expected_equity}")

if __name__ == '__main__':
    unittest.main()
