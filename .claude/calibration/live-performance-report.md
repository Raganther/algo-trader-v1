Status: current | Epistemic: live observation | Last verified: 2026-05-07 (20:37 UTC)

# Live Performance Report

Live forward-test on 7-bot lineup, deployed Apr 15-16 (metals four) + Apr 28 (energy/biotech three). Re-run with `python3 -m backend.analysis.live_performance_report`.

## Headline metrics (Apr 15 → today)

| Metric | Live | Backtest expectation | Status |
|---|---:|---:|---|
| Trading days | 0 | – | – |
| Equity start → end | $0 → $0 | – | – |
| Cumulative return | +0.00% | +0.00% | – |
| Sharpe (daily-resampled) | 0.00 | 5.73 | – |
| Max DD | 0.00% | 3.05% | – |
| Total trades closed | 0 | – | – |

## Tripwires

| Status | Signal | Context |
|---|---|---|
| · WATCH | Live Sharpe 0.00 | Threshold not yet binding (0 days, need 30+) |
| ✓ OK | Max DD 0.00% within tolerance | Backtest 3.05%, +1.6pp tolerance |
| · WATCH | Trade sample 0 too small | Need 20+ trades for distributional read |

## Daily equity curve

```
```

## Decision rules (from CLAUDE.md tripwires section)

Anchored to **HWM backtest expectation** (Sharpe 5.73, deployed live May 7 2026 PM). HWM bypasses the 1-bar polling delay artifact (see `trail-anchor-hwm.md`), so live should track backtest within noise.

- **Sharpe < 1.5 at 30 days → degraded.** Investigate execution (slippage, fills, stop behaviour, HWM tracking).
- **Sharpe < 3.0 at 60 days → degraded.** Stop adding capital; root-cause analysis.
- **Sharpe < 4.0 at 90 days → stop & investigate.** Real-money pilot blocked.
- **Win rate < 35% on 50+ trades → distributional shift.** Compare to backtest per-symbol win rates.
- **Avg-win/avg-loss < 1.3 → right tail collapsing.** Trailing-stop or K-exit may be clipping winners.
- **No |daily P&L|>0.5% day in 4+ weeks → swing days missing.** The strategy depends on these.
- **Single-day loss > 1.5% of equity → cluster correlation tighter live than backtest.**
