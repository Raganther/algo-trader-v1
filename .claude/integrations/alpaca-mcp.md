# Alpaca MCP — Tool Reference

Status: current | Epistemic: confirmed | Last verified: 2026-04-01

Alpaca MCP server (`uvx alpaca-mcp-server`) configured in `~/.claude/settings.json`. Uses existing Alpaca paper trading keys. Requires Claude Code restart to activate after config changes.

---

## What's available (57 tools, 11 categories)

### Account & Config (4 tools)
- `get_account_info` — balances, equity, buying power, account status
- `get_account_config` — trading restrictions, margin, PDT, options level
- `update_account_config` — change margin, shorting, fractional trading settings
- `get_account_activities` — fills, dividends, transfers; filterable by type + date range (max 100/page, paginated)

### Orders (7 tools)
- `get_orders` — list orders with filters (status, symbols, date range, side); max 500
- `get_order_by_id` / `get_order_by_client_id` — single order lookup
- `place_stock_order` — full order placement (market, limit, stop, stop_limit, trailing_stop, bracket)
- `replace_order_by_id` — modify open order (price, qty, TIF, trail)
- `cancel_order_by_id` / `cancel_all_orders` — cancel orders

### Positions (3 tools)
- `get_all_positions` — all open positions with unrealised P&L
- `get_open_position` — single position by symbol
- `close_position` — emergency close (sells at market)

### Portfolio (1 tool)
- `get_portfolio_history` — equity + P&L curve over time (1Min–1Day resolution, start/end/period)

### Stock Market Data (7 tools)
- `get_stock_bars` — historical OHLCV (1Min–1Month, up to 10k points, feed: sip/iex)
- `get_stock_latest_bar` — latest minute bar
- `get_stock_latest_quote` — latest bid/ask
- `get_stock_latest_trade` — latest trade price
- `get_stock_quotes` — historical bid/ask quotes
- `get_stock_trades` — historical tick-level trades
- `get_stock_snapshot` — combined snapshot (latest trade + quote + minute bar + daily bar)

### Calendar & Assets (4 tools)
- `get_clock` — market open/closed + next open/close times
- `get_calendar` — trading calendar with open/close for date range (always pass start+end)
- `get_asset` — single symbol details (tradable, shortable, fractionable)
- `get_all_assets` — full asset list (always filter by status/exchange to avoid huge response)

### Market Screeners (2 tools)
- `get_market_movers` — top gainers/losers (stocks or crypto)
- `get_most_active_stocks` — most active by volume or trade count

### Corporate Actions (3 tools)
- `get_corporate_actions` — dividends, splits, mergers by symbol/date
- `get_corporate_action_announcements` — upcoming/recent announcements (max 90 day range)
- `get_corporate_action_announcement` — single announcement by ID

### Options (10 tools)
Chain, contracts, bars, trades, latest quote/trade, snapshot (with Greeks/IV), exchange codes, order placement. Not relevant to current equity/ETF strategy.

### Crypto (7 tools)
Bars, quotes, trades, latest bar/quote/trade, orderbook, snapshot, order placement. Not relevant to precious metals strategy.

### Watchlists (5 tools)
CRUD for watchlists. Minor utility.

---

## What's NOT in the MCP
- **News** — no news endpoint. Use web search for market context/news correlation.
- **Streaming/WebSocket** — request/response only, no real-time streaming.
- **Account statements** — no tax docs or statement downloads.

---

## High-value tools for this project

Ranked by impact for the forward testing / calibration phase:

| Rank | Tool | Replaces | Use case |
|------|------|----------|----------|
| 1 | `get_orders(status="closed", symbols="GLD,IAU,SLV,GDX")` | SSH → DB audit | Pull all closed orders for calibration window — entry/exit prices, timestamps, stop levels |
| 2 | `get_account_activities(activity_types=["FILL"])` | SSH → DB cross-reference | Fill-level detail (exact prices, timestamps, quantities) |
| 3 | `get_portfolio_history` | Manual equity calc | Daily equity curve for calibration comparison |
| 4 | `get_stock_bars` | `fetch_price_data.py` | Spot-check price action on specific trade days |
| 5 | `get_all_positions` | SSH → pm2 logs | Quick overnight hold check |
| 6 | `get_calendar` | Manual count | Confirm trading days in calibration window |
| 7 | `get_corporate_action_announcements` | Web search | Check for dividends/splits causing price gaps |
| 8 | `get_clock` | SSH → `date -u` | Market status check |

---

## Usage notes

- **Feed parameter:** paper accounts default to `iex` (free). `sip` (all exchanges) requires paid data subscription. For historical bars, specify `feed="iex"` explicitly to avoid 403 errors.
- **Pagination:** `get_account_activities` and `get_orders` return max 100/500 per page. Use `page_token` / `after_order_id` for full history.
- **Date formats:** most tools accept RFC 3339 (`2026-03-20T00:00:00Z`) or `YYYY-MM-DD`.
- **Order placement tools exist but bots handle all trading.** Only use `place_stock_order` / `close_position` / `cancel_*` in emergencies — never for routine operations.
- **`get_calendar` and `get_all_assets` produce huge responses without filters.** Always pass date range or status/exchange filters.

---

## Example commands for daily audit

```
# All closed orders for calibration window
get_orders(status="closed", symbols="GLD,IAU,SLV,GDX", after="2026-03-20T00:00:00Z", direction="asc", limit=500)

# All fills for a specific day
get_account_activities(activity_types=["FILL"], date="2026-04-01")

# Current positions (overnight hold check)
get_all_positions()

# Equity curve for calibration window
get_portfolio_history(start="2026-03-20T00:00:00Z", end="2026-04-20T00:00:00Z", timeframe="1D")

# Check for corporate actions during calibration
get_corporate_action_announcements(ca_types="Dividend,Split", symbol="GLD", since="2026-03-20", until="2026-04-20")

# Spot-check 15m bars for a specific day
get_stock_bars(symbols="GLD", timeframe="15Min", start="2026-03-23T13:30:00Z", end="2026-03-23T20:00:00Z", feed="iex")
```
