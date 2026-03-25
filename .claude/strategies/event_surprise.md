# EventSurprise — Economic Data Surprise Trading

> **Status:** BUILT, initial backtest positive, not yet paper tested
> **Strategy file:** `backend/strategies/event_surprise.py`
> **Bot script:** `scripts/run_event_surprise_test.sh`
> **Diagnostic scripts:** `backend/scripts/event_surprise_analysis.py`, `backend/scripts/event_surprise_gaps.py`

## Concept

Trade GLD based on economic data surprise direction. When key releases (CPI, NFP, Unemployment) show significant surprises vs forecast, enter in the implied gold direction with delayed entry and time-based exit.

## Research Findings (Feb 17)

### Gap Analysis (event_surprise_gaps.py) — 5 investigations:

**1. Entry Timing — Post-bar move is tradeable:**
- CPI miss -> gold UP: **+0.80% avg 1h move** with delayed entry (enter 15min after event bar closes)
- **93% correct direction** at 1h window
- Post-bar move is NOT front-loaded in the event bar — the move develops AFTER
- Even at 10x spread (0.30%), the expected move covers costs

**2. Co-release deduplication:**
- NFP + Unemployment release simultaneously — must dedup
- CPI m/m + CPI y/y + Core CPI release together — pick largest |surprise|
- After dedup: still sufficient sample (62 unique moments with all events)

**3. Stop sizing (Max Adverse Excursion):**
- A 0.5% stop survives ~80% of CPI trades within the 1h window
- Tighter stops (0.2-0.3%) get stopped out too often

**4. Signal strength by event type:**

| Event | Direction | Avg 1h Move | Correct % | Strength |
|---|---|---|---|---|
| CPI miss | Gold UP | +0.80% | 93% | Strong |
| NFP beat | Gold DOWN | +0.37% | 55% | Weak |
| Unemployment miss | Gold DOWN | +0.52% | 64% | Moderate |

**5. Beat vs Miss asymmetry:**
- Misses (actual < forecast) produce cleaner, more directional moves
- Beats are noisier — `trade_beats=False` by default

## Direction Mapping

| Event | Beat (actual > forecast) | Miss (actual < forecast) |
|---|---|---|
| CPI m/m, CPI y/y | Gold DOWN (hawkish) | Gold UP (dovish) |
| NFP | Gold DOWN (strong jobs) | Gold UP (weak jobs) |
| Unemployment Rate | Gold UP (higher = bad for USD) | Gold DOWN (lower = good for USD) |

## Strategy Parameters

| Param | Default | Description |
|---|---|---|
| `event_types` | `["CPI m/m", "CPI y/y"]` | Which events to trade |
| `surprise_threshold` | `0.5` | Min |surprise| as multiple of that event type's std |
| `hold_bars` | `4` | Bars to hold after entry (4 = 1h on 15m TF) |
| `stop_pct` | `0.5` | Stop loss % from entry |
| `entry_delay` | `1` | Bars to wait after event bar before entering |
| `risk_pct` | `0.02` | Fraction of equity to risk per trade |
| `trade_beats` | `false` | Whether to also trade beat surprises (weaker signal) |
| `dedup_minutes` | `5` | Co-release dedup window |

## Backtest Results (Feb 17)

### CPI-only (misses only — strongest signal):
```
Return: 2.36%, Max DD: 0.13%, Trades: 14, Win Rate: 86%
```
- 15 tradeable events from 54 unique CPI moments (2020-2025)
- All entries are LONG gold on CPI misses
- Very high win rate but low trade frequency (~3/year)

### All events (CPI + NFP + Unemployment, beats + misses):
```
Return: 2.95%, Max DD: 1.10%, Trades: 58, Win Rate: 48%
```
- 62 tradeable events from 103 unique moments
- Mix of long and short entries
- More trades but lower win rate — beats dilute the signal

### Yearly breakdown (CPI-only):
| Year | Return | DD | Trades |
|---|---|---|---|
| 2021 | +0.08% | 0.02% | 1 |
| 2022 | +1.10% | 0.11% | 3 |
| 2023 | +0.58% | 0.08% | 5 |
| 2024 | +0.46% | 0.15% | 4 |
| 2025 | +0.11% | 0.00% | 1 |

## How It Works (Technical)

1. **`__init__`:** Loads events via `DataLoader.fetch_economic_events()`, matches each event to GLD bar indices using bisect, deduplicates co-releases (5min window, keeps largest |surprise|), classifies surprises using per-event-type std threshold, builds `event_schedule: {bar_index: event_info}`
2. **`on_bar`:** Checks stop loss (priority) -> time-based exit (hold_bars) -> new entry (if current bar is in event_schedule). Position sizing: risk_pct * equity / stop_distance, capped at 25% equity.
3. **Events pre-matched to bars** — no runtime event processing needed. Strategy is self-contained (loads its own event data from CSV).

## Backtest Commands

```bash
# CPI-only (strongest signal)
python3 -m backend.runner backtest --strategy EventSurprise --symbol GLD --timeframe 15m \
  --start 2020-01-01 --end 2025-12-31 --source alpaca --spread 0.0003 --delay 0 \
  --parameters '{"event_types":["CPI m/m","CPI y/y"],"hold_bars":4,"stop_pct":0.5,"entry_delay":1}'

# All events
python3 -m backend.runner backtest --strategy EventSurprise --symbol GLD --timeframe 15m \
  --start 2020-01-01 --end 2025-12-31 --source alpaca --spread 0.0003 --delay 0 \
  --parameters '{"event_types":["CPI m/m","CPI y/y","Non-Farm Employment Change","Unemployment Rate"],"hold_bars":4,"stop_pct":0.5,"entry_delay":1,"trade_beats":true}'
```

## Next Steps

- [ ] Paper test on cloud (CPI-only config) — `scripts/run_event_surprise_test.sh`
- [ ] Test wider hold windows (hold_bars=8 for 2h, hold_bars=16 for 4h) — diagnostic showed moves continue
- [ ] Test on SLV/IAU (gold-correlated ETFs) — should show similar CPI sensitivity
- [ ] Explore FOMC rate decisions as additional event type
- [ ] Consider combining with StochRSI — event surprise as entry filter for existing strategy
- [ ] Explore actual vs forecast surprise magnitude for position sizing (larger surprise = larger position)

---

*Last updated: 2026-02-17 (Strategy built, initial backtests run)*
