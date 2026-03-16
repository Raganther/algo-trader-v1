# Recent Git History

> Auto-generated on git save. Do not edit manually.

----
**2026-03-16** — chore: note Observations section in session start
Added one-line clarification to CLAUDE.md session start so future sessions know plan.md Observations holds active working insights, not just plan steps.

 CLAUDE.md | 2 +-
 1 file changed, 1 insertion(+), 1 deletion(-)

----
**2026-03-16** — chore: consolidate plan.md active steps
Removed unnecessary chart section — trade overlays are just another active step, not a separate plan. Keeps plan.md flat and readable.

 memory/MEMORY.md | 28 +++++++++++-----------------
 memory/plan.md   | 15 ++++-----------
 2 files changed, 15 insertions(+), 28 deletions(-)

----
**2026-03-16** — chore: restructure plan.md + calibration baseline Mar 5-16
Restructured plan.md: removed completed debugging history, added Observations section for working insights. First calibration snapshot: backtest vs live Mar 5-16 shows reasonable alignment (SLV exact, GLD close, IAU/GDX within 2-3 trades). Established calibration methodology using Jan 1 lead-in to eliminate warmup distortion. Fixed adx_threshold documentation — test bots use 50 not 20. Next calibration check due ~Apr 16.

 CLAUDE.md        |  12 ++---
 memory/MEMORY.md |  24 ++++-----
 memory/plan.md   | 149 ++++++++++++++++++++-----------------------------------
 3 files changed, 73 insertions(+), 112 deletions(-)

----
**2026-03-16** — fix: wash trade prevention — cancel open orders before long entry
pending_fills retries can leave a hanging sell order on Alpaca pre-market. When a new buy signal fires, Alpaca rejects it as a wash trade. Fix: cancel_all_orders_for_symbol before every long entry in live_broker.buy() — same pattern already used in the short-close path. Root cause confirmed via SLV Mar 13 audit. All known long-side bugs now fixed. Remaining before real money: trailing stop firing in profit (passive wait), short entry guard fix, short mechanics verification.

 CLAUDE.md        |  4 ++--
 memory/MEMORY.md | 57 +++++++++++++++++++++++++-------------------------------
 memory/plan.md   |  2 +-
 3 files changed, 28 insertions(+), 35 deletions(-)

----
**2026-03-16** — fix: cancel open orders before long entry to prevent wash trade rejection
pending_fills can leave a hanging sell order from a previous exit sitting
open on Alpaca pre-market. When a new buy signal fires, Alpaca rejects it
as a wash trade. Fix: cancel_all_orders_for_symbol before placing any long
entry — same pattern already used in the short-close path. Confirmed root
cause: SLV Mar 13 audit showed exactly this sequence.

Co-Authored-By: Claude Sonnet 4.6 <noreply@anthropic.com>

 backend/engine/live_broker.py | 7 ++++++-
 1 file changed, 6 insertions(+), 1 deletion(-)

----
**2026-03-16** — fix: pre-market signal guard + Mar 16 trade audit
Added market hours gate to runner.py — on_bar() now skipped outside 13:30-20:00 UTC after SLV placed a live order 45min before open on Mar 16. Full Alpaca order audit confirmed all records match pm2 logs. GDX zero-trade question resolved (2 trades on first active day — was no signal conditions, not a bug). 14 bugs found and fixed total; core infrastructure assessed as sound. Trailing stop FIRING in profit still unconfirmed; wash trade pre-market and short entry guard still open.

 CLAUDE.md        | 14 +++++++++-----
 memory/MEMORY.md | 43 ++++++++++++++++++++++++-------------------
 memory/plan.md   |  3 ++-
 3 files changed, 35 insertions(+), 25 deletions(-)

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

