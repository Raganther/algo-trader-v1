"""
Fill-fidelity audit — Phase 0/1 of the backtest-fidelity harness.

Purpose
-------
The backtester credits every stop exit at *exactly* the stop price
(`trend_framework.py:277` -> `self.sell(price=sl_for_check, ...)`) and every
entry at the signal bar's Close. Live fills do neither: orders fragment into
partials and the price walks across them.

This module measures the gap using Alpaca as ground truth, with no modelling
assumptions. It answers two questions:

  1. What did live ACTUALLY earn?  (round-trip realised P&L per symbol)
  2. What does the backtester's fill model ignore?  (execution shortfall)

Two shortfall metrics, both computed from broker records only:

  * intra-order walk  — VWAP(fill) vs first partial price. The backtester fills
    100% of size at a single price; this is the cost of that assumption alone.
    It is a hard LOWER bound on fill-model error.
  * stop shortfall    — VWAP(fill) vs the stop order's trigger price, signed so
    that negative = worse than the backtester assumed. The backtester assumes
    this is exactly zero on every stop exit.

Run:  python3 -m backend.analysis.fill_fidelity_audit [--start YYYY-MM-DD] [--end YYYY-MM-DD]
"""

import argparse
import os
import sys
from collections import defaultdict
from datetime import datetime, timezone

import requests
from dotenv import load_dotenv

load_dotenv()

BASE = os.getenv("ALPACA_ENDPOINT", "https://paper-api.alpaca.markets").rstrip("/")
HEADERS = {
    "APCA-API-KEY-ID": os.getenv("ALPACA_API_KEY") or "",
    "APCA-API-SECRET-KEY": os.getenv("ALPACA_SECRET_KEY") or "",
}

EQUITY_SYMBOLS = {"GLD", "IAU", "SLV", "GDX", "OIH", "XBI", "XOP", "XLE", "IWM", "SPY", "QQQ", "DIA"}


# ---------------------------------------------------------------- fetching

def _get(path, params):
    r = requests.get(f"{BASE}{path}", headers=HEADERS, params=params, timeout=30)
    r.raise_for_status()
    return r.json()


def fetch_fills(start, end):
    """All FILL/partial_fill activities in [start, end), paginated."""
    out, token = [], None
    while True:
        params = {"after": start, "until": end, "page_size": 100, "direction": "asc"}
        if token:
            params["page_token"] = token
        page = _get("/v2/account/activities/FILL", params)
        if not page:
            break
        out.extend(page)
        if len(page) < 100:
            break
        token = page[-1]["id"]
    return out


def fetch_orders(start, end):
    """Closed orders in the window, keyed by id — gives us type + stop price."""
    out, after = {}, start
    while True:
        page = _get("/v2/orders", {
            "status": "closed", "after": after, "until": end,
            "limit": 500, "direction": "asc", "nested": "false",
        })
        if not page:
            break
        new = 0
        for o in page:
            if o["id"] not in out:
                out[o["id"]] = o
                new += 1
        if new == 0 or len(page) < 500:
            break
        after = page[-1]["submitted_at"]
    return out


# ---------------------------------------------------------------- aggregation

def group_orders(fills):
    """Collapse partial fills into one record per order_id (size-weighted VWAP)."""
    agg = defaultdict(lambda: {"qty": 0.0, "notional": 0.0, "n": 0,
                               "first": None, "last": None, "t0": None, "t1": None})
    for f in fills:
        sym = f["symbol"]
        if sym not in EQUITY_SYMBOLS:
            continue
        a = agg[f["order_id"]]
        q, p = float(f["qty"]), float(f["price"])
        a["qty"] += q
        a["notional"] += q * p
        a["n"] += 1
        a["symbol"] = sym
        a["side"] = f["side"]
        if a["first"] is None:
            a["first"], a["t0"] = p, f["transaction_time"]
        a["last"], a["t1"] = p, f["transaction_time"]
    for a in agg.values():
        a["vwap"] = a["notional"] / a["qty"] if a["qty"] else 0.0
    return agg


def round_trips(orders_agg):
    """
    Walk each symbol's fills chronologically, netting signed size.
    Emit a closed trade whenever the running position returns to (or crosses) flat.
    Realised P&L uses actual VWAP fill prices — this is ground truth.
    """
    by_sym = defaultdict(list)
    for oid, a in orders_agg.items():
        by_sym[a["symbol"]].append((a["t0"], oid, a))
    trades = []
    for sym, recs in by_sym.items():
        recs.sort(key=lambda r: r[0])
        pos, basis, opened = 0.0, 0.0, None
        for t0, oid, a in recs:
            signed = a["qty"] if a["side"].startswith("buy") else -a["qty"]
            price = a["vwap"]
            if pos == 0:
                pos, basis, opened = signed, price, t0
                continue
            if (pos > 0) == (signed > 0):                      # adding
                total = pos + signed
                basis = (basis * pos + price * signed) / total
                pos = total
                continue
            closing = min(abs(pos), abs(signed))               # reducing / closing
            pnl = (price - basis) * closing * (1 if pos > 0 else -1)
            trades.append({"symbol": sym, "opened": opened, "closed": t0,
                           "qty": closing, "entry": basis, "exit": price, "pnl": pnl})
            pos += signed
            if pos != 0 and (pos > 0) != (signed < 0):
                basis, opened = price, t0                      # flipped through flat
            elif pos == 0:
                opened = None
    return trades


# ---------------------------------------------------------------- shortfall

def shortfall(orders_agg, orders_meta):
    """Per-order execution shortfall, signed so negative = worse than backtest assumes."""
    walk, stops = [], []
    for oid, a in orders_agg.items():
        sign = 1 if a["side"].startswith("buy") else -1
        # intra-order walk: paying more (buy) or receiving less (sell) than first touch
        walk.append({"symbol": a["symbol"], "n": a["n"], "qty": a["qty"],
                     "per_share": -sign * (a["vwap"] - a["first"]),
                     "dollars": -sign * (a["vwap"] - a["first"]) * a["qty"]})
        m = orders_meta.get(oid)
        if not m:
            continue
        trigger = m.get("stop_price")
        if m.get("type") in ("stop", "stop_limit") and trigger:
            trig = float(trigger)
            stops.append({"symbol": a["symbol"], "trigger": trig, "vwap": a["vwap"],
                          "qty": a["qty"], "n": a["n"],
                          "per_share": -sign * (a["vwap"] - trig),
                          "dollars": -sign * (a["vwap"] - trig) * a["qty"]})
    return walk, stops


def reconcile(orders_agg, start, end):
    """
    Self-check: net signed size per symbol implied by the fills in the window,
    vs the broker's actual position now. If the window opened with a position
    already held, the first fill is a CLOSE that round_trips() mistakes for an
    OPEN — which corrupts every basis downstream. This guard makes that visible
    instead of silently producing a confident wrong P&L.
    """
    net = defaultdict(float)
    for a in orders_agg.values():
        net[a["symbol"]] += a["qty"] if a["side"].startswith("buy") else -a["qty"]
    actual = {p["symbol"]: float(p["qty"]) for p in _get("/v2/positions", {})}
    rows = []
    for sym in sorted(set(net) | set(actual)):
        implied, real = round(net.get(sym, 0.0), 4), actual.get(sym, 0.0)
        rows.append((sym, implied, real, abs(implied - real) < 1e-6))
    return rows


def _stat(rows, key):
    if not rows:
        return None
    vals = sorted(r[key] for r in rows)
    n = len(vals)
    return {"n": n, "total": sum(vals), "mean": sum(vals) / n,
            "median": vals[n // 2], "p10": vals[int(n * 0.10)], "p90": vals[int(n * 0.90)],
            "worst": vals[0]}


# ---------------------------------------------------------------- report

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--start", default="2026-04-13",
                    help="window of interest (reporting slice)")
    ap.add_argument("--end", default=datetime.now(timezone.utc).strftime("%Y-%m-%d"))
    ap.add_argument("--chain-from", default="2025-04-24",
                    help="account inception — chain is built from here so cost basis "
                         "is correct, then sliced to --start/--end")
    args = ap.parse_args()

    if not HEADERS["APCA-API-KEY-ID"]:
        sys.exit("No ALPACA_API_KEY in environment (.env)")

    print(f"Fill-fidelity audit  {args.start} -> {args.end}\n" + "=" * 72)

    # Chain from inception (position provably flat) so cost basis is correct;
    # the reporting window is applied afterwards as a slice.
    fills = fetch_fills(args.chain_from, args.end)
    meta = fetch_orders(args.start, args.end)
    agg_all = group_orders(fills)
    agg = {oid: a for oid, a in agg_all.items() if a["t0"][:10] >= args.start}
    print(f"  chain from {args.chain_from}: {len(fills)} fill events -> {len(agg_all)} orders")
    print(f"  window slice: {len(agg)} orders  ({len(meta)} order records joined)")

    frag = defaultdict(int)
    for a in agg.values():
        frag[a["n"]] += 1
    multi = sum(v for k, v in frag.items() if k > 1)
    print(f"  fragmented orders: {multi}/{len(agg)} ({100*multi/max(len(agg),1):.0f}%)  "
          f"max partials on one order: {max(frag) if frag else 0}")

    # -- reconciliation guard: is the trade chain trustworthy at all?
    rec = reconcile(agg_all, args.chain_from, args.end)
    bad = [r for r in rec if not r[3]]
    print(f"\n-- RECONCILIATION (implied net position vs broker) --")
    for sym, implied, real, ok in rec:
        print(f"    {sym:5s} implied {implied:>9,.0f}   broker {real:>9,.0f}   {'ok' if ok else 'MISMATCH'}")
    if bad:
        print(f"  !! {len(bad)} symbol(s) mismatched -> window opened with an inherited")
        print(f"     position. Round-trip P&L below is NOT trustworthy for those symbols.")

    # -- ground truth P&L (chain built from inception, sliced to window by close date)
    trades = [t for t in round_trips(agg_all) if t["closed"][:10] >= args.start]
    total = sum(t["pnl"] for t in trades)
    wins = [t for t in trades if t["pnl"] > 0]
    print(f"\n-- GROUND TRUTH (round-trip realised, actual fill prices) --")
    print(f"  {len(trades)} closed trades   total P&L ${total:,.2f}   "
          f"win rate {100*len(wins)/max(len(trades),1):.1f}%")
    per = defaultdict(lambda: [0, 0.0])
    for t in trades:
        per[t["symbol"]][0] += 1
        per[t["symbol"]][1] += t["pnl"]
    for sym, (n, p) in sorted(per.items(), key=lambda kv: kv[1][1]):
        print(f"    {sym:5s} n={n:3d}  ${p:>10,.2f}")

    # -- what the backtester ignores
    walk, stops = shortfall(agg, meta)
    print(f"\n-- EXECUTION SHORTFALL (backtester models this as exactly $0) --")
    w = _stat(walk, "dollars")
    if w:
        ws = _stat(walk, "per_share")
        print(f"  intra-order walk   n={w['n']:4d}  total ${w['total']:>10,.2f}   "
              f"mean ${w['mean']:+.2f}/order   median {ws['median']:+.4f}/share")
    s = _stat(stops, "dollars")
    if s:
        ss = _stat(stops, "per_share")
        print(f"  stop-fill vs trigger n={s['n']:4d}  total ${s['total']:>10,.2f}   "
              f"mean ${s['mean']:+.2f}/stop    median {ss['median']:+.4f}/share")
        print(f"                       p10 ${s['p10']:,.2f}  p90 ${s['p90']:,.2f}  "
              f"worst ${s['worst']:,.2f}")
    else:
        print("  stop-fill vs trigger: no stop orders matched in window")

    measured = (w["total"] if w else 0.0) + (s["total"] if s else 0.0)
    print(f"\n-- ATTRIBUTION --")
    print(f"  measured execution cost the backtester assumes away : ${measured:,.2f}")
    print(f"  actual realised P&L                                 : ${total:,.2f}")
    print(f"  implied P&L if fills were free (backtest's world)    : ${total - measured:,.2f}")
    if total:
        print(f"  execution cost as multiple of realised P&L          : {abs(measured/total):.2f}x")


if __name__ == "__main__":
    main()
