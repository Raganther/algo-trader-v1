# Procedure: Daily Trade Audit

**When to apply:** after each trading day to verify live bot execution, or when backfilling the calibration window. Run before git save on any day with active trades.

## Steps

1. **Query cloud DB for the day**
```bash
gcloud compute ssh algotrader2026 --zone=europe-west2-a --command="python3 -c \"
import sqlite3
conn = sqlite3.connect('/home/alistairelliman/algo-trader-v1/backend/research.db')
rows = conn.execute(\\\"SELECT id, symbol, side, qty, fill_price, pnl, timestamp, iteration_index, order_id FROM live_trade_log WHERE timestamp LIKE 'YYYY-MM-DD%' ORDER BY timestamp\\\").fetchall()
for r in rows: print(r)
\""
```

2. **User provides Alpaca records** — from the Alpaca web UI, export all orders for the day (includes filled and canceled).

3. **Cross-reference** — for every filled Alpaca order, find the matching DB record:
   - Symbol, side, qty, fill_price, and fill timestamp must match
   - Canceled orders (trail ratchets) don't need DB records — they're normal
   - Flag any DB record with no Alpaca match, or any filled Alpaca order with no DB record

4. **Reconstruct trades** — pair each buy with its sell to build the trade table:
   - Entry: first filled buy for that symbol in the session
   - Exit: corresponding filled sell
   - Exit type: `K` (market sell, iteration_index='0'), `TS` (server stop after trail ratchet), `SS` (server stop at initial stop level, no ratchet)
   - Stop level at exit: the stop price of the filled stop order (from Alpaca)
   - Slippage: fill_price − stop_level (negative = filled below stop, expected)

5. **Log to live-trade-log.md** — add a section for the day with audit status and trade table. Format:
```
## YYYY-MM-DD
**Audit status:** PASS (N/N DB records matched Alpaca)
| Bot | Entry time (UTC) | Entry $ | Exit time (UTC) | Exit $ | Exit type | Stop level at exit | P&L/share | Notes |
```

6. **Note anomalies** — delayed fills, simultaneous correlated stops, unprotected positions, unusual slippage.

## Notes
- Local DB only has data to Feb 2026 — always query cloud DB
- sqlite3 not installed on cloud server — use python3 sqlite3 module
- Canceled stop orders in Alpaca = trail ratchets, not errors
- iteration_index: '0' = K-signal or normal exit, 'server_stop' = Alpaca stop fired, 'reconciled' = added by startup reconciliation

## Example (Mar 20–27 2026)
Backfilled 6 trading days. Total 60 DB records across all days — all matched Alpaca exactly (PASS every day). Identified Mar 24 server stop count correction (5→6) and Mar 26 pending_fills bug evidence (no stop placed for delayed SLV fill).
