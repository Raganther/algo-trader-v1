"""
Gap-conditional stop-fill model — Phase 2 of the backtest-fidelity harness.

Problem
-------
`trend_framework.py:277/290` fills every stop at exactly the trigger price.
The fill-fidelity audit measured what that assumption costs live: -$6,022 across
111 stops (mean -$54.26/stop) over Apr-Jul 2026 — comparable in size to the
strategy's entire modelled edge.

Model
-----
A bar-resolution backtest cannot know the intrabar path. The only signal it has
about how badly a stop was breached is how far the bar's extreme ran past the
trigger. So we fill at a point *between* the trigger and the bar extreme:

    long  (sell stop):  fill = trigger - k * (trigger - low)
    short (buy stop):   fill = trigger + k * (high - trigger)

k = 0 reproduces today's (broken) model. k = 1 fills at the worst price in the
bar. k is fit from real fills so the backtest is UNBIASED IN AGGREGATE. It will
still be wrong trade-by-trade — that is unavoidable at bar resolution and is
stated rather than hidden.

Run:  python3 -m backend.analysis.stop_fill_model
Writes: backend/analysis/stop_fill_model.json
"""

import json
import os
from collections import defaultdict
from datetime import datetime, timedelta, timezone

import requests

from backend.analysis.fill_fidelity_audit import (
    EQUITY_SYMBOLS, HEADERS, fetch_fills, fetch_orders, group_orders,
)

DATA_BASE = "https://data.alpaca.markets"
OUT = os.path.join(os.path.dirname(__file__), "stop_fill_model.json")


def fetch_bar(symbol, ts_iso, timeframe="15Min"):
    """The bar containing ts_iso (fills land inside a 15m bar)."""
    t = datetime.fromisoformat(ts_iso.replace("Z", "+00:00"))
    start = (t - timedelta(minutes=20)).astimezone(timezone.utc)
    end = (t + timedelta(minutes=20)).astimezone(timezone.utc)
    r = requests.get(f"{DATA_BASE}/v2/stocks/bars", headers=HEADERS, timeout=30, params={
        "symbols": symbol, "timeframe": timeframe,
        "start": start.strftime("%Y-%m-%dT%H:%M:%SZ"),
        "end": end.strftime("%Y-%m-%dT%H:%M:%SZ"),
        "feed": "iex", "limit": 10,
    })
    if r.status_code != 200:
        return None
    bars = r.json().get("bars", {}).get(symbol, [])
    best = None
    for b in bars:
        bt = datetime.fromisoformat(b["t"].replace("Z", "+00:00"))
        if bt <= t and (best is None or bt > best[0]):
            best = (bt, b)
    return best[1] if best else None


def collect(start="2026-04-13", end=None):
    """Join stop fills to their containing bar. Returns observation rows."""
    end = end or datetime.now(timezone.utc).strftime("%Y-%m-%d")
    fills = fetch_fills(start, end)
    meta = fetch_orders(start, end)
    agg = group_orders(fills)

    rows, skipped = [], 0
    for oid, a in agg.items():
        m = meta.get(oid)
        if not m or m.get("type") not in ("stop", "stop_limit") or not m.get("stop_price"):
            continue
        trig = float(m["stop_price"])
        bar = fetch_bar(a["symbol"], a["t1"])
        if not bar:
            skipped += 1
            continue
        is_sell = a["side"].startswith("sell")          # long exit -> sell stop
        extreme = float(bar["l"]) if is_sell else float(bar["h"])
        breach = (trig - extreme) if is_sell else (extreme - trig)
        slip = (trig - a["vwap"]) if is_sell else (a["vwap"] - trig)   # +ve = worse
        rows.append({
            "symbol": a["symbol"], "side": a["side"], "qty": a["qty"],
            "trigger": trig, "vwap": a["vwap"], "extreme": extreme,
            "breach": breach, "slip": slip,
            "breach_frac": breach / trig if trig else 0.0,
        })
    return rows, skipped


def fit_k(rows):
    """
    Least-squares k through the origin: slip ~= k * breach.
    Also report the dollar-weighted k, which is what actually matters for P&L
    (a few large-qty stops dominate the account impact).
    """
    usable = [r for r in rows if r["breach"] > 0]
    num = sum(r["breach"] * r["slip"] for r in usable)
    den = sum(r["breach"] ** 2 for r in usable)
    k_ls = num / den if den else 0.0

    wnum = sum(r["qty"] * r["breach"] * r["slip"] for r in usable)
    wden = sum(r["qty"] * r["breach"] ** 2 for r in usable)
    k_w = wnum / wden if wden else 0.0

    # Moment-matching k: the value that makes total predicted cost equal total
    # measured cost. This — not least squares — is what "unbiased in aggregate"
    # means, and it is the one we ship. LS minimises squared error and so
    # over-weights the few large-breach stops.
    k_m = (sum(r["slip"] * r["qty"] for r in rows)
           / sum(r["breach"] * r["qty"] for r in rows if r["breach"] > 0))
    return k_ls, k_w, k_m, usable


def main():
    print("Gap-conditional stop-fill model\n" + "=" * 68)
    rows, skipped = collect()
    print(f"  {len(rows)} stop fills joined to bars ({skipped} unmatched)")
    if not rows:
        return

    k_ls, k_w, k_m, usable = fit_k(rows)
    breached = len(usable)
    print(f"  {breached}/{len(rows)} breached the trigger within the bar "
          f"({100*breached/len(rows):.0f}%)\n")

    print(f"  k (least squares, per-order)  = {k_ls:.4f}")
    print(f"  k (share-weighted LS)         = {k_w:.4f}")
    print(f"  k (moment-matched)  <-- SHIP  = {k_m:.4f}")

    # Validate: does the fitted model reproduce aggregate live cost?
    for label, k in (("current model (k=0)", 0.0), ("LS k", k_w),
                     ("moment-matched k", k_m), ("worst-case (k=1)", 1.0)):
        pred = sum(k * r["breach"] * r["qty"] for r in rows)
        print(f"    {label:22s} -> predicted cost ${-pred:>10,.2f}")
    actual = sum(r["slip"] * r["qty"] for r in rows)
    print(f"    {'ACTUAL measured':22s} -> ${-actual:>10,.2f}")

    by_sym = defaultdict(lambda: [0, 0.0, 0.0])
    for r in rows:
        s = by_sym[r["symbol"]]
        s[0] += 1
        s[1] += r["slip"] * r["qty"]
        s[2] += r["breach"] * r["qty"]
    print("\n  per-symbol   n   actual $      breach $   implied k")
    for sym, (n, sl, br) in sorted(by_sym.items()):
        print(f"    {sym:5s}    {n:3d}  {-sl:>10,.2f}  {-br:>10,.2f}   "
              f"{(sl/br if br else 0):.3f}")

    model = {
        "fitted_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "window": "2026-04-13..present",
        "n_stops": len(rows), "n_breached": breached,
        "k_least_squares": round(k_ls, 4),
        "k_share_weighted": round(k_w, 4),
        "k": round(k_m, 4),
        "actual_cost_usd": round(actual, 2),
        "note": "fill = trigger -/+ k * (trigger - low | high - trigger). "
                "Unbiased in aggregate, noisy per-trade — bar resolution cannot "
                "recover the intrabar path.",
    }
    with open(OUT, "w") as f:
        json.dump(model, f, indent=2)
    print(f"\n  wrote {OUT}")


if __name__ == "__main__":
    main()
