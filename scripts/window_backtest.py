"""One-off: run the 7-bot portfolio over a date window with the LIVE config
(HWM trail anchor + adx_filter_mode='all' default) and dump equity + trades to JSON.

Used for the live-vs-backtest day-14 gate (roadmap: HWM convergence horizons).

  python3 scripts/window_backtest.py --start 2026-02-01 --end 2026-05-21 \
      --source alpaca --out /tmp/bt_recent.json
  python3 scripts/window_backtest.py --start 2020-07-27 --end 2026-04-27 \
      --source cache --out /tmp/bt_full.json
"""
import argparse, json, sys
import pandas as pd
from backend.engine.alpaca_loader import AlpacaDataLoader
from backend.database import DatabaseManager
from backend.engine.portfolio_runner import PortfolioRunner
from backend.strategies.trend_framework import TrendFrameworkStrategy

LIVE_PARAMS = {
    "rsi_period": 7, "stoch_period": 14, "overbought": 80, "oversold": 15,
    "adx_threshold": 20, "skip_adx_filter": False, "sl_atr": 2.0,
    "dynamic_adx": False, "trailing_stop": True, "trail_atr": 2.0,
    "trail_after_bars": 10, "min_hold_bars": 10, "skip_days": [0],
    "trading_hours": [13.5, 20], "trail_anchor": "hwm",
    "adx_filter_mode": "all",  # matches the live bots (run scripts pinned to 'all' May 21)
}


def load(symbols, start, end, source):
    data = {}
    if source == "cache":
        db = DatabaseManager(); db.initialize_db()
        s = int(pd.Timestamp(start, tz="UTC").timestamp())
        e = int(pd.Timestamp(end, tz="UTC").timestamp())
        for sym in symbols:
            rows = db.get_price_bars(sym, start_ts=s, end_ts=e)
            if not rows:
                print(f"  WARN no cache for {sym}"); continue
            df = pd.DataFrame(rows)
            df["timestamp"] = pd.to_datetime(df["timestamp"], unit="s", utc=True)
            df = df.set_index("timestamp").sort_index().rename(
                columns={"open": "Open", "high": "High", "low": "Low",
                         "close": "Close", "volume": "Volume"})
            data[sym] = df
            print(f"  CACHE {sym}: {len(df)} bars {df.index[0]} -> {df.index[-1]}")
    else:
        loader = AlpacaDataLoader()
        for sym in symbols:
            df = loader.fetch_data(sym, "15m", start, end)
            if df is None or df.empty:
                print(f"  WARN no alpaca data for {sym}"); continue
            data[sym] = df
            print(f"  OK {sym}: {len(df)} bars {df.index[0]} -> {df.index[-1]}")
    return data


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--start", required=True)
    ap.add_argument("--end", required=True)
    ap.add_argument("--symbols", default="GLD,IAU,SLV,GDX,OIH,XBI,XOP")
    ap.add_argument("--source", choices=["cache", "alpaca"], default="alpaca")
    ap.add_argument("--initial", type=float, default=94000.0)
    ap.add_argument("--spread", type=float, default=0.0003)
    ap.add_argument("--out", required=True)
    ap.add_argument("--adx-mode", default=None, choices=["all", "entry_only"],
                    help="override adx_filter_mode (default: omit -> 'all', matches live)")
    ap.add_argument("--trail-anchor", default=None, choices=["close", "hwm"],
                    help="override trail_anchor (default: hwm)")
    args = ap.parse_args()

    symbols = [s.strip() for s in args.symbols.split(",")]
    print(f"Loading {symbols} {args.start} -> {args.end} ({args.source})")
    data = load(symbols, args.start, args.end, args.source)
    if not data:
        print("No data."); sys.exit(1)

    params = dict(LIVE_PARAMS)
    if args.adx_mode:
        params["adx_filter_mode"] = args.adx_mode
    if args.trail_anchor:
        params["trail_anchor"] = args.trail_anchor
    pr = PortfolioRunner(symbol_data=data, strategy_class=TrendFrameworkStrategy,
                         parameters=params, initial_capital=args.initial,
                         spread=args.spread)
    res = pr.run()
    print(f"\nReturn {res['return_pct']}%  Sharpe {res['sharpe']}  "
          f"DD {res['max_drawdown']}%  trades {res['total_trades']}")

    def jsonable(v):
        if isinstance(v, pd.Timestamp):
            return v.isoformat()
        return v
    trades = [{k: jsonable(v) for k, v in t.items()} for t in res["trade_history"]]
    out = {
        "params": LIVE_PARAMS, "window": [args.start, args.end],
        "summary": {k: res[k] for k in ("initial_capital", "final_equity",
                    "return_pct", "max_drawdown", "sharpe", "total_trades",
                    "per_symbol", "max_concurrent")},
        "equity_history": res["equity_history"],
        "trade_history": trades,
    }
    with open(args.out, "w") as f:
        json.dump(out, f, default=str)
    print(f"Wrote {args.out}  ({len(trades)} trades, {len(res['equity_history'])} equity pts)")


if __name__ == "__main__":
    main()
