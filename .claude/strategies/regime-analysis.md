Status: current | Epistemic: confirmed | Last verified: 2026-04-11

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
- **Data:** Daily bars stored in `price_data_daily` table in `research.db`. Two sources merged: Yahoo Finance (GLD from Nov 2004, IAU from Jan 2005, SLV/GDX from Apr–May 2006) and Alpaca IEX (Jul 2020 onward). Alpaca is authoritative for the overlap period — Yahoo rows deleted where Alpaca rows exist for the same date. To extend/refresh: `python3 scripts/fetch_price_data_yfinance.py` (Yahoo, full history) or `python scripts/fetch_price_data.py --timeframe 1d --symbols GLD,IAU,SLV,GDX --start 2020-01-01` (Alpaca, recent only).
- **Analysis script:** `python scripts/analyse_regimes.py` — runs classifier, prints overall distribution, year-by-year breakdown, and transition matrix.
- **Parameters:** ADX period 14, SMA period 200, ATR period 14, ADX threshold 25, ATR vol lookback 50 bars, ATR vol multiplier 1.5×.

---

## Findings — GLD/IAU/SLV/GDX Daily (2004–2026)

*Extended dataset: Yahoo Finance back to ETF inception (GLD Nov 2004, IAU Jan 2005, SLV/GDX Apr–May 2006) merged with Alpaca from Jul 2020. 2091 daily bars per symbol. SMA(200) requires 200 bars to initialise — early years (2004–2005 for GLD, earlier for others) show inflated RANGING% as a result; treat pre-2007 as partially unreliable for regime distribution but valid for transition statistics once SMA is initialised.*

### Overall regime distribution (~20 years)

| Symbol | Bars | RANGING% | TRENDING_UP% | TRENDING_DOWN% | HIGH_VOL% |
|--------|------|----------|-------------|----------------|-----------|
| GLD | 2091 | 58.9% | 27.6% | 7.8% | 5.7% |
| IAU | 2091 | 60.4% | 28.8% | 3.1% | 7.7% |
| SLV | 2091 | 62.8% | 21.5% | 11.2% | 4.5% |
| GDX | 2091 | 79.6% | 11.2% | 3.4% | 5.8% |

**RANGING remains dominant at 59–80%.** GDX is structurally more ranging than the others (79.6%) — its trend regimes are shorter and less frequent. SLV has the highest TRENDING_DOWN exposure (11.2%) reflecting silver's higher volatility and sharper bear cycles.

### Average regime duration (trading days)

| Symbol | RANGING avg | RANGING max | TRENDING_UP avg | HIGH_VOL avg |
|--------|------------|------------|----------------|-------------|
| GLD | 36.2 | 244 | 17.0 | 9.2 |
| IAU | 43.6 | 199 | 18.8 | 10.0 |
| SLV | 38.6 | 199 | 15.0 | 11.8 |
| GDX | 87.6 | 230 | 13.0 | 17.3 |

GDX ranging periods average 87 days — more than double the others. This reflects its structurally different character as a mining equity: it spends long stretches consolidating and has shorter, sharper trend episodes. HIGH_VOL periods are short across all symbols (9–17 days avg) — they resolve quickly.

### Year-by-year regime distribution — GLD

| Year | RANGING% | UP% | DOWN% | HIGH_VOL% |
|------|----------|-----|-------|-----------|
| 2020 | 95.6% | 0.7% | 3.7% | 0.0% |
| 2021 | 60.4% | 11.2% | 28.4% | 0.0% |
| 2022 | 66.2% | 14.2% | 13.4% | 6.2% |
| 2023 | 35.8% | 57.6% | 1.2% | 5.4% |
| 2024 | 60.2% | 34.2% | 0.0% | 5.6% |
| 2025 | 49.0% | 38.2% | 0.0% | 12.8% |
| 2026 | 30.4% | 46.4% | 6.2% | 17.0% |

*2020 shows 95.6% RANGING because SMA(200) was still initialising on the Alpaca dataset (data starts Jul 2020, only ~130 bars by year end). Treat 2020 as unreliable for regime distribution.*

**Key pattern:** TRENDING_DOWN dominated 2021 (gold gave back COVID gains). TRENDING_UP emerged strongly from 2023 onward as the metals bull began. 2026 is the most extreme year — 46.4% TRENDING_UP and 17.0% HIGH_VOL simultaneously, driven by the Iran conflict macro event.

### Transition matrices (% probability on regime exit)

**GLD:**

| From → | TRENDING_UP | TRENDING_DOWN | HIGH_VOL | RANGING |
|--------|------------|--------------|---------|---------|
| RANGING | 64.7% | 32.4% | 2.9% | — |
| TRENDING_UP | — | 15.2% | 36.4% | 48.5% |
| TRENDING_DOWN | 12.5% | — | 0.0% | 87.5% |
| HIGH_VOL | 76.9% | 0.0% | — | 23.1% |

**GDX:**

| From → | TRENDING_UP | TRENDING_DOWN | HIGH_VOL | RANGING |
|--------|------------|--------------|---------|---------|
| RANGING | 57.9% | 21.1% | 21.1% | — |
| TRENDING_UP | — | 23.5% | 17.6% | 58.8% |
| TRENDING_DOWN | 62.5% | — | 0.0% | 37.5% |
| HIGH_VOL | 28.6% | 0.0% | — | 71.4% |

Full matrices for all symbols: `python3 scripts/analyse_regimes.py`

**Key transitions:**
- **HIGH_VOL → TRENDING_UP: 77% (GLD), 75% (IAU), 50% (SLV), 29% (GDX).** Volatility spikes strongly precede uptrends in GLD/IAU. GDX is weaker — HIGH_VOL more often resolves back to RANGING (71%) for mining equities.
- **RANGING → TRENDING_UP: 55–68% across all symbols.** When ranging breaks, it breaks upward more often than downward.
- **TRENDING_DOWN → RANGING: 88% (GLD).** Downtrends almost always resolve back to ranging, not to uptrend directly. Mean reversion after a downtrend, not immediate reversal.
- **Current regime implication:** We are in HIGH_VOL. Based on GLD history, 77% probability the next regime is TRENDING_UP. Average HIGH_VOL duration is 9 days — if we're already several days in, resolution is likely soon.

---

## Implications for Strategy

### 1. Regime confirms structural edge

59–63% RANGING for GLD/IAU/SLV (79% for GDX) is the foundation of Sharpe 2.47. The ADX filter already partially gates on this, but the regime classifier quantifies it explicitly and enables more granular control.

### 2. Regime-dependency explains live performance

2023–2026 are the most TRENDING_UP years in the dataset. Long-only mean reversion in a bull uptrend = oversold bounces are cleaner and more frequently profitable. The live K-exit win rate of 76% is consistent with operating in the most favourable regime historically. This is not evidence the edge disappears in other regimes — but it may be weaker.

### 3. HIGH_VOL is the regime to protect against

- 2026 HIGH_VOL is 17% for GLD — well above the 5.7% historical average
- The two largest slippage outliers in the live dataset (-$0.297, -$0.140) both occurred on high-volatility days
- TS exits cluster on high-volatility days — tight trail fires on noise
- HIGH_VOL resolves to TRENDING_UP 77% of the time for GLD/IAU — so halving size (not skipping entirely) is the right response; the following uptrend is worth participating in
- Action: halve position size during HIGH_VOL regime

### 4. TRENDING_DOWN is rare but dangerous for long-only

- 7.8% of GLD days historically, nearly absent since 2023
- In a downtrend, oversold often means momentum continuation, not reversal
- TRENDING_DOWN resolves back to RANGING 88% of the time (GLD) — not directly to TRENDING_UP
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
