# Recent Git History

> Auto-generated on git save. Do not edit manually.

----
**2026-03-22** — chore: set up OpenBrain workflow and identify first candidates
Confirmed OpenBrain hooks are live (all three: SessionStart, PreToolUse guard, PostToolUse audit reminder). Identified 10 candidates for first OpenBrain write: 5 Alpaca API gotchas, 4 trading system methodology patterns, 1 validated edge. Removed redundant openbrain_guide.md — global CLAUDE.md description is sufficient to guide candidate selection.

 memory/observations.md | 2 ++
 1 file changed, 2 insertions(+)

----
**2026-03-22** — chore: add OpenBrain audit hook to memory system
Added openbrain-audit-reminder.sh PostToolUse hook — fires after every git save and prompts OpenBrain audit for cross-project knowledge candidates. Project now has all three standard hooks. Future git saves will include an OpenBrain audit step.

Co-Authored-By: Claude Sonnet 4.6 <noreply@anthropic.com>

 .claude/hooks/openbrain-audit-reminder.sh | 19 +++++++++++++++++++
 .claude/settings.json                     | 11 +++++++++++
 CLAUDE.md                                 |  1 +
 memory/observations.md                    |  5 +++++
 4 files changed, 36 insertions(+)

----
**2026-03-21** — chore: update calibration window to Mar 20 – Apr 20
Adjusted calibration window start from Mar 16 to Mar 20 — first fully confirmed clean day with current params (trail_atr=0.5, trail_after_bars=1) and all fixes deployed (race condition fix Mar 19, 18/18 audit passed Mar 20). End date moved from Apr 19 to Apr 20 to maintain exactly 1 month window. Updated CLAUDE.md, plan.md, and observations.md.

 CLAUDE.md              |  4 ++--
 memory/MEMORY.md       | 22 +++++++++++-----------
 memory/observations.md | 12 +++++++-----
 memory/plan.md         |  4 ++--
 4 files changed, 22 insertions(+), 20 deletions(-)

----
**2026-03-19** — chore: set Apr 19 as calibration target date
Formalised the 1-month forward test plan: keep aggressive params (OB 60/OS 40, trail 0.5 ATR after 1 bar) running until Apr 19, then run backtest with identical params over the same window. Aggressive params are intentional — they generate ~2x more trades than validated params, giving a more statistically meaningful calibration dataset. Clean window is Mar 16 (all bugs fixed) to Apr 19. Also corrected the calibration command in observations.md to use current trail params (0.5 ATR, 1 bar) instead of old ones.

 CLAUDE.md              |  4 ++--
 memory/MEMORY.md       | 20 +++++++++++---------
 memory/observations.md | 14 ++++++++------
 memory/plan.md         |  4 ++--
 4 files changed, 23 insertions(+), 19 deletions(-)

----
**2026-03-19** — fix: trailing stop update race condition + Mar 19 audit
GDX trail update failed today: cancel_order_by_id returns immediately but Alpaca processes the cancel async, so the new stop placement raced against the cancel and hit 40310000 (insufficient qty). Fixed with 1s sleep in update_stop_order after cancel, before placing new stop. Bug existed since Mar 4 (fallback was added then but root cause left unfixed) and was exposed by trail_after_bars=1 firing the update very early after entry. All 4 bots Mar 19: 4 trades, full Alpaca audit clean, all 12 orders matched.

 CLAUDE.md              |  1 +
 memory/MEMORY.md       | 41 ++++++++++++++++++++++-------------------
 memory/observations.md | 10 ++++++++++
 3 files changed, 33 insertions(+), 19 deletions(-)

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

