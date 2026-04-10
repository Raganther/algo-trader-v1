Status: current | Epistemic: confirmed | Last verified: 2026-04-10

# Regime Analysis — Algo Trader V1

> **Purpose:** Market regime classification, statistics, and implications for strategy sizing and risk management.
> Read when: designing regime-aware sizing, interpreting live performance, planning regime-gated enhancements.

---

## What is a Regime?

A market regime is the prevailing character of price action over a sustained period. Four regimes defined:

| Regime | Definition | Strategy implication |
|--------|-----------|---------------------|
| RANGING | ADX < 25, ATR normal | Ideal — mean reversion works cleanly |
| TRENDING_UP | ADX > 25, close > 200 SMA | Tradeable long-only — bounces cleaner in uptrend |
| TRENDING_DOWN | ADX > 25, close ≤ 200 SMA | Dangerous long-only — oversold often means continuation |
| HIGH_VOL | ATR > 1.5× its 50-bar rolling mean | Avoid or halve size — slippage spikes, stops fire on noise |

HIGH_VOL takes priority over TRENDING — a volatile trending session is classified HIGH_VOL.

---

## Implementation

- **Module:** `backend/indicators/regime.py` — `classify_regime(df)` takes OHLC DataFrame, returns Series of regime labels. `regime_stats(regimes)` computes duration statistics.
- **Data:** Daily bars stored in `price_data_daily` table in `research.db`. Fetch with: `python scripts/fetch_price_data.py --timeframe 1d --symbols GLD,IAU,SLV,GDX --start 2020-01-01`
- **Analysis script:** `python scripts/analyse_regimes.py` — runs classifier, prints overall distribution, year-by-year breakdown, and transition matrix.
- **Parameters:** ADX period 14, SMA period 200, ATR period 14, ADX threshold 25, ATR vol lookback 50 bars, ATR vol multiplier 1.5×.

---

## Findings — GLD/IAU/SLV/GDX Daily (Jul 2020 – Apr 2026)

*Note: Alpaca data starts 2020-07-27. 2020 shows 100% RANGING because fewer than 200 bars existed for SMA(200) to initialise — treat 2020 as incomplete.*

### Overall regime distribution (5.5 years)

| Symbol | RANGING% | TRENDING_UP% | HIGH_VOL% | TRENDING_DOWN% |
|--------|----------|-------------|-----------|----------------|
| GLD | 68.0% | 21.4% | 6.6% | 4.0% |
| IAU | 66.1% | 23.2% | 7.6% | 3.1% |
| SLV | 71.9% | 15.8% | 4.9% | 7.5% |
| GDX | 71.8% | 18.8% | 3.0% | 6.4% |

**The dominant regime is RANGING — 66–72% of all trading days.** The strategy is a mean-reversion strategy designed for ranging markets. This is the structural reason the backtest Sharpe is 2.47 — not luck, alignment.

### Average regime duration (trading days)

| Symbol | RANGING avg | RANGING max | TRENDING_UP avg | HIGH_VOL avg |
|--------|------------|------------|----------------|-------------|
| GLD | 44.3 | 205 | 11.8 | 9.4 |
| IAU | 41.2 | 207 | 11.9 | 8.4 |
| SLV | 68.7 | 206 | 18.8 | 14.0 |
| GDX | 41.2 | 199 | 11.7 | 10.8 |

Ranging periods last a long time — average 41–69 days, max over 200 days. Trending and volatile regimes are shorter — averaging 9–19 days before resolving. This means: once a regime flip occurs, it typically resolves back to ranging within 2–3 weeks.

### Year-by-year regime distribution — GLD

| Year | RANGING% | UP% | DOWN% | HIGH_VOL% |
|------|----------|-----|-------|-----------|
| 2021 | 86.5% | 7.5% | 6.0% | 0.0% |
| 2022 | 72.9% | 5.2% | 15.1% | 6.8% |
| 2023 | 58.8% | 36.0% | 2.0% | 3.2% |
| 2024 | 58.3% | 36.5% | 0.0% | 5.2% |
| 2025 | 58.4% | 25.2% | 0.0% | 16.4% |
| 2026 | 32.8% | 44.8% | 0.0% | 22.4% |

**Key pattern:** TRENDING_UP barely existed before 2023, then became the dominant non-ranging regime. 2026 is already 44.8% TRENDING_UP and 22.4% HIGH_VOL — the most extreme year in the dataset. The live forward test is running in the strongest bull + highest volatility environment of the entire 6-year window.

### Transition matrix — GLD (% probability on regime exit)

| From → | TRENDING_UP | TRENDING_DOWN | HIGH_VOL | RANGING |
|--------|------------|--------------|---------|---------|
| RANGING | 71.4% | 23.8% | 4.8% | — |
| TRENDING_UP | — | 15.4% | 34.6% | 50.0% |
| TRENDING_DOWN | 44.4% | — | 0.0% | 55.6% |
| HIGH_VOL | 70.0% | 0.0% | — | 30.0% |

IAU/SLV/GDX transition matrices are similar — available via `python scripts/analyse_regimes.py`.

**Key transitions:**
- RANGING ends → TRENDING_UP 57–71% of the time across all symbols. When ranging breaks, it's more likely to break upward than downward.
- HIGH_VOL ends → TRENDING_UP 40–70% of the time. Volatility spikes tend to precede sustained upward moves in precious metals.
- TRENDING_UP ends → back to RANGING ~50% of the time. Uptrends resolve more often than they reverse directly.

---

## Implications for Strategy

### 1. Regime confirms structural edge

68–72% RANGING is the foundation of Sharpe 2.47. The ADX filter already partially gates on this, but the regime classifier quantifies it explicitly and enables more granular control.

### 2. Regime-dependency explains live performance

2024–2025 are the most TRENDING_UP years in the dataset. Long-only mean reversion in a bull uptrend = oversold bounces are cleaner and more frequently profitable. The live +K-exit win rate of 76% is consistent with operating in the most favourable regime historically. This is not evidence the edge disappears in other regimes — but it may be weaker.

### 3. HIGH_VOL is the regime to protect against

- 2026 HIGH_VOL is 22% for GLD/GDX — well above the historical 3–7% average
- The two largest slippage outliers in the live dataset (-$0.297, -$0.140) both occurred on high-volatility days
- TS exits cluster on high-volatility days — tight trail fires on noise
- Action: halve position size or skip entries during HIGH_VOL regime

### 4. TRENDING_DOWN is rare but dangerous for long-only

- Only 3–7% of days historically, and nearly absent since 2023
- In a downtrend, oversold often means momentum continuation, not reversal
- Action: skip entries or reduce to 0.5% risk during TRENDING_DOWN

### 5. Regime duration as a real-time risk signal

Current ranging period length vs historical average tells you where you are in the cycle:
- Young ranging (< avg duration): low risk of flip, full size
- Old ranging (> avg duration): statistically overdue, reduce size
- Very old ranging (> 2× avg duration): elevated flip risk, further reduce

Average ranging duration is 41–69 bars — a new ranging period has typically 6–10 weeks of runway before flip risk rises meaningfully.

### 6. Post-HIGH_VOL transition as a supplementary signal

HIGH_VOL → TRENDING_UP 70% of the time for GLD. The first bars of a new uptrend after a volatility spike are often strong. This could be a supplementary entry signal for a trend-following variant alongside the mean-reversion strategy. Speculative — requires backtesting before use.

---

## Regime-Aware Sizing Framework (proposed — not yet implemented)

| Regime | Regime age | Proposed risk per trade |
|--------|-----------|------------------------|
| RANGING | < avg duration | 2.0% (full) |
| RANGING | > avg duration | 1.5% |
| TRENDING_UP | Any | 1.5% |
| TRENDING_DOWN | Any | 0.5% or skip |
| HIGH_VOL | Any | 0.5% or skip |

This works alongside correlation-aware sizing — the two are independent dimensions. Correlation sizing controls how much risk is taken across simultaneous positions; regime sizing controls how much risk is taken in any given market environment.

**Implementation path:**
1. Regime classifier already built (`backend/indicators/regime.py`)
2. Live regime detection: run classifier on most recent N daily bars at session start, read current regime and duration
3. Pass regime context into position sizing function in `live_broker.py`
4. Backtest integration: tag each trade with entry regime, compute per-regime P&L — validates the sizing rationale before deploying live

---

## Post-Apr-20 Test Plan — Regime-Aware Sizing Backtest

### What we're testing
Fixed 2% risk on every trade vs dynamic sizing based on regime at entry. If regime-sized Sharpe > baseline with similar or lower drawdown, regime information is adding real value.

### Three pieces to build

**1. Regime state lookup**
The classifier already produces daily regime labels. For each 15m bar in the backtest, look up the corresponding daily bar's regime label and duration (how many consecutive days in the current regime). This is a join: 15m bar timestamp → daily bar date → regime label + age.

**2. Sizing function**
Takes `(regime, regime_age, avg_duration)` → returns a risk multiplier. Starting point:

| Regime | Age condition | Risk multiplier |
|--------|--------------|----------------|
| RANGING | age < avg_duration | 1.0× (full) |
| RANGING | age > avg_duration | 0.75× |
| TRENDING_UP | any | 0.75× |
| TRENDING_DOWN | any | 0.25× or skip |
| HIGH_VOL | any | 0.25× or skip |

Exact thresholds are parameters — the backtest tests different values to find what adds most value.

**3. Portfolio-level backtest runner**
Run all 4 symbols simultaneously on a shared timeline, apply the sizing function at each entry, aggregate P&L across all symbols. This is the same shared-timeline runner needed for the correlation analysis — one build unlocks both. This is the critical dependency.

### Comparison matrix
Run all variants over the same 5-year window with validated params:

| Config | Expected outcome |
|--------|-----------------|
| Fixed 2% all regimes | Baseline |
| Regime-sized (proposed multipliers) | Higher Sharpe if regime info adds value |
| Regime-sized + skip HIGH_VOL | Lower trade count, potentially better risk-adjusted return |
| Regime-sized + skip TRENDING_DOWN | Minimal impact — TRENDING_DOWN is rare (3–7% of days) |
| Regime age only (no skip) | Tests whether duration signal alone adds value |

### Sequencing
1. Apr 20 calibration — confirms backtest engine is accurate (gate for all of the above)
2. Build shared-timeline portfolio runner — needed for correlation analysis and regime backtest (same piece of work)
3. Add regime lookup to runner — join 15m bars to daily regime labels at each entry bar
4. Run comparison matrix — fixed vs regime-sized across all 4 symbols

Steps 2 and 3 are approximately one day each. Step 4 is just running the script.

### What success looks like
- Regime-sized Sharpe meaningfully higher than baseline on the same 5-year window
- Drawdown reduced in HIGH_VOL and TRENDING_DOWN years (2022, 2026)
- Trade count reduction in skip-regime variants is acceptable (not too many missed trades)
- Results consistent across all 4 symbols — not just GLD

### The honest limit
The classifier is a rear-view mirror — it confirms a regime after it starts, not before. The edge is rapid adaptation: as soon as the classifier detects a regime change, sizing adjusts immediately. The backtest will show whether that adaptation is fast enough to matter or whether the regime lag (daily bars updating once per day) blunts the signal.

---

## Open Questions

- **Per-regime strategy performance** — need to run the validated params backtest, tag each trade with the daily regime at entry, and compute win rate / Sharpe / avg P&L per regime. This validates the sizing framework empirically rather than theoretically.
- **15m micro-regime vs daily macro-regime** — current classifier operates on daily bars. A 15m regime layer (intraday ranging vs trending) may add further signal. Whether the two layers are independent or redundant is unknown — test post-calibration.
- **Regime-aware backtesting** — the full value of regime sizing requires a backtest that applies dynamic sizing rules based on real-time regime state. This is the portfolio backtester with regime overlay — a significant but high-value build.
- **SLV 2026 anomaly** — SLV shows 49% HIGH_VOL in 2026 vs 22% for GLD. Silver is more volatile than gold in absolute terms; the fixed ATR multiplier (1.5×) may be classifying normal SLV volatility as HIGH_VOL. Consider symbol-specific ATR thresholds or normalising ATR as % of price.
