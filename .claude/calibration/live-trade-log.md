# Live Trade Log — Calibration Window

Status: current | Epistemic: confirmed | Last verified: 2026-03-30

Detailed per-trade records for the Mar 20 – Apr 20 calibration window.
Used for Apr 20 calibration comparison: Layer 2 (entry/exit prices vs backtest) and Layer 3 (stop fill slippage).

**Exit types:** `K` = bot K-signal at candle close | `SS` = server-side stop (stop loss) | `TS` = trailing stop fired intrabar

---

## Format

| Bot | Entry time (UTC) | Entry $ | Exit time (UTC) | Exit $ | Exit type | Stop level at exit | P&L/share | Notes |
|-----|-----------------|---------|-----------------|--------|-----------|-------------------|-----------|-------|

**Audit status:** PASS / FAIL — all Alpaca records matched pm2 logs

---

## 2026-03-20

**Audit status:** PASS (9/9 DB records matched Alpaca — first fully clean day, all fixes deployed)

| Bot | Entry time (UTC) | Entry $ | Exit time (UTC) | Exit $ | Exit type | Stop level at exit | P&L/share | Notes |
|-----|-----------------|---------|-----------------|--------|-----------|-------------------|-----------|-------|
| slv-test | 15:31:09 | 63.005 | 15:49:37 | 62.353 | TS | 62.39 | -0.652 | Trail ratcheted 61.61→62.39 after 1 bar; stop fired below entry (choppy). Slippage: -0.037 |
| iau-test | 16:31:18 | 86.150 | 17:16:35 | 86.110 | K | - | -0.040 | K-signal exit. Trail ratcheted 3× (85.20→85.96→86.03) but K fired first |
| gld-test | 16:31:33 | 420.505 | 17:16:50 | 420.430 | K | - | -0.075 | K-signal exit. Trail ratcheted 3× (415.83→419.37→419.91) but K fired first |
| gdx-test | 17:01:42 | 80.803 | 17:32:21 | 80.431 | TS | 80.44 | -0.372 | Trail ratcheted 79.46→80.44 after 1 bar; stop fired below entry (choppy). Slippage: -0.009 |
| gdx-test | 19:46:29 | 80.050 | — (Mar 23) | 83.317 | TS | 83.35 | +3.267 | Overnight hold. Initial stop 79.04 expired at 20:00 (DAY TIF). Trail ratcheted over 3 days to 83.35; server stop fired in profit Mar 23. Slippage: -0.033 |

---

## 2026-03-21

**Audit status:** (data needed)

---

## 2026-03-22

Weekend — market closed.

---

## 2026-03-23

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

---

## 2026-03-24

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

---

## 2026-03-25

**Audit status:** PASS (2/2 DB records matched Alpaca — GLD/IAU/SLV flat)

| Bot | Entry time (UTC) | Entry $ | Exit time (UTC) | Exit $ | Exit type | Stop level at exit | P&L/share | Notes |
|-----|-----------------|---------|-----------------|--------|-----------|-------------------|-----------|-------|
| gdx-test | 17:31:24 | 86.800 | 17:52:55 | 86.480 | TS | 86.49 | -0.320 | Trail ratcheted 85.74→86.49 after 1 bar; stop fired below entry. Slippage: -0.010 |

---

## 2026-03-26

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

---

## 2026-03-27

**Audit status:** PASS (6/6 DB records matched Alpaca — GDX flat)

| Bot | Entry time (UTC) | Entry $ | Exit time (UTC) | Exit $ | Exit type | Stop level at exit | P&L/share | Notes |
|-----|-----------------|---------|-----------------|--------|-----------|-------------------|-----------|-------|
| gld-test | 18:46:23 | 415.569 | 19:05:01 | 414.222 | TS | 414.23 | -1.347 | Slippage: -0.008 |
| iau-test | 18:46:31 | 85.101 | 19:03:55 | 84.898 | TS | 84.90 | -0.203 | Slippage: -0.002 |
| slv-test | 18:46:52 | 63.700 | 19:03:57 | 63.422 | TS | 63.43 | -0.278 | Slippage: -0.008 |

*All 3 entries within 31s (18:46 UTC), all 3 exits within 1:06 (19:03–19:05 UTC). Trail fired after 1 bar on all 3, exits below entry — correlated metals hit by same intrabar move.*

---

## 2026-03-31

**Audit status:** PASS (36/36 Alpaca orders matched pm2 logs — strong metals rally day, 7 completed trades + 1 overnight)

| Bot | Entry time (UTC) | Entry $ | Exit time (UTC) | Exit $ | Exit type | Stop level at exit | P&L/share | Notes |
|-----|-----------------|---------|-----------------|--------|-----------|-------------------|-----------|-------|
| gld-test | 14:32 | 419.834 | 15:01 | 423.817 | K | - | +3.983 | Fill delay: placed 14:31, filled 14:32 (1:26). Trail ratcheted 1× ($417.77→$423.21) |
| iau-test | 14:33 | 86.031 | 15:01 | 86.855 | K | - | +0.824 | Fill delay: placed 14:31, filled 14:33 (2:37). Trail ratcheted 1× ($85.53→$86.68) |
| slv-test | 14:32 | 65.880 | 15:16 | 66.901 | K | - | +1.021 | Fill delay: placed 14:31, filled 14:32 (1:46). Trail ratcheted 2× ($64.95→$66.40→$66.70) |
| gdx-test | 17:46 | 90.891 | 18:24 | 90.787 | TS | 90.81 | -0.104 | Trail ratcheted 2× ($89.49→$90.65→$90.81). Slippage: -0.023 |
| slv-test | 17:46 | 67.384 | 19:01 | 67.909 | K | - | +0.525 | Trail ratcheted 4× ($66.70→$67.37→$67.37→$67.47→$67.60). Duplicate at $67.37 (same ATR calc on consecutive bars — harmless) |
| gld-test | 18:31 | 427.426 | 19:16 | 428.550 | K | - | +1.124 | Trail ratcheted 2× ($424.05→$427.15→$427.85) |
| gdx-test | 19:31 | 91.072 | 20:06 | 90.880 | TS | 90.89 | -0.192 | Trail ratcheted 2× ($89.96→$90.81→$90.89). Slippage: -0.010 |
| slv-test | 20:46 | 68.100 | — (Apr 1) | — | — | 67.50 | — | Overnight hold. Stop $67.42 expired 21:00 (DAY TIF). New stop $67.50 placed 22:10 UTC after bot restart — expected mechanism is re-placement at market open Apr 1, so timing is unexpected. Position protected for tomorrow |

*GLD/IAU/SLV all delayed fills at open (simultaneous 14:31 entries), all profitable K-exits. GDX going against metals rally — both TS exits near entry. 5 of 7 closed trades profitable.*

---

## 2026-03-28

**Audit status:** (data needed)

---

## 2026-03-29

Weekend — market closed.

---

## 2026-03-30

**Audit status:** PASS (15/15 Alpaca records matched pm2 logs — GLD flat, 5 trades across 3 bots)

| Bot | Entry time (UTC) | Entry $ | Exit time (UTC) | Exit $ | Exit type | Stop level at exit | P&L/share | Notes |
|-----|-----------------|---------|-----------------|--------|-----------|-------------------|-----------|-------|
| slv-test | 14:36 | 64.403 | 14:46 | 63.820 | K | - | -0.583 | Fill delay: placed 14:31, filled 14:36 (4:46 delay). Exit via local SL check (no min_hold guard) — price hit SL within 1 bar. set_entry_metadata warning = metadata loss bug (fixed Mar 30) |
| gdx-test | 14:35 | 87.211 | 14:46 | 86.678 | K | - | -0.533 | Fill delay: placed 14:31, filled 14:35 (4:00 delay). Same as SLV T1 — local SL hit after 1 bar. set_entry_metadata warning = metadata loss bug (fixed Mar 30) |
| gdx-test | 16:01 | 87.200 | 16:57 | 87.073 | TS | 87.10 | -0.127 | Trail ratcheted 3× ($85.65→$86.37→$86.51→$87.10). Slippage: -0.027 |
| slv-test | 16:46 | 64.463 | 17:04 | 64.045 | TS | 64.05 | -0.418 | Trail ratcheted 1× ($63.57→$64.05). Slippage: -0.005 |
| iau-test | 17:01 | 85.558 | 17:30 | 85.380 | TS | 85.38 | -0.178 | Trail ratcheted 1× ($84.96→$85.38). Slippage: ~0.000 |

*All 5 exits losing. SLV/GDX T1 simultaneous delayed fills (14:31 UTC) — both K-exited on next bar due to set_entry_metadata failure. GDX T2 had 3 ratchets over 56 min but TS still fired near entry. Choppy session.*

---
