# Procedure: Daily Trade Audit

**When to apply:** after each trading day to verify live bot execution, or when backfilling the calibration window. Run before git save on any day with active trades.

## Steps

1. **Pull all orders for the day via Alpaca MCP**
```
get_orders(status="closed", symbols="GLD,IAU,SLV,GDX", after="YYYY-MM-DDT00:00:00Z", until="YYYY-MM-DDT23:59:59Z", direction="asc", limit=500)
```

2. **Separate filled from canceled orders**
   - Filled orders = actual trades (buys, sells, stop fires)
   - Canceled stop orders = trail ratchets (normal, not errors)
   - N trail updates = N+1 canceled stops per trade

3. **Reconstruct trades** — pair each buy with its corresponding sell:
   - Entry: filled buy (market order, `side="buy"`)
   - Exit: filled sell — determine exit type from order type:
     - `type="market"`, `side="sell"` → K-exit (bot signal)
     - `type="stop"`, `side="sell"`, `status="filled"` → TS or SS (server stop fired)
     - TS vs SS: if canceled stop orders precede it (trail ratchets), it's TS. If the filled stop is the only stop for that trade, it's SS.
   - Stop level at exit: `stop_price` on the filled stop order
   - Slippage: `filled_avg_price` − `stop_price` (negative = filled below stop, expected)
   - P&L/share: exit `filled_avg_price` − entry `filled_avg_price`

4. **Extract trail ratchet history** — from canceled stop orders for each trade:
   - Sort by `created_at`
   - The sequence of `stop_price` values shows the trail ratcheting up
   - Record as "ratcheted $X→$Y→$Z (N×)"

5. **Check for overnight holds**
```
get_all_positions()
```
   - Any open position at EOD is an overnight hold — note in the trade log with entry details and current stop level

6. **Log to live-trade-log.md** — add a section for the day:
```
## YYYY-MM-DD
**Audit status:** PASS (N/N Alpaca filled orders matched — M trades reconstructed)
| Bot | Entry time (UTC) | Entry $ | Exit time (UTC) | Exit $ | Exit type | Stop level at exit | P&L/share | Notes |
```

7. **Note anomalies** — delayed fills (gap between `created_at` and `filled_at`), simultaneous correlated entries/exits, unusual slippage, overnight holds.

## Key fields from get_orders response
- `created_at` — when order was placed (use for "entry time" on buys)
- `filled_at` — when order was filled (use for exact fill time)
- `filled_avg_price` — actual fill price
- `stop_price` — stop level (on stop orders)
- `type` — "market" or "stop"
- `side` — "buy" or "sell"
- `status` — "filled" or "canceled"
- `qty` / `filled_qty` — share count

## Fallback: SSH method
If MCP is unavailable, use SSH to query the cloud DB directly:
```bash
gcloud compute ssh algotrader2026 --zone=europe-west2-a --command="python3 -c \"
import sqlite3
conn = sqlite3.connect('/home/alistairelliman/algo-trader-v1/backend/research.db')
rows = conn.execute(\\\"SELECT id, symbol, side, qty, fill_price, pnl, timestamp, iteration_index, order_id FROM live_trade_log WHERE timestamp LIKE 'YYYY-MM-DD%' ORDER BY timestamp\\\").fetchall()
for r in rows: print(r)
\""
```
Then cross-reference with Alpaca web UI manually.

## Notes
- MCP `get_orders` returns both filled and canceled in one call — no separate DB + Alpaca cross-reference needed
- Canceled stop orders are trail ratchets, not errors
- For fill delays: compare `created_at` vs `filled_at` — gap > 30s means the buy went through pending_fills
- Paper accounts use `iex` feed — price data calls need `feed="iex"` to avoid 403
- Overnight hold stops expire at 20:00 UTC (DAY TIF) — re-placed on bot restart or next market open

## Example (Mar 23 2026)
Single `get_orders` call returned 26 orders: 13 filled + 13 canceled. Reconstructed 7 trades (6 K-exits + 1 TS fire). All prices, timestamps, and trail ratchet levels matched the existing trade log exactly. Validated Apr 1 2026 as proof that MCP replaces the SSH→DB→Alpaca workflow.
