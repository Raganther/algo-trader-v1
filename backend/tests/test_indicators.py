import unittest
import pandas as pd
import numpy as np
from backend.indicators.sma import sma
from backend.indicators.atr import atr
from backend.indicators.donchian import donchian_channels

class TestIndicators(unittest.TestCase):
    def setUp(self):
        # Create sample data
        self.data = pd.DataFrame({
            'High': [10, 12, 11, 13, 15, 14, 16, 18, 17, 19],
            'Low':  [ 8,  9,  9, 10, 12, 11, 13, 15, 14, 16],
            'Close':[ 9, 11, 10, 12, 14, 13, 15, 17, 16, 18]
        })
        
    def test_sma(self):
        # Simple 3-period SMA
        # [9, 11, 10] -> 10
        # [11, 10, 12] -> 11
        result = sma(self.data['Close'], 3)
        self.assertAlmostEqual(result.iloc[2], 10.0)
        self.assertAlmostEqual(result.iloc[3], 11.0)
        
    def test_donchian(self):
        # Entry Period 3, Exit Period 2
        # Highs: [10, 12, 11, 13]
        # Lows:  [ 8,  9,  9, 10]
        # Upper Entry (Shift 1): Max of prev 3. 
        # Index 3 (Value 13): Prev 3 are [10, 12, 11]. Max=12.
        
        result = donchian_channels(self.data['High'], self.data['Low'], 3, 2)
        
        # Check Upper Entry at index 3
        self.assertEqual(result['upper_entry'].iloc[3], 12.0)
        
        # Check Lower Entry at index 3
        # Prev 3 Lows: [8, 9, 9]. Min=8.
        self.assertEqual(result['lower_entry'].iloc[3], 8.0)
        
    def test_atr(self):
        # Just check it runs and returns correct shape
        result = atr(self.data['High'], self.data['Low'], self.data['Close'], 3)
        self.assertEqual(len(result), 10)
        self.assertTrue(np.isnan(result.iloc[0])) # First few should be NaN

if __name__ == '__main__':
    unittest.main()
