# Recent Git History

> Auto-generated on git save. Do not edit manually.

----
**2026-03-14** — feat: add long_only param + establish long-only performance baseline
Added long_only=True parameter to StochRSIMeanReversionStrategy to gate short entry logic. Ran backtests across all 4 assets to establish the live baseline (bots are long-only due to Alpaca fractional short restriction). Key finding: SLV long-only is actually better risk-adjusted (Sharpe ~3.29 vs 2.54 full); GDX is most impacted (-42% return, Sharpe 2.41→~1.54). Results recorded in all 4 strategy cards and plan.md.

 .claude/memory/strategies/stochrsi_enhanced_gdx.md | 19 +++++++++++++++++++
 .claude/memory/strategies/stochrsi_enhanced_gld.md | 19 +++++++++++++++++++
 .claude/memory/strategies/stochrsi_enhanced_iau.md | 17 +++++++++++++++++
 .claude/memory/strategies/stochrsi_enhanced_slv.md | 19 +++++++++++++++++++
 CLAUDE.md                                          |  2 ++
 backend/strategies/stoch_rsi_mean_reversion.py     |  5 +++--
 memory/plan.md                                     | 11 +++++++++++
 7 files changed, 90 insertions(+), 2 deletions(-)

----
**2026-03-14** — chore: log Mar 13 trade audit + wash trade pre-market issue
All 12 Mar 13 Alpaca orders verified against DB — complete match across GLD, IAU, SLV. SLV overnight hold (Mar 12 buy, Mar 13 close at market open) revealed root cause of recurring wash trade rejection: pending_fills can submit a sell pre-market which sits open for hours, colliding with new entry signals before filling. Logged as known issue in plan and CLAUDE.md. Also confirmed Alpaca timestamps are UTC not ET, and fractional short selling constraint added to constraints.

 CLAUDE.md        |  8 ++++-
 memory/MEMORY.md | 99 +++++++++++++++++++++++---------------------------------
 memory/plan.md   |  3 ++
 3 files changed, 50 insertions(+), 60 deletions(-)

----
**2026-03-12** — fix: disable short selling — Alpaca rejects fractional short orders
Short entry attempts caused cascade failures: rejection left strategy
flat, subsequent long entries timed out, false SERVER STOP FIRED events.
Reverted sell() guard to block all sells from flat position. Short trading
requires whole-share quantity support before re-enabling.

Co-Authored-By: Claude Sonnet 4.6 <noreply@anthropic.com>

 backend/engine/live_broker.py | 27 +++------------------------
 1 file changed, 3 insertions(+), 24 deletions(-)

----
**2026-03-11** — feat: enable short trading in live broker
sell() now distinguishes three cases: closing a long (position > 0),
opening a short from flat (position == 0 + stop_loss provided), and
duplicate exit signal (position == 0, no stop_loss — blocked).
buy() now handles short closes (position < 0) by cancelling pending
buy stop before executing. update_stop_order() uses pending_stop_side
('sell' for longs, 'buy' for shorts) so trailing stops ratchet correctly
in both directions. Server stop logging in runner.py now records correct
exit side based on strategy position direction.

Co-Authored-By: Claude Sonnet 4.6 <noreply@anthropic.com>

 backend/engine/live_broker.py | 110 ++++++++++++++++++++++++++++--------------
 backend/runner.py             |  26 +++++-----
 2 files changed, 87 insertions(+), 49 deletions(-)

----
**2026-03-11** — docs: add short trading requirement to plan
Discovered live bots are long-only due to sell() guard blocking short entries from flat — an unintended side effect of the duplicate exit fix. Sharpe 2.54 backtest includes both long and short P&L. Plan updated with three steps: add long_only param to strategy, fix the sell guard to distinguish exit vs short entry, and re-verify all mechanics for short trades before switching to real money.

 memory/MEMORY.md | 21 ++++++++++-----------
 memory/plan.md   | 11 ++++++++++-
 2 files changed, 20 insertions(+), 12 deletions(-)

----
**2026-03-11** — fix: split bot check into today/yesterday to eliminate log misreading
Concatenating two log files and grepping produced unlabelled output, making it impossible to tell which lines were today vs yesterday. Now checks each file separately with clear -- today -- / -- yesterday -- headers. Eliminates the recurring misread bug.

 CLAUDE.md        |  4 ++--
 memory/MEMORY.md | 24 +++++++++++-------------
 2 files changed, 13 insertions(+), 15 deletions(-)

----
**2026-03-10** — fix: server stop DB logging + confirm server-side stop firing
Server stop fired for first time on SLV Mar 10 — confirmed Alpaca auto-executes intrabar. Discovered and fixed fill logging bug: get_recent_filled_sell failed due to API propagation delay. Now queries specific order ID directly, queues in pending_fills if not yet visible. Clarified two exit mechanics (not three): bot K-signal and Alpaca server-side stop (covers both stop loss and trailing stop).

 CLAUDE.md        |  6 ++++--
 memory/MEMORY.md | 41 +++++++++++++++++++++++++----------------
 memory/plan.md   |  4 ++--
 3 files changed, 31 insertions(+), 20 deletions(-)

----
**2026-03-10** — fix: server stop DB logging — query by order ID, retry via pending_fills
get_recent_filled_sell was failing due to Alpaca API propagation delay
(fill exists but not yet visible in orders list). Now queries the specific
stop order by ID directly. If not yet visible, queues in pending_fills for
retry on next bar. Falls back to get_recent_filled_sell only if no order ID.
Also tracks pending_stop_qty alongside pending_stop_order_id in live_broker.

Co-Authored-By: Claude Sonnet 4.6 <noreply@anthropic.com>

 backend/engine/live_broker.py |  5 +++++
 backend/runner.py             | 29 +++++++++++++++++++++++++----
 2 files changed, 30 insertions(+), 4 deletions(-)

