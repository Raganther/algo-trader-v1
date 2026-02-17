"""
EventSurpriseStrategy — Trade gold based on economic data surprise direction.

Enters GLD trades when key economic releases (CPI, NFP, Unemployment) show
significant surprises vs forecast. Uses delayed entry (post-event-bar) and
time-based exits.

Key finding from diagnostics:
- CPI miss -> gold UP: +0.80% avg 1h move, 93% correct direction (delayed entry)
- NFP beat -> gold DOWN: +0.37% avg, 55% correct (weaker)
- Unemployment miss -> gold DOWN: +0.52%, 64% correct (moderate)
"""

from backend.engine.strategy import Strategy
from backend.engine.data_loader import DataLoader
from backend.indicators.atr import atr
import pandas as pd
import numpy as np
import bisect
from collections import defaultdict


# Direction mapping: what gold does when the indicator BEATS forecast
# Beat = actual > forecast (except unemployment where higher = worse)
EVENT_DIRECTION = {
    'Non-Farm Employment Change': {'beat_gold_dir': 'down'},  # Strong jobs = strong USD = gold down
    'CPI m/m':                    {'beat_gold_dir': 'down'},  # High inflation = hawkish Fed = gold down (short-term)
    'Core CPI m/m':               {'beat_gold_dir': 'down'},
    'CPI y/y':                    {'beat_gold_dir': 'down'},
    'Unemployment Rate':          {'beat_gold_dir': 'up'},    # Higher unemployment = weak USD = gold up
}


class EventSurpriseStrategy(Strategy):
    def __init__(self, data, events, parameters, initial_cash=10000.0, broker=None):
        super().__init__(data, events, parameters, initial_cash, broker)

        # Parameters
        self.symbol = parameters.get('symbol', 'GLD')
        self.event_types = parameters.get('event_types', ['CPI m/m', 'CPI y/y'])
        self.surprise_threshold = float(parameters.get('surprise_threshold', 0.5))
        self.hold_bars = int(parameters.get('hold_bars', 4))
        self.stop_pct = float(parameters.get('stop_pct', 0.5))
        self.entry_delay = int(parameters.get('entry_delay', 1))
        self.risk_pct = float(parameters.get('risk_pct', 0.02))
        self.trade_beats = parameters.get('trade_beats', False)
        self.dedup_minutes = int(parameters.get('dedup_minutes', 5))

        # State
        self.bar_index = 0
        self.entry_bar = None
        self.entry_price = None
        self.current_sl = None
        self.trade_direction = None  # 'long' or 'short'

        # Pre-calculate ATR
        if data is not None and not data.empty:
            self.data['atr'] = atr(data['High'], data['Low'], data['Close'], 14)

        # Build event schedule
        self.event_schedule = {}  # {bar_index: {direction, surprise, event_name}}
        if data is not None and not data.empty:
            self._build_event_schedule(data, parameters)

    def _build_event_schedule(self, data, parameters):
        """Load events, match to bars, dedup co-releases, classify surprises."""
        # Load events — use injected data if available, otherwise load from DataLoader
        event_data = parameters.get('_event_data', None)
        if event_data is None:
            loader = DataLoader()
            start = str(data.index[0].date()) if hasattr(data.index[0], 'date') else str(data.index[0])[:10]
            end = str(data.index[-1].date()) if hasattr(data.index[-1], 'date') else str(data.index[-1])[:10]
            event_data = loader.fetch_economic_events(start, end, currency='USD')

        if event_data is None or event_data.empty:
            print("[EVENT SURPRISE] No economic events loaded")
            return

        # Build bar index for bisect matching
        bar_timestamps = data.index.tolist()
        # Ensure tz-naive for comparison
        if hasattr(bar_timestamps[0], 'tzinfo') and bar_timestamps[0].tzinfo is not None:
            bar_timestamps = [t.tz_localize(None) for t in bar_timestamps]

        # Step 1: Filter to requested event types and match to bars
        raw_events = []  # list of {event_name, surprise, bar_pos, date}

        # Collect all surprises per event type for std calculation
        surprises_by_type = defaultdict(list)

        for event_name in self.event_types:
            if event_name not in EVENT_DIRECTION:
                print(f"[EVENT SURPRISE] Warning: unknown event type '{event_name}', skipping")
                continue

            mask = event_data['event'].str.contains(event_name, case=False, na=False)
            evt_df = event_data[mask].copy()
            if evt_df.empty:
                continue

            evt_df['surprise'] = evt_df['actual_val'] - evt_df['forecast_val']

            for _, row in evt_df.iterrows():
                surprises_by_type[event_name].append(row['surprise'])

                # Match event to bar
                evt_time = row['date']
                if hasattr(evt_time, 'tzinfo') and evt_time.tzinfo is not None:
                    evt_time = evt_time.tz_localize(None)

                bar_pos = self._find_event_bar(evt_time, bar_timestamps)
                if bar_pos is None:
                    continue

                raw_events.append({
                    'event_name': event_name,
                    'surprise': row['surprise'],
                    'bar_pos': bar_pos,
                    'date': evt_time,
                })

        # Step 2: Compute per-type std thresholds
        std_by_type = {}
        for etype, surprises in surprises_by_type.items():
            if len(surprises) >= 3:
                std_by_type[etype] = np.std(surprises)
            else:
                std_by_type[etype] = 0.001  # fallback

        # Step 3: Dedup co-releases (within dedup_minutes window)
        # Group by rounded time
        dedup_window = pd.Timedelta(minutes=self.dedup_minutes)
        moment_groups = defaultdict(list)
        for evt in raw_events:
            rounded = evt['date'].floor(f'{self.dedup_minutes}min')
            moment_groups[rounded].append(evt)

        # Step 4: For each moment, pick dominant event and classify
        for moment_time, events_list in moment_groups.items():
            # Pick event with largest |surprise|
            dominant = max(events_list, key=lambda e: abs(e['surprise']))

            event_name = dominant['event_name']
            surprise = dominant['surprise']
            bar_pos = dominant['bar_pos']

            # Check threshold: |surprise| > threshold * std_of_that_event_type
            event_std = std_by_type.get(event_name, 0.001)
            if event_std > 0 and abs(surprise) < self.surprise_threshold * event_std:
                continue  # inline — not significant enough

            # Determine trade direction
            config = EVENT_DIRECTION[event_name]
            beat_dir = config['beat_gold_dir']

            if surprise > 0:
                # Beat
                if not self.trade_beats:
                    continue  # skip beats by default (weaker signal)
                direction = beat_dir  # 'down' for CPI/NFP beats
            elif surprise < 0:
                # Miss
                direction = 'up' if beat_dir == 'down' else 'down'
            else:
                continue  # exactly zero, skip

            # Store in schedule (keyed by bar_pos where we check for entry)
            # Entry happens at bar_pos + entry_delay
            entry_bar = bar_pos + self.entry_delay
            if entry_bar < len(data):
                self.event_schedule[entry_bar] = {
                    'direction': direction,
                    'surprise': surprise,
                    'event_name': event_name,
                    'event_bar': bar_pos,
                }

        print(f"[EVENT SURPRISE] Loaded {len(self.event_schedule)} tradeable events "
              f"from {len(moment_groups)} unique moments "
              f"(types: {self.event_types}, threshold: {self.surprise_threshold}x std, "
              f"trade_beats: {self.trade_beats})")

    def _find_event_bar(self, event_time, bar_timestamps):
        """Find the bar that contains or immediately follows the event time."""
        idx = bisect.bisect_left(bar_timestamps, event_time)
        if idx < len(bar_timestamps):
            diff = (bar_timestamps[idx] - event_time).total_seconds()
            if 0 <= diff <= 1800:  # within 30min
                return idx
        if idx > 0:
            diff = (event_time - bar_timestamps[idx - 1]).total_seconds()
            if 0 <= diff < 900:  # within 15min
                return idx - 1
        return None

    def on_data(self, index, row):
        self.on_bar(row, self.bar_index, self.data)
        self.bar_index += 1

    def on_event(self, event):
        pass  # Events handled via pre-matching in __init__

    def on_bar(self, row, i, df):
        # Skip warmup (need ATR)
        if i < 20:
            return

        # 1. Check stop loss (priority — before entries)
        if self.position == 'long' and self.current_sl is not None:
            if row['Low'] <= self.current_sl:
                qty = abs(self.broker.get_position(self.symbol))
                if qty > 0:
                    result = self.sell(price=self.current_sl, size=qty, timestamp=i, exit_reason='stop')
                    if result is not None:
                        self._reset_position()
                return

        elif self.position == 'short' and self.current_sl is not None:
            if row['High'] >= self.current_sl:
                qty = abs(self.broker.get_position(self.symbol))
                if qty > 0:
                    result = self.buy(price=self.current_sl, size=qty, timestamp=i, exit_reason='stop')
                    if result is not None:
                        self._reset_position()
                return

        # 2. Check time-based exit
        if self.position in ('long', 'short') and self.entry_bar is not None:
            bars_held = i - self.entry_bar
            if bars_held >= self.hold_bars:
                qty = abs(self.broker.get_position(self.symbol))
                if qty > 0:
                    if self.position == 'long':
                        result = self.sell(price=row['Close'], size=qty, timestamp=i, exit_reason='time_exit')
                    else:
                        result = self.buy(price=row['Close'], size=qty, timestamp=i, exit_reason='time_exit')
                    if result is not None:
                        self._reset_position()
                return

        # 3. Check for new entry
        if self.position == 0 and i in self.event_schedule:
            event_info = self.event_schedule[i]
            direction = event_info['direction']

            price = row['Close']
            stop_distance = price * (self.stop_pct / 100.0)

            if stop_distance <= 0:
                return

            # Position sizing: risk_pct * equity / stop_distance
            equity = self.broker.get_equity()
            risk_amt = equity * self.risk_pct
            size = risk_amt / stop_distance

            # Cap to 25% of equity
            max_size = (equity * 0.25) / price
            size = min(size, max_size)
            size = round(size, 4)

            if size <= 0:
                return

            if direction == 'up':
                # Long gold
                sl = price - stop_distance
                result = self.buy(price=price, size=size, timestamp=i, stop_loss=sl)
                if result is not None:
                    self.position = 'long'
                    self.entry_bar = i
                    self.entry_price = price
                    self.current_sl = sl
                    self.trade_direction = 'long'
                    print(f"[EVENT ENTRY] LONG {self.symbol} @ ${price:.2f} | "
                          f"{event_info['event_name']} surprise={event_info['surprise']:.4f} | "
                          f"SL=${sl:.2f} | Hold {self.hold_bars} bars")
            else:
                # Short gold
                sl = price + stop_distance
                result = self.sell(price=price, size=size, timestamp=i, stop_loss=sl)
                if result is not None:
                    self.position = 'short'
                    self.entry_bar = i
                    self.entry_price = price
                    self.current_sl = sl
                    self.trade_direction = 'short'
                    print(f"[EVENT ENTRY] SHORT {self.symbol} @ ${price:.2f} | "
                          f"{event_info['event_name']} surprise={event_info['surprise']:.4f} | "
                          f"SL=${sl:.2f} | Hold {self.hold_bars} bars")

    def _reset_position(self):
        """Clear position state after exit."""
        self.position = 0
        self.entry_bar = None
        self.entry_price = None
        self.current_sl = None
        self.trade_direction = None
