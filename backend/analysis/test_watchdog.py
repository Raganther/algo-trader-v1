"""
Watchdog alarm tests — an alarm that has never been seen to fire is not an alarm.

Feeds synthetic broker states through watchdog.check_broker() and asserts the
right alerts appear. Covers the exact conditions that went undetected in
production: the Jul 7 2026 naked position and the Jun 16 2026 oversized short.

Run:  python3 -m backend.analysis.test_watchdog
"""

import sys

from backend.analysis import watchdog as W


def _run(account, positions, orders):
    """Drive check_broker() against a synthetic broker state."""
    W.CRIT.clear(); W.WARN.clear(); W.INFO.clear(); W.SKIP.clear()
    W._api = lambda path, params=None: {          # noqa: SLF001
        "/v2/account": account,
        "/v2/positions": positions,
        "/v2/orders": orders,
    }[path]
    W.check_broker()
    return list(W.CRIT)


ACCT = {"equity": "100000"}


def pos(sym, qty, mv):
    return {"symbol": sym, "qty": str(qty), "market_value": str(mv)}


def order(sym, side, qty, typ="stop"):
    return {"symbol": sym, "side": side, "qty": str(qty), "type": typ}


CASES = []


def case(name):
    def deco(fn):
        CASES.append((name, fn))
        return fn
    return deco


@case("naked long is CRITICAL (the Jul 7 failure)")
def _():
    crit = _run(ACCT, [pos("XBI", 156, 23798)], [])
    assert any("NAKED POSITION" in c and "XBI" in c for c in crit), crit


@case("naked short is CRITICAL")
def _():
    crit = _run(ACCT, [pos("GLD", -64, -24000)], [])
    assert any("NAKED POSITION" in c and "GLD" in c for c in crit), crit


@case("partially covered position is CRITICAL")
def _():
    crit = _run(ACCT, [pos("GDX", 328, 25000)], [order("GDX", "sell", 100)])
    assert any("NAKED POSITION" in c for c in crit), crit


@case("fully covered long is clean")
def _():
    crit = _run(ACCT, [pos("GDX", 328, 25000)], [order("GDX", "sell", 328)])
    assert not crit, crit


@case("covered by market exit (not just stop) is clean")
def _():
    crit = _run(ACCT, [pos("XBI", 156, 23798)], [order("XBI", "sell", 156, "market")])
    assert not crit, crit


@case("wrong-side order does NOT count as coverage")
def _():
    crit = _run(ACCT, [pos("GDX", 328, 25000)], [order("GDX", "buy", 328)])
    assert any("NAKED POSITION" in c for c in crit), crit


@case("short covered by buy stop is clean")
def _():
    crit = _run(ACCT, [pos("GLD", -64, -24000)], [order("GLD", "buy", 64)])
    assert not crit, crit


@case("oversized position is CRITICAL (the Jun 16 464sh short)")
def _():
    crit = _run(ACCT, [pos("GLD", -464, -172000)], [order("GLD", "buy", 464)])
    assert any("OVERSIZED" in c for c in crit), crit
    assert any("LEVERAGE" in c for c in crit), crit


@case("normal 25% position is not flagged oversized")
def _():
    crit = _run(ACCT, [pos("GDX", 328, 25000)], [order("GDX", "sell", 328)])
    assert not any("OVERSIZED" in c for c in crit), crit


@case("flat account is clean")
def _():
    assert not _run(ACCT, [], []), "flat account should raise nothing"


def main():
    passed = failed = 0
    for name, fn in CASES:
        try:
            fn()
            print(f"  PASS  {name}")
            passed += 1
        except AssertionError as e:
            print(f"  FAIL  {name}\n          {e}")
            failed += 1
    print(f"\n{passed} passed, {failed} failed")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
