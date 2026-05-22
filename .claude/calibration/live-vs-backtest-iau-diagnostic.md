Status: current | Epistemic: single-symbol diagnostic, magnitude refined by May 8 audit + May 9 bug-fix re-run | Last verified: 2026-05-09

> **May 9 2026 update — HWM A/B re-run under bug fix sharpens the picture.** Bug-fixed HWM A/B is +0.45 Sharpe (close 3.72 → HWM 4.17), not +0.78. The "~0.7 Sharpe delay artifact ≈ +0.78 HWM lift" identity that this diagnostic spawned is now superseded — most of the gap is the ADX-bug, not the polling delay. Live tripwire anchor revised to **~4.0 ±0.5** (5.73 → 5.50 → 4.0). Path 3 ("accept the gap, anchor tripwires to corrected expectation") shipped May 9: `live_performance_report.py` bars 1.8/2.5/3.0 at 30/60/90d. Paths 1 (fix `--delay 1`) and 2 (HWM, already done) remain available; Path 1's value is reduced now that we know most of the gap was the bug. See `calibration-journal.md` §2 May 9 entry.
>
> **May 8 2026 audit update — magnitude refined from "~0.7 Sharpe" to "~0.4–0.7 Sharpe".** The data-shift falsification audit (`.claude/calibration/audit-hwm-delay-mechanism.md`) reproduced only 0.42 Sharpe of the predicted 0.7 close-anchored artifact under a clean 1-bar shift. Either the real delay artifact is smaller than estimated, or it has additional components beyond pure 1-bar phase shift (sub-bar fill price differences, polling-cadence variance, etc.). Treat 0.7 as an upper bound and 0.4 as a lower bound on the close-anchored live-vs-backtest gap. HWM's gap appears smaller (~0.15 measured, possibly 0.2–0.3 in live).
>
> **May 8 2026 PM further revision — the gap was conflating two effects.** A second audit found an ADX-filter exit-block bug (`trend_framework.py:211-239`) that contributes ~1.23 Sharpe to the buggy backtest. Live partially escapes the bug via server-side stops + transient ADX dips; backtest cannot. This means the May 7 "live-vs-backtest gap" attributed to polling delay was actually a *combined* effect: pure delay artifact + ADX-bug expressing differently in the two environments. **True polling-delay magnitude is likely substantially smaller than 0.7 Sharpe** — the IAU Apr 23 smoking-gun trade specifically may have been driven by the ADX bug rather than the delay artifact alone. Cleanly isolating the two requires re-running the audit under `adx_filter_mode='entry_only'`. See `calibration-journal.md` §2 May 8 PM entries.

# IAU Live-vs-Backtest Diagnostic (May 7 2026)

> First systematic diff of live forward-test vs backtest over the same window. Identified a structural 1-bar delay artifact in the backtest model — explains a meaningful fraction of live underperformance vs backtest expectations.

## Trigger

Live perf report at 14 trading days showed metals four roughly tracking backtest, except IAU which diverged sharply: backtest +$384, live −$196, gap of $580. Cross-referenced both runs' trade-level history.

## Comparison window

- Symbols: GLD, IAU, SLV, GDX
- Window: 2026-04-15 → 2026-05-07 (14 active trading days)
- Initial: $94k
- Params: validated (sl_atr=2.0, trail_atr=2.0, trail_after_bars=10, min_hold_bars=10, skip_days=[0])
- Source: Alpaca 15m

| Metric | Backtest | Live | Δ |
|---|---:|---:|---:|
| Trades | 17 | 20 | +3 |
| Return | +1.26% | ~−0.0% | −1.26pp |
| Sharpe | 3.44 | ~−0.9 | −4.3 (noise at 14d) |
| Max DD | 0.70% | 2.27% | +1.57pp |

Per-symbol P&L:

| Symbol | Backtest | Live | Δ | Verdict |
|---|---:|---:|---:|---|
| SLV | +$910 | +$957 | +$47 | tracks model perfectly |
| GLD | −$415 | −$424 | −$9 | tracks |
| GDX | −$350 | −$328 | +$22 | tracks |
| **IAU** | **+$384** | **−$196** | **−$580** | **single material divergence** |

## IAU per-trade diff

**Backtest (4 trades):**

| # | Entry | Side | Entry $ | Exit $ | Reason | P&L |
|---|---|---|---:|---:|---|---:|
| 1 | Apr 22 16:45 | short | 88.93 | 89.37 | stop | −$118 |
| 2 | Apr 23 13:30 | short | 89.05 | 88.00 | **K-signal** | **+$274** |
| 3 | Apr 23 18:15 | long | 88.67 | 88.66 | stop | −$4 |
| 4 | **Apr 30 19:30** | short | 86.94 | 86.08 | **K-signal** | **+$232** |

**Live (4 trades):**

| # | Entry | Side | Entry $ | Exit $ | Reason | P&L |
|---|---|---|---:|---:|---|---:|
| 1 | **Apr 16 19:02** | long | 90.20 | 90.18 | stop | −$4 |
| 2 | Apr 22 18:37 | short | 89.04 | 89.24 | stop | −$55 |
| 3 | Apr 23 13:44 | short | 89.05 | 89.10 | **stop** | −$14 |
| 4 | Apr 23 18:18 | long | 88.66 | 88.21 | stop | −$123 |

Three patterns:
- **Live takes signals backtest doesn't, and vice versa** (live #1, backtest #4)
- **Apr 22 short — same direction, ~2 hour timing skew** (16:45 vs 18:37)
- **Apr 23 short — IDENTICAL entry, opposite exits** (backtest K-exit +$274, live trail-stop −$14)

## Root cause: structural 1-bar delay

Investigation of `backend/strategies/trend_framework.py` (lines 168–189, 222–246) confirmed:

**The backtest's stop-check mechanism is correct.** It compares against bar `High` (shorts) and bar `Low` (longs), so intra-bar wicks are detected. The trail formula uses `Close + ATR × trail_atr` (not trade high-water-mark), with ratcheting only in the favourable direction.

**The actual divergence comes from execution timing:**

1. **Backtest evaluates signals at bar Close**, "fills" instantly at that price → effective delay 0 bars
2. **Live polls Alpaca every ~minute**, signal evaluated at first poll *after* bar Close, fill happens ~1 minute later → effective delay ~1 bar
3. **`trail_after_bars=10`** is counted from entry bar. With a 1-bar entry skew, live's trail activates 1 bar later than backtest's — at a different reference Close
4. **The trail formula anchors to bar Close.** A 1-bar phase shift = different reference Close = different trail level. On a non-monotonic price path (Apr 23: down to 88.71 by 16:00, back up to 89.08 by 16:45), this difference propagates into different stop-fire bars

**On Apr 23 short (the smoking gun):**
- Both entered at $89.05 (same price)
- Backtest entry bar 13:30; trail activates bar 16:00 with Close $88.78 → trail anchored low
- Live entry bar 13:45; trail activates bar 16:15 with Close $88.83 → trail anchored higher
- The 16:45 bar high of $89.08 hit live's trail but not backtest's
- Backtest let the position run to K-exit at $88.00 (+$274); live got whipsawed at $89.10 (−$14)

## Sensitivity test — wider trail

Tested whether widening trail to 2.5 ATR mitigates the whipsaw:

| Window | Trail | Return | Sharpe | DD |
|---|---:|---:|---:|---:|
| 2020-07 → 2026-04 (long, 7-bot) | 2.0 | +424% | **4.95** | 3.41% |
| 2020-07 → 2026-04 (long, 7-bot) | 2.5 | +391% | 4.33 | **4.07%** |
| 2026-04-15 → 2026-05-07 (metals 4) | 2.0 | +1.26% | 3.44 | 0.70% |
| 2026-04-15 → 2026-05-07 (metals 4) | 2.5 | +1.14% | 3.19 | 0.70% |

**Wider trail loses on every dimension** — both return AND DD get worse. Confirms widening is the wrong fix; the issue isn't trail width, it's the 1-bar phase shift.

## Implications

- **The backtest is structurally optimistic by ~0.5–1.0 Sharpe** for this strategy because it doesn't model the live polling delay
- The CLAUDE.md guidance "size for Sharpe 1.0–1.5 on metals (not 2.46 backtest)" was the right call; this diagnostic gives it a concrete mechanistic basis
- Some of the spot-proxy vs ETF Sharpe gap (HistData ~1.5 vs Alpaca ~2.5) may actually be the **same delay artifact** rather than ETF microstructure premium — both backtests use bar-Close evaluation, but ETF backtests get "compared" to ETF live which has the polling delay; spot proxies have nothing to compare to
- The validated-edges Sharpe table (GLD 2.48, SLV 2.46, etc.) overstates live expectation by approximately the same delay-cost across all symbols
- IAU is not specifically broken — the divergence pattern would replicate on any symbol with similar entry frequency in chop. IAU happened to be the one symbol where the artifact compounded enough trades in this 14-day window to show up in aggregate P&L

## Three paths forward

**Path 1: Fix the backtester delay model.** Investigate the broken `--delay 1` mode, fix it, re-run all validated-edges backtests at `delay=1`. Expected: Sharpe figures drop ~0.5–1.0 across the lineup but become live-realistic. Major epistemic update across the entire research roadmap. **Real engineering work.**

**Path 2: Change trail formula to use trade high-water-mark.** Trail = `lowest_low_since_entry + ATR × trail_atr` (shorts) / `highest_high_since_entry - ATR × trail_atr` (longs). Less sensitive to bar-Close phase shifts since it ratchets only on trade extremes. Needs backtesting before live deployment. **Strategy parameter change.**

**Path 3: Accept the gap, anchor live tripwires to corrected expectation.** Document live-Sharpe ≈ backtest-Sharpe − 0.7 as the working estimate. Update `live_performance_report.py` decision rules to use that anchor. **Documentation only — can do today.**

## Recommended priority

Path 3 immediately (zero engineering, accurate framing). Path 2 next (parameter change, can backtest in an hour). Path 1 last (real engineering work, but the most epistemically honest fix).

## What this is NOT — disambiguation from Apr 28-29 XBI incident

This finding is **unrelated to the Apr 28-29 XBI gap-through-stop incident** (committed Apr 29, `runner.py:943-983` patch). They occurred in the same calendar window because Apr 28 was a busy day (e2-micro → e2-small server upgrade + oih-test/xbi-test/xop-test deployment + the XBI overnight gap), but the two issues are mechanistically distinct:

| | XBI gap-through-stop (Apr 28-29) | 1-bar polling delay (May 7 finding) |
|---|---|---|
| Type | One-time bug in gap-recovery code path | Structural mismatch in backtest model |
| Frequency | One position, one symbol, one night | Every trade, every bot, every day |
| Cause | Tried to place a stop above current price after overnight gap; Alpaca rejected | Backtest assumes 0-delay execution; live has ~60s polling cycle |
| Status | **Fixed** — `runner.py:943-983` adds breach-check | **Not fixed** — Paths 1/2/3 documented |
| Impact | Single XBI trade left unprotected for hours | Systematic ~0.7 Sharpe gap backtest vs live |

The server upgrade (e2-micro 1GB → e2-small 2GB on Apr 28) probably made polling cadence more *consistent* under load, but did not cause and does not fix the 1-bar delay — that's structural to the polling architecture itself.

## Files referenced

- `backend/strategies/trend_framework.py` — stop-check (line 222), trail update (line 168)
- `backend/engine/paper_trader.py` — fill mechanics
- `backend/runner.py` — `--delay` flag (currently broken at delay=1, per CLAUDE.md)
- `.claude/calibration/live-performance-report.md` — live tripwire dashboard
- `.claude/strategies/long-window-validation.md` — spot-proxy vs ETF Sharpe gap (partially explained by this finding)
