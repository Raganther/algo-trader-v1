# Recent Git History

> Auto-generated on git save. Do not edit manually.

----
**2026-03-19** — fix: trailing stop update race condition + Mar 19 audit
GDX trail update failed today: cancel_order_by_id returns immediately but Alpaca processes the cancel async, so the new stop placement raced against the cancel and hit 40310000 (insufficient qty). Fixed with 1s sleep in update_stop_order after cancel, before placing new stop. Bug existed since Mar 4 (fallback was added then but root cause left unfixed) and was exposed by trail_after_bars=1 firing the update very early after entry. All 4 bots Mar 19: 4 trades, full Alpaca audit clean, all 12 orders matched.

 CLAUDE.md              |  1 +
 memory/observations.md | 10 ++++++++++
 2 files changed, 11 insertions(+)

----
**2026-03-19** — fix: add 1s sleep after cancel in update_stop_order to fix trail update race condition
Alpaca processes cancel_order asynchronously. Without a pause, the new stop
placement races against the cancel — Alpaca still sees shares held_for_orders
and rejects with code 40310000. 1s sleep gives the cancel time to propagate.
Observed in GDX today: trail update to $79.75 failed, fallback re-placed at $79.48.

Co-Authored-By: Claude Sonnet 4.6 <noreply@anthropic.com>

 backend/engine/live_broker.py | 5 ++++-
 1 file changed, 4 insertions(+), 1 deletion(-)

----
**2026-03-18** — chore: Mar 18 bot check + trailing stop diagnostic
All 4 bots traded Mar 18, all flat EOD. SLV server stop fired (another stop loss confirmation). Ran per-trade exit-type diagnostic: with old trail params (2.0 ATR), backtest predicts zero profitable trail fires in Jan-Mar 2026 — matches live exactly, no bug. With tightened params (0.5 ATR, since Mar 17), predicts ~5 per symbol. The trailing stop Sharpe improvement is earned in bull markets; this metals selloff window never gives the trail enough room to ratchet above entry with 2.0 ATR distance. Also caught dynamic_adx gotcha: defaults True and overrides adx_threshold silently.

 CLAUDE.md              |  2 ++
 memory/MEMORY.md       | 20 +++++++++++---------
 memory/observations.md | 14 ++++++++++++++
 memory/plan.md         |  2 +-
 4 files changed, 28 insertions(+), 10 deletions(-)

----
**2026-03-17** — feat: tighten trail params to provoke trailing stop fire in profit
Reduced trail_atr from 2.0 to 0.5 and trail_after_bars from 3 to 1 on all 4 bots. Goal: see trailing stop fire intrabar in profit — the last unconfirmed mechanic. Paper money so calibration impact is acceptable. Deployed and restarted.

 CLAUDE.md               | 10 +++++-----
 memory/MEMORY.md        | 27 ++++++++++++++++-----------
 memory/observations.md  |  1 +
 scripts/run_gdx_test.sh |  2 +-
 scripts/run_gld_test.sh |  2 +-
 scripts/run_iau_test.sh |  2 +-
 scripts/run_slv_test.sh |  2 +-
 7 files changed, 26 insertions(+), 20 deletions(-)

----
**2026-03-17** — chore: Mar 17 end-of-day audit — all 4 bots, all records matched
Full Alpaca vs pm2 audit for Mar 17. GDX server stop fired intrabar at 19:06 UTC (stop loss exit) — caught post-check. SLV trail ratcheted but closed via K-signal. Trailing stop firing in profit still unconfirmed. 4/4 clean record match.

 CLAUDE.md              |  2 +-
 memory/MEMORY.md       | 24 ++++++++++++------------
 memory/observations.md |  2 +-
 3 files changed, 14 insertions(+), 14 deletions(-)

----
**2026-03-17** — chore: Mar 17 bot check — all 4 flat, no trades
Routine session check. All bots healthy, market open, no trades today. Yesterday's SLV fill timeout confirmed as pre-fix artifact. No code changes this session.

 CLAUDE.md              |  1 +
 memory/MEMORY.md       | 20 ++++++++++----------
 memory/observations.md |  1 +
 3 files changed, 12 insertions(+), 10 deletions(-)

----
**2026-03-17** — chore: add git-save guard hook + document memory restructure
Added PreToolUse hook (git-save-guard.sh) that blocks git-save.sh if memory files are unchanged since last commit — ensures plan.md and observations.md are always updated before saving. Updated settings.json to register the hook. Documented the memory restructure rationale in observations.md.

 .claude/hooks/git-save-guard.sh | 24 ++++++++++++++++++++++++
 .claude/settings.json           | 11 +++++++++++
 memory/MEMORY.md                | 27 ++++++++++++---------------
 memory/observations.md          |  7 +++++++
 4 files changed, 54 insertions(+), 15 deletions(-)

----
**2026-03-17** — chore: update session start hook — correct file paths
Hook was referencing stale paths (.claude/claude.md, recent_history.md). Updated to show the actual read order: MEMORY.md, plan.md, observations.md.

 .claude/hooks/load-context.sh |  7 ++++---
 memory/MEMORY.md              | 19 +++++++++----------
 2 files changed, 13 insertions(+), 13 deletions(-)

