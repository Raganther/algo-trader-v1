"""
Regime analysis — classify daily bars into market regimes and report statistics.

Reads daily bars from price_data_daily (fetch first with fetch_price_data.py --timeframe 1d).
Reports per-regime duration stats and year-by-year regime distribution.

Usage:
    python scripts/analyse_regimes.py
    python scripts/analyse_regimes.py --symbols GLD,SLV --start 2020-01-01
    python scripts/analyse_regimes.py --adx-threshold 25 --atr-multiplier 1.5
"""

import argparse
import sys
from datetime import datetime, timezone

sys.path.insert(0, '.')

import pandas as pd
from backend.database import DatabaseManager
from backend.indicators.regime import classify_regime, regime_stats, TRENDING_UP, TRENDING_DOWN, HIGH_VOL, RANGING

SYMBOLS = ['GLD', 'IAU', 'SLV', 'GDX']


def analyse_symbol(symbol, df, adx_threshold, atr_multiplier):
    if len(df) < 200:
        print(f"\n{symbol}: insufficient data ({len(df)} bars, need 200+)")
        return

    regimes = classify_regime(
        df,
        adx_threshold=adx_threshold,
        atr_vol_multiplier=atr_multiplier,
    )

    print(f"\n{'='*60}")
    print(f"{symbol} — {len(df)} daily bars")
    print(f"{'='*60}")

    # Overall regime stats
    stats = regime_stats(regimes)
    print("\nOverall regime distribution:")
    print(stats.to_string(index=False))

    # Year-by-year breakdown
    print("\nYear-by-year regime distribution (% of trading days):")
    df_regimes = df.copy()
    df_regimes['regime'] = regimes
    df_regimes['year'] = df_regimes.index.year

    pivot = (
        df_regimes.groupby(['year', 'regime'])
        .size()
        .unstack(fill_value=0)
    )
    # Ensure all regime columns present
    for col in [TRENDING_UP, TRENDING_DOWN, HIGH_VOL, RANGING]:
        if col not in pivot.columns:
            pivot[col] = 0
    pivot = pivot[[TRENDING_UP, TRENDING_DOWN, HIGH_VOL, RANGING]]
    pivot_pct = (pivot.div(pivot.sum(axis=1), axis=0) * 100).round(1)
    pivot_pct.columns = ['UP%', 'DOWN%', 'HIGH_VOL%', 'RANGING%']
    print(pivot_pct.to_string())

    # Transition matrix
    print("\nRegime transition matrix (row=from, col=to, % of exits):")
    order = [TRENDING_UP, TRENDING_DOWN, HIGH_VOL, RANGING]
    transitions = {r: {c: 0 for c in order} for r in order}
    prev = None
    for label in regimes:
        if prev is not None and prev != label:
            transitions[prev][label] += 1
        prev = label

    trans_df = pd.DataFrame(transitions).T[order]
    row_sums = trans_df.sum(axis=1)
    trans_pct = trans_df.div(row_sums, axis=0).multiply(100).round(1).fillna(0)
    trans_pct.index = ['FROM ' + r for r in trans_pct.index]
    trans_pct.columns = ['→' + c for c in trans_pct.columns]
    print(trans_pct.to_string())


def main():
    parser = argparse.ArgumentParser(description='Analyse market regimes from daily price data')
    parser.add_argument('--symbols', default=','.join(SYMBOLS))
    parser.add_argument('--start', default='2020-01-01')
    parser.add_argument('--end', default=datetime.now().strftime('%Y-%m-%d'))
    parser.add_argument('--adx-threshold', type=float, default=25.0)
    parser.add_argument('--atr-multiplier', type=float, default=1.5)
    args = parser.parse_args()

    symbols = [s.strip() for s in args.symbols.split(',')]
    start_ts = int(datetime.strptime(args.start, '%Y-%m-%d').replace(tzinfo=timezone.utc).timestamp())
    end_ts   = int(datetime.strptime(args.end,   '%Y-%m-%d').replace(tzinfo=timezone.utc).timestamp())

    db = DatabaseManager()
    db.initialize_db()

    for symbol in symbols:
        df = db.get_daily_bars(symbol, start_ts=start_ts, end_ts=end_ts)
        if df.empty:
            print(f"\n{symbol}: no daily bars found. Run: python scripts/fetch_price_data.py --timeframe 1d")
            continue
        try:
            analyse_symbol(symbol, df, args.adx_threshold, args.atr_multiplier)
        except Exception as e:
            print(f"\n{symbol}: ERROR — {e}")

    print("\nDone.")


if __name__ == '__main__':
    main()
