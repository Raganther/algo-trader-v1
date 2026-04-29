Status: current | Epistemic: trades confirmed; edge interpretation revised Apr 28 | Last verified: 2026-04-28

# Forward Test Log — Validated Params

Per-trade records for the validated-params forward test (Apr 15 2026 onward).
Distinct from `live-trade-log.md` (Mar 20–Apr 20 calibration window, test params).

> **Apr 28 2026 caveat — framework attribution finding.** Trade records below are observational fact and unaffected. However, any interpretation that reads forward-test win rates as confirming "the StochRSI mean-reversion edge" is now under review. Apr 28 random-entry control shows random entries with the same framework produce comparable Sharpes; live forward-test results may largely reflect framework performance, not signal performance. See `research-log.md` → "Random-Entry Control — Apr 28 2026".

**Bot config (all 7):** OB 80 / OS 15, ADX threshold 20, 10-bar min hold, 2.0 ATR trail after 10 bars, GTC stops, whole-share sizing, shorts enabled, `skip_days:[0]` (skip Monday). GLD/IAU/SLV/GDX deployed Apr 15–16; OIH/XBI/XOP added Apr 28.

### Live Observation Framework (Apr 28 evening)

While the 7 bots run, four measurements convert time-passing into real-money confidence. Build these as recurring (weekly/quarterly) reports, not one-offs.

1. **Live Sharpe vs backtest Sharpe — per cluster.** Once ~3 months of trades accumulated (target: late Jul 2026), compute live daily-resampled Sharpe per cluster (gold = GLD/IAU/SLV/GDX combined; energy = OIH/XOP combined; biotech = XBI). Compare to backtest expectations: gold cluster ~2.46 (size for 1.5 due to regime risk), energy cluster ~2.30, biotech 2.18. **Decision rule:** live within 30% of backtest = framework + execution sound; live <1.0 = something material in slippage/spread/timing is mis-modelled.

2. **Slippage tracking.** This log captures intended vs actual fill prices. Aggregate quarterly into a stop-slippage distribution. Backtest assumes ~$0.013/share median; live should be in that range. If consistently higher, backtest Sharpe is overstated by approximately (live_slippage − model_slippage) × annual stop count × position size / equity.

3. **Regime check.** If metals enter a sustained bear or sideways regime during this window, **that's the data we have nowhere else.** Don't act on a few weeks of weakness — record it. Test 3 inversion predicts metals Sharpe drops materially in non-bull regimes; a live observation either way is highly informative. Energy and biotech regime sensitivity also untested.

4. **Correlated-entry frequency.** Track how often 3+ correlated bots in the same cluster enter within 30 minutes (e.g. GLD + IAU + SLV all long). Theoretical concern from `gap-distribution.md` was correlated overnight gap risk; live frequency tells us whether the theoretical worst case is actually rare or common.

**Why this matters:** the bot lineup represents ~3 independent economic bets (gold cluster, energy cluster, biotech), not 7. Capital cap binds at 4 simultaneous full positions. Adding more bots without these measurements producing favourable data, AND without correlation-aware sizing built, is premature. See `research-roadmap.md` → "Live Observation Framework — What to Measure While Bots Run" for the structured task list.

**Source:** Alpaca MCP `get_orders` (status=filled). pm2/DB cross-check not performed — MCP is canonical.

**Exit types:** `K` = bot K-signal at candle close (market exit) | `SS` = server-side stop (stop loss) | `TS` = trailing stop fired intrabar in profit

## Knowledge

### Apr 15 – Apr 24 dataset summary (10 trading days)

12 completed round-trips + 3 currently open. Mostly choppy regime (post-metals-crash recovery), one strong trend day (Apr 20 SLV), one overnight gap (Apr 22→23 SLV).

#### Apr 16 — first short confirmed working

GLD short entered 14:17 @ $440.43 (sell-to-open, market), covered 16:46 @ $439.73 (buy K-exit). +$0.70/share × 55 = **+$38.50**. Whole-share sizing path executed cleanly; short broker plumbing validated end-to-end.

#### Apr 20 — validated 2.0 ATR trail fires in profit

SLV entered Apr 16 15:31 @ $71.29 (qty 342), held over weekend, trail ratcheted intraday Apr 20 from $70.72 → $72.14 (per CLAUDE.md), server stop fired 19:35 @ $72.12. +$0.83/share × 342 = **+$283.86**. The mechanism that drives Sharpe 2.47 confirmed live on validated params.

#### Apr 22→23 — first overnight gap-through

SLV entered Apr 22 18:16 @ $70.48 (qty 347), gapped down overnight, GTC stop @ $70.15 fired at open Apr 23 13:32 @ $68.74. Fill is clean against the open print — the $1.41/share delta is **gap risk, not slippage**. -$605.52 realised. Closed the single-symbol gap-policy item (see `gap-distribution.md`).

#### Apr 23 — first organic short stop-fire against us

IAU entered short 13:44 @ $89.05 (sell-to-open, market), buy-stop @ $89.09 fired 16:51 @ $89.10 (cover). -$0.05/share × 273 = **-$13.65**. Small loss, but mechanically significant — closes the "awaiting organic short stop fire" data point flagged in `research-roadmap.md`.

#### Apr 23 — GLD stop-cycle whiplash

3 GLD long entries in one session, each stopped within 30–60 min:
- 15:01 @ $434.53 → 15:54 stop @ $433.11 (-$1.42/share)
- 16:46 @ $434.71 → 17:05 stop @ $433.20 (-$1.51/share)
- 18:16 @ $432.78 → still open

Choppy regime + tight 2.0 ATR trail = repeated re-entry/stop-out. Validated-params behaviour, not a bug. The 3rd entry is the current open position.

#### Stop slippage — Layer 3 sample expansion (9 new fires, 8 intraday)

Excluding the Apr 23 SLV overnight gap (gap risk, not slippage):

| Date | Symbol | Side | Stop $ | Fill $ | Slippage |
|------|--------|------|--------|--------|----------|
| Apr 20 | GLD | sell-stop (long) | 440.10 | 440.05 | -0.0500 |
| Apr 20 | IAU | sell-stop (long) | 90.18 | 90.18 | +0.0044 |
| Apr 20 | SLV | sell-stop (long, TS) | 72.14 | 72.12 | -0.0200 |
| Apr 22 | IAU | buy-stop (short cover) | 89.23 | 89.24 | +0.0100 |
| Apr 23 | GLD | sell-stop (long) | 433.67 | 433.61 | -0.0650 |
| Apr 23 | GLD | sell-stop (long) | 433.19 | 433.11 | -0.0800 |
| Apr 23 | IAU | buy-stop (short cover) | 89.09 | 89.10 | +0.0100 |
| Apr 23 | GLD | sell-stop (long) | 433.21 | 433.20 | -0.0069 |

Mean: -0.0247/share. Median: -0.0134/share. Consistent with previous calibration (median $0.010, mean $0.025). **New observation:** sign is no longer 100% negative — 3 of 8 are positive (+0.004 to +0.010), all on buy-stops (short covers / long sell-stops at ratchet). Sell-stops on long positions remain mostly negative.

Cumulative Layer 3 sample: 33 → 41 intraday fires. Within striking distance of the 50-target before deciding whether to bake `stop_slippage` into the backtest.

#### Correlated entries — none in window

Surprisingly, no GLD/IAU/SLV simultaneous-entry events in the Apr 15–24 window (cf. Mar 27, Mar 31, Apr 8 in calibration log). Apr 22 and Apr 23 saw GLD/IAU/SLV positions overlap intraday but not from synchronous entries. Sample size still too small to draw a conclusion about validated-params correlation — `skip_days:[0]` plus the choppy regime may suppress the open-of-day cluster pattern.

### Format

| Bot | Entry time (UTC) | Entry $ | Exit time (UTC) | Exit $ | Exit type | Stop level at exit | P&L/share | Notes |
|-----|-----------------|---------|-----------------|--------|-----------|-------------------|-----------|-------|

---

## 2026-04-15

| Bot | Entry time (UTC) | Entry $ | Exit time (UTC) | Exit $ | Exit type | Stop level at exit | P&L/share | Notes |
|-----|-----------------|---------|-----------------|--------|-----------|-------------------|-----------|-------|
| slv-test | 19:01:57 | 71.78 | (Apr 16) | 71.17 | K | - | -0.610 | First validated-params entry. Late-session entry held overnight. Closed Apr 16 14:01 K-exit. qty 340 → -$207.40 |

## 2026-04-16

| Bot | Entry time (UTC) | Entry $ | Exit time (UTC) | Exit $ | Exit type | Stop level at exit | P&L/share | Notes |
|-----|-----------------|---------|-----------------|--------|-----------|-------------------|-----------|-------|
| slv-test | (Apr 15) 19:01:57 | 71.78 | 14:01:39 | 71.17 | K | - | -0.610 | Overnight K-exit. qty 340 → -$207.40 |
| gld-test | 14:17:16 | 440.43 | 16:46:29 | 439.73 | K | - | +0.700 | **First short confirmed.** Sell-to-open 14:17, buy K-exit 16:46. qty 55 → +$38.50 |
| slv-test | 15:31:05 | 71.29 | (Apr 20) | 72.12 | TS | 72.14 | +0.830 | Re-entry. Held weekend → Apr 20 trail fire. qty 342 → +$283.86 (validated trail fire) |
| iau-test | 19:02:27 | 90.20 | (Apr 20) | 90.18 | SS | 90.18 | -0.020 | Late-session entry, weekend carry. qty 270 → -$5.40 |
| gld-test | 19:47:34 | 440.59 | (Apr 20) | 440.05 | SS | 440.10 | -0.540 | Late-session entry, weekend carry. qty 55 → -$29.70 |

## 2026-04-17

Friday. No new fills (no signal qualifying). GLD/IAU/SLV all carrying overnight from Apr 16 19:47/19:02/15:31.

## 2026-04-18 – 2026-04-19

Weekend — market closed. GLD/IAU/SLV positions held GTC stops (validated overnight stop survival).

## 2026-04-20

**Skip-Monday in effect** — no new entries. Pre-existing weekend carries resolved via stop fires.

| Bot | Entry time (UTC) | Entry $ | Exit time (UTC) | Exit $ | Exit type | Stop level at exit | P&L/share | Notes |
|-----|-----------------|---------|-----------------|--------|-----------|-------------------|-----------|-------|
| gld-test | (Apr 16) 19:47 | 440.59 | 14:51:23 | 440.05 | SS | 440.10 | -0.540 | Weekend carry. Stop fired ~80 min after open. Slippage: -0.050. qty 55 → -$29.70 |
| iau-test | (Apr 16) 19:02 | 90.20 | 14:51:24 | 90.184 | SS | 90.18 | -0.016 | Weekend carry, simultaneous fire with GLD. Slippage: +0.004 (positive — ratchet caught open). qty 270 → -$4.32 |
| slv-test | (Apr 16) 15:31 | 71.29 | 19:35:25 | 72.12 | TS | 72.14 | +0.830 | **Validated trail fire.** Trail ratcheted $70.72→$72.14, server stop fired in profit. Slippage: -0.020. qty 342 → **+$283.86** |

## 2026-04-21

Tuesday. No fills — GLD/IAU/GDX/SLV all flat, no qualifying signals.

## 2026-04-22

| Bot | Entry time (UTC) | Entry $ | Exit time (UTC) | Exit $ | Exit type | Stop level at exit | P&L/share | Notes |
|-----|-----------------|---------|-----------------|--------|-----------|-------------------|-----------|-------|
| gld-test | 17:31:13 | 434.94 | (Apr 23) | 433.61 | SS | 433.67 | -1.330 | Held overnight; gap-down stop Apr 23 14:00. qty 56 → -$74.48 |
| slv-test | 18:16:55 | 70.48 | (Apr 23) | 68.736 | SS | 70.15 | -1.744 | Held overnight; **gap-through Apr 23**. Fill clean vs open; delta = gap risk, not slippage. qty 347 → **-$605.52** |
| iau-test | 18:37:01 | 89.04 | 18:46:35 | 89.24 | SS | 89.23 | -0.200 | **Short entry** (sell-to-open). Buy-stop fired 9 min later. Slippage: +0.010. qty 274 → -$54.80 |

## 2026-04-23

Choppy session — 10 fills total, 3 GLD stop-cycles, IAU short→long flip, SLV gap-out.

| Bot | Entry time (UTC) | Entry $ | Exit time (UTC) | Exit $ | Exit type | Stop level at exit | P&L/share | Notes |
|-----|-----------------|---------|-----------------|--------|-----------|-------------------|-----------|-------|
| slv-test | (Apr 22) 18:16:55 | 70.48 | 13:32:55 | 68.736 | SS | 70.15 | -1.744 | Overnight gap-through. Pre-market $68.67, open $68.75, fill $68.74. qty 347 → -$605.52 |
| iau-test | 13:44:26 | 89.05 | 16:51:32 | 89.10 | SS | 89.09 | -0.050 | **Short entry**, buy-stop fired 3h later. **First organic short stop fire against us.** Slippage: +0.010. qty 273 → -$13.65 |
| gld-test | (Apr 22) 17:31:13 | 434.94 | 14:00:08 | 433.605 | SS | 433.67 | -1.335 | Overnight stop. Slippage: -0.065. qty 56 → -$74.76 |
| gld-test | 15:01:25 | 434.53 | 15:54:54 | 433.11 | SS | 433.19 | -1.420 | Re-entry, stopped 53 min later. Slippage: -0.080. qty 55 → -$78.10 |
| gld-test | 16:46:11 | 434.71 | 17:05:38 | 433.203 | SS | 433.21 | -1.507 | Re-entry, stopped 19 min later. Slippage: -0.007. qty 55 → -$82.89 |
| gld-test | 18:16:29 | 432.78 | OPEN | — | — | — | — | 3rd GLD long entry of the day. Currently open. qty 56 |
| iau-test | 18:18:15 | 88.66 | OPEN | — | — | — | — | New long entry after morning short covered. Currently open. qty 273 |

*GLD whiplash: 3 consecutive entry→stop cycles in one session, all losses (-$1.42, -$1.51, -$1.34/share). 3rd re-entry survives into today.*

## 2026-04-24

| Bot | Entry time (UTC) | Entry $ | Exit time (UTC) | Exit $ | Exit type | Stop level at exit | P&L/share | Notes |
|-----|-----------------|---------|-----------------|--------|-----------|-------------------|-----------|-------|
| slv-test | 18:46:59 | 69.14 | OPEN | — | — | — | — | **Short entry** (sell-to-open). Currently open. qty 350 |

## 2026-04-25 – 2026-04-26

Weekend — market closed. GLD long, IAU long, SLV short carrying overnight via GTC stops.

## 2026-04-27

Monday — `skip_days:[0]` in effect, no new entries. Open positions (as of session start, market closed):

| Bot | Side | Qty | Avg Entry | Current | Unrealized P&L |
|-----|------|-----|-----------|---------|----------------|
| gld-test | long | 56 | $434.00* | $432.00 | -$111.94 |
| iau-test | long | 273 | $88.88* | $88.45 | -$117.39 |
| slv-test | short | 350 | $69.14 | $68.42 | +$252.00 |
| gdx-test | flat | — | — | — | — |

\* Alpaca position `avg_entry_price` is ~$1 above MCP fill avg for GLD/IAU due to cumulative cost-basis after rapid same-day close/reopen cycles. Quantities and current prices are exact.

Net unrealized: **+$22.67**.

---

## Realised P&L summary (closed trades only)

| Date | Trades | Net P&L |
|------|--------|---------|
| Apr 15→16 | 1 (SLV K-exit) | -$207.40 |
| Apr 16 | 1 (GLD short K-exit) | +$38.50 |
| Apr 20 | 3 (2 SS, 1 TS — SLV trail) | +$249.84 |
| Apr 22 | 1 (IAU short SS) | -$54.80 |
| Apr 23 | 6 (SLV gap, 3 GLD SS, IAU short SS, IAU long open) | -$854.92 |
| Apr 29 | 1 (XBI EM — gap-through-stop guard) | -$313.61 |
| **Total (13 closed)** | | **-$1,142.39** |

Apr 23 dominates the loss tape (-$855 across 6 fills). Removing that single session: net **+$26.14** across the other 6 closed trades. The validated trail fire (+$283.86) almost exactly offsets the SLV gap-through (-$605.52), with the GLD whiplash (-$244) being the residual hit.

**Sample is small** — 12 closed round-trips is far below the calibration window's 65. Win-rate convergence vs backtest predictions (GLD 48% / SLV 57% / GDX 59% / IAU 37%) is not yet meaningful. Continue collecting.

---

## Apr 29 2026 — correlation-aware sizing V1 deployed

Per-trade `risk_frac` discounted by cluster occupancy: `risk_frac = 0.02 / N` where N = peers in same cluster currently held + self. Hardcoded clusters: gold = GLD/IAU/SLV/GDX, energy = OIH/XOP/XLE, biotech = XBI. Effective from this date forward.

**What to record on each entry from this date:**

- N at entry time (count of cluster peers held + self)
- Risk fraction applied (0.02, 0.01, 0.0067, or 0.005)
- Whether the `[CORR-SIZE]` line appeared in pm2 logs (it should appear iff N > 1)
- Approximate share count vs what an undiscounted entry of the same symbol/ATR would have produced (rough sanity check — should scale ~1/N until 25% notional cap binds)

**V1 race condition to watch for:** if two cluster peers fire within ~1s of the same 15m close, both may see N=1 (neither has filled yet when the other polls). Symptom: both bots log a normal entry, no `[CORR-SIZE]` line on either, and total cluster exposure ends up at ~4% (2 × 2%) instead of the intended 3% (2% + 1%). If this materialises in the first ~5 cluster simultaneous entries, the V2 plan (DB advisory lock or staggered polling offsets) should be prioritised. If it doesn't, accept the looseness.

**First cluster-simultaneous entry that triggers the discount: TBD.** Log here with N, risk_frac, share count, and a comparison to the most recent solo entry on the same symbol.

---

## 2026-04-29 — XBI gap-through-stop fix + market exit

XBI long position (entered Apr 28 19:31 @ $131.25, qty 185) went unprotected overnight after the bot's "DAY stop gap recovery" logic canceled the GTC stop @ $130.85 at session re-open today and the re-place at $130.68 was rejected by Alpaca (price had gapped down to $129.36–$130.30, so "stop above market" for a long sell-stop). Bot entered a retry loop with no active protection.

**Manual intervention:** placed safety stop @ $128.50 GTC at 13:55 UTC via Alpaca MCP (order id `447f0e3f`).

**Fix deployed:** runner.py [LOOP] gap-recovery path + [SYNC] startup path now check whether the intended stop level is on the wrong side of current price. If breached, place a market exit + reset strategy state instead of retrying a stop Alpaca will keep rejecting. Two commits (`cfdc514` + `82fd682`), bots restarted at 14:03 and 14:11 UTC.

**Outcome:** first new-bar [LOOP] iteration after restart fired the new guard correctly:
```
[LOOP] 🚨 Stop $130.68 already breached by price $129.50 — exiting at market
```
Market sell filled 14:06:11 UTC @ $129.5548 (185 shares). Manual safety stop auto-canceled by `cancel_all_orders_for_symbol` before the market exit.

| Bot | Entry time (UTC) | Entry $ | Exit time (UTC) | Exit $ | Exit type | Stop level at exit | P&L/share | Notes |
|-----|-----------------|---------|-----------------|--------|-----------|-------------------|-----------|-------|
| xbi-test | (Apr 28) 19:31 | 131.25 | 14:06:11 | 129.5548 | EM (emergency market — gap-through-stop guard) | 130.68 (intended trail) | -1.6952 | qty 185 → **-$313.61**. Gap-through-stop bug surfaced + fixed same-session. New exit type `EM` introduced. Manual safety stop $128.50 was cheaper insurance — actual exit $1.06/share better than the manual stop level. |

**Cost of the bug ultimately:** the bot would have exited cleanly via the GTC stop @ $130.85 (-$74) had the gap-recovery path not canceled it. Realised exit at $129.55 vs $130.85 = ~$240 incremental loss attributable to the bug. Net exit -$313.61.

**New exit type:** `EM` (emergency market, gap-through-stop guard). Distinct from `K` (signal close), `SS` (stop fired), `TS` (trail fired). Should be rare — only fires when the bot's tracked stop is invalid against current price.

**Still open:** root cause of why `pending_stop_order_id` was None despite a live GTC stop. Defensive guard means we don't end up unprotected even when the gate spuriously triggers, but the trigger condition itself should be investigated when convenient.
