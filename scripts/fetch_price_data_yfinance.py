"""
Fetch historical daily OHLCV data from Yahoo Finance via yfinance and store in research.db.

Extends price_data_daily back to 2004 (GLD inception) using Yahoo Finance as the source.
Alpaca data (Jul 2020 onward) is already in the table — INSERT OR IGNORE prevents duplicates.

Usage:
    python3 scripts/fetch_price_data_yfinance.py
    python3 scripts/fetch_price_data_yfinance.py --symbols GLD,SLV --start 2004-01-01
"""

import argparse
import sys
from datetime import datetime, timezone

import pandas as pd
import yfinance as yf

sys.path.insert(0, '.')

from backend.database import DatabaseManager

SYMBOLS = ['GLD', 'IAU', 'SLV', 'GDX']
DEFAULT_START = '2004-01-01'


def main():
    parser = argparse.ArgumentParser(description='Fetch historical daily price data from Yahoo Finance')
    parser.add_argument('--symbols', default=','.join(SYMBOLS), help='Comma-separated symbols')
    parser.add_argument('--start', default=DEFAULT_START, help='Start date YYYY-MM-DD')
    parser.add_argument('--end', default=datetime.now().strftime('%Y-%m-%d'), help='End date YYYY-MM-DD')
    args = parser.parse_args()

    symbols = [s.strip() for s in args.symbols.split(',')]

    db = DatabaseManager()
    db.initialize_db()

    print(f"Fetching daily bars for {symbols} from {args.start} to {args.end} (single batch request)...")
    raw = yf.download(symbols, start=args.start, end=args.end, interval='1d', auto_adjust=True, progress=False)

    if raw.empty:
        print("No data returned.")
        return

    # Normalise index to UTC midnight
    raw.index = pd.to_datetime(raw.index).tz_localize('UTC').normalize()

    for symbol in symbols:
        try:
            min_ts, max_ts, count = db.get_daily_bars_range(symbol)
            print(f"\n{symbol}: existing bars={count}", end='')
            if max_ts:
                print(f", last bar={datetime.fromtimestamp(max_ts, tz=timezone.utc).strftime('%Y-%m-%d')}", end='')
            print()

            # Extract this symbol's OHLCV — yfinance 1.x uses MultiIndex (Price, Ticker)
            df = pd.DataFrame({
                'Open':   raw['Open'][symbol],
                'High':   raw['High'][symbol],
                'Low':    raw['Low'][symbol],
                'Close':  raw['Close'][symbol],
                'Volume': raw['Volume'][symbol],
            }) if isinstance(raw.columns, pd.MultiIndex) else raw[['Open','High','Low','Close','Volume']]
            df.index.name = 'timestamp'
            df = df.dropna()

            saved = db.save_daily_bars(symbol, df)

            min_ts2, max_ts2, count2 = db.get_daily_bars_range(symbol)
            first = datetime.fromtimestamp(min_ts2, tz=timezone.utc).strftime('%Y-%m-%d')
            last = datetime.fromtimestamp(max_ts2, tz=timezone.utc).strftime('%Y-%m-%d')
            print(f"{symbol}: inserted {saved} new rows → total {count2} bars ({first} to {last})")

        except Exception as e:
            print(f"{symbol}: ERROR — {e}")

    print("\nDone.")


if __name__ == '__main__':
    main()
