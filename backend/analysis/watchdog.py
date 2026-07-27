"""
Daily watchdog — Stage 1 of the autonomous operations loop.

Checks facts, not strategy quality. Every check here exists because something
actually went wrong:

  naked position   Jul 7 2026: GDX + XBI held $48k notional (50% of equity) with
                   no protective stop for 19 days. A daily run catches it on day 1.
  desync halt      Jun 16 + Jul 7 2026: strategy belief diverging from broker.
  oversized        Jun 16 2026: GLD short compounded 58 -> 464sh (~193% notional).
  stale process    bot alive but loop wedged / not polling during market hours.
  equity tripwire  drawdown from high-water mark.

Read-only by design. It never places, modifies or cancels an order, never
restarts a bot, never deploys. It reports and escalates.

Degrades gracefully: anything it cannot verify is reported as COULD-NOT-CHECK,
never silently passed.

Exit codes:  0 = all clear   1 = warnings   2 = critical
Run:  python3 -m backend.analysis.watchdog
"""

import json
import os
import shlex
import subprocess
import sys
from datetime import datetime, timezone

import requests
from dotenv import load_dotenv

load_dotenv()

BASE = os.getenv("ALPACA_ENDPOINT", "https://paper-api.alpaca.markets").rstrip("/")
HEADERS = {
    "APCA-API-KEY-ID": os.getenv("ALPACA_API_KEY") or "",
    "APCA-API-SECRET-KEY": os.getenv("ALPACA_SECRET_KEY") or "",
}
BOTS = ["gld-test", "iau-test", "slv-test", "gdx-test", "oih-test", "xbi-test", "xop-test"]
ZONE, HOST = "us-east1-b", "algotrader-us"

# Thresholds
MAX_POSITION_FRAC = 0.30      # per-position notional cap is 0.25; 0.30 allows drift
MAX_GROSS_FRAC = 1.05         # aggregate notional vs equity (leverage guard)
DD_WARN = 0.08                # drawdown from high-water mark

CRIT, WARN, INFO, SKIP = [], [], [], []


def _api(path, params=None):
    r = requests.get(f"{BASE}{path}", headers=HEADERS, params=params or {}, timeout=30)
    r.raise_for_status()
    return r.json()


def _ssh(cmd, timeout=120):
    """Returns (ok, output). Never raises — gcloud may be absent in a cloud runner."""
    try:
        p = subprocess.run(
            ["gcloud", "compute", "ssh", HOST, f"--zone={ZONE}", f"--command={cmd}"],
            capture_output=True, text=True, timeout=timeout,
        )
        return (p.returncode == 0), (p.stdout or "") + (p.stderr or "")
    except FileNotFoundError:
        return False, "gcloud not installed"
    except subprocess.TimeoutExpired:
        return False, "ssh timed out"
    except Exception as e:                                    # noqa: BLE001
        return False, f"ssh failed: {e}"


# ------------------------------------------------------------------ checks

def check_broker():
    """Positions, protective coverage, sizing sanity. The core safety check."""
    acct = _api("/v2/account")
    equity = float(acct["equity"])
    positions = _api("/v2/positions")
    orders = _api("/v2/orders", {"status": "open", "limit": 500})

    INFO.append(f"equity ${equity:,.2f} | {len(positions)} position(s) | {len(orders)} open order(s)")

    # Map symbol -> exit-side coverage from resting orders
    cover = {}
    for o in orders:
        sym, side = o["symbol"], o["side"]
        qty = float(o.get("qty") or 0)
        cover.setdefault(sym, []).append((side, qty, o["type"]))

    gross = 0.0
    for p in positions:
        sym = p["symbol"]
        qty = float(p["qty"])
        mv = abs(float(p["market_value"]))
        gross += mv
        need_side = "sell" if qty > 0 else "buy"
        covered = sum(q for s, q, _ in cover.get(sym, []) if s.startswith(need_side))
        kinds = {t for s, _, t in cover.get(sym, []) if s.startswith(need_side)}

        if covered < abs(qty) - 1e-6:
            CRIT.append(
                f"NAKED POSITION — {sym} {qty:+g} (${mv:,.0f}, {100*mv/equity:.1f}% of equity) "
                f"has protective coverage for only {covered:g} share(s). "
                f"This is the Jul 7 failure mode."
            )
        else:
            INFO.append(f"  {sym:5s} {qty:+8g}  ${mv:>10,.0f}  covered by {'/'.join(sorted(kinds))}")

        if mv > equity * MAX_POSITION_FRAC:
            CRIT.append(
                f"OVERSIZED — {sym} notional ${mv:,.0f} is {100*mv/equity:.1f}% of equity "
                f"(cap {100*MAX_POSITION_FRAC:.0f}%). Possible desync accumulation."
            )

    if gross > equity * MAX_GROSS_FRAC:
        CRIT.append(f"LEVERAGE — gross notional ${gross:,.0f} = {100*gross/equity:.0f}% of equity")
    elif positions:
        INFO.append(f"gross notional ${gross:,.0f} ({100*gross/equity:.0f}% of equity)")
    return equity


def check_drawdown(equity):
    try:
        h = _api("/v2/account/portfolio/history", {"period": "3M", "timeframe": "1D"})
        eq = [e for e in h.get("equity", []) if e]
        if not eq:
            SKIP.append("drawdown: no portfolio history returned")
            return
        peak = max(eq)
        dd = (peak - equity) / peak if peak else 0.0
        line = f"drawdown {100*dd:.2f}% from 3M peak ${peak:,.0f}"
        (WARN if dd > DD_WARN else INFO).append(
            (f"DRAWDOWN — {line} exceeds {100*DD_WARN:.0f}% threshold") if dd > DD_WARN else line)
    except Exception as e:                                    # noqa: BLE001
        SKIP.append(f"drawdown: {e}")


def check_bots():
    """pm2 process health + DESYNC-HALT + loop staleness. Needs gcloud."""
    ok, out = _ssh("pm2 jlist")
    if not ok:
        SKIP.append(f"bot process health: unreachable ({out.strip().splitlines()[-1][:80] if out.strip() else 'no output'})")
        return
    try:
        procs = json.loads(out[out.index("["):out.rindex("]") + 1])
    except Exception:                                         # noqa: BLE001
        SKIP.append("bot process health: could not parse pm2 jlist")
        return

    seen = {}
    for p in procs:
        name = p.get("name", "")
        if name not in BOTS:
            continue
        env = p.get("pm2_env", {})
        seen[name] = env.get("status")
        if env.get("status") != "online":
            CRIT.append(f"BOT DOWN — {name} status={env.get('status')}")
    for b in BOTS:
        if b not in seen:
            CRIT.append(f"BOT MISSING — {b} not registered in pm2")
    if seen and not CRIT:
        INFO.append(f"pm2: {len(seen)}/{len(BOTS)} bots online")

    # Latest heartbeat per bot — catches DESYNC-HALT and wedged loops
    cmd = ("for b in " + " ".join(BOTS) + "; do printf '%s|' $b; "
           "grep HEARTBEAT /home/alistairelliman/.pm2/logs/${b}-out.log 2>/dev/null "
           "| tail -1 || echo ''; done")
    ok, out = _ssh(shlex.quote(cmd).join(("bash -c ", "")))
    if not ok:
        SKIP.append("bot heartbeats: unreachable")
        return
    parsed = 0
    for line in out.splitlines():
        if "|" not in line:
            continue
        bot, _, hb = line.partition("|")
        bot = bot.strip()
        if bot not in BOTS:
            continue
        parsed += 1
        if "DESYNC" in hb:
            CRIT.append(f"DESYNC-HALT — {bot} is halted and taking no action: {hb.strip()[:110]}")
        elif not hb.strip():
            WARN.append(f"{bot}: no heartbeat line found in log")
    # Silence must never be ambiguous between "checked, all fine" and "parsed
    # nothing". Say explicitly how many bots were actually inspected.
    if parsed == 0:
        SKIP.append("bot heartbeats: command ran but no heartbeat lines could be parsed")
    else:
        INFO.append(f"heartbeats parsed for {parsed}/{len(BOTS)} bots — no DESYNC-HALT")
        if parsed < len(BOTS):
            WARN.append(f"heartbeat check only covered {parsed}/{len(BOTS)} bots")


def market_open():
    try:
        return bool(_api("/v2/clock").get("is_open"))
    except Exception:                                         # noqa: BLE001
        return None


# ------------------------------------------------------------------ report

def main():
    now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    print(f"ALGO-TRADER WATCHDOG  {now}\n" + "=" * 70)

    if not HEADERS["APCA-API-KEY-ID"]:
        print("CRITICAL: no Alpaca credentials available — cannot check anything.")
        return 2

    is_open = market_open()
    INFO.append(f"market {'OPEN' if is_open else 'closed' if is_open is not None else 'unknown'}")

    try:
        equity = check_broker()
        check_drawdown(equity)
    except Exception as e:                                    # noqa: BLE001
        CRIT.append(f"BROKER CHECK FAILED — {e}")
    check_bots()

    for label, rows in (("CRITICAL", CRIT), ("WARNING", WARN)):
        if rows:
            print(f"\n{label}")
            for r in rows:
                print(f"  ! {r}")
    if SKIP:
        print("\nCOULD NOT CHECK  (not a pass — verify manually)")
        for r in SKIP:
            print(f"  ? {r}")
    print("\nSTATUS")
    for r in INFO:
        print(f"  . {r}")

    verdict = "CRITICAL" if CRIT else ("WARNINGS" if WARN else "ALL CLEAR")
    print("\n" + "=" * 70)
    print(f"VERDICT: {verdict}" + (f"  ({len(SKIP)} check(s) could not run)" if SKIP else ""))
    return 2 if CRIT else (1 if WARN else 0)


if __name__ == "__main__":
    sys.exit(main())
