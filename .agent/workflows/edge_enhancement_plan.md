# Edge Enhancement Plan

> **Goal**: Squeeze better performance from validated edges (GLD 15m Sharpe 1.66, GLD 1h Sharpe 1.44) through targeted analysis and incremental improvements.

---

## Context

We have validated edges but they're running with default assumptions:
- **Fixed ATR stop** (no trailing, no time-based exit)
- **No time-of-day filtering** (trades all hours equally)
- **No volatility scaling** (same size regardless of conditions)
- **47% win rate** — room to improve with better filtering

The backtester currently **does not store** enough trade-level data for analysis. We need to enrich it first.

---

## Phase 1: Enrich Trade Records (~20 mins)

### Problem
PaperTrader's `trade_history` only stores: symbol, side, qty, entry price, exit price, PnL, exit timestamp (as bar index).

### Missing fields needed for analysis
| Field | Why |
|---|---|
| `entry_time` (datetime) | Time-of-day analysis |
| `exit_time` (datetime) | Trade duration |
| `entry_hour` (int) | Quick hour bucketing |
| `atr_at_entry` (float) | Volatility regime analysis |
| `exit_reason` (str) | "stop" vs "signal" — understand what's working |

### Implementation
- Add `entry_time` tracking to StochRSI strategy (store `row.name` at entry)
- Pass enriched metadata through to PaperTrader's trade record on close
- ~15 lines across `stoch_rsi_mean_reversion.py` and `paper_trader.py`

### Files to modify
- `backend/engine/paper_trader.py` — accept + store extra fields in trade_history
- `backend/strategies/stoch_rsi_mean_reversion.py` — capture and pass entry metadata

---

## Phase 2: Diagnostic Backtest + Analysis (~15 mins)

### Run single baseline backtest
Run GLD 15m with validated params (RSI 7, Stoch 14, OB 80, OS 15, ADX 20, ATR 2x) and dump all ~1,155 trades to CSV.

### Analysis slices

**Time-of-day:**
- Bucket trades by entry hour (ET)
- Calculate win rate + avg PnL per hour
- Identify dead zones (hours with negative expectancy)
- Look for golden hours (significantly above average)

**Day-of-week:**
- Win rate + PnL by day
- Monday (gap effects) vs mid-week vs Friday (position squaring)

**Volatility regime:**
- Bucket by ATR at entry (low/medium/high terciles)
- Does mean reversion work better in calm or volatile markets?

**Exit analysis:**
- What % of trades hit the ATR stop vs exit on signal?
- Avg PnL for stop exits vs signal exits
- Avg duration for winners vs losers

**Trade duration:**
- Histogram of bars held
- Do trades that haven't profited within N bars ever recover?

### Output
Markdown report with tables + clear directional findings. This tells us which enhancements are worth building.

---

## Phase 3: Build Targeted Enhancements (~30 mins each)

Only build what Phase 2 flags as promising. Possible enhancements:

### 3a. Time-of-Day Filter (trivial — 5 lines)
Add `trade_start_hour` and `trade_end_hour` params to strategy. Skip bars outside the window. `row.name.hour` already accessible.

### 3b. Exit Improvements (moderate — ~30 lines each)
- **Trailing ATR stop**: Move stop to entry price after N bars in profit, then trail at 2x ATR
- **Time-based exit**: Close trade if not profitable after N bars (cuts slow bleeders)
- **Partial profit-taking**: Close half at 1x ATR profit, trail remainder

### 3c. Volatility-Scaled Sizing (moderate — ~20 lines)
Scale position size inversely to ATR. Low vol = larger position (mean reversion is stronger). High vol = smaller position (more noise). Already have ATR calculated.

### 3d. Limit Order Entries (moderate — ~20 lines)
Place limit order slightly below close (for longs) instead of market order. Improves average entry by a few cents. Over 1,155 trades this compounds.

### 3e. News/Event Blackout (moderate — ~15 lines)
Skip entries around FOMC, NFP, CPI releases. Gold whipsaws on macro events. Could use a static calendar or external API.

---

## Phase 4: A/B Sweep (~10 mins compute)

### Method
- Baseline: GLD 15m Sharpe 1.66 (current validated params)
- Each enhancement tested independently vs baseline
- ~10-20 variants per enhancement
- Total: ~50-80 backtests
- Compare: Sharpe, win rate, max drawdown, total trades

### Sweep variants per enhancement
| Enhancement | Variants | Example params |
|---|---|---|
| Time filter | ~10 | Skip hour 9, skip hour 15, London only, NY only, overlap only |
| Trailing stop | ~10 | Trail after 5/10/15 bars, trail at 1.5x/2x/2.5x ATR |
| Time exit | ~8 | Close after 10/20/30/50 bars if unprofitable |
| Vol scaling | ~8 | Scale factor 0.5-2x, ATR lookback 10/20/50 |
| Limit offset | ~5 | 0.01%/0.02%/0.05%/0.1% below close |

### Scoring
Enhancement is a "win" if it improves Sharpe without significantly reducing trade count (<20% fewer trades). Improving win rate at the cost of fewer trades is fine if Sharpe goes up.

---

## Phase 5: Stack Winners (~15 mins)

Combine the 2-3 best individual enhancements. Test ~10 combinations. Validate the stacked version through the same holdout + walk-forward pipeline used in Phase 2 of the discovery engine.

---

## Time Estimate

| Phase | Effort | Compute |
|---|---|---|
| 1. Enrich trade records | 20 mins | 0 |
| 2. Diagnostic backtest + analysis | 15 mins | 10 sec |
| 3. Build enhancements (only flagged ones) | 30-90 mins | 0 |
| 4. A/B sweep | 10 mins | 10 mins |
| 5. Stack + validate | 15 mins | 5 mins |
| **Total** | **~2-3 hours** | **~15 mins** |

---

## Key Principles

1. **Analyse before building** — Phase 2 tells us what's worth doing
2. **One variable at a time** — isolate each enhancement's effect
3. **Compare to baseline** — everything measured against Sharpe 1.66
4. **Avoid overfitting** — validate stacked enhancements through walk-forward
5. **Minimum viable changes** — 5-30 lines per enhancement, not new frameworks

---

*Created: 2026-02-13*
*Status: Plan ready, waiting for validation run to complete before starting*
