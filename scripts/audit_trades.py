"""
Trade completeness audit — Alpaca filled orders vs DB records.

For each symbol, for each day, shows how many Alpaca fills are in DB.
Completeness trending toward 100% over time = bugs are being fixed.

Usage:
    python3 scripts/audit_trades.py [--days N]
"""

import sys
import os
import argparse
from datetime import datetime, timezone, timedelta
from collections import defaultdict

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.engine.alpaca_trader import AlpacaTrader
from backend.database import DatabaseManager

SYMBOLS = ['GLD', 'IAU', 'SLV', 'GDX']

def match(alpaca_order, db_trades):
    """True if this Alpaca order is already in DB (by side, qty, timestamp ±60s)."""
    for t in db_trades:
        if alpaca_order['side'] != (t.get('side') or ''):
            continue
        if abs(alpaca_order['qty'] - (t.get('qty') or 0)) > 0.01:
            continue
        try:
            ao_ts = datetime.fromisoformat(alpaca_order['filled_at'].replace('Z', '+00:00'))
            db_ts = datetime.fromisoformat((t.get('timestamp') or '').replace('Z', '+00:00'))
            if db_ts.tzinfo is None:
                db_ts = db_ts.replace(tzinfo=timezone.utc)
            if abs((ao_ts - db_ts).total_seconds()) <= 60:
                return True
        except Exception:
            continue
    return False

def run(days):
    trader = AlpacaTrader(paper=True)
    db = DatabaseManager()

    # Fetch all data upfront
    alpaca_all = {}
    db_all = {}
    for sym in SYMBOLS:
        alpaca_all[sym] = trader.get_filled_orders(sym, lookback_days=days)
        db_all[sym] = db.get_recent_live_trades(sym, days=days)

    # Group Alpaca orders by date
    by_date = defaultdict(lambda: defaultdict(list))  # date -> symbol -> [orders]
    for sym in SYMBOLS:
        for o in alpaca_all[sym]:
            if not o['filled_at']:
                continue
            date = o['filled_at'][:10]
            by_date[date][sym].append(o)

    print(f"\n{'='*65}")
    print(f"  Trade Completeness Audit — last {days} days")
    print(f"{'='*65}")
    print(f"{'Date':<12} {'Sym':<6} {'Alpaca':>6} {'DB':>4} {'Missing':>8}  {'Rate':>5}  {'Missing fills'}")
    print(f"{'-'*65}")

    total_alpaca = 0
    total_db = 0

    for date in sorted(by_date.keys()):
        for sym in SYMBOLS:
            orders = by_date[date][sym]
            if not orders:
                continue

            matched = sum(1 for o in orders if match(o, db_all[sym]))
            missing = len(orders) - matched
            rate = matched / len(orders) * 100
            total_alpaca += len(orders)
            total_db += matched

            missing_detail = ''
            if missing > 0:
                gaps = [o for o in orders if not match(o, db_all[sym])]
                missing_detail = ', '.join(
                    f"{g['side']} {g['qty']:.0f}@{g['fill_price']:.2f}" for g in gaps
                )

            flag = '  ✅' if missing == 0 else '  ❌'
            print(f"{date:<12} {sym:<6} {len(orders):>6} {matched:>4} {missing:>8}  {rate:>4.0f}%{flag}  {missing_detail}")

    print(f"{'-'*65}")
    overall = total_db / total_alpaca * 100 if total_alpaca else 0
    print(f"{'TOTAL':<12} {'ALL':<6} {total_alpaca:>6} {total_db:>4} {total_alpaca-total_db:>8}  {overall:>4.0f}%")
    print(f"{'='*65}\n")

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--days', type=int, default=7)
    args = parser.parse_args()
    run(args.days)
