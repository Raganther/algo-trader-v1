# Recent Git History

> Auto-generated on git save. Do not edit manually.

----
**2026-04-21** — chore: Apr 21 — validated trail fired in profit (SLV +$283.86), pm2 startup registered, path to real money updated

 .claude/memory/observations.md | 21 +++++++++++----------
 1 file changed, 11 insertions(+), 10 deletions(-)

----
**2026-04-19** — chore: Apr 19 — trail ratcheting confirmed, server migration complete, all files updated

 .claude/hooks/load-context.sh  |  4 ++--
 .claude/memory/gitlog.md       | 20 +++++++++++---------
 .claude/memory/observations.md | 24 ++++++++++++++++--------
 CLAUDE.md                      |  4 ++--
 4 files changed, 31 insertions(+), 21 deletions(-)

----
**2026-04-19** — chore: migrate to algotrader-us (us-east1-b) — update server refs, trail ratcheting confirmed

 .claude/memory/gitlog.md | 20 ++++++++++----------
 CLAUDE.md                |  6 +++---
 2 files changed, 13 insertions(+), 13 deletions(-)

----
**2026-04-17** — chore: Apr 17 update — validated params live, first short confirmed, GTC stop fix deployed

 .claude/memory/gitlog.md       | 64 +++++++++++++++++++++++++++---------------
 .claude/memory/observations.md | 27 ++++++++++--------
 CLAUDE.md                      | 30 ++++++++------------
 3 files changed, 67 insertions(+), 54 deletions(-)

----
**2026-04-17** — fix: switch stop orders to GTC TIF — eliminates overnight expiry gap
DAY stops expire at 20:00 UTC each session. With fractional shares this
was unavoidable (Alpaca rejects GTC for fractional). Whole-share sizing
(deployed Apr 17) removes that constraint — GTC stops now persist across
sessions without daily re-placement.

Root cause of current bug: bots running continuously (3D uptime) never
cleared pending_stop_order_id when DAY stop expired, so the re-placement
guard never triggered. GTC removes the expiry problem entirely.

Co-Authored-By: Claude Sonnet 4.6 <noreply@anthropic.com>

 backend/engine/alpaca_trader.py | 11 ++++-------
 1 file changed, 4 insertions(+), 7 deletions(-)

----
**2026-04-13** — feat: deploy full validated strategy — whole-share sizing + shorts + validated params
- stoch_rsi_mean_reversion.py: math.floor sizing (long + short), skip sub-1-share signals
- alpaca_trader.py: int(qty) for stock market + stop orders
- live_broker.py: unblock short entry in sell(), place buy-stop with pending_stop_side='buy'
- all 4 bot scripts: OB 80/OS 15, ADX 20, 10-bar hold, 2.0 ATR trail after 10 bars, skip Monday, 13:30-20:00 UTC

 backend/engine/alpaca_trader.py                |  4 ++--
 backend/engine/live_broker.py                  | 31 +++++++++++++++++++++++---
 backend/strategies/stoch_rsi_mean_reversion.py | 11 +++++++--
 scripts/run_gdx_test.sh                        |  5 ++---
 scripts/run_gld_test.sh                        |  5 ++---
 scripts/run_iau_test.sh                        |  5 ++---
 scripts/run_slv_test.sh                        |  5 ++---
 7 files changed, 47 insertions(+), 19 deletions(-)

----
**2026-04-13** — chore: Apr 13 calibration complete — Layers 1/2/4 PASS, Layer 2 overnight hypothesis refuted, Layer 4 live 2.8x backtest explained by shared-capital stacking, execution layer validated

 .claude/calibration/calibration-notes.md | 75 ++++++++++++++++++++++++++------
 .claude/memory/gitlog.md                 | 18 ++++----
 .claude/memory/observations.md           |  4 +-
 3 files changed, 72 insertions(+), 25 deletions(-)

----
**2026-04-13** — chore: Apr 13 calibration run — Layer 1 PASS (75v75 1.00x), Layer 2 PARTIAL — backtest over-predicts overnight holds 2–3x, overnight stop model gap identified as next critical task

 .claude/calibration/calibration-notes.md | 39 +++++++++++++++++++++++++++++---
 .claude/memory/gitlog.md                 | 18 +++++++--------
 .claude/memory/observations.md           |  6 ++---
 3 files changed, 48 insertions(+), 15 deletions(-)

