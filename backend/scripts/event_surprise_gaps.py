"""
Event Surprise Gap Analysis — Follow-Up Diagnostic

Addresses 5 critical gaps from the initial event_surprise_analysis.py:
  1. Year coverage — why are recent years missing? Event matching diagnostics.
  2. Double-counting — co-released events (NFP+Unemployment, CPI m/m+y/y+Core)
  3. Entry timing — intra-bar vs post-bar move (can we actually trade it?)
  4. Spread/slippage — event-bar volatility vs normal, break-even spread
  5. Max adverse excursion — worst drawdown before window closes, stop sizing

Usage:
    python -m backend.scripts.event_surprise_gaps
"""

import pandas as pd
import numpy as np
import sys
import os
import bisect
from collections import defaultdict

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from backend.engine.data_loader import DataLoader
from backend.engine.alpaca_loader import AlpacaDataLoader

# Same event config as original diagnostic
EVENT_TYPES = {
    'Non-Farm Employment Change': {'beat_gold_dir': 'down'},
    'CPI m/m': {'beat_gold_dir': 'down'},
    'Core CPI m/m': {'beat_gold_dir': 'down'},
    'CPI y/y': {'beat_gold_dir': 'down'},
    'Federal Funds Rate': {'beat_gold_dir': 'down'},
    'Unemployment Rate': {'beat_gold_dir': 'up'},
}

# Co-release groups — events that release at the same time
CO_RELEASE_GROUPS = {
    'Employment': ['Non-Farm Employment Change', 'Unemployment Rate'],
    'CPI': ['CPI m/m', 'CPI y/y', 'Core CPI m/m'],
}

# Reaction windows in 15m bars
WINDOWS = {
    '15min': 1,
    '1h': 4,
    '2h': 8,
    '4h': 16,
}


def load_gld_15m():
    """Load GLD 15m data from Alpaca."""
    print("Loading GLD 15m data from Alpaca...")
    alpaca = AlpacaDataLoader()
    raw = alpaca.fetch_data('GLD', '1m', '2020-01-01', '2025-12-31')
    if raw is None or raw.empty:
        print("ERROR: No data returned from Alpaca")
        sys.exit(1)

    ohlc_dict = {'Open': 'first', 'High': 'max', 'Low': 'min', 'Close': 'last', 'Volume': 'sum'}
    data = raw.resample('15min').agg(ohlc_dict).dropna()

    if data.index.tz is not None:
        data.index = data.index.tz_localize(None)

    print(f"  {len(data)} bars ({data.index[0]} to {data.index[-1]})")
    return data


def load_events_raw():
    """Load economic events CSV directly (not filtered) for coverage analysis."""
    csv_path = 'backend/data_csv/economic_calendar.csv'
    if not os.path.exists(csv_path):
        print(f"ERROR: CSV not found at {csv_path}")
        sys.exit(1)

    df = pd.read_csv(csv_path)
    df['DateTime'] = pd.to_datetime(df['DateTime'], utc=True).dt.tz_localize(None)
    df.rename(columns={
        'DateTime': 'date', 'Currency': 'currency', 'Impact': 'impact',
        'Event': 'event', 'Actual': 'actual', 'Forecast': 'forecast', 'Previous': 'previous'
    }, inplace=True)
    return df


def load_events_filtered():
    """Load events via DataLoader (high-impact USD with actual+forecast)."""
    loader = DataLoader()
    events = loader.fetch_economic_events('2020-01-01', '2025-12-31', currency='USD')
    print(f"  {len(events)} high-impact USD events with actual+forecast values")
    return events


def find_event_bar(event_time, bar_index):
    """Find the bar that contains or immediately follows the event time."""
    idx = bisect.bisect_left(bar_index, event_time)
    if idx < len(bar_index):
        diff = (bar_index[idx] - event_time).total_seconds()
        if 0 <= diff <= 1800:
            return idx
    if idx > 0:
        diff = (event_time - bar_index[idx - 1]).total_seconds()
        if 0 <= diff < 900:
            return idx - 1
    return None


def classify_surprises(surprises):
    """Classify surprises as beat/miss/inline using ±0.5 std threshold."""
    if len(surprises) < 3:
        return [], [], []
    std = np.std(surprises)
    threshold = 0.5 * std if std > 0 else 0.001
    beats, misses, inlines = [], [], []
    for i, s in enumerate(surprises):
        if s > threshold:
            beats.append(i)
        elif s < -threshold:
            misses.append(i)
        else:
            inlines.append(i)
    return beats, misses, inlines


# =============================================================================
# Investigation 1: Year Coverage & Event Matching
# =============================================================================

def investigate_coverage(events_raw, events_filtered, gld, bar_index):
    print()
    print("=" * 80)
    print("  INVESTIGATION 1: YEAR COVERAGE & EVENT MATCHING")
    print("=" * 80)

    for event_name in EVENT_TYPES:
        # All events in CSV (any impact, any currency — just matching name)
        raw_mask = events_raw['event'].str.contains(event_name, case=False, na=False)
        raw_usd_high = events_raw[raw_mask &
                                   events_raw['currency'].str.contains('USD', na=False) &
                                   events_raw['impact'].str.contains('High', case=False, na=False)]

        # Filtered events (high-impact USD with actual+forecast)
        filt_mask = events_filtered['event'].str.contains(event_name, case=False, na=False)
        filt = events_filtered[filt_mask]

        # Calculate surprise for filtered events
        filt = filt.copy()
        filt['surprise'] = filt['actual_val'] - filt['forecast_val']

        print(f"\n  {event_name}:")
        print(f"  {'Year':<6} {'In CSV':>8} {'Has A+F':>8} {'Matched':>9} {'Unmatched':>10} {'Match%':>8}")
        print(f"  {'-'*6} {'-'*8} {'-'*8} {'-'*9} {'-'*10} {'-'*8}")

        years = sorted(set(raw_usd_high['date'].dt.year))
        unmatched_samples = []

        for year in years:
            # Count in raw CSV
            csv_count = len(raw_usd_high[raw_usd_high['date'].dt.year == year])
            # Count with actual+forecast
            af_count = len(filt[filt['date'].dt.year == year])
            # Count matched to GLD bars
            year_filt = filt[filt['date'].dt.year == year]
            matched = 0
            for _, row in year_filt.iterrows():
                bp = find_event_bar(row['date'], bar_index)
                if bp is not None:
                    matched += 1
                else:
                    unmatched_samples.append(row['date'])
            unmatched = af_count - matched
            match_pct = (matched / af_count * 100) if af_count > 0 else 0
            print(f"  {year:<6} {csv_count:>8} {af_count:>8} {matched:>9} {unmatched:>10} {match_pct:>7.0f}%")

        # Show sample unmatched events
        if unmatched_samples:
            print(f"\n  Sample unmatched events (up to 5):")
            for dt in unmatched_samples[:5]:
                dow = dt.strftime('%A')
                print(f"    {dt} ({dow})")


# =============================================================================
# Investigation 2: Double-Counting / Co-Release
# =============================================================================

def investigate_co_release(events_filtered, gld, bar_index):
    print()
    print("=" * 80)
    print("  INVESTIGATION 2: CO-RELEASED EVENTS (DOUBLE-COUNTING)")
    print("=" * 80)

    # Build a mapping: event_time → list of (event_name, surprise, row)
    event_moments = defaultdict(list)

    for event_name in EVENT_TYPES:
        mask = events_filtered['event'].str.contains(event_name, case=False, na=False)
        evt_df = events_filtered[mask].copy()
        if evt_df.empty:
            continue
        evt_df['surprise'] = evt_df['actual_val'] - evt_df['forecast_val']

        for _, row in evt_df.iterrows():
            # Round to 5-min window for co-release detection
            rounded = row['date'].floor('5min')
            event_moments[rounded].append({
                'event_name': event_name,
                'surprise': row['surprise'],
                'actual': row['actual_val'],
                'forecast': row['forecast_val'],
                'date': row['date'],
            })

    # Identify co-releases (>1 event at same time)
    co_releases = {k: v for k, v in event_moments.items() if len(v) > 1}
    solo_releases = {k: v for k, v in event_moments.items() if len(v) == 1}

    print(f"\n  Total unique event moments: {len(event_moments)}")
    print(f"  Solo releases: {len(solo_releases)}")
    print(f"  Co-releases (2+ events same time): {len(co_releases)}")

    # Analyse co-release groups
    group_stats = defaultdict(lambda: {'count': 0, 'same_dir': 0, 'opposite': 0, 'one_inline': 0})

    for moment_time, events_list in co_releases.items():
        names = sorted([e['event_name'] for e in events_list])
        # Identify which co-release group
        for group_name, group_events in CO_RELEASE_GROUPS.items():
            matching = [e for e in events_list if e['event_name'] in group_events]
            if len(matching) >= 2:
                group_stats[group_name]['count'] += 1
                # Check surprise directions
                directions = []
                for e in matching:
                    beat_dir = EVENT_TYPES[e['event_name']]['beat_gold_dir']
                    if e['surprise'] > 0:
                        # Beat — gold expected to go beat_dir
                        directions.append(beat_dir)
                    elif e['surprise'] < 0:
                        # Miss — gold expected opposite
                        directions.append('up' if beat_dir == 'down' else 'down')
                    else:
                        directions.append('inline')

                non_inline = [d for d in directions if d != 'inline']
                if len(non_inline) == 0:
                    group_stats[group_name]['one_inline'] += 1
                elif len(set(non_inline)) == 1:
                    group_stats[group_name]['same_dir'] += 1
                else:
                    group_stats[group_name]['opposite'] += 1

    print(f"\n  Co-release group analysis:")
    for group_name, stats in group_stats.items():
        events_in_group = ', '.join(CO_RELEASE_GROUPS[group_name])
        print(f"\n  {group_name} ({events_in_group}):")
        print(f"    Co-releases: {stats['count']}")
        print(f"    Same direction: {stats['same_dir']} ({stats['same_dir']/max(1,stats['count'])*100:.0f}%)")
        print(f"    Opposite direction: {stats['opposite']} ({stats['opposite']/max(1,stats['count'])*100:.0f}%)")
        print(f"    All inline: {stats['one_inline']} ({stats['one_inline']/max(1,stats['count'])*100:.0f}%)")

    # Deduplicated reaction analysis — one entry per unique moment
    print(f"\n  --- DEDUPLICATED REACTION TABLE (unique event moments) ---")
    print(f"  For co-releases, using the event with the largest |surprise|")

    dedup_events = []
    for moment_time, events_list in event_moments.items():
        # Pick the dominant event (largest absolute surprise)
        dominant = max(events_list, key=lambda e: abs(e['surprise']))
        bar_pos = find_event_bar(dominant['date'], bar_index)
        if bar_pos is None:
            continue

        max_bars = max(WINDOWS.values())
        if bar_pos + max_bars >= len(gld):
            continue

        event_close = gld.iloc[bar_pos]['Close']
        if event_close == 0 or pd.isna(event_close):
            continue

        reactions = {}
        for wname, n_bars in WINDOWS.items():
            future_close = gld.iloc[bar_pos + n_bars]['Close']
            reactions[wname] = (future_close - event_close) / event_close * 100

        beat_dir = EVENT_TYPES[dominant['event_name']]['beat_gold_dir']
        miss_dir = 'up' if beat_dir == 'down' else 'down'

        dedup_events.append({
            'event_name': dominant['event_name'],
            'surprise': dominant['surprise'],
            'date': dominant['date'],
            'reactions': reactions,
            'beat_gold_dir': beat_dir,
            'n_events_at_time': len(events_list),
        })

    # Classify and show summary
    surprises = [e['surprise'] for e in dedup_events]
    # Use per-event threshold: classify based on dominant event's own distribution
    # Simplified: use global classification
    beat_idx, miss_idx, inline_idx = classify_surprises(surprises)

    print(f"\n  Deduplicated: {len(dedup_events)} unique event moments "
          f"({len(beat_idx)} beats, {len(miss_idx)} misses, {len(inline_idx)} inline)")

    # Print reaction table for beats and misses
    for label, indices, exp_fn in [
        ("BEATS (dominant event surprise > 0)", beat_idx, lambda e: e['beat_gold_dir']),
        ("MISSES (dominant event surprise < 0)", miss_idx, lambda e: 'up' if e['beat_gold_dir'] == 'down' else 'down'),
    ]:
        if not indices:
            continue
        print(f"\n  {label} (N={len(indices)}):")
        print(f"  {'Window':<10} {'Avg Move':>10} {'N':>5}")
        print(f"  {'-'*10} {'-'*10} {'-'*5}")
        for wname in WINDOWS:
            moves = [dedup_events[i]['reactions'][wname] for i in indices]
            avg = np.mean(moves)
            print(f"  {wname:<10} {avg:>+10.3f}% {len(moves):>5}")

    return dedup_events


# =============================================================================
# Investigation 3: Intra-Bar vs Post-Bar Move
# =============================================================================

def investigate_entry_timing(events_filtered, gld, bar_index):
    print()
    print("=" * 80)
    print("  INVESTIGATION 3: INTRA-BAR vs POST-BAR MOVE (ENTRY TIMING)")
    print("=" * 80)

    for event_name, config in EVENT_TYPES.items():
        beat_dir = config['beat_gold_dir']
        miss_dir = 'up' if beat_dir == 'down' else 'down'

        mask = events_filtered['event'].str.contains(event_name, case=False, na=False)
        evt_df = events_filtered[mask].copy()
        if evt_df.empty:
            continue
        evt_df['surprise'] = evt_df['actual_val'] - evt_df['forecast_val']

        results = []
        for _, row in evt_df.iterrows():
            bar_pos = find_event_bar(row['date'], bar_index)
            if bar_pos is None:
                continue
            # Need enough bars ahead: event bar + 16 more (4h) + 1 delayed entry bar
            if bar_pos + 17 >= len(gld):
                continue

            event_bar = gld.iloc[bar_pos]
            event_open = event_bar['Open']
            event_close = event_bar['Close']

            if event_close == 0 or pd.isna(event_close) or event_open == 0:
                continue

            # Event bar move (open to close) — the move we CAN'T trade
            intra_bar_move = (event_close - event_open) / event_open * 100

            # Post-bar moves (from event bar close) — what we CAN trade
            post_moves = {}
            for wname, n_bars in WINDOWS.items():
                future_close = gld.iloc[bar_pos + n_bars]['Close']
                post_moves[wname] = (future_close - event_close) / event_close * 100

            # Delayed entry: enter at close of bar+1, measure from there
            delayed_entry_close = gld.iloc[bar_pos + 1]['Close']
            delayed_moves = {}
            for wname, n_bars in WINDOWS.items():
                if bar_pos + 1 + n_bars >= len(gld):
                    continue
                future_close = gld.iloc[bar_pos + 1 + n_bars]['Close']
                delayed_moves[wname] = (future_close - delayed_entry_close) / delayed_entry_close * 100

            results.append({
                'surprise': row['surprise'],
                'intra_bar': intra_bar_move,
                'post_moves': post_moves,
                'delayed_moves': delayed_moves,
            })

        if not results:
            continue

        surprises = [r['surprise'] for r in results]
        beat_idx, miss_idx, _ = classify_surprises(surprises)

        print(f"\n  {event_name}:")

        for label, indices, exp_dir in [
            (f"Beat → expect gold {beat_dir.upper()}", beat_idx, beat_dir),
            (f"Miss → expect gold {miss_dir.upper()}", miss_idx, miss_dir),
        ]:
            if not indices:
                continue

            print(f"\n  {label} (N={len(indices)}):")
            print(f"  {'Metric':<20} {'Event Bar':>12} {'Post 15m':>12} {'Post 1h':>12} {'Post 4h':>12} {'Delay 1h':>12} {'Delay 4h':>12}")
            print(f"  {'-'*20} {'-'*12} {'-'*12} {'-'*12} {'-'*12} {'-'*12} {'-'*12}")

            intra = [results[i]['intra_bar'] for i in indices]
            post_15m = [results[i]['post_moves'].get('15min', np.nan) for i in indices]
            post_1h = [results[i]['post_moves'].get('1h', np.nan) for i in indices]
            post_4h = [results[i]['post_moves'].get('4h', np.nan) for i in indices]
            delay_1h = [results[i]['delayed_moves'].get('1h', np.nan) for i in indices if '1h' in results[i]['delayed_moves']]
            delay_4h = [results[i]['delayed_moves'].get('4h', np.nan) for i in indices if '4h' in results[i]['delayed_moves']]

            def safe_mean(arr):
                arr = [x for x in arr if not np.isnan(x)]
                return np.mean(arr) if arr else np.nan

            def correct_pct(arr, exp_d):
                arr = [x for x in arr if not np.isnan(x)]
                if not arr:
                    return np.nan
                if exp_d == 'down':
                    return sum(1 for m in arr if m < 0) / len(arr) * 100
                else:
                    return sum(1 for m in arr if m > 0) / len(arr) * 100

            # Avg move row
            print(f"  {'Avg move':<20} {safe_mean(intra):>+11.3f}% {safe_mean(post_15m):>+11.3f}% "
                  f"{safe_mean(post_1h):>+11.3f}% {safe_mean(post_4h):>+11.3f}% "
                  f"{safe_mean(delay_1h):>+11.3f}% {safe_mean(delay_4h):>+11.3f}%")

            # Correct direction row
            print(f"  {'Correct dir %':<20} {correct_pct(intra, exp_dir):>11.0f}% {correct_pct(post_15m, exp_dir):>11.0f}% "
                  f"{correct_pct(post_1h, exp_dir):>11.0f}% {correct_pct(post_4h, exp_dir):>11.0f}% "
                  f"{correct_pct(delay_1h, exp_dir):>11.0f}% {correct_pct(delay_4h, exp_dir):>11.0f}%")


# =============================================================================
# Investigation 4: Spread/Slippage Reality Check
# =============================================================================

def investigate_spread(events_filtered, gld, bar_index):
    print()
    print("=" * 80)
    print("  INVESTIGATION 4: EVENT BAR VOLATILITY & SPREAD REALITY CHECK")
    print("=" * 80)

    # Normal bar range for GLD 15m
    gld_ranges = ((gld['High'] - gld['Low']) / gld['Close'] * 100).dropna()
    normal_range_pct = gld_ranges.median()
    normal_range_dollar = ((gld['High'] - gld['Low']).median())

    print(f"\n  Normal GLD 15m bar: range ${normal_range_dollar:.2f} ({normal_range_pct:.4f}%)")

    for event_name in EVENT_TYPES:
        mask = events_filtered['event'].str.contains(event_name, case=False, na=False)
        evt_df = events_filtered[mask].copy()
        if evt_df.empty:
            continue

        event_ranges = []
        event_ranges_dollar = []
        post_1h_moves = []

        evt_df['surprise'] = evt_df['actual_val'] - evt_df['forecast_val']

        for _, row in evt_df.iterrows():
            bar_pos = find_event_bar(row['date'], bar_index)
            if bar_pos is None:
                continue
            if bar_pos + 4 >= len(gld):
                continue

            bar = gld.iloc[bar_pos]
            range_pct = (bar['High'] - bar['Low']) / bar['Close'] * 100
            range_dollar = bar['High'] - bar['Low']
            event_ranges.append(range_pct)
            event_ranges_dollar.append(range_dollar)

            # Post-bar 1h move for break-even calc
            event_close = bar['Close']
            future_close = gld.iloc[bar_pos + 4]['Close']
            post_1h = abs((future_close - event_close) / event_close * 100)
            post_1h_moves.append(post_1h)

        if not event_ranges:
            continue

        avg_range = np.mean(event_ranges)
        avg_range_dollar = np.mean(event_ranges_dollar)
        multiple = avg_range / normal_range_pct if normal_range_pct > 0 else 0
        avg_post_1h = np.mean(post_1h_moves) if post_1h_moves else 0

        print(f"\n  {event_name} (N={len(event_ranges)}):")
        print(f"    Event bar avg range: ${avg_range_dollar:.2f} ({avg_range:.4f}%) — {multiple:.1f}x normal")
        print(f"    Avg |post-1h move|: {avg_post_1h:.4f}%")
        print(f"    Break-even spread: {avg_post_1h:.4f}% = ${avg_post_1h/100 * gld['Close'].iloc[-1]:.2f}")
        print(f"    Normal spread (0.03%): covered if post-1h > 0.03% ({'YES' if avg_post_1h > 0.03 else 'NO'})")
        print(f"    At 5x spread (0.15%): covered if post-1h > 0.15% ({'YES' if avg_post_1h > 0.15 else 'NO'})")
        print(f"    At 10x spread (0.30%): covered if post-1h > 0.30% ({'YES' if avg_post_1h > 0.30 else 'NO'})")


# =============================================================================
# Investigation 5: Max Adverse Excursion (MAE)
# =============================================================================

def investigate_mae(events_filtered, gld, bar_index):
    print()
    print("=" * 80)
    print("  INVESTIGATION 5: MAX ADVERSE EXCURSION (MAE) — STOP SIZING")
    print("=" * 80)

    for event_name, config in EVENT_TYPES.items():
        beat_dir = config['beat_gold_dir']
        miss_dir = 'up' if beat_dir == 'down' else 'down'

        mask = events_filtered['event'].str.contains(event_name, case=False, na=False)
        evt_df = events_filtered[mask].copy()
        if evt_df.empty:
            continue
        evt_df['surprise'] = evt_df['actual_val'] - evt_df['forecast_val']

        # Collect trade data
        trades = []
        for _, row in evt_df.iterrows():
            bar_pos = find_event_bar(row['date'], bar_index)
            if bar_pos is None:
                continue
            if bar_pos + 17 >= len(gld):  # need 4h + 1 bar
                continue

            entry_price = gld.iloc[bar_pos]['Close']
            if entry_price == 0 or pd.isna(entry_price):
                continue

            # Determine trade direction based on surprise
            if row['surprise'] > 0:
                # Beat — expect gold to go beat_dir
                trade_dir = beat_dir
            elif row['surprise'] < 0:
                trade_dir = miss_dir
            else:
                continue  # inline, skip

            # Track MAE for each window
            mae_by_window = {}
            final_by_window = {}
            for wname, n_bars in WINDOWS.items():
                worst_adverse = 0
                for b in range(1, n_bars + 1):
                    if bar_pos + b >= len(gld):
                        break
                    bar_data = gld.iloc[bar_pos + b]

                    if trade_dir == 'up':
                        # Long trade — adverse is price going down
                        adverse = (bar_data['Low'] - entry_price) / entry_price * 100
                        worst_adverse = min(worst_adverse, adverse)
                    else:
                        # Short trade — adverse is price going up
                        adverse = (bar_data['High'] - entry_price) / entry_price * 100
                        worst_adverse = max(worst_adverse, adverse)
                        # Store as negative for consistency (MAE is always negative)
                        worst_adverse_store = -worst_adverse if worst_adverse > 0 else worst_adverse

                if trade_dir == 'up':
                    mae_by_window[wname] = worst_adverse  # already negative
                else:
                    mae_by_window[wname] = -worst_adverse if worst_adverse > 0 else worst_adverse

                # Final move
                future_close = gld.iloc[bar_pos + n_bars]['Close']
                if trade_dir == 'up':
                    final_by_window[wname] = (future_close - entry_price) / entry_price * 100
                else:
                    final_by_window[wname] = -(future_close - entry_price) / entry_price * 100

            trades.append({
                'surprise': row['surprise'],
                'trade_dir': trade_dir,
                'mae': mae_by_window,
                'final': final_by_window,
            })

        if not trades:
            continue

        print(f"\n  {event_name} (N={len(trades)} directional trades):")
        print(f"  {'Window':<10} {'Avg MAE':>10} {'Median MAE':>12} {'90th pctl':>12} {'Avg Final':>12}")
        print(f"  {'-'*10} {'-'*10} {'-'*12} {'-'*12} {'-'*12}")

        for wname in WINDOWS:
            maes = [t['mae'].get(wname, np.nan) for t in trades]
            finals = [t['final'].get(wname, np.nan) for t in trades]
            maes = [m for m in maes if not np.isnan(m)]
            finals = [f for f in finals if not np.isnan(f)]

            if not maes:
                continue

            avg_mae = np.mean(maes)
            median_mae = np.median(maes)
            pctl_90 = np.percentile(maes, 10)  # 10th percentile of negative = worst 90%
            avg_final = np.mean(finals) if finals else np.nan

            print(f"  {wname:<10} {avg_mae:>+10.3f}% {median_mae:>+11.3f}% {pctl_90:>+11.3f}% {avg_final:>+11.3f}%")

        # Stop survival analysis
        print(f"\n  Stop survival (% of trades that DON'T hit stop before 1h window closes):")
        maes_1h = [t['mae'].get('1h', np.nan) for t in trades]
        maes_1h = [m for m in maes_1h if not np.isnan(m)]
        if maes_1h:
            for stop_pct in [0.1, 0.2, 0.3, 0.5, 0.75, 1.0]:
                survived = sum(1 for m in maes_1h if m > -stop_pct) / len(maes_1h) * 100
                print(f"    Stop at -{stop_pct:.1f}%: {survived:.0f}% survive")


# =============================================================================
# Main
# =============================================================================

def run():
    print("=" * 80)
    print("  EVENT SURPRISE GAP ANALYSIS")
    print("  Follow-up diagnostic: 5 investigations")
    print("=" * 80)

    gld = load_gld_15m()
    print("\nLoading events...")
    events_raw = load_events_raw()
    events_filtered = load_events_filtered()
    bar_index = gld.index.tolist()

    investigate_coverage(events_raw, events_filtered, gld, bar_index)
    investigate_co_release(events_filtered, gld, bar_index)
    investigate_entry_timing(events_filtered, gld, bar_index)
    investigate_spread(events_filtered, gld, bar_index)
    investigate_mae(events_filtered, gld, bar_index)

    print()
    print("=" * 80)
    print("  GO/NO-GO CHECKLIST")
    print("=" * 80)
    print("""
  Review the output above to answer:
  1. Do we have enough events in recent years (2023-2025) to trust the signal?
  2. After deduplication, is the sample still large enough (>30 unique events)?
  3. Is the post-bar move (what we can actually trade) still meaningful (>0.2%)?
  4. Does the expected move cover realistic event-time spreads?
  5. Can we set a stop that survives 80%+ of trades?

  If yes to all -> proceed to strategy design.
  If any are no -> the event surprise edge may not be tradeable.
""")


if __name__ == '__main__':
    run()
