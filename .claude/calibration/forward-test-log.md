Status: current | Epistemic: milestones + patterns; raw trades in cloud DB / MCP | Last verified: 2026-05-08

# Forward Test Log — Validated Params

Milestone + pattern record for the validated-params forward test (Apr 15 2026 onward). **Per-trade detail is not maintained here** — query the cloud `live_trade_log` table or Alpaca MCP `get_orders` for that. This file holds the durable knowledge: first occurrences, canonical examples, named patterns, and anomaly notes that took analysis to derive and would otherwise be lost across sessions.

> **May 8 2026 restructure.** Previous form had per-trade tables for every session. They went stale after Apr 24 and were re-derivable from the DB anyway. Now: durable findings here, per-trade ad-hoc on demand.

> **May 7 2026 — live-vs-backtest gap structurally explained.** First diagnostic at 14 trading days revealed the backtest is structurally optimistic by ~0.4–0.7 Sharpe due to a 1-bar polling delay live execution has but the backtest doesn't model (refined May 8 audit — see `audit-hwm-delay-mechanism.md`). HWM trail anchor (deployed May 7 PM) is the structural fix.

> **Apr 28 2026 — framework attribution caveat.** Forward-test win rates reflect framework + StochRSI tilt, not pure StochRSI mean-reversion edge. Per Apr 28 random-entry control, the framework alone produces Sharpe ≥ 2.0 with zero signal information. See `research-log.md` → "Random-Entry Control".

**Bot config (all 7):** OB 80 / OS 15, ADX threshold 20, 10-bar min hold, 2.0 ATR trail after 10 bars, GTC stops, whole-share sizing, shorts enabled, `skip_days:[0]`. GLD/IAU/SLV/GDX deployed Apr 15–16; OIH/XBI/XOP added Apr 28; HWM trail anchor deployed all 7 May 7 PM.

**Source of truth for raw trade data:**
- Alpaca MCP `get_orders` (canonical, queried on demand)
- Cloud `research.db` `live_trade_log` table (bot's own log, auto-populated at execution)

Use the procedure in `.claude/procedures/daily-trade-audit.md` for ad-hoc per-trade analysis.

**Exit types:** `K` = bot K-signal at candle close · `SS` = server-side stop loss · `TS` = trailing stop fired intrabar in profit · `EM` = emergency market exit (gap-through-stop guard, introduced Apr 29)

---

## First-occurrence milestones

| Date | Event | Significance |
|---|---|---|
| Apr 15 | First validated-params entry (SLV K-exit, −$207) | Forward test begins |
| Apr 16 | **First short confirmed** — GLD short, 14:17 sell-to-open @ $440.43, K-exit 16:46 @ $439.73 (+$38.50) | Whole-share sizing path validated end-to-end for shorts |
| Apr 20 | **First trail fire in profit** — SLV, entered Apr 16 @ $71.29, trail ratcheted $70.72 → $72.14, server stop fired @ $72.12 (+$283.86) | The mechanism that drives validated-params Sharpe — confirmed live |
| Apr 22→23 | **First overnight gap-through** — SLV, entered $70.48, gapped down, GTC stop @ $70.15 fired at open @ $68.74 (−$605.52) | Closed single-symbol gap-policy item; delta = gap risk, not slippage |
| Apr 23 | **First organic short stop-fire against us** — IAU short @ $89.05, buy-stop fired @ $89.10 (−$13.65) | Closed "awaiting organic short stop" data point |
| Apr 28 | OIH/XBI/XOP bots added (4 → 7 lineup) | Energy + biotech clusters introduced live |
| Apr 29 | **Correlation-aware sizing V1 deployed** | `risk_frac = 0.02 / N` (cluster occupancy discount). First cluster-simultaneous entry that triggers discount: TBD — record N, risk_frac, share count when it happens |
| Apr 29 | **First EM exit** — XBI, entered Apr 28 @ $131.25, gap-through-stop guard fired market exit @ $129.55 (−$313.61) | New exit type `EM` introduced; gap-recovery code path bug surfaced + fixed same session |
| May 7 | **HWM trail anchor deployed live** all 7 bots | First HWM trade: TBD (existing OIH short continues with close-anchored fallback; HWM only initializes on entry) |
| May 7 | First HWM live entry | TBD — record date, symbol, exit type when it fires |

## Named patterns

**GLD stop-cycle whiplash (observed Apr 23).** Choppy regime + 2.0 ATR trail produces ≥3 entry→stop cycles in one session, all losses. Apr 23: 3 GLD entries within ~3 hours, each stopped within 30–60 min ($-1.42, $-1.51, $-1.34/share). Validated-params behaviour, not a bug — the cost of running mean-reversion in chop with a tight trail. Worth flagging if it repeats often enough to suggest a regime gate.

**Stop-slippage sign asymmetry (observed Apr 20–23).** Sell-stops on long positions slip mostly negative (fill below stop level). Buy-stops on short covers / long sell-stops at trail-ratchet slip mostly positive (fill above stop level). The "100% negative" framing from early calibration didn't hold — direction is side-dependent.

**Gap-through-stop bug pattern (observed + fixed Apr 29).** Bot's gap-recovery code path can cancel a valid GTC stop at session re-open, then fail to re-place if the new stop level would be "wrong-side" of current price (Alpaca rejects). Fixed by `runner.py:943-983` breach-check guard. Symptom to watch for: any future bot session that logs `[LOOP] 🚨 Stop $X already breached by price $Y` — the guard is doing its job, but the underlying root cause (`pending_stop_order_id` becoming None despite live GTC stop) is unresolved.

## Layer 3 — stop slippage running sample

**Last refresh:** Apr 24 2026. **Sample at refresh:** 41 fires (33 calibration window + 8 forward-test through Apr 24).

**Stats at last refresh:** mean −$0.0247/share, median −$0.0134/share. Consistent with prior calibration (median $0.010, mean $0.025). 3 of 8 most recent fires are positive (sign asymmetry above).

**Target:** 50 intraday fires before deciding whether to bake `stop_slippage` into the backtest. **Probably already crossed** — Apr 25 → today is ~10 trading days unlogged. Refresh requires running `daily-trade-audit.md` over Apr 25 → today and counting filled stop orders. Treat the "41" figure as a floor, not the current count.

## Realised P&L (closed trades only, through Apr 29)

| Window | Trades | Net P&L |
|---|---|---|
| Apr 15 → Apr 29 (closed) | 13 | **−$1,142.39** |

Apr 23 alone was −$855 (SLV gap + 3 GLD whiplash + IAU short). Removing that session: net +$26 across the other 6. The validated trail fire (+$283.86) almost exactly offsets the SLV gap-through (−$605.52). **Sample size still too small for win-rate convergence** vs backtest predictions (GLD 48% / SLV 57% / GDX 59% / IAU 37%).

For trades after Apr 29, query Alpaca MCP or the cloud `live_trade_log` directly. **Do not maintain the running P&L total here** — it goes stale within days; `live-performance-report.md` (auto-generated) is the source of truth for aggregate metrics.

## Live observation framework

While the 7 bots run, four measurements convert time-passing into real-money confidence. These are *what to look for*, not *what to log here*:

1. **Live Sharpe vs backtest Sharpe — per cluster.** Once ~3 months of trades accumulated (target: late Jul 2026), per-cluster live Sharpe vs backtest expectation (gold ~2.46 close-anchored / ~5.50 portfolio HWM, energy ~2.30, biotech 2.18). Decision rule: live within 30% of backtest = framework + execution sound; live <1.0 = something material mis-modelled. Surface in `live-performance-report.md` (auto-generated) once per-cluster split is built.

2. **Slippage tracking.** Aggregate quarterly. Backtest assumes ~$0.013/share median. If consistently higher in live, the backtest Sharpe is overstated by approximately (live − model) × annual stop count × position size / equity.

3. **Regime check.** If metals enter sustained bear / sideways during this window, that's data we have nowhere else. Apr 28 framework-attribution finding predicts the framework is *strong* in sustained directional moves (bull or bear) and *weak* in transitions. Live observation either way is informative.

4. **Correlated-entry frequency.** How often 3+ peers in the same cluster enter within 30 min. Theoretical concern from `gap-distribution.md` was correlated overnight gap risk; live frequency tells us whether the worst case is rare or common. Apr 15–24 window saw zero — sample too small for a conclusion.

**Why this matters:** the bot lineup represents ~3 independent economic bets, not 7. Capital cap binds at 4 simultaneous full positions. See `research-roadmap.md` for the structured task list.
