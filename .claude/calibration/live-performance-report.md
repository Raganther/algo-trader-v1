Status: current | Epistemic: live observation | Last refreshed: 2026-05-07 18:56 UTC

# Live Performance Report

Live forward-test on 7-bot lineup, deployed Apr 15-16 (metals four) + Apr 28 (energy/biotech three). Re-run with `python3 -m backend.analysis.live_performance_report`.

## Headline metrics (Apr 15 → today)

| Metric | Live | Backtest expectation | Status |
|---|---:|---:|---|
| Trading days | 15 | – | – |
| Equity start → end | $97,882 → $96,804 | – | – |
| Cumulative return | -1.10% | +1.90% | – |
| Sharpe (daily-resampled) | -1.62 | 4.25 | – |
| Max DD | 2.75% | 3.41% | – |
| Total trades closed | 30 | – | – |
| Win rate | 20.0% | 41–47% | – |
| Avg win / avg loss | 2.24 | ≥1.3 | – |
| Total realised P&L | $-1,569.96 | – | – |
| Stop-exit % | 76.7% | – | – |

## Tripwires

| Status | Signal | Context |
|---|---|---|
| · WATCH | Live Sharpe -1.62 | Threshold not yet binding (15 days, need 30+) |
| ✓ OK | Max DD 2.75% within tolerance | Backtest 3.41%, +1.6pp tolerance |
| ⚠ WARN | Win rate 20.0% < 35% | Backtest 41–47% |
| ✓ OK | Avg-win/avg-loss 2.24 ≥ 1.3 | Right tail intact |
| ✓ OK | Big-day rate 2.7/8d | Backtest expects ~1/8d |

## Per-symbol breakdown

| Symbol | Trades | P&L | Wins |
|---|---:|---:|---:|
| GLD | 7 | $-423.60 | 1 |
| IAU | 4 | $-195.52 | 0 |
| SLV | 7 | $+957.18 | 4 |
| GDX | 2 | $-327.51 | 0 |
| OIH | 6 | $-733.11 | 1 |
| XBI | 2 | $-548.15 | 0 |
| XOP | 2 | $-299.25 | 0 |

## Daily equity curve

```
  2026-04-16  $ 97,882.10
  2026-04-17  $ 97,636.74
  2026-04-18  $ 99,094.47
  2026-04-21  $ 97,942.51
  2026-04-22  $ 97,942.51
  2026-04-23  $ 97,867.65
  2026-04-24  $ 96,848.37
  2026-04-25  $ 97,206.50
  2026-04-28  $ 97,046.95
  2026-04-29  $ 97,724.31
  2026-04-30  $ 97,865.19
  2026-05-01  $ 97,835.63
  2026-05-02  $ 97,395.72
  2026-05-05  $ 97,395.72
  2026-05-06  $ 96,365.83
  2026-05-07  $ 96,803.77
```

## Decision rules (from CLAUDE.md tripwires section)

Anchored to **live-realistic expectation** (backtest Sharpe 4.95 − 0.7 delay artifact = ~4.25 expected). See `live-vs-backtest-iau-diagnostic.md` for the 0.7 derivation.

- **Sharpe < 0.5 at 30 days → degraded.** Investigate execution (slippage, fills, stop behaviour).
- **Sharpe < 1.5 at 60 days → degraded.** Stop adding capital; root-cause analysis.
- **Sharpe < 2.0 at 90 days → stop & investigate.** Real-money pilot blocked.
- **Win rate < 35% on 50+ trades → distributional shift.** Compare to backtest per-symbol win rates.
- **Avg-win/avg-loss < 1.3 → right tail collapsing.** Trailing-stop or K-exit may be clipping winners.
- **No |daily P&L|>0.5% day in 4+ weeks → swing days missing.** The strategy depends on these.
- **Single-day loss > 1.5% of equity → cluster correlation tighter live than backtest.**
