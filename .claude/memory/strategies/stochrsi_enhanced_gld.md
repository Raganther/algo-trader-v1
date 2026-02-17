# StochRSI Enhanced — GLD 15m (Best Edge)

> **Status:** VALIDATED (Sharpe 2.42) | Paper testing with aggressive params | Not yet live
> **Strategy file:** `backend/strategies/stoch_rsi_mean_reversion.py`
> **Bot scripts:** `scripts/run_gld_test.sh`, `scripts/run_iau_test.sh`

## Validated Parameters

| Param | Value | Notes |
|---|---|---|
| RSI period | 7 | |
| Stoch period | 14 | |
| Overbought | 80 | |
| Oversold | 15 | Asymmetric — long-biased |
| ADX threshold | 20 | |
| ATR stop | 2x | |
| Trailing stop | 2x ATR after 10 bars | Key enhancement |
| Min hold | 10 bars | Filters noise trades |
| Skip days | Monday (0) | Near-zero edge day |

## Performance Summary

- **Full-period return:** 38.1%, **Max drawdown:** 0.7%, **Trades:** 465 over 5 years (2020-2025)
- **Holdout test:** Train +18.6% (Sharpe 2.27), Test +16.4% (Sharpe 2.69) — minimal degradation
- **Walk-forward:** 4/4 windows positive (100%), all years profitable
- **Multi-asset:** GLD +38%, SLV +92%, IAU +31% — generalises strongly
- **Previous baseline:** Sharpe 1.57, 664 trades, 1.2% DD — enhancements nearly doubled Sharpe

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

## Enhancement Verification Bots (deployed Feb 17)

Testing with aggressive params to generate more trades faster:

| Param | Aggressive (testing) | Validated (target) |
|---|---|---|
| OB / OS | 60 / 40 | 80 / 15 |
| ADX threshold | 50 | 20 |
| Trail after bars | 3 | 10 |
| Min hold | 3 | 10 |

- **gld-test:** GLD 15m — verifying trailing stop + min hold + skip Monday mechanics
- **iau-test:** IAU 15m — same params, tests on second gold ETF
- **gld-15m-enhanced:** STOPPED — will resume once enhancement mechanics are verified
- **Key lesson:** Two bots on same symbol conflict (Alpaca = one shared position per symbol)

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
| **GLD** | **15m** | **+38.1%** | **2.42** | **Best edge** |
| GLD | 1h | +18.3% ann | 1.44 | Validated |
| IAU | 1h | +11.6% ann | 1.22 | Validated |
| XLE | 1h | +11.1% ann | 1.11 | Validated |
| XBI | 1h | +9.0% ann | 0.90 | Sweep positive |
| TLT | 1h | +8.5% ann | 0.85 | Sweep positive |

## Next Steps

- [ ] Monitor gld-test + iau-test for correct trailing stop / min hold / skip Monday behaviour
- [ ] Once verified: switch to validated params (OB 80/OS 15, trail 10 bars, hold 10)
- [ ] Start real-money micro trading on Alpaca with EUR100-200 (fractional GLD)
- [ ] Apply trailing stop to other validated strategies (GLD 1h, IAU, XLE, SLV)
- [ ] Position sizing / Kelly criterion with Sharpe 2.42 and DD 0.7%

---

*Last updated: 2026-02-17*
