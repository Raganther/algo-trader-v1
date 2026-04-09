Status: current | Epistemic: confirmed | Last verified: 2026-04-08

# Live Trade Log — Calibration Window

Detailed per-trade records for the Mar 20 – Apr 20 calibration window.
Used for Apr 20 calibration comparison: Layer 2 (entry/exit prices vs backtest) and Layer 3 (stop fill slippage).

**Exit types:** `K` = bot K-signal at candle close | `SS` = server-side stop (stop loss) | `TS` = trailing stop fired intrabar

## Plan

### Active
- [ ] Log each trading day through Apr 20 — check bots daily, add trade rows, update analysis totals
- [ ] Run Apr 20 calibration comparison — see `.claude/calibration/calibration-notes.md` for commands and framework

### Research
- [ ] After Apr 20: does the backtest reproduce the 50/50 K/TS split? If not, stop execution model needs investigation
- [ ] After Apr 20: does backtest show GDX underperforming the other three, or does it predict GDX strong? Determines whether GDX divergence is regime or model issue

## Knowledge

### Analysis — Mar 20–Apr 7 (62 completed trades, 1 open)

**Dataset:** 62 completed trades + 1 open (GLD Apr 7), 14 active days (Mar 20, 23–27, 30–31, Apr 1–2, 6–7). Mar 21 and Mar 28 confirmed zero-trade days (no K crossings met all conditions). Apr 3 market holiday (Good Friday). Apr 6–7 Alpaca MCP verified, DB audit pending.

#### K-exits are profitable, trailing stops are not — dramatically

| Exit type | Trades | Winners | Win rate |
|-----------|--------|---------|----------|
| K-signal | 29 | 22 | 76% |
| Trailing stop (TS) | 33 | 5 | 15% |

The 5 TS wins: GDX multi-day hold (+3.267), two near-zero exits (+0.040, +0.020), GLD Apr 2 (+1.995), IAU Apr 7 (+0.033 near-zero). Apr 6–7 added 8 new TS exits, all losing or near-zero — reinforcing the pattern. Apr 6–7 added 4 new K-exits: 2 winners (GDX +0.240, SLV +0.235), 2 near-flat losers (GDX -0.020, SLV -0.169). K-exit win rate dipped slightly (80%→76%) as the strategy generated some exits near entry on choppy days.

K/TS split shifted to 29/33 (47/53) — slightly more TS exits than K-exits now. Still broadly consistent with 50/50 expectation.

**Calibration signal:** the Apr 20 backtest should show roughly the same 50/50 K vs TS split and similarly poor TS win rate. If backtest shows significantly more K-exits and fewer TS exits, the stop execution model is wrong.

#### GDX diverges from the other three

| Symbol | Trades | Winners | Win rate |
|--------|--------|---------|----------|
| GLD | 16 | 9 | 56% |
| IAU | 14 | 6 | 43% |
| SLV | 16 | 8 | 50% |
| GDX | 16 | 8 | 50% |

GDX recovered from 42% to 50% on the back of 3 active trades Apr 6 (2 K-exits including a winner, one TS loss). GLD dipped from 67% to 56% — Apr 6 TS loss + two Apr 7 TS losses. IAU weakest at 43% — Apr 7 was particularly bad (2 quick TS exits near entry). GDX TS exits: 12 trades, 3 positive (same three as before — no new TS wins on GDX).

#### Correlated simultaneous entries — matters for real money

Four days show GLD/IAU/SLV entering within seconds: Mar 27 18:46 UTC (all 3 within 31s, all 3 hit same TS fire within 1:06) and Mar 31 13:31 UTC (all 3 delayed fills, all 3 profitable K-exits). With 2% risk per trade, three simultaneous entries = 6% portfolio in one correlated move. Before real money: reduce per-trade risk to ~0.75% when 3+ correlated bots are in simultaneously, or require minimum K-value threshold difference to stagger entries.

#### Market open is the most active — and most delayed — entry window

Most profitable K-exit days start with a delayed fill at 13:31–14:00 UTC. Mar 23 (best day: +5.333 GLD, +2.102 SLV) had fills 3–4 min late. Mar 31 had fills 1–3 min late. Delay doesn't prevent profitability — the stop placement fix (Mar 26) was critical; without it those trades ran unprotected.

#### One multi-day hold outperformed the entire rest of the dataset

GDX Mar 20→23: +3.267/share. Validated params produce more multi-day holds (trail after 10 bars). This single trade illustrates what the validated strategy is designed to capture — test params deliberately sacrifice P&L for trade volume.

#### Signal confirmed — full edge not yet confirmed

The K-exit win rate (80%) confirms that the **entry signal + K-exit signal** have real alpha in live conditions. It does not confirm the full validated edge. The trail is not just protection — at validated params (2.0 ATR, after 10 bars) it's the component that holds profitable positions through noise and captures extended moves. The three components work together: entry finds the setup, trail lets it run, K-exit closes it cleanly. We've confirmed two of three in live conditions. The trail at validated params has never run live.

**Full edge confirmation requires a second clean window on validated params after Apr 20.**

The Apr 20 calibration is also the precondition for trusting the validated params projection. If the backtest faithfully models what we've observed here, the Sharpe 2.54 and return predictions for validated params are grounded. If it doesn't match, the projection is ungrounded regardless of backtest numbers.

#### Apr 20 calibration — specific things to watch

1. ~~K vs TS exit ratio~~ — **RESOLVED (Apr 4).** Backtest stop-check ordering bug fixed. Backtest now matches live 50/50. No longer an open question.
2. GDX underperformance — does backtest also show GDX trailing GLD/IAU/SLV?
3. Entry time distribution — does backtest cluster entries at open the same way live does?
4. Stop slippage — **CHARACTERISED (Apr 4).** Mean $0.022/share, median $0.010/share, 100% negative direction (27 exits). Backtest assumes $0. Known ~$0.010–0.022/share systematic bias — will cause small P&L overstatement in Layer 4. Decision: add `stop_slippage` param only after Apr 20 confirms bias on larger sample.
5. **Use corrected command** — `trading_hours:[13.5,20]` and `long_only:true` are both required. Without them the comparison is invalid (confirmed Apr 3).

### Format

| Bot | Entry time (UTC) | Entry $ | Exit time (UTC) | Exit $ | Exit type | Stop level at exit | P&L/share | Notes |
|-----|-----------------|---------|-----------------|--------|-----------|-------------------|-----------|-------|

**Audit status:** PASS / FAIL — all Alpaca records matched pm2 logs

### 2026-03-20

**Audit status:** PASS (9/9 DB records matched Alpaca — first fully clean day, all fixes deployed)

| Bot | Entry time (UTC) | Entry $ | Exit time (UTC) | Exit $ | Exit type | Stop level at exit | P&L/share | Notes |
|-----|-----------------|---------|-----------------|--------|-----------|-------------------|-----------|-------|
| slv-test | 15:31:09 | 63.005 | 15:49:37 | 62.353 | TS | 62.39 | -0.652 | Trail ratcheted 61.61→62.39 after 1 bar; stop fired below entry (choppy). Slippage: -0.037 |
| iau-test | 16:31:18 | 86.150 | 17:16:35 | 86.110 | K | - | -0.040 | K-signal exit. Trail ratcheted 3× (85.20→85.96→86.03) but K fired first |
| gld-test | 16:31:33 | 420.505 | 17:16:50 | 420.430 | K | - | -0.075 | K-signal exit. Trail ratcheted 3× (415.83→419.37→419.91) but K fired first |
| gdx-test | 17:01:42 | 80.803 | 17:32:21 | 80.431 | TS | 80.44 | -0.372 | Trail ratcheted 79.46→80.44 after 1 bar; stop fired below entry (choppy). Slippage: -0.009 |
| gdx-test | 19:46:29 | 80.050 | — (Mar 23) | 83.317 | TS | 83.35 | +3.267 | Overnight hold. Initial stop 79.04 expired at 20:00 (DAY TIF). Trail ratcheted over 3 days to 83.35; server stop fired in profit Mar 23. Slippage: -0.033 |

### 2026-03-21

**Audit status:** PASS — zero trades (confirmed via DB query: no K crossings met all conditions)

### 2026-03-22

Weekend — market closed.

### 2026-03-23

**Audit status:** PASS (13/13 DB records matched Alpaca)

| Bot | Entry time (UTC) | Entry $ | Exit time (UTC) | Exit $ | Exit type | Stop level at exit | P&L/share | Notes |
|-----|-----------------|---------|-----------------|--------|-----------|-------------------|-----------|-------|
| slv-test | 13:34:34 | 61.138 | 14:16:49 | 63.240 | K | - | +2.102 | Fill delay: created 13:31:07, filled 13:34:34 (3:27 delay at market open) |
| gld-test | 13:35:00 | 406.037 | 14:17:00 | 411.370 | K | - | +5.333 | Fill delay: created 13:31:15, filled 13:35:00 (3:45 delay at market open) |
| iau-test | 14:01:45 | 84.023 | 14:16:54 | 84.231 | K | - | +0.208 | Trail ratcheted 82.78→84.01 (2×) but K fired first |
| iau-test | 16:46:43 | 82.550 | 17:32:00 | 83.230 | K | - | +0.680 | Trail ratcheted 81.13→82.17→82.44→82.70 (4×) but K fired first |
| slv-test | 17:01:32 | 62.590 | 17:46:49 | 62.820 | K | - | +0.230 | Trail ratcheted 61.04→62.23→62.57 (3×) but K fired first |
| gld-test | 17:16:54 | 403.631 | 18:01:15 | 406.127 | K | - | +2.496 | Trail ratcheted 397.62→403.64→404.51→404.64 (4×) but K fired first |
| gdx-test | 19:46:29 (Mar 20) | 80.050 | 19:13:28 | 83.317 | TS | 83.35 | +3.267 | Multi-day hold. Trail ratcheted to 83.35 over weekend; server stop fired in profit. Slippage: -0.033. Trail fire confirmed ✅ |

### 2026-03-24

**Audit status:** PASS (16/16 DB records matched Alpaca — 6 of 8 exits via server stop)

| Bot | Entry time (UTC) | Entry $ | Exit time (UTC) | Exit $ | Exit type | Stop level at exit | P&L/share | Notes |
|-----|-----------------|---------|-----------------|--------|-----------|-------------------|-----------|-------|
| slv-test | 14:16:47 | 62.070 | 15:01:05 | 63.120 | K | - | +1.050 | |
| gdx-test | 14:16:14 | 82.531 | 15:01:31 | 82.960 | K | - | +0.429 | |
| iau-test | 14:31:57 | 82.900 | 15:10:42 | 82.800 | TS | 82.82 | -0.100 | Slippage: -0.020. Simultaneous fire with GLD at 15:10:42 — correlated intrabar move |
| gld-test | 14:31:02 | 404.796 | 15:10:42 | 404.040 | TS | 404.18 | -0.756 | Slippage: -0.140. Simultaneous fire with IAU at 15:10:42 |
| gdx-test | 18:16:24 | 83.400 | 18:47:44 | 83.440 | TS | 83.45 | +0.040 | Slippage: -0.010. Tiny profit — trail just above entry |
| gld-test | 18:31:09 | 405.249 | 18:58:09 | 403.255 | TS | 403.26 | -1.994 | Slippage: -0.005. Simultaneous fire with IAU at 18:58:09 |
| iau-test | 18:32:00 | 83.168 | 18:58:09 | 82.600 | TS | 82.61 | -0.568 | Slippage: -0.010. Simultaneous fire with GLD at 18:58:09 |
| slv-test | 19:16:48 | 63.230 | 19:35:52 | 62.870 | TS | 62.87 | -0.360 | Slippage: ~0.000 |

### 2026-03-25

**Audit status:** PASS (2/2 DB records matched Alpaca — GLD/IAU/SLV flat)

| Bot | Entry time (UTC) | Entry $ | Exit time (UTC) | Exit $ | Exit type | Stop level at exit | P&L/share | Notes |
|-----|-----------------|---------|-----------------|--------|-----------|-------------------|-----------|-------|
| gdx-test | 17:31:24 | 86.800 | 17:52:55 | 86.480 | TS | 86.49 | -0.320 | Trail ratcheted 85.74→86.49 after 1 bar; stop fired below entry. Slippage: -0.010 |

### 2026-03-26

**Audit status:** PASS (14/14 DB records matched Alpaca)

| Bot | Entry time (UTC) | Entry $ | Exit time (UTC) | Exit $ | Exit type | Stop level at exit | P&L/share | Notes |
|-----|-----------------|---------|-----------------|--------|-----------|-------------------|-----------|-------|
| slv-test | 13:33:00 | 61.940 | 14:16:39 | 62.684 | K | - | +0.744 | Fill delay: created 13:31:47, filled 13:33:00 (1:13). No stop placed — pending_fills bug (fixed same day). Ran unprotected 43 min |
| gdx-test | 13:46:17 | 85.850 | 14:04:38 | 85.340 | TS | 85.39 | -0.510 | Slippage: -0.050 |
| gld-test | 14:01:10 | 408.700 | 14:46:30 | 410.060 | K | - | +1.360 | Trail ratcheted 4× but K fired first |
| iau-test | 17:16:25 | 82.670 | 18:16:47 | 82.480 | K | - | -0.190 | Trail ratcheted 2× but K fired first |
| gld-test | 18:16:42 | 402.430 | 19:02:03 | 403.950 | K | - | +1.520 | Trail ratcheted 3× but K fired first |
| gdx-test | 18:31:52 | 83.450 | 19:03:40 | 83.470 | TS | 83.48 | +0.020 | Slippage: -0.010. Tiny profit |
| slv-test | 18:46:15 | 61.160 | 19:04:55 | 61.090 | TS | 61.10 | -0.070 | Slippage: -0.010 |

### 2026-03-27

**Audit status:** PASS (6/6 DB records matched Alpaca — GDX flat)

| Bot | Entry time (UTC) | Entry $ | Exit time (UTC) | Exit $ | Exit type | Stop level at exit | P&L/share | Notes |
|-----|-----------------|---------|-----------------|--------|-----------|-------------------|-----------|-------|
| gld-test | 18:46:23 | 415.569 | 19:05:01 | 414.222 | TS | 414.23 | -1.347 | Slippage: -0.008 |
| iau-test | 18:46:31 | 85.101 | 19:03:55 | 84.898 | TS | 84.90 | -0.203 | Slippage: -0.002 |
| slv-test | 18:46:52 | 63.700 | 19:03:57 | 63.422 | TS | 63.43 | -0.278 | Slippage: -0.008 |

*All 3 entries within 31s (18:46 UTC), all 3 exits within 1:06 (19:03–19:05 UTC). Trail fired after 1 bar on all 3, exits below entry — correlated metals hit by same intrabar move.*

### 2026-03-28

**Audit status:** PASS — zero trades (confirmed via DB query: no K crossings met all conditions)

### 2026-03-29

Weekend — market closed.

### 2026-03-30

**Audit status:** PASS (15/15 Alpaca records matched pm2 logs — GLD flat, 5 trades across 3 bots)

*Note: timestamps corrected from IST→UTC (Irish DST began Mar 29, Alpaca UI was showing UTC+1)*

| Bot | Entry time (UTC) | Entry $ | Exit time (UTC) | Exit $ | Exit type | Stop level at exit | P&L/share | Notes |
|-----|-----------------|---------|-----------------|--------|-----------|-------------------|-----------|-------|
| slv-test | 13:36 | 64.403 | 13:46 | 63.820 | K | - | -0.583 | Fill delay: placed 13:31, filled 13:36 (4:46 delay). Exit via local SL check (no min_hold guard) — price hit SL within 1 bar. set_entry_metadata warning = metadata loss bug (fixed Mar 30) |
| gdx-test | 13:35 | 87.211 | 13:46 | 86.678 | K | - | -0.533 | Fill delay: placed 13:31, filled 13:35 (4:00 delay). Same as SLV T1 — local SL hit after 1 bar. set_entry_metadata warning = metadata loss bug (fixed Mar 30) |
| gdx-test | 15:01 | 87.200 | 15:57 | 87.073 | TS | 87.10 | -0.127 | Trail ratcheted 3× ($85.65→$86.37→$86.51→$87.10). Slippage: -0.027 |
| slv-test | 15:46 | 64.463 | 16:04 | 64.045 | TS | 64.05 | -0.418 | Trail ratcheted 1× ($63.57→$64.05). Slippage: -0.005 |
| iau-test | 16:01 | 85.558 | 16:30 | 85.380 | TS | 85.38 | -0.178 | Trail ratcheted 1× ($84.96→$85.38). Slippage: ~0.000 |

*All 5 exits losing. SLV/GDX T1 simultaneous delayed fills (13:31 UTC) — both local SL hits after 1 bar. GDX T2 had 3 ratchets over 56 min but TS still fired near entry. Choppy session.*

### 2026-03-31

**Audit status:** PASS (36/36 Alpaca orders matched pm2 logs — strong metals rally day, 7 completed trades + 1 overnight)

*Note: timestamps corrected from IST→UTC (Irish DST began Mar 29, Alpaca UI was showing UTC+1)*

| Bot | Entry time (UTC) | Entry $ | Exit time (UTC) | Exit $ | Exit type | Stop level at exit | P&L/share | Notes |
|-----|-----------------|---------|-----------------|--------|-----------|-------------------|-----------|-------|
| gld-test | 13:32 | 419.834 | 14:01 | 423.817 | K | - | +3.983 | Fill delay: placed 13:31, filled 13:32 (1:26). Trail ratcheted 1× ($417.77→$423.21) |
| iau-test | 13:33 | 86.031 | 14:01 | 86.855 | K | - | +0.824 | Fill delay: placed 13:31, filled 13:33 (2:37). Trail ratcheted 1× ($85.53→$86.68) |
| slv-test | 13:32 | 65.880 | 14:16 | 66.901 | K | - | +1.021 | Fill delay: placed 13:31, filled 13:32 (1:46). Trail ratcheted 2× ($64.95→$66.40→$66.70) |
| gdx-test | 16:46 | 90.891 | 17:24 | 90.787 | TS | 90.81 | -0.104 | Trail ratcheted 2× ($89.49→$90.65→$90.81). Slippage: -0.023 |
| slv-test | 16:46 | 67.384 | 18:01 | 67.909 | K | - | +0.525 | Trail ratcheted 4× ($66.70→$67.37→$67.37→$67.47→$67.60). Duplicate at $67.37 (same ATR calc on consecutive bars — harmless) |
| gld-test | 17:31 | 427.426 | 18:16 | 428.550 | K | - | +1.124 | Trail ratcheted 2× ($424.05→$427.15→$427.85) |
| gdx-test | 18:31 | 91.072 | 19:06 | 90.880 | TS | 90.89 | -0.192 | Trail ratcheted 2× ($89.96→$90.81→$90.89). Slippage: -0.010 |
| slv-test | 19:46 | 68.100 | Apr 1 13:42 | 67.841 | SS | 67.87 | -0.259 | Overnight hold exits Apr 1. Stop $67.42 expired 20:00 UTC. Stop $67.50 attempt at 21:10 UTC — REJECTED (market closed, not placed as originally noted). New stop $67.87 placed at market open Apr 1 13:31 UTC (startup sync on bot restart). Slippage: -0.029 |

*GLD/IAU/SLV all delayed fills at open (simultaneous 13:31 entries), all profitable K-exits. GDX going against metals rally — both TS exits near entry. 5 of 7 closed trades profitable.*

### 2026-04-01

**Audit status:** PASS (4/4 Alpaca orders matched — SLV only active bot, GLD/IAU/GDX 0 trades)

| Bot | Entry time (UTC) | Entry $ | Exit time (UTC) | Exit $ | Exit type | Stop level at exit | P&L/share | Notes |
|-----|-----------------|---------|-----------------|--------|-----------|-------------------|-----------|-------|
| slv-test | Mar 31 19:46 | 68.100 | 13:42 | 67.841 | SS | 67.87 | -0.259 | Overnight hold from Mar 31. Stop re-placed at market open 13:31 UTC (startup sync). Slippage: -0.029 |
| slv-test | 15:01 | 68.210 | 15:30 | 68.132 | TS | 68.14 | -0.078 | Trail ratcheted 1× ($67.54→$68.14). Fired below entry — same-day TS loss pattern. Slippage: -0.008 |

*GLD/IAU/GDX: no signals. SLV: overnight exit (SS loss) + same-day TS loss. Both SLV exits losing — choppy day, no sustained momentum.*

### 2026-04-02

**Audit status:** PASS (30 Alpaca orders confirmed via MCP — 6 trades across all 4 bots)

*Note: Good Friday Apr 3 is market holiday — next session Monday Apr 6.*

| Bot | Entry time (UTC) | Entry $ | Exit time (UTC) | Exit $ | Exit type | Stop level at exit | P&L/share | Notes |
|-----|-----------------|---------|-----------------|--------|-----------|-------------------|-----------|-------|
| gdx-test | 14:01 | 93.486 | 14:46 | 94.920 | K | - | +1.434 | Trail ratcheted 3× (91.86→93.51→93.82→94.31), K-signal fired |
| slv-test | 14:01 | 64.462 | 14:46 | 65.910 | K | - | +1.448 | Trail ratcheted 3× (63.43→64.48→64.65→65.62), K-signal fired |
| gld-test | 14:17 | 427.590 | 14:50 | 429.585 | TS | 429.64 | +1.995 | Trail ratcheted 2× (422.45→427.09→429.64); stop fired in profit. Slippage: -0.055 |
| iau-test | 14:46 | 88.170 | 15:22 | 87.700 | TS | 87.71 | -0.470 | Trail ratcheted 1× (87.12→87.71); stop fired below entry (no sustained move). Slippage: -0.010 |
| iau-test | 18:18 | 87.610 | 19:01 | 87.920 | K | - | +0.310 | Trail ratcheted 3× (87.16→87.50→87.67→87.80), K-signal fired |
| gld-test | 18:31 | 427.800 | 19:16 | 429.080 | K | - | +1.280 | Trail ratcheted 2× (425.38→427.88→428.71), K-signal fired |

*5/6 trades profitable. GLD T1 TS exit in profit — another server-side trail fire confirmed. IAU T1 TS fired below entry (1 ratchet, still short of entry). GDX/SLV clean K-signal exits with good ratchet progression. All bots flat EOD.*

### 2026-04-03

Market closed — Good Friday (US market holiday).

### 2026-04-04 — 2026-04-05

Weekend — market closed.

### 2026-04-06

**Audit status:** PARTIAL — Alpaca MCP verified (orders confirmed), pm2/DB audit pending

*Note: Easter Monday — US markets open (Easter Monday is not a US market holiday). GDX had 3 complete trades in one session — most active single-bot day so far.*

| Bot | Entry time (UTC) | Entry $ | Exit time (UTC) | Exit $ | Exit type | Stop level at exit | P&L/share | Notes |
|-----|-----------------|---------|-----------------|--------|-----------|-------------------|-----------|-------|
| gdx-test | 15:01 | 94.480 | 15:41 | 93.760 | TS | 93.80 | -0.720 | Trail ratcheted 93.17→93.40→93.80 (2×). Slippage: -0.040 |
| gdx-test | 16:01 | 94.310 | 16:46 | 94.290 | K | - | -0.020 | Trail ratcheted 92.90→93.76→93.87→93.93 (3×); K-signal fired |
| slv-test | 16:16 | 65.829 | 17:01 | 65.660 | K | - | -0.169 | Trail ratcheted 65.07→65.61→65.65 (2×); K-signal fired. Loss despite K-exit — closed near entry |
| gdx-test | 17:46 | 94.160 | 18:31 | 94.400 | K | - | +0.240 | Trail ratcheted 93.28→93.70→94.03→94.25 (3×); K-signal fired |
| iau-test | 18:16 | 87.740 | 18:34 | 87.670 | TS | 87.68 | -0.070 | Trail ratcheted 87.39→87.68 (1×); stop fired below entry. Slippage: -0.010 |
| gld-test | 18:31 | 428.326 | 19:07 | 427.273 | TS | 427.57 | -1.053 | Trail ratcheted 426.71→426.87→427.57 (2×); stop fired below entry. Slippage: -0.297 (largest seen) |

*1/6 trades profitable. GDX dominated: 3 trades, two K-exits (near-flat and small win). SLV K-exit was still a loss — closed near entry before momentum. IAU and GLD both TS exits below entry. GLD slippage -0.297 notable — largest in dataset. Choppy day overall.*

### 2026-04-07

**Audit status:** PARTIAL — Alpaca MCP verified (orders confirmed), pm2/DB audit pending

*Note: GLD T3 still open as of Apr 8 pre-market — not logged here until closed.*

| Bot | Entry time (UTC) | Entry $ | Exit time (UTC) | Exit $ | Exit type | Stop level at exit | P&L/share | Notes |
|-----|-----------------|---------|-----------------|--------|-----------|-------------------|-----------|-------|
| iau-test | 13:44 | 87.350 | 14:01 | 87.250 | TS | 87.25 | -0.100 | Trail ratcheted 87.18→87.25 (1×); stop fired below entry. Slippage: 0.000 |
| gld-test | 13:44 | 426.234 | 14:01 | 425.800 | TS | 425.82 | -0.434 | Trail ratcheted 424.50→425.82 (1×); stop fired below entry. Slippage: -0.020 |
| gdx-test | 14:32 | 93.540 | 15:03 | 93.103 | TS | 93.15 | -0.437 | Trail ratcheted 92.56→93.04→93.15 (2×). Slippage: -0.047 |
| iau-test | 14:32 | 87.417 | 14:50 | 87.450 | TS | 87.45 | +0.033 | Trail ratcheted 86.97→87.45 (1×); stop fired just above entry. Slippage: 0.000 |
| gld-test | 14:47 | 427.149 | 15:05 | 424.790 | TS | 424.82 | -2.359 | Trail ratcheted 424.53→424.82 (1×); stop fired well below entry. Slippage: -0.030. Largest per-share loss in dataset |
| slv-test | 15:31 | 64.465 | 16:20 | 64.700 | K | - | +0.235 | Trail ratcheted 63.51→64.06→64.40→64.47 (3×); K-signal fired |
| gld-test | ~15:30+ | ~427.919 | OPEN | — | — | — | — | 3rd GLD entry on Apr 7, still open Apr 8 pre-market. Unrealized +$735 (+3.0%) at $440.93 |

*2/6 closed trades profitable (IAU T2 tiny, SLV K-exit). 5 of 6 closed exits via TS — all TS exits losing or near-flat except IAU T2. GLD T2 largest per-share loss in dataset (-2.359). IAU and GLD both stopped within 17 min of entry on first trades — very fast adverse moves at open. GLD T3 (open overnight) sitting on +$735 unrealized.*

## Open Questions

- **Time-of-day filter** — market open (13:31–14:15 UTC) is consistently the most active and most profitable window. Whether this is a persistent edge or regime-specific (post-crash recovery bouncing at open) is unknown. Worth testing as an explicit parameter in backtest after Apr 20.
- **GDX separate params** — GDX behaves structurally differently from GLD/IAU/SLV (mining equity beta layered on physical metal beta). Whether it warrants different OB/OS thresholds or ADX settings, or whether it simply doesn't suit this strategy at all, won't be clear until Apr 20 calibration shows whether the backtest also predicts GDX underperforming. Don't adjust params before then.
- **Overnight hold strategy** — the GDX +3.267 multi-day hold outperformed 49 other trades. Validated params partially capture this pattern (trail after 10 bars). Whether an explicit multi-day hold strategy variant is worth designing is a post-calibration, post-validated-params question.
- **Correlation-aware position sizing** — GLD/IAU/SLV enter simultaneously multiple times per week. At 2% risk per trade, three simultaneous entries = 6% portfolio in one correlated move. Before implementing sizing logic: run portfolio correlation analysis on validated params (all 4 symbols, shared timeline, 5 years) to tally how often simultaneous positions all lose vs all win vs mixed, split by year. If 6% simultaneous loss is rare or GDX divergence provides natural diversification, the sizing constraint may be looser than assumed. Implementation approach (fixed total exposure cap vs scaling function) decided after analysis. Pre-real-money requirement.
- **Late-session entry risk** — Apr 8 shows SLV + GLD + GDX all entering at 19:46 UTC (14 min before close). DAY stops expire at 20:00 before providing protection. Positions carry overnight unprotected until bot re-places stop next morning. A late-session entry guard (block or halve size within ~30 min of close) is a simpler companion mechanism to correlation-aware sizing, testable with the existing single-symbol engine.
