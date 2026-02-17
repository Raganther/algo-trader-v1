"""
Event Surprise → Gold Price Reaction Diagnostic

For each high-impact event type (NFP, CPI, Fed Funds, Unemployment Rate):
  1. Load events with actual + forecast values
  2. Calculate surprise = actual - forecast
  3. Classify: positive surprise (beat), negative surprise (miss), inline
  4. Load GLD 15m price data from Alpaca
  5. Measure gold's reaction at 15min, 1h, 2h, 4h, 24h after event
  6. Report: avg move, correct direction %, median, best, worst — by surprise direction

Usage:
    python -m backend.scripts.event_surprise_analysis
"""

import pandas as pd
import numpy as np
import sys
import os
import bisect

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from backend.engine.data_loader import DataLoader
from backend.engine.alpaca_loader import AlpacaDataLoader

# Event types to analyse and their expected gold reaction
# USD beat (positive surprise) → USD strengthens → Gold DOWN
# USD miss (negative surprise) → USD weakens → Gold UP
EVENT_TYPES = {
    'Non-Farm Employment Change': {'beat_gold_dir': 'down'},
    'CPI m/m': {'beat_gold_dir': 'down'},  # Higher inflation → hawkish → USD up → gold down
    'Core CPI m/m': {'beat_gold_dir': 'down'},
    'CPI y/y': {'beat_gold_dir': 'down'},
    'Federal Funds Rate': {'beat_gold_dir': 'down'},  # Higher rate → USD up → gold down
    'Unemployment Rate': {'beat_gold_dir': 'up'},  # Higher unemployment is bad for USD → gold up
}

# Reaction windows in number of 15m bars
WINDOWS = {
    '15min': 1,
    '1h': 4,
    '2h': 8,
    '4h': 16,
    '24h': 96,
}


def load_gld_15m():
    """Load GLD 15m data from Alpaca (fetches 1m and resamples like the existing scripts)."""
    print("Loading GLD 15m data from Alpaca...")
    alpaca = AlpacaDataLoader()
    raw = alpaca.fetch_data('GLD', '1m', '2020-01-01', '2025-12-31')
    if raw is None or raw.empty:
        print("ERROR: No data returned from Alpaca")
        sys.exit(1)

    ohlc_dict = {'Open': 'first', 'High': 'max', 'Low': 'min', 'Close': 'last', 'Volume': 'sum'}
    data = raw.resample('15min').agg(ohlc_dict).dropna()

    # Make tz-naive for matching with event times
    if data.index.tz is not None:
        data.index = data.index.tz_localize(None)

    print(f"  {len(data)} bars ({data.index[0]} to {data.index[-1]})")
    return data


def load_events():
    """Load economic events with actual + forecast values."""
    print("Loading economic events...")
    loader = DataLoader()
    events = loader.fetch_economic_events('2020-01-01', '2025-12-31', currency='USD')
    print(f"  {len(events)} high-impact USD events with actual+forecast values")
    return events


def find_event_bar(event_time, bar_index):
    """Find the bar that contains or immediately follows the event time.

    Returns the integer position in bar_index, or None if no match within 30 min.
    """
    idx = bisect.bisect_left(bar_index, event_time)
    # bisect_left gives us the first bar >= event_time
    if idx < len(bar_index):
        # Check it's within 30 min (event should fall within or just before a bar)
        diff = (bar_index[idx] - event_time).total_seconds()
        if 0 <= diff <= 1800:  # within 30 min forward
            return idx
    # Also check the bar just before (event might be inside that 15m bar)
    if idx > 0:
        diff = (event_time - bar_index[idx - 1]).total_seconds()
        if 0 <= diff < 900:  # within the 15m bar
            return idx - 1
    return None


def measure_reaction(data, bar_pos, windows):
    """Measure price change at each window from the event bar.

    Returns dict of {window_name: pct_change} or None if insufficient data.
    """
    max_bars_needed = max(windows.values())
    if bar_pos + max_bars_needed >= len(data):
        return None

    event_close = data.iloc[bar_pos]['Close']
    if event_close == 0 or pd.isna(event_close):
        return None

    reactions = {}
    for name, n_bars in windows.items():
        future_close = data.iloc[bar_pos + n_bars]['Close']
        pct = (future_close - event_close) / event_close * 100
        reactions[name] = pct

    return reactions


def classify_surprises(event_surprises):
    """Classify surprises as beat/miss/inline using ±0.5 std threshold."""
    if len(event_surprises) < 3:
        return [], [], []

    std = np.std(event_surprises)
    threshold = 0.5 * std if std > 0 else 0.001

    beats, misses, inlines = [], [], []
    for i, s in enumerate(event_surprises):
        if s > threshold:
            beats.append(i)
        elif s < -threshold:
            misses.append(i)
        else:
            inlines.append(i)

    return beats, misses, inlines


def print_reaction_table(rows, label, expected_dir):
    """Print a formatted reaction table for a set of events."""
    if not rows:
        print(f"  No events in this category")
        return

    # rows is a list of reaction dicts
    print(f"  {'Window':<10} {'Avg Move':>10} {'Correct%':>10} {'Median':>10} {'Best':>10} {'Worst':>10} {'N':>5}")
    print(f"  {'-'*10} {'-'*10} {'-'*10} {'-'*10} {'-'*10} {'-'*10} {'-'*5}")

    for window_name in WINDOWS:
        moves = [r[window_name] for r in rows if window_name in r]
        if not moves:
            continue

        avg = np.mean(moves)
        median = np.median(moves)

        # "Correct" = gold moved in the expected direction
        if expected_dir == 'down':
            correct = sum(1 for m in moves if m < 0)
            best = min(moves)   # most negative = biggest drop = best for "expect down"
            worst = max(moves)
        else:  # expected_dir == 'up'
            correct = sum(1 for m in moves if m > 0)
            best = max(moves)
            worst = min(moves)

        correct_pct = correct / len(moves) * 100

        print(f"  {window_name:<10} {avg:>+10.3f}% {correct_pct:>9.0f}% {median:>+10.3f}% {best:>+10.3f}% {worst:>+10.3f}% {len(moves):>5}")


def print_yearly_table(events_with_reactions, beat_indices, miss_indices, expected_dir):
    """Print year-by-year consistency table."""
    years = sorted(set(e['year'] for e in events_with_reactions))
    if not years:
        return

    print(f"\n  Year-by-year (avg gold move, correct direction %):")
    print(f"  {'Year':<6} {'Beat→Gold':>12} {'Dir%':>6} {'N':>4}   {'Miss→Gold':>12} {'Dir%':>6} {'N':>4}")
    print(f"  {'-'*6} {'-'*12} {'-'*6} {'-'*4}   {'-'*12} {'-'*6} {'-'*4}")

    beat_set = set(beat_indices)
    miss_set = set(miss_indices)

    for year in years:
        # Beat events for this year — use 1h window
        beat_moves = [e['reactions']['1h'] for e in events_with_reactions
                      if e['year'] == year and e['idx'] in beat_set and '1h' in e['reactions']]
        miss_moves = [e['reactions']['1h'] for e in events_with_reactions
                      if e['year'] == year and e['idx'] in miss_set and '1h' in e['reactions']]

        def fmt(moves, exp_dir):
            if not moves:
                return f"{'---':>12} {'---':>6} {0:>4}"
            avg = np.mean(moves)
            if exp_dir == 'down':
                correct = sum(1 for m in moves if m < 0)
            else:
                correct = sum(1 for m in moves if m > 0)
            pct = correct / len(moves) * 100
            return f"{avg:>+12.3f}% {pct:>5.0f}% {len(moves):>4}"

        # For beats, expected gold direction is the beat_gold_dir
        # For misses, expected gold direction is opposite
        opp = 'up' if expected_dir == 'down' else 'down'
        print(f"  {year:<6} {fmt(beat_moves, expected_dir)}   {fmt(miss_moves, opp)}")


def run_analysis():
    # Load data
    gld = load_gld_15m()
    events = load_events()

    if events.empty:
        print("No events found. Exiting.")
        return

    bar_index = gld.index.tolist()

    print(f"\nAnalysing {len(EVENT_TYPES)} event types across {len(events)} events...")
    print(f"GLD data range: {bar_index[0]} to {bar_index[-1]}")
    print()

    for event_name, config in EVENT_TYPES.items():
        beat_gold_dir = config['beat_gold_dir']
        miss_gold_dir = 'up' if beat_gold_dir == 'down' else 'down'

        # Filter events for this type (partial match on event name)
        mask = events['event'].str.contains(event_name, case=False, na=False)
        evt_df = events[mask].copy()

        if len(evt_df) == 0:
            print(f"=== {event_name.upper()} ===")
            print(f"  No events found matching '{event_name}'")
            print()
            continue

        # Calculate surprise
        evt_df = evt_df.copy()
        evt_df['surprise'] = evt_df['actual_val'] - evt_df['forecast_val']
        evt_df['norm_surprise'] = evt_df.apply(
            lambda r: r['surprise'] / abs(r['forecast_val']) if r['forecast_val'] != 0 else 0, axis=1)

        # Match events to GLD bars and measure reactions
        events_with_reactions = []
        for i, (_, row) in enumerate(evt_df.iterrows()):
            bar_pos = find_event_bar(row['date'], bar_index)
            if bar_pos is None:
                continue
            reactions = measure_reaction(gld, bar_pos, WINDOWS)
            if reactions is None:
                continue
            events_with_reactions.append({
                'idx': i,
                'date': row['date'],
                'year': row['date'].year,
                'actual': row['actual_val'],
                'forecast': row['forecast_val'],
                'surprise': row['surprise'],
                'norm_surprise': row['norm_surprise'],
                'reactions': reactions,
            })

        if not events_with_reactions:
            print(f"=== {event_name.upper()} ===")
            print(f"  {len(evt_df)} events found but none matched to GLD bars")
            print()
            continue

        # Classify surprises
        surprises = [e['surprise'] for e in events_with_reactions]
        beat_indices, miss_indices, inline_indices = classify_surprises(surprises)

        n_beat = len(beat_indices)
        n_miss = len(miss_indices)
        n_inline = len(inline_indices)

        print("=" * 80)
        print(f"  {event_name.upper()}")
        print("=" * 80)
        print(f"Events matched to GLD bars: {len(events_with_reactions)} "
              f"(of {len(evt_df)} total) | {n_beat} beats, {n_miss} misses, {n_inline} inline")
        print(f"Surprise stats: mean={np.mean(surprises):.4f}, std={np.std(surprises):.4f}, "
              f"threshold=±{0.5*np.std(surprises):.4f}")
        print(f"Expected: USD beat → gold {beat_gold_dir}, USD miss → gold {miss_gold_dir}")

        # Beat reactions
        beat_reactions = [events_with_reactions[i]['reactions'] for i in beat_indices]
        miss_reactions = [events_with_reactions[i]['reactions'] for i in miss_indices]

        print(f"\nGold reaction after POSITIVE surprise (USD beat → expect gold {beat_gold_dir.upper()}):")
        print_reaction_table(beat_reactions, "beat", beat_gold_dir)

        print(f"\nGold reaction after NEGATIVE surprise (USD miss → expect gold {miss_gold_dir.upper()}):")
        print_reaction_table(miss_reactions, "miss", miss_gold_dir)

        # Top/bottom quartile analysis
        abs_surprises = [(abs(e['norm_surprise']), i) for i, e in enumerate(events_with_reactions)]
        abs_surprises.sort(reverse=True)
        q_size = max(1, len(abs_surprises) // 4)
        top_q_indices = set(idx for _, idx in abs_surprises[:q_size])

        top_q_beats = [events_with_reactions[i]['reactions'] for i in beat_indices if i in top_q_indices]
        top_q_misses = [events_with_reactions[i]['reactions'] for i in miss_indices if i in top_q_indices]

        if top_q_beats or top_q_misses:
            print(f"\nTop quartile surprises (biggest magnitude, N={q_size}):")
            if top_q_beats:
                print(f"  Biggest beats ({len(top_q_beats)}):")
                print_reaction_table(top_q_beats, "top_beat", beat_gold_dir)
            if top_q_misses:
                print(f"  Biggest misses ({len(top_q_misses)}):")
                print_reaction_table(top_q_misses, "top_miss", miss_gold_dir)

        # Year-by-year consistency
        print_yearly_table(events_with_reactions, set(beat_indices), set(miss_indices), beat_gold_dir)

        print()

    # --- Cross-event summary ---
    print("=" * 80)
    print("  CROSS-EVENT SUMMARY (1h window)")
    print("=" * 80)
    print(f"  {'Event':<35} {'Beat→Gold':>10} {'Dir%':>6} {'Miss→Gold':>10} {'Dir%':>6} {'N':>5}")
    print(f"  {'-'*35} {'-'*10} {'-'*6} {'-'*10} {'-'*6} {'-'*5}")

    for event_name, config in EVENT_TYPES.items():
        beat_gold_dir = config['beat_gold_dir']
        miss_gold_dir = 'up' if beat_gold_dir == 'down' else 'down'

        mask = events['event'].str.contains(event_name, case=False, na=False)
        evt_df = events[mask].copy()
        if len(evt_df) == 0:
            continue

        evt_df['surprise'] = evt_df['actual_val'] - evt_df['forecast_val']

        matched = []
        for _, row in evt_df.iterrows():
            bar_pos = find_event_bar(row['date'], bar_index)
            if bar_pos is None:
                continue
            reactions = measure_reaction(gld, bar_pos, WINDOWS)
            if reactions is None:
                continue
            matched.append({'surprise': row['surprise'], 'reactions': reactions})

        if not matched:
            continue

        surprises = [m['surprise'] for m in matched]
        beat_idx, miss_idx, _ = classify_surprises(surprises)

        beat_moves = [matched[i]['reactions'].get('1h', 0) for i in beat_idx]
        miss_moves = [matched[i]['reactions'].get('1h', 0) for i in miss_idx]

        def summary(moves, exp_dir):
            if not moves:
                return f"{'---':>10} {'---':>6}"
            avg = np.mean(moves)
            if exp_dir == 'down':
                correct = sum(1 for m in moves if m < 0)
            else:
                correct = sum(1 for m in moves if m > 0)
            pct = correct / len(moves) * 100 if moves else 0
            return f"{avg:>+10.3f}% {pct:>5.0f}%"

        total = len(beat_moves) + len(miss_moves)
        print(f"  {event_name:<35} {summary(beat_moves, beat_gold_dir)} {summary(miss_moves, miss_gold_dir)} {total:>5}")

    print()
    print("Key: 'Correct%' = gold moved in the expected direction (beat→down or miss→up)")
    print("Signal worth exploring if: avg move > 0.1%, correct% > 55%, consistent across years")
    print()


if __name__ == '__main__':
    run_analysis()
