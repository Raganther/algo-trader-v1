"""Fetch historical 1-minute bars from HistData and store in research.db.

Spot prices, not ETF prices. Stored under their HistData symbol names
(XAUUSD, XAGUSD, WTIUSD) — distinct from ETF tickers (GLD, SLV, OIH) so
live bots can never accidentally read them.

US ETF market hours filter (13:30-20:00 UTC) is applied at fetch time so
the bar set is comparable to what the live ETF bots see.

Usage:
    python scripts/fetch_price_data_histdata.py
    python scripts/fetch_price_data_histdata.py --symbols XAUUSD --start 2009-03-01
    python scripts/fetch_price_data_histdata.py --timeframe 1m --no-rth
"""

import argparse
import sys
from datetime import datetime, timezone

sys.path.insert(0, '.')

from backend.database import DatabaseManager
from backend.engine.histdata_loader import HistDataLoader

DEFAULT_SYMBOLS = ['XAUUSD', 'XAGUSD', 'WTIUSD']
DEFAULT_START = '2009-03-01'


def fetch_and_store(symbol, timeframe, start, end, loader, db):
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

    saved = db.save_price_bars(symbol, df)
    min_ts2, max_ts2, count2 = db.get_price_data_range(symbol)
    first = datetime.fromtimestamp(min_ts2, tz=timezone.utc).strftime('%Y-%m-%d')
    last = datetime.fromtimestamp(max_ts2, tz=timezone.utc).strftime('%Y-%m-%d')
    print(f"{symbol}: inserted {saved} rows -> total {count2} bars ({first} to {last})")


def main():
    parser = argparse.ArgumentParser(description='Fetch historical price data from HistData (spot prices)')
    parser.add_argument('--symbols', default=','.join(DEFAULT_SYMBOLS), help='Comma-separated HistData symbols')
    parser.add_argument('--timeframe', default='15m', choices=['1m', '5m', '15m', '1h'], help='Bar timeframe to store')
    parser.add_argument('--start', default=DEFAULT_START, help='Start date YYYY-MM-DD')
    parser.add_argument('--end', default=datetime.now().strftime('%Y-%m-%d'), help='End date YYYY-MM-DD')
    parser.add_argument('--no-rth', action='store_true', help='Disable US ETF market hours filter (default: 13:30-20:00 UTC)')
    args = parser.parse_args()

    symbols = [s.strip().upper() for s in args.symbols.split(',')]

    db = DatabaseManager()
    db.initialize_db()

    loader = HistDataLoader(restrict_to_rth=not args.no_rth)

    for symbol in symbols:
        try:
            fetch_and_store(symbol, args.timeframe, args.start, args.end, loader, db)
        except Exception as e:
            print(f"{symbol}: ERROR -- {e}")
            import traceback
            traceback.print_exc()

    print("\nDone.")


if __name__ == '__main__':
    main()
