# StochRSI Enhanced — GLD 15m (Best Edge)

> **Status:** VALIDATED (Sharpe 2.42) | Paper testing with aggressive params | Not yet live
> **Strategy file:** `backend/strategies/stoch_rsi_mean_reversion.py`
> **Bot scripts:** `scripts/run_gld_test.sh`, `scripts/run_iau_test.sh`

## Validated Parameters

| Param | Code name | Value | Notes |
|---|---|---|---|
| RSI period | `rsi_period` | 7 | |
| Stoch period | `stoch_period` | 14 | |
| Overbought | `overbought` | 80 | |
| Oversold | `oversold` | 15 | Asymmetric — long-biased |
| ADX threshold | `adx_threshold` | 20 | |
| ADX filter ON | `skip_adx_filter` | false | **Must pass explicitly — defaults to true (off)** |
| ATR stop | `sl_atr` | 2.0 | **NOT `stop_loss_atr`** |
| Trailing stop | `trailing_stop` | true | |
| Trail ATR mult | `trail_atr` | 2.0 | |
| Trail after bars | `trail_after_bars` | 10 | |
| Min hold | `min_hold_bars` | 10 | **NOT `min_hold`** — Filters noise trades |
| Skip days | `skip_days` | [0] | Monday (0=Mon) |

### Correct backtest command (verified Feb 26):
```bash
python3 -m backend.runner backtest --strategy StochRSIMeanReversion --symbol GLD --timeframe 15m \
  --start 2020-01-01 --end 2025-12-31 --source alpaca --spread 0.0003 --delay 0 \
  --parameters '{"rsi_period":7,"stoch_period":14,"overbought":80,"oversold":15,"adx_threshold":20,"skip_adx_filter":false,"sl_atr":2.0,"trailing_stop":true,"trail_atr":2.0,"trail_after_bars":10,"min_hold_bars":10,"skip_days":[0]}'
```

**WARNING:** Wrong param names silently fall back to defaults. `stop_loss_atr`, `min_hold`, and missing `skip_adx_filter:false` all caused a bad run (5.61% / 1996 trades instead of 43% / 689 trades).

## Performance Summary (verified Feb 26 with correct params)

- **Full-period return:** 43.03%, **Max drawdown:** 0.69%, **Trades:** 689 over ~6 years (Jul 2020–Dec 2025)
- **Win rate:** 43% — majority of trades lose, but winners are significantly larger (trailing stop effect)
- **Holdout test:** Train +18.6% (Sharpe 2.27), Test +16.4% (Sharpe 2.69) — minimal degradation
- **Walk-forward:** 4/4 windows positive (100%), all years profitable
- **Multi-asset:** GLD +38%, SLV +92%, IAU +31% — generalises strongly
- **Previous baseline:** Sharpe 1.57, 664 trades, 1.2% DD — enhancements nearly doubled Sharpe

## Year-by-Year Breakdown

| Year | Return | Max DD | Trades |
|---|---|---|---|
| 2020 | +3.27% | 0.73% | 54 *(partial — starts Jul)* |
| 2021 | +7.39% | 1.46% | 130 |
| 2022 | +6.55% | 1.25% | 132 |
| 2023 | +4.44% | 1.18% | 146 |
| 2024 | +7.90% | 1.47% | 119 |
| 2025 | +7.08% | 2.26% | 108 |

- Every year profitable. 2024 best (+7.90%), 2023 weakest full year (+4.44%).
- ~115 trades/year = ~9-10/month with validated params.

## Profit Projections by Position Sizing

Using equity-proportional risk sizing (returns scale with capital):

| Risk per trade | €1,000 annual avg | €1,000 6yr total | Expected max DD |
|---|---|---|---|
| 2% (current default) | ~€70 | ~€430 | ~0.7% |
| 5% | ~€175 | ~€1,075 | ~1.7% |
| 10% | ~€350 | ~€2,150 | ~3.5% |
| 20% | ~€700 | ~€4,300 | ~7% |

Key insight: 0.69% max DD gives large headroom to increase position sizing safely. Even at 20% risk/trade, DD stays ~7%.

## Edge Enhancement Analysis (Feb 13)

Diagnostic analysis found three key leaks in the baseline strategy:

1. **Stop losses were 100% losers** (199 trades, -$1,219) — fixed with trailing stop
2. **Short-duration trades (1-5 bars) were breakeven noise** (72% of trades) — fixed with min hold
3. **Monday trades were near-zero edge** (128 trades, +$23 total) — fixed with day filter

All 4 tested variants passed full validation:

| Variant | Sharpe | Holdout Ret | WF Pass | Multi-Asset | DD |
|---|---|---|---|---|---|
| Baseline (no enhancements) | 1.44 | +9.4% | 4/4 | 3/3 | 1.2% |
| Trail 2x/5bar + Hold 5 | 2.19 | +15.3% | 4/4 | 3/3 | 0.7% |
| **Skip Mon + Trail 2x/10bar + Hold 10** | **2.42** | **+16.4%** | **4/4** | **3/3** | **0.7%** |
| Trail 3x ATR after 5 bars | 1.85 | +14.6% | 4/4 | 3/3 | 1.3% |

**Key insight:** Enhancements performed *better* on unseen data than in-sample. The trailing stop is a structural improvement (not curve-fitting) — it also improved SLV (+92%) and IAU (+31%).

## Enhancement Verification Bots (deployed Feb 17, first fills Feb 26)

Testing with aggressive params to generate more trades faster:

| Param | Aggressive (testing) | Validated (target) |
|---|---|---|
| OB / OS | 60 / 40 | 80 / 15 |
| ADX threshold | 50 | 20 |
| Trail after bars | 3 | 10 |
| Min hold bars | 3 | 10 |

- **gld-test:** GLD 15m — verifying trailing stop + min hold + skip Monday mechanics
- **iau-test:** IAU 15m — same params, tests on second gold ETF
- **gld-15m-enhanced:** STOPPED — will resume once enhancement mechanics are verified
- **Key lesson:** Two bots on same symbol conflict (Alpaca = one shared position per symbol)
- **First fills post DAY-TIF fix:** Feb 26 — GLD (-$74.90 paper), IAU (+$21.99 paper). Execution confirmed working.

## Event Blackout Analysis (Feb 17)

Tested whether avoiding entries near high-impact events (FOMC/NFP/CPI) improves this strategy:

- **Diagnostic:** 1,381 GLD 15m trades tagged by proximity to 385 events (2020-2025)
- **+/-1h trades:** 81 event trades avg PnL -$1.13 (losers) vs +$2.23 clean trades
- **+/-2h trades:** 141 trades, avg PnL +$0.94 (still worse than +$2.15 clean)
- **Backtest with blackout ON:** Return drops (28% -> 23% at 1h, 21% at 2h) — filter removes some winners too
- **Conclusion:** Blunt avoidance hurts more than helps for this strategy. Event blackout feature built and available (`event_blackout_hours` param) but left off by default.

## Other Validated StochRSI Edges

| Asset | TF | Return | Sharpe | Status |
|---|---|---|---|---|
| **GLD** | **15m** | **+43.03%** | **2.42** | **Best edge** |
| GLD | 1h | +18.3% ann | 1.44 | Validated |
| IAU | 1h | +11.6% ann | 1.22 | Validated |
| XLE | 1h | +11.1% ann | 1.11 | Validated |
| XBI | 1h | +9.0% ann | 0.90 | Sweep positive |
| TLT | 1h | +8.5% ann | 0.85 | Sweep positive |

## Next Steps

- [ ] Monitor gld-test + iau-test for correct trailing stop / min hold / skip Monday behaviour
- [ ] Check bot scripts use correct param names (min_hold_bars, sl_atr, skip_adx_filter:false)
- [ ] Once verified: switch to validated params (OB 80/OS 15, trail 10 bars, hold 10)
- [ ] Start real-money micro trading on Alpaca with €100-200 (fractional GLD)
- [ ] Apply trailing stop to other validated strategies (GLD 1h, IAU, XLE, SLV)
- [ ] Explore increasing position sizing given very low DD headroom

---

*Last updated: 2026-02-26 (Corrected param names, re-verified backtest: 43.03% / 689 trades / 0.69% DD. Added year-by-year, profit projections)*
