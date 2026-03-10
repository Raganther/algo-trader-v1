# Recent Git History

> Auto-generated on git save. Do not edit manually.

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
 reports/regime_chart_SPY_1d.html    |  3885 -------
 research/spy                        |   450 -
 run_full_history.sh                 |    11 -
 scripts/curate_memory.py            |    84 -
 scripts/realistic-test.sh           |    53 -
 scripts/run_gld.sh                  |     8 -
 scripts/test-and-sync.sh            |    70 -
 validation_run.log                  |    44 -
 31 files changed, 29432 deletions(-)

----
**2026-03-10** — docs: update strategy cards to reflect forward testing phase
All 4 StochRSI strategy files updated — status headers corrected, stale Next Steps cleaned up, forward testing sections added with backtest predictions and Mar 09 trail ratchet observations for SLV and GDX. EventSurprise and composable results unchanged.

 .claude/memory/strategies/stochrsi_enhanced_gdx.md | 10 +++++++-
 .claude/memory/strategies/stochrsi_enhanced_gld.md | 30 ++++++++++++++++------
 .claude/memory/strategies/stochrsi_enhanced_iau.md |  8 +++++-
 .claude/memory/strategies/stochrsi_enhanced_slv.md | 10 +++++++-
 memory/MEMORY.md                                   | 21 ++++++++-------
 5 files changed, 59 insertions(+), 20 deletions(-)

----
**2026-03-10** — chore: delete system_manual.md — consolidated into CLAUDE.md
File was stale (last updated Feb 14), sections 1-7 referenced dead scripts and workflows. Section 8 content already covered by CLAUDE.md run commands and constraints. Run commands are the documentation — a separate how-to manual adds maintenance burden without value.

 .claude/memory/system_manual.md | 407 ----------------------------------------
 CLAUDE.md                       |   1 -
 memory/MEMORY.md                |  32 ++--
 3 files changed, 13 insertions(+), 427 deletions(-)

----
**2026-03-10** — fix: correct bot log check command + document log format
Logs rotate at midnight via pm2-logrotate — previous command searched only the current log file, missing all same-day trades. New command takes the 2 most recent log files per bot covering both cases. Actual log keywords documented in system_manual.md (LIVE BUY, FILLED, TRAILING STOP etc). CLAUDE.md run command updated. Dev.md updated with agent ideas (#22).

 .claude/memory/system_manual.md | 22 +++++++++++++++++++
 CLAUDE.md                       |  7 ++----
 docs/dev.md                     | 21 ++++++++++++++++++
 memory/MEMORY.md                | 47 +++++++++++++++++------------------------
 4 files changed, 64 insertions(+), 33 deletions(-)

----
**2026-03-09** — fix: pass body argument to git commit in git-save.sh
git commit -m "$1" ${2:+-m "$2"} — body was silently dropped, MEMORY.md only ever showed subject + file stats. Now both subject and body are captured in the commit and appear in MEMORY.md.

 scripts/git-save.sh | 2 +-
 1 file changed, 1 insertion(+), 1 deletion(-)

----
**2026-03-09** — docs: update plan.md — Mar 09 audit complete, reconcile fixed, completeness baseline established

 memory/MEMORY.md | 86 +++++++++++++++++++++++++++++++-------------------------
 memory/plan.md   | 49 +++++++++++++++++++++-----------
 2 files changed, 80 insertions(+), 55 deletions(-)

----
**2026-03-09** — fix: case-insensitive side comparison in trade matching (BUY/SELL vs buy/sell)
Alpaca SDK returns side as uppercase ('BUY'/'SELL') but DB stores
lowercase ('buy'/'sell'). This caused reconcile_trades and audit_trades
to never match any orders, silently treating all fills as missing.
Same root cause as the status field case bug.

Co-Authored-By: Claude Sonnet 4.6 <noreply@anthropic.com>

 backend/runner.py       | 2 +-
 scripts/audit_trades.py | 2 +-
 2 files changed, 2 insertions(+), 2 deletions(-)

----
**2026-03-09** — fix: case-insensitive status check in get_filled_orders (was silently returning empty)
Alpaca SDK returns 'OrderStatus.FILLED' (uppercase) but the filter
checked for 'OrderStatus.filled' (lowercase) — case mismatch caused
get_filled_orders() to always return []. reconcile_trades() was
therefore always seeing 0 Alpaca orders and reporting 'DB up to date'
even when fills were missing. Every reconcile since deploy has been
a no-op.

Co-Authored-By: Claude Sonnet 4.6 <noreply@anthropic.com>

 backend/engine/alpaca_trader.py | 2 +-
 1 file changed, 1 insertion(+), 1 deletion(-)

