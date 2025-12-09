from backend.engine.strategy import Strategy
from backend.data.news_data_loader import NewsDataLoader
from backend.indicators.atr import atr
import pandas as pd
import numpy as np

class NFPBreakoutStrategy(Strategy):
    def __init__(self, data: pd.DataFrame, events: pd.DataFrame = None, parameters: dict = {}, initial_cash: float = 10000.0, broker=None):
        super().__init__(data, events, parameters, initial_cash, broker)
        
        # Parameters
        self.symbol = parameters.get('symbol', 'Unknown')
        self.buffer_pips = parameters.get('buffer_pips', 5)
        self.risk_pct = parameters.get('risk_pct', 0.02)
        self.trend_period = parameters.get('trend_period', 200)
        self.pip_value = 0.0001 if 'JPY' not in self.symbol else 0.01
        
        # Pre-calculate SMA and ATR
        self.sma_series = data['Close'].rolling(window=self.trend_period).mean()
        
        # Calculate ATR(14) and ATR(50) for Volatility Filter
        # Note: Our modular 'atr' function returns a Series (not DataFrame)
        self.atr_14 = atr(data['High'], data['Low'], data['Close'], 14)
        self.atr_50 = atr(data['High'], data['Low'], data['Close'], 50)
        
        # Load NFP Dates
        loader = NewsDataLoader()
        # Get year range from data
        start_year = data.index[0].year
        end_year = data.index[-1].year
        self.nfp_dates = loader.load_nfp_dates(start_year, end_year)
        
        # Convert to set for fast lookup (round to hour/minute if needed)
        # We need to match the exact candle time. 
        # NFP is usually 12:30 UTC or 13:30 UTC depending on DST.
        # We will check if the current candle *contains* the NFP release.
        
        self.pending_orders = {} # { 'buy_stop': price, 'sell_stop': price, 'stop_loss': price }
        self.trade_active = False

    def on_data(self, index, row):
        # 1. Check if we are in a trade
        positions = self.broker.get_positions()
        position = positions.get(self.symbol)
        current_qty = position['size'] if position else 0
        
        # Exit at End of Day (21:00 UTC approx)
        if current_qty != 0:
            if index.hour >= 21:
                self.broker.place_order(self.symbol, 'sell' if current_qty > 0 else 'buy', abs(current_qty), row['Close'], timestamp=index)
                self.trade_active = False
                return

        # 2. Check for NFP Event
        # We want to identify the "News Candle".
        # Let's say we trade the breakout of the 15m candle that *contains* the release.
        # Release is usually at minute 30.
        
        is_nfp_candle = False
        for nfp_time in self.nfp_dates:
            # Check if nfp_time is within this candle's duration
            # Ensure index is tz-aware for comparison
            current_time = index
            if current_time.tzinfo is None:
                current_time = current_time.tz_localize('UTC')
            
            if current_time <= nfp_time < current_time + pd.Timedelta(minutes=15):
                is_nfp_candle = True
                break
        
        if is_nfp_candle and current_qty == 0:
            # Define Breakout Levels
            high = row['High']
            low = row['Low']
            
            buy_trigger = high + (self.buffer_pips * self.pip_value)
            sell_trigger = low - (self.buffer_pips * self.pip_value)
            
            # Store for NEXT candle execution (simulating stop orders)
            self.pending_orders = {
                'buy_stop': buy_trigger,
                'sell_stop': sell_trigger,
                'high': high,
                'low': low,
                'expires': index + pd.Timedelta(hours=4) # Orders valid for 4 hours
            }
            return

        # 3. Check Pending Orders (Breakout Execution)
        if self.pending_orders and current_qty == 0:
            # Check Expiry
            if index > self.pending_orders['expires']:
                self.pending_orders = {}
                return

            buy_level = self.pending_orders['buy_stop']
            sell_level = self.pending_orders['sell_stop']
            
            # Trend Filter (SMA)
            # We need enough history. If not enough, skip filter (or skip trade).
            # Let's use a rolling window if available, or just calculate on the fly.
            # Since on_data is called row by row, we can't easily do rolling(200) here efficiently without full history access.
            # However, Backtester passes 'data' to init. We can pre-calculate SMA there!
            
            # See __init__ for pre-calculation.
            # Here we just look up the SMA value for the current timestamp.
            
            current_sma = self.sma_series.get(index)
            current_atr_14 = self.atr_14.get(index)
            current_atr_50 = self.atr_50.get(index)
            
            # If SMA or ATR is missing, skip
            if pd.isna(current_sma) or pd.isna(current_atr_14) or pd.isna(current_atr_50):
                return

            # Volatility Filter: Trade ONLY if ATR(14) < ATR(50) (Compression)
            if current_atr_14 >= current_atr_50:
                return

            # Check for Breakout with Trend Filter
            
            # Long Breakout (Only if Price > SMA)
            if row['High'] > buy_level:
                if row['Close'] > current_sma: # Trend Filter
                    # Calculate Risk
                    stop_loss = self.pending_orders['low'] 
                    risk_per_share = buy_level - stop_loss
                    if risk_per_share > 0:
                        qty = self._calculate_position_size(buy_level, risk_per_share)
                        self.broker.place_order(self.symbol, 'buy', qty, buy_level, timestamp=index)
                        self.trade_active = True
                        self.pending_orders = {} 
                        return

            # Short Breakout (Only if Price < SMA)
            if row['Low'] < sell_level:
                if row['Close'] < current_sma: # Trend Filter
                    # Calculate Risk
                    stop_loss = self.pending_orders['high']
                    risk_per_share = stop_loss - sell_level
                    if risk_per_share > 0:
                        qty = self._calculate_position_size(sell_level, risk_per_share)
                        self.broker.place_order(self.symbol, 'sell', qty, sell_level, timestamp=index)
                        self.trade_active = True
                        self.pending_orders = {}
                        return

    def _calculate_position_size(self, entry_price, risk_per_share):
        account_value = self.broker.get_equity()
        risk_amount = account_value * self.risk_pct
        return int(risk_amount / risk_per_share)

    def on_event(self, event):
        pass
