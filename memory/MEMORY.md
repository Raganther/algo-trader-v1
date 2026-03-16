# Recent Git History

> Auto-generated on git save. Do not edit manually.

----
**2026-03-16** — fix: pre-market signal guard + Mar 16 trade audit
Added market hours gate to runner.py — on_bar() now skipped outside 13:30-20:00 UTC after SLV placed a live order 45min before open on Mar 16. Full Alpaca order audit confirmed all records match pm2 logs. GDX zero-trade question resolved (2 trades on first active day — was no signal conditions, not a bug). 14 bugs found and fixed total; core infrastructure assessed as sound. Trailing stop FIRING in profit still unconfirmed; wash trade pre-market and short entry guard still open.

 CLAUDE.md      | 14 +++++++++-----
 memory/plan.md |  3 ++-
 2 files changed, 11 insertions(+), 6 deletions(-)

----
**2026-03-16** — fix: gate on_bar to market hours (13:30-20:00 UTC)
Pre-market bars (e.g. 12:45 UTC) were triggering live buy signals because
on_bar had no market hours guard. SLV placed a real order 45min before open
today — it sat unfilled, caused a SERVER STOP false-positive on state reset.
Fix: skip on_bar outside 13:30-20:00 UTC; pending_fills still runs every bar.

Co-Authored-By: Claude Sonnet 4.6 <noreply@anthropic.com>

 backend/runner.py | 11 +++++++++--
 1 file changed, 9 insertions(+), 2 deletions(-)

----
**2026-03-14** — chore: full 2-week audit — update stale status across memory files
Full audit of 40 commits Mar 1-14. No major circular bugs found. One 3-day blind spot: DB reconcile deployed Mar 6 but silently broken (case mismatch) until Mar 9. Two stale references found and fixed: CLAUDE.md still said 'waiting to confirm server-side stop firing' (confirmed Mar 10); auto-memory MEMORY.md Exit Mechanics section unchanged since Mar 4. GDX zero-trades added as open question in plan.md. Only remaining unconfirmed long mechanic: trailing stop FIRING in profit.

 CLAUDE.md        |  2 +-
 memory/MEMORY.md | 30 +++++++++++++++---------------
 memory/plan.md   |  3 +++
 3 files changed, 19 insertions(+), 16 deletions(-)

----
**2026-03-14** — fix: mark long_only step complete in plan, update strategy card dates
Two corrections from double-check: plan.md still showed long_only param step as unchecked despite being done; all 4 strategy cards still showed last-updated as Mar 10. Both fixed.

 .claude/memory/strategies/stochrsi_enhanced_gdx.md |  2 +-
 .claude/memory/strategies/stochrsi_enhanced_gld.md |  2 +-
 .claude/memory/strategies/stochrsi_enhanced_iau.md |  2 +-
 .claude/memory/strategies/stochrsi_enhanced_slv.md |  2 +-
 memory/MEMORY.md                                   | 40 ++++++++++------------
 memory/plan.md                                     |  2 +-
 6 files changed, 24 insertions(+), 26 deletions(-)

----
**2026-03-14** — feat: add long_only param + establish long-only performance baseline
Added long_only=True parameter to StochRSIMeanReversionStrategy to gate short entry logic. Ran backtests across all 4 assets to establish the live baseline (bots are long-only due to Alpaca fractional short restriction). Key finding: SLV long-only is actually better risk-adjusted (Sharpe ~3.29 vs 2.54 full); GDX is most impacted (-42% return, Sharpe 2.41→~1.54). Results recorded in all 4 strategy cards and plan.md.

 .claude/memory/strategies/stochrsi_enhanced_gdx.md | 19 +++++++++++++++
 .claude/memory/strategies/stochrsi_enhanced_gld.md | 19 +++++++++++++++
 .claude/memory/strategies/stochrsi_enhanced_iau.md | 17 +++++++++++++
 .claude/memory/strategies/stochrsi_enhanced_slv.md | 19 +++++++++++++++
 CLAUDE.md                                          |  2 ++
 backend/strategies/stoch_rsi_mean_reversion.py     |  5 ++--
 memory/MEMORY.md                                   | 28 +++++++++++++---------
 memory/plan.md                                     | 11 +++++++++
 8 files changed, 107 insertions(+), 13 deletions(-)

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

