Status: current | Epistemic: confirmed | Last verified: 2026-04-02

# Live Trade Log — Calibration Window

Detailed per-trade records for the Mar 20 – Apr 20 calibration window.
Used for Apr 20 calibration comparison: Layer 2 (entry/exit prices vs backtest) and Layer 3 (stop fill slippage).

**Exit types:** `K` = bot K-signal at candle close | `SS` = server-side stop (stop loss) | `TS` = trailing stop fired intrabar

## Knowledge

### Analysis — Mar 20–31 (43 completed trades)

**Dataset:** 43 completed trades, 10 audited days (Mar 20, 23–27, 30–31). Mar 21 and Mar 28 confirmed zero-trade days (no K crossings met all conditions).

#### K-exits are profitable, trailing stops are not — dramatically

| Exit type | Trades | Winners | Win rate |
|-----------|--------|---------|----------|
| K-signal | 21 | 16 | 76% |
| Trailing stop (TS) | 22 | 3 | 14% |

The 3 TS wins: GDX multi-day hold (+3.267), two near-zero exits (+0.040, +0.020). Every same-day TS exit is a loss. The 0.5 ATR trail after 1 bar fires on normal intrabar noise before the position has moved. Expected for test params — validated params (trail after 10 bars, 2.0 ATR) would look completely different.

**Calibration signal:** the Apr 20 backtest should show roughly the same 50/50 K vs TS split and similarly poor TS win rate. If backtest shows significantly more K-exits and fewer TS exits, the stop execution model is wrong.

#### GDX diverges from the other three

| Symbol | Trades | Winners |
|--------|--------|---------|
| GLD | 10 | 6 |
| IAU | 8 | 4 |
| SLV | 12 | 6 |
| GDX | 11 | 4 |

GDX TS exits: 9 trades, only 3 positive (the multi-day +3.267 carries almost all of it). Backtest predicted GDX as strongest performer (+2.45% Dec–Mar). If live GDX is flat or negative at Apr 20 while backtest predicts positive, worth investigating.

#### Correlated simultaneous entries — matters for real money

Four days show GLD/IAU/SLV entering within seconds: Mar 27 18:46 UTC (all 3 within 31s, all 3 hit same TS fire within 1:06) and Mar 31 13:31 UTC (all 3 delayed fills, all 3 profitable K-exits). With 2% risk per trade, three simultaneous entries = 6% portfolio in one correlated move. Before real money: reduce per-trade risk to ~0.75% when 3+ correlated bots are in simultaneously, or require minimum K-value threshold difference to stagger entries.

#### Market open is the most active — and most delayed — entry window

Most profitable K-exit days start with a delayed fill at 13:31–14:00 UTC. Mar 23 (best day: +5.333 GLD, +2.102 SLV) had fills 3–4 min late. Mar 31 had fills 1–3 min late. Delay doesn't prevent profitability — the stop placement fix (Mar 26) was critical; without it those trades ran unprotected.

#### One multi-day hold outperformed the entire rest of the dataset

GDX Mar 20→23: +3.267/share. Validated params produce more multi-day holds (trail after 10 bars). This single trade illustrates what the validated strategy is designed to capture — test params deliberately sacrifice P&L for trade volume.

#### Apr 20 calibration — specific things to watch

1. K vs TS exit ratio — should be close to 50/50, matching live
2. GDX underperformance — does backtest also show GDX trailing GLD/IAU/SLV?
3. Entry time distribution — does backtest cluster entries at open the same way live does?
4. Stop slippage — live range $0.000–$0.140/share, most under $0.05; if backtest assumes 0, that's a small but known gap

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
