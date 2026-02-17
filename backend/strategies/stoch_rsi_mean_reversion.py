from backend.engine.strategy import Strategy
from backend.indicators.stoch_rsi import StochRSI
from backend.indicators.adx import adx
from backend.indicators.atr import atr
import pandas as pd
from datetime import timedelta

class StochRSIMeanReversionStrategy(Strategy):
    def __init__(self, data, events, parameters, initial_cash=10000.0, broker=None):
        super().__init__(data, events, parameters, initial_cash, broker)
        
        # Extract Parameters with Defaults
        self.rsi_period = int(parameters.get('rsi_period', 14))
        self.stoch_period = int(parameters.get('stoch_period', 14))
        self.k_period = int(parameters.get('k_period', 3))
        self.d_period = int(parameters.get('d_period', 3))
        self.overbought = float(parameters.get('overbought', 50))  # EXTREME testing: 50 (trades every reversal)
        self.oversold = float(parameters.get('oversold', 50))  # EXTREME testing: 50 (trades every reversal)
        self.adx_threshold = float(parameters.get('adx_threshold', 50))  # EXTREME testing: 50 (almost no filter)
        self.dynamic_adx = parameters.get('dynamic_adx', True) # Default to True for backward compatibility
        self.position_size = float(parameters.get('position_size', 100000.0))
        self.sl_atr = float(parameters.get('sl_atr', 3.0))
        
        self.skip_adx_filter = parameters.get('skip_adx_filter', True)  # Default True for forward testing validation
        self.atr_col = parameters.get('atr_col', 'atr')
        self.symbol = parameters.get('symbol', 'Unknown')

        # Enhancement params (all off by default — no impact on existing behaviour)
        self.skip_days = parameters.get('skip_days', [])  # e.g. [0] to skip Monday (0=Mon, 4=Fri)
        self.trading_hours = parameters.get('trading_hours', [])  # e.g. [14, 21] = only trade 14:00-21:00 UTC
        self.trailing_stop = parameters.get('trailing_stop', False)  # Enable trailing stop
        self.trail_after_bars = int(parameters.get('trail_after_bars', 0))  # Start trailing after N bars in profit
        self.trail_atr = float(parameters.get('trail_atr', self.sl_atr))  # Trailing ATR multiplier
        self.min_hold_bars = int(parameters.get('min_hold_bars', 0))  # Minimum bars before signal exit allowed
        self.event_blackout_hours = int(parameters.get('event_blackout_hours', 0))  # Skip entries within N hours of high-impact event (0=off)
        self.blackout_times = set()  # precomputed set of bar timestamps in blackout windows

        # Precompute blackout bar timestamps if enabled
        if self.event_blackout_hours > 0:
            event_times = parameters.get('_event_times', set())  # injected by runner
            if event_times and data is not None and not data.empty:
                buffer = timedelta(hours=self.event_blackout_hours)
                # Normalize all timestamps to tz-naive for comparison
                has_tz = data.index.tz is not None
                bar_times = set(data.index.tz_localize(None)) if has_tz else set(data.index)
                for evt in event_times:
                    evt_ts = pd.Timestamp(evt)
                    if evt_ts.tzinfo is not None:
                        evt_ts = evt_ts.tz_localize(None)
                    for bt in bar_times:
                        if abs(bt - evt_ts) <= buffer:
                            # Store in original form (with tz if data has tz) for on_bar lookup
                            if has_tz:
                                self.blackout_times.add(bt.tz_localize(data.index.tz))
                            else:
                                self.blackout_times.add(bt)
                print(f"[EVENT BLACKOUT] {len(self.blackout_times)} bars in blackout zones ({self.event_blackout_hours}h buffer, {len(event_times)} events)")

        # State
        self.in_oversold_zone = False
        self.in_overbought_zone = False
        self.bar_index = 0
        self.current_sl = None
        self.entry_bar = None  # bar index at entry (for duration calc)
        self.entry_price = None  # for trailing stop breakeven check
        
        self.generate_signals(self.data)

    def generate_signals(self, df: pd.DataFrame):
        # 1. Calculate Indicators Iteratively
        stoch = StochRSI(self.rsi_period, self.stoch_period, self.k_period, self.d_period)
        k_values = []
        d_values = []
        
        for price in df['Close']:
            stoch.update(price)
            k_values.append(stoch.k if stoch.ready else None)
            d_values.append(stoch.d if stoch.ready else None)
            
        adx_series = adx(df['High'], df['Low'], df['Close'], 14)
        atr_series = atr(df['High'], df['Low'], df['Close'], 14)
        
        # Add to DataFrame
        df['k'] = k_values
        df['d'] = d_values
        df['adx'] = adx_series
        df[self.atr_col] = atr_series
        
        # Fill NaNs for safety
        df['k'] = df['k'].fillna(50)
        df['d'] = df['d'].fillna(50)
        
        return df

    def on_data(self, index, row):
        # Delegate to on_bar logic
        # We need the full dataframe for indicators, which is self.data
        # 'index' is the DataFrame TimeSeries index - use bar_index for integer position
        self.on_bar(row, self.bar_index, self.data)
        self.bar_index += 1

    def on_event(self, event):
        # No event handling logic for now
        pass

    def on_bar(self, row, i, df):
        # Skip if not enough data (use passed index, not self.bar_index for paper trading)
        if i < 50: return

        current_k = row['k']
        # Use .iloc for previous row access using passed integer position
        prev_k = df.iloc[i-1]['k']
        current_adx = row['adx']

        # Print every bar for monitoring (FORWARD TESTING VISIBILITY)
        print(f"[{row.name}] {self.symbol} ${row['Close']:.2f} | K: {current_k:.1f} (prev: {prev_k:.1f}) | ADX: {current_adx:.1f}")

        # Day-of-week filter (skip entries on specified days, but allow exits)
        skip_entry = False
        if self.skip_days and hasattr(row.name, 'dayofweek'):
            if row.name.dayofweek in self.skip_days:
                skip_entry = True

        # Hour-of-day filter (skip entries outside trading hours, but allow exits)
        if self.trading_hours and hasattr(row.name, 'hour') and len(self.trading_hours) == 2:
            start_hour, end_hour = self.trading_hours
            if not (start_hour <= row.name.hour < end_hour):
                skip_entry = True

        # Event blackout filter (skip entries near high-impact economic events, but allow exits)
        if self.event_blackout_hours > 0 and row.name in self.blackout_times:
            skip_entry = True

        # Trailing stop update (move stop to lock in profits)
        if self.trailing_stop and self.entry_bar is not None and self.current_sl is not None:
            bars_held = i - self.entry_bar
            atr_val = row[self.atr_col]
            if bars_held >= self.trail_after_bars and atr_val > 0:
                if self.position == 'long':
                    new_sl = row['Close'] - (atr_val * self.trail_atr)
                    if new_sl > self.current_sl:
                        self.current_sl = new_sl
                elif self.position == 'short':
                    new_sl = row['Close'] + (atr_val * self.trail_atr)
                    if new_sl < self.current_sl:
                        self.current_sl = new_sl

        # Regime Filter: Only trade if Market is Ranging (ADX < Threshold)
        # Skip this check when called from HybridRegime (which already filtered by ADX)
        if not self.skip_adx_filter:
            # --- Adaptive Logic ---
            if self.dynamic_adx:
                # Calculate ATR % (Volatility)
                # atr_val is already calculated in generate_signals
                atr_val = row[self.atr_col]
                close_price = row['Close']
                
                if close_price > 0:
                    atr_pct = (atr_val / close_price) * 100
                else:
                    atr_pct = 0
                    
                # Determine Threshold based on Volatility
                # If Volatility is High (> 0.12%), be Defensive (Threshold 20)
                # If Volatility is Low (<= 0.12%), be Aggressive (Threshold 30)
                if atr_pct > 0.12:
                    dynamic_threshold = 20
                else:
                    dynamic_threshold = 30
                    
                # Use the dynamic threshold
                if current_adx > dynamic_threshold:
                    # Market is trending too strongly for the current regime
                    return
            else:
                # Static Threshold (Strict Filter)
                if current_adx > self.adx_threshold:
                    return

        # 0. Check Stop Loss (Priority)
        if self.position == 'long' and self.current_sl:
            if row['Low'] <= self.current_sl:
                # SL Hit
                qty = abs(self.broker.get_position(self.symbol))
                if qty > 0:
                    result = self.sell(price=self.current_sl, size=qty, timestamp=i, exit_reason='stop')
                    if result is not None:
                        self.position = 0
                        self.current_sl = None
                        self.entry_bar = None
                return # Exit logic done

        elif self.position == 'short' and self.current_sl:
            if row['High'] >= self.current_sl:
                # SL Hit
                qty = abs(self.broker.get_position(self.symbol))
                if qty > 0:
                    result = self.buy(price=self.current_sl, size=qty, timestamp=i, exit_reason='stop')
                    if result is not None:
                        self.position = 0
                        self.current_sl = None
                        self.entry_bar = None
                return # Exit logic done

        # Entry Logic
        if self.position == 0: # 0 means flat
            # Long Setup
            if prev_k <= self.oversold:  # Fixed: <= instead of < to include exact threshold
                self.in_oversold_zone = True

            if self.in_oversold_zone and current_k > 50 and not skip_entry:
                # Dynamic Sizing
                equity = self.broker.get_equity()
                risk_amt = equity * 0.02 # 2% Risk
                atr_val = row[self.atr_col]
                stop_dist = atr_val * self.sl_atr

                if stop_dist > 0:
                    size = risk_amt / stop_dist

                    # Cap to 25% of equity per position (leaves room for multiple positions + fees)
                    max_size = (equity * 0.25) / row['Close']
                    size = min(size, max_size)
                    size = round(size, 4)

                    self.current_sl = row['Close'] - stop_dist
                    result = self.buy(price=row['Close'], size=size, timestamp=i, stop_loss=self.current_sl)
                    # Only update position state if order was actually executed
                    if result is not None:
                        self.in_oversold_zone = False
                        self.position = 'long'
                        self.entry_bar = i
                        self.entry_price = row['Close']
                        if hasattr(self.broker, 'set_entry_metadata'):
                            self.broker.set_entry_metadata(self.symbol, {
                                'entry_time': str(row.name),
                                'entry_bar': i,
                                'entry_hour': row.name.hour if hasattr(row.name, 'hour') else None,
                                'entry_dow': row.name.dayofweek if hasattr(row.name, 'dayofweek') else None,
                                'atr_at_entry': float(atr_val),
                                'direction': 'long',
                            })

            if current_k > 50:
                self.in_oversold_zone = False

            # Short Setup (skip for crypto — Alpaca doesn't support crypto shorting)
            is_crypto = '/' in self.symbol
            if not is_crypto and prev_k >= self.overbought:  # Fixed: >= instead of > to include exact threshold
                self.in_overbought_zone = True

            if self.in_overbought_zone and current_k < 50 and not skip_entry:
                # Dynamic Sizing
                equity = self.broker.get_equity()
                risk_amt = equity * 0.02
                atr_val = row[self.atr_col]
                stop_dist = atr_val * self.sl_atr

                if stop_dist > 0:
                    size = risk_amt / stop_dist

                    # Cap to 25% of equity per position (leaves room for multiple positions + fees)
                    max_size = (equity * 0.25) / row['Close']
                    size = min(size, max_size)
                    size = round(size, 4)

                    self.current_sl = row['Close'] + stop_dist
                    result = self.sell(price=row['Close'], size=size, timestamp=i, stop_loss=self.current_sl)
                    # Only update position state if order was actually executed
                    if result is not None:
                        self.in_overbought_zone = False
                        self.position = 'short'
                        self.entry_bar = i
                        self.entry_price = row['Close']
                        if hasattr(self.broker, 'set_entry_metadata'):
                            self.broker.set_entry_metadata(self.symbol, {
                                'entry_time': str(row.name),
                                'entry_bar': i,
                                'entry_hour': row.name.hour if hasattr(row.name, 'hour') else None,
                                'entry_dow': row.name.dayofweek if hasattr(row.name, 'dayofweek') else None,
                                'atr_at_entry': float(atr_val),
                                'direction': 'short',
                            })

            if current_k < 50:
                self.in_overbought_zone = False

        # Exit Logic (Signal Based) — respect min_hold_bars
        elif self.position == 'long':
            bars_held = (i - self.entry_bar) if self.entry_bar is not None else 999
            if current_k > self.overbought and bars_held >= self.min_hold_bars:
                qty = abs(self.broker.get_position(self.symbol))
                if qty > 0:
                    result = self.sell(price=row['Close'], size=qty, timestamp=i, exit_reason='signal')
                    if result is not None:
                        self.position = 0
                        self.current_sl = None
                        self.entry_bar = None
                        self.entry_price = None

        elif self.position == 'short':
            bars_held = (i - self.entry_bar) if self.entry_bar is not None else 999
            if current_k < self.oversold and bars_held >= self.min_hold_bars:
                qty = abs(self.broker.get_position(self.symbol))
                if qty > 0:
                    result = self.buy(price=row['Close'], size=qty, timestamp=i, exit_reason='signal')
                    if result is not None:
                        self.position = 0
                        self.current_sl = None
                        self.entry_bar = None
                        self.entry_price = None
