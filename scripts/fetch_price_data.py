"""
Fetch historical OHLCV data from Alpaca and store in research.db.

15m bars → price_data table (default)
Daily bars → price_data_daily table

Usage:
    python scripts/fetch_price_data.py
    python scripts/fetch_price_data.py --symbols GLD,SLV --start 2022-01-01
    python scripts/fetch_price_data.py --symbols GLD,IAU,SLV,GDX --timeframe 1d --start 2020-01-01
"""

import argparse
import sys
from datetime import datetime, timezone

sys.path.insert(0, '.')

from backend.database import DatabaseManager
from backend.engine.alpaca_loader import AlpacaDataLoader

SYMBOLS = ['GLD', 'IAU', 'SLV', 'GDX']
DEFAULT_START = '2020-01-01'


def fetch_and_store(symbol, timeframe, start, end, loader, db):
    if timeframe == '1d':
        min_ts, max_ts, count = db.get_daily_bars_range(symbol)
    else:
        min_ts, max_ts, count = db.get_price_data_range(symbol)

    print(f"\n{symbol} ({timeframe}): existing bars={count}", end='')
    if max_ts:
        existing_end = datetime.fromtimestamp(max_ts, tz=timezone.utc).strftime('%Y-%m-%d')
        print(f", last bar={existing_end}", end='')
    print()

    print(f"{symbol}: fetching {timeframe} bars from {start} to {end} ...")
    df = loader.fetch_data(symbol, timeframe, start, end)

    if df.empty:
        print(f"{symbol}: no data returned")
        return

    if timeframe == '1d':
        saved = db.save_daily_bars(symbol, df)
        min_ts2, max_ts2, count2 = db.get_daily_bars_range(symbol)
    else:
        saved = db.save_price_bars(symbol, df)
        min_ts2, max_ts2, count2 = db.get_price_data_range(symbol)

    first = datetime.fromtimestamp(min_ts2, tz=timezone.utc).strftime('%Y-%m-%d')
    last = datetime.fromtimestamp(max_ts2, tz=timezone.utc).strftime('%Y-%m-%d')
    print(f"{symbol}: inserted {saved} rows → total {count2} bars ({first} to {last})")


def main():
    parser = argparse.ArgumentParser(description='Fetch historical price data from Alpaca')
    parser.add_argument('--symbols', default=','.join(SYMBOLS), help='Comma-separated symbols')
    parser.add_argument('--timeframe', default='15m', choices=['15m', '1h', '1d'], help='Bar timeframe')
    parser.add_argument('--start', default=DEFAULT_START, help='Start date YYYY-MM-DD')
    parser.add_argument('--end', default=datetime.now().strftime('%Y-%m-%d'), help='End date YYYY-MM-DD')
    args = parser.parse_args()

    symbols = [s.strip() for s in args.symbols.split(',')]

    db = DatabaseManager()
    db.initialize_db()

    loader = AlpacaDataLoader()

    for symbol in symbols:
        try:
            fetch_and_store(symbol, args.timeframe, args.start, args.end, loader, db)
        except Exception as e:
            print(f"{symbol}: ERROR — {e}")

    print("\nDone.")


if __name__ == '__main__':
    main()
