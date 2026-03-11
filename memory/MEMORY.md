# Recent Git History

> Auto-generated on git save. Do not edit manually.

----
**2026-03-11** — docs: add short trading requirement to plan
Discovered live bots are long-only due to sell() guard blocking short entries from flat — an unintended side effect of the duplicate exit fix. Sharpe 2.54 backtest includes both long and short P&L. Plan updated with three steps: add long_only param to strategy, fix the sell guard to distinguish exit vs short entry, and re-verify all mechanics for short trades before switching to real money.

 memory/plan.md | 11 ++++++++++-
 1 file changed, 10 insertions(+), 1 deletion(-)

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

----
**2026-03-10** — fix: restore head -2 in bot check command, add HEARTBEAT warning
Reverted head -1 back to head -2 so the bot check covers today + yesterday, catching overnight holds. Root cause of earlier false 'no trades' report was adding HEARTBEAT to an ad-hoc grep, not head -2 itself. Added comment to CLAUDE.md explicitly warning never to include HEARTBEAT in the grep pattern.

 CLAUDE.md        |  2 +-
 memory/MEMORY.md | 25 ++++++++++---------------
 2 files changed, 11 insertions(+), 16 deletions(-)

----
**2026-03-10** — fix: add timezone/market hours to CLAUDE.md, add server time check command
Recurring mistake: assuming current time from stale conversation context. Fix: always run date -u on server first when checking bots. Added explicit timezone rules to Constraints — Irish/UTC relationship, DST 2026 start date, pre/post-DST market hours in UTC.

 CLAUDE.md        | 13 +++++++++++++
 memory/MEMORY.md | 24 +++++++++---------------
 2 files changed, 22 insertions(+), 15 deletions(-)

----
**2026-03-10** — chore: repository cleanup — remove dead files and legacy subsystems
Deleted backend/agent/ (unused AI agent subsystem), scripts/curate_memory.py (its only dependent), logs/, reports/, research/, zipdata/ (stale output dirs), empty DBs, validation_run.log, docs/testing-standards.md (superseded by CLAUDE.md run commands), realistic-test.sh, test-and-sync.sh, run_full_history.sh, and run_gld.sh. All active functionality preserved.

 backend/agent/critic.py             |   404 -
 backend/agent/memory_system.py      |    77 -
 backend/agent/planner.py            |    72 -
 backend/agent/registrar.py          |    61 -
 backend/agent/researcher.py         |   118 -
 backend/agent/strategy_generator.py |   177 -
 backend/agent/toolbox.py            |    52 -
 docs/testing-standards.md           |   185 -
 logs/api_response.json              |     1 -
 logs/backend.log                    | 20565 ----------------------------------
 logs/debug_output.txt               |     9 -
 logs/debug_output_2.txt             |   535 -
 logs/debug_output_3.txt             |   176 -
 logs/debug_output_4.txt             |   165 -
 logs/debug_output_batch.txt         |    12 -
 logs/debug_output_batch_15m.txt     |   411 -
 logs/debug_output_papertrader.txt   |    15 -
 logs/debug_output_stoch.txt         |    16 -
 logs/debug_output_stress_test.txt   |    12 -
 logs/debug_results.txt              |   290 -
 logs/history.json                   |  1470 ---
 logs/runner_debug.log               |     3 -
 logs/test_output.txt                |     1 -
 memory/MEMORY.md                    |    50 +-
 reports/regime_chart_SPY_1d.html    |  3885 -------
 research/spy                        |   450 -
 run_full_history.sh                 |    11 -
 scripts/curate_memory.py            |    84 -
 scripts/realistic-test.sh           |    53 -
 scripts/run_gld.sh                  |     8 -
 scripts/test-and-sync.sh            |    70 -
 validation_run.log                  |    44 -
 32 files changed, 39 insertions(+), 29443 deletions(-)

----
**2026-03-10** — docs: update strategy cards to reflect forward testing phase
All 4 StochRSI strategy files updated — status headers corrected, stale Next Steps cleaned up, forward testing sections added with backtest predictions and Mar 09 trail ratchet observations for SLV and GDX. EventSurprise and composable results unchanged.

 .claude/memory/strategies/stochrsi_enhanced_gdx.md | 10 +++++++-
 .claude/memory/strategies/stochrsi_enhanced_gld.md | 30 ++++++++++++++++------
 .claude/memory/strategies/stochrsi_enhanced_iau.md |  8 +++++-
 .claude/memory/strategies/stochrsi_enhanced_slv.md | 10 +++++++-
 memory/MEMORY.md                                   | 21 ++++++++-------
 5 files changed, 59 insertions(+), 20 deletions(-)

