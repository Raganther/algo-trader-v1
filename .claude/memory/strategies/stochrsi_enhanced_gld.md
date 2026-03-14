# StochRSI Enhanced — GLD 15m (Best Edge)

> **Status:** VALIDATED (Sharpe 2.54, audited Feb 27) | Forward testing active — gld-test bot running on cloud
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

## Performance Summary (full audit Feb 27)

- **Full-period return (2020–Feb 2026):** 44.7%, **Max drawdown:** 0.69%, **Trades:** 710
- **2026 YTD (to Feb 27):** +1.16%, 21 trades
- **Sharpe:** 2.54 (computed from daily equity curve returns, annualised ×√252)
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
| 2026 (YTD) | +1.16% | — | 21 |

- Every year profitable. 2024 best (+7.90%), 2023 weakest full year (+4.44%).
- ~115 trades/year = ~9-10/month with validated params.

## Feb 27 Comprehensive Audit

### Data Quality

- **Source:** Alpaca IEX (free tier) — resampled 1m → 15m bars
- **Bar count:** 36,075 bars covering Jan 2020 – Feb 2026
- **Data continuity:** Gaps around major US holidays only — expected for IEX
- **Assessment:** Data quality sufficient. Resampling from 1m is standard practice, matches live execution.

### Parameter Sensitivity

| Variant | Return | Max DD | Trades | Notes |
|---|---|---|---|---|
| **Baseline (validated)** | **44.7%** | **0.69%** | **710** | **trail_atr=2.0** |
| trail_atr=1.5 | 47.5% | 0.71% | 696 | Tighter trail — more profit captured |
| trail_atr=2.5 | 41.8% | 0.68% | 714 | Looser trail — slightly worse |
| trail_after_bars=5 | 43.2% | 0.72% | 728 | Earlier activation, more trades |
| trail_after_bars=15 | 42.1% | 0.65% | 698 | Later activation, slightly worse |
| min_hold_bars=5 | 31.4% | 1.12% | 934 | **Large degradation** — confirms min_hold=10 is critical |
| min_hold_bars=15 | 40.8% | 0.58% | 604 | Marginally worse, fewer trades |
| OB=75, OS=20 | 43.5% | 0.71% | 742 | Minor change |

**Key finding:** Strategy is robust to most parameter changes. The `min_hold_bars=10` is the most important parameter — reducing to 5 causes significant degradation. Worth investigating `trail_atr=1.5` further.

### Spread Sensitivity

| Spread | Return | Still Profitable? |
|---|---|---|
| 0.0003 (baseline, ~$0.21) | 44.7% | ✓ |
| 0.0010 (~$0.70) | 39.2% | ✓ |
| 0.0020 (~$1.40) | 33.1% | ✓ |
| 0.0050 (~$3.50) | 18.4% | ✓ |
| 0.0010 + 0.0010 slippage | 33.8% | ✓ |
| 0.0022 (~breakeven) | ~0% | ✗ |

**Key finding:** Profitable up to ~0.22% spread. Real GLD market spread is ~0.01–0.03%. We have 7–20× headroom on transaction costs. Strategy is not sensitive to realistic slippage.

### Buy & Hold Comparison

| Metric | StochRSI Enhanced | Buy & Hold GLD |
|---|---|---|
| Total return (2020–2026) | +44.7% | +117.5% |
| Max drawdown | 0.69% | 22% |
| Sharpe | 2.54 | ~0.98 |
| In market | ~15% of time | 100% |
| Worst year | +3.27% (2020 partial) | -0.3% (2022) |

**Honest assessment:** Buy & Hold returned 2.6× more in absolute terms (2020–2026 was a gold bull run). However:
- Strategy max DD is 32× lower (0.69% vs 22%)
- Strategy Sharpe is 2.6× better (2.54 vs 0.98)
- Strategy is only in-market ~15% of the time — capital can be deployed elsewhere
- Strategy produces consistent returns in all market conditions; B&H returns are front-loaded to bull phases

This is a *risk-adjusted* edge, not a "beat gold" strategy. The real value is the low DD enabling aggressive position sizing and compounding.

### Key Risk

Gold is in a multi-year bull market (2020–2026: +117%). The mean reversion strategy **significantly underperforms buy & hold in trending markets**. If gold enters a bear market, the strategy's non-directional mean reversion edge should hold — but this has not been validated against a sustained gold bear.

## Bear Market Backtest (Daily, Feb 27 2026)

Tested on GLD daily bars (Stooq data, 2005–2019) to cover the 2011–2015 bear market (-45.6% peak to trough). Note: this uses daily bars, not 15m — fewer trades but directionally informative.

| Period | Strategy | Sharpe | DD | Trades | B&H |
|---|---|---|---|---|---|
| Bull 2007–2011 | +21.7% | 1.06 | 4.15% | 31 | +144% |
| 2012 (transition) | -0.6% | -0.54 | 1.41% | 3 | +3.9% |
| **2013 (bear yr 1)** | **+3.6%** | **1.07** | **0.89%** | **2** | **-28.8%** |
| **2014 (bear yr 2)** | **+1.2%** | **0.78** | **0.37%** | **3** | **-3.7%** |
| **2015 (bear yr 3)** | **+2.2%** | **1.43** | **0.57%** | **5** | **-11.1%** |
| 2016 (recovery) | +2.1% | 1.16 | 1.12% | 3 | +6.5% |
| **Full bear 2012–15** | **+6.0%** | **0.50** | **1.41%** | **20** | **-34.9%** |

**Key finding:** Strategy stayed positive through the entire bear market. B&H lost 34.9%; strategy made +6.0%. Every individual bear year was positive.

**Why it survives:** Strategy is in-market only ~15% of the time. It catches short bounces within the downtrend and exits flat — not holding through the decline. Most bear market losses happen while the strategy is in cash.

**Weakest period:** 2012 (-0.6%) — gold transitioning from bull to bear, choppy and indecisive. This is the hardest environment for mean reversion.

**Caveat:** Daily bars only — 15m would fire far more trades and face more micro stop-outs. Daily result is directionally encouraging but not a direct test of the live strategy. Next step: run 15m backtest on 2016–2019 as a proxy for post-bull conditions.

**Data:** `backend/data/gld_daily_2005_2019.csv` (Stooq, 3,737 daily bars)

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

## Profit Projections by Position Sizing

Using equity-proportional risk sizing (returns scale with capital):

| Risk per trade | €1,000 annual avg | €1,000 6yr total | Expected max DD |
|---|---|---|---|
| 2% (current default) | ~€70 | ~€430 | ~0.7% |
| 5% | ~€175 | ~€1,075 | ~1.7% |
| 10% | ~€350 | ~€2,150 | ~3.5% |
| 20% | ~€700 | ~€4,300 | ~7% |

Key insight: 0.69% max DD gives large headroom to increase position sizing safely. Even at 20% risk/trade, DD stays ~7%.

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
| **GLD** | **15m** | **+44.7% (2020–2026)** | **2.54** | **Best edge (audited)** |
| GLD | 1h | +18.3% ann | 1.44 | Validated |
| IAU | 1h | +11.6% ann | 1.22 | Validated |
| XLE | 1h | +11.1% ann | 1.11 | Validated |
| XBI | 1h | +9.0% ann | 0.90 | Sweep positive |
| TLT | 1h | +8.5% ann | 0.85 | Sweep positive |

## Long-Only Baseline (live constraint — Mar 14 2026)

Live bots run long-only — Alpaca rejects fractional short orders. This is the actual performance baseline for what the bots can execute today.

| Metric | Full Strategy | Long-Only |
|--------|--------------|-----------|
| Return (2020–2025) | +44.7% | +31.2% |
| Max Drawdown | 0.69% | 0.93% |
| Trades | ~710 | 467 |
| Win Rate | 43% | 45% |
| Sharpe (approx) | 2.54 | ~1.91 |

**Return drop:** -30%. **Sharpe drop:** 2.54 → ~1.91. Short trades contribute meaningfully — GLD is one of the assets where shorts add real alpha. Long-only is still a good strategy but materially weaker.

**Year-by-year (long-only):** 2020: +2.37% | 2021: +2.34% | 2022: +3.50% | 2023: +4.21% | 2024: +6.42% | 2025: +8.23%
All years profitable. Consistent upward trend.

**Implication:** Solving fractional short selling (whole-share sizing) is worth the effort for GLD. Live bots should not be considered equivalent to the validated 2.54 Sharpe strategy until shorts are enabled.

## Forward Testing Status (as of Mar 10 2026)

Running with aggressive test params (OB 60/OS 40, 3-bar hold/trail) to generate more trades faster for mechanics verification. All 4 bots (GLD, IAU, SLV, GDX) running simultaneously.

**Backtest prediction for test params (Dec 2025 – Mar 2026):** GLD +0.16%, 58 trades, 48% WR

**Mechanics confirmed:**
- [x] Bot-initiated exits (signal fires, stops cancelled, market sell placed)
- [x] Trailing stop UPDATE (ratchets up on each bar)
- [x] DAY TIF stop orders, position sync on restart, DB reconciliation

**Mechanics pending** (require specific market conditions to trigger):
- [ ] Server-side stop FIRING — Alpaca auto-executes stop between candles
- [ ] Trailing stop FIRING — price reverses through trail intrabar, Alpaca fills

## Next Steps

- [ ] Run 2-4 weeks forward testing, compare live results to backtest predictions
- [ ] Once mechanics verified: switch to validated params (OB 80/OS 15, trail 10, hold 10, skip Monday)
- [ ] Start real-money micro trading on Alpaca (€100-200, fractional GLD)
- [ ] Investigate trail_atr=1.5 (audit found +47.5% vs +43.0% — worth a full validation run)
- [ ] Explore increasing position sizing given very low DD headroom (0.69%)

---

*Last updated: 2026-03-14 (Long-only baseline added. Forward testing active, mechanics status updated. Feb 27 audit data unchanged.)*
