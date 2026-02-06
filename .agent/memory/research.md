# Research: Beyond Indicator-Only Strategies

> Last updated: 2026-02-06

## Context

After extensive backtesting with corrected cost model (`--spread 0.0003 --delay 0`), all indicator-only strategies on liquid US ETFs collapsed:

| Strategy | Before Fix | After Fix | Root Cause |
|---|---|---|---|
| QQQ 5m StochRSI | 44.9% | 0.99% | delay=1 phantom profit |
| IWM 15m StochRSI | 19.8% | -1.13% | delay=1 phantom profit |
| QQQ 4h Donchian | 22.6% | -6.38% | delay=1 phantom profit |
| SwingBreakout (daily, triple confirm) | N/A | -0.01% to +1.39% | No alpha to begin with |

**Conclusion:** Public indicators (RSI, MACD, Bollinger, Donchian) on SPY/QQQ/IWM cannot generate alpha after realistic costs. These markets are too efficient and the signals too widely known.

**Key insight:** The edge for retail isn't in WHAT you trade, but WHEN and WHY you trade.

---

## Tier 1: Highest Conviction Avenues

### 1. Economic Announcement Event Strategy

**The case:** Scheduled macro releases (NFP, CPI, FOMC) create predictable volatility spikes and multi-day drift patterns that are exploitable by patient traders.

**Evidence:**
- S&P 500 returns on FOMC days are 5x greater than normal days (Quantpedia)
- Pre-FOMC drift: +49 bps in 24 hours before announcement (Lucca & Moench 2015, NY Fed)
  - Caveat: weakened substantially since 2016 (Tandfonline 2024)
- Post-announcement drift persists for days when surprise shifts macro narrative
- Options IV crush of 30-40% after releases is a structural feature

**Which announcements matter most:**

| Announcement | Time (ET) | Frequency | Typical SPY Move |
|---|---|---|---|
| FOMC Rate Decision | 2:00 PM | 8x/year | 1-3% |
| Non-Farm Payrolls | 8:30 AM | Monthly (1st Fri) | 0.5-1.5% |
| CPI | 8:30 AM | Monthly (~15th) | 0.5-2% |
| GDP (advance) | 8:30 AM | Quarterly | 0.3-1% |
| Core PCE | 8:30 AM | Monthly | 0.3-0.8% |

**Timing of reaction (critical for retail):**
- First 5 min: HFT dominated, spreads 3-5x wider. DO NOT trade.
- 5-30 min: Initial reaction settles, reversals still common.
- 30 min to end of day: "True" move emerges. Best window for retail.
- 1-5 days after: If surprise shifts narrative, momentum continues. Highest probability.

**Implementable strategies:**
1. **Post-announcement momentum:** Wait 30 min, enter direction of sustained move, hold hours to days. ~12-24 trades/year.
2. **Volatility crush (options):** Sell iron butterflies/condors day before major release. 70% win rate, 4.83 profit factor documented. ~8-12 trades/year.
3. **Pre-FOMC drift:** Buy SPY 24h before FOMC, sell at/after announcement. Weakening edge. ~8 trades/year.

**Data sources:**

| Source | Cost | Notes |
|---|---|---|
| FRED API | Free | Macro data, `fredapi` package |
| EODHD Calendar | Free tier | 30+ countries, 50+ event types |
| Trading Economics | $50/mo | Best quality (actual vs forecast vs previous) |
| Investing.com | Free (scrape) | Good but fragile |
| BLS.gov | Free | Official release schedules |

**Academic references:**
- Lucca & Moench (2015), NY Fed Staff Report 512 — Pre-FOMC drift
- Quantpedia — FOMC Meeting Effect in Stocks
- Chicago Booth Review — How to Make Money on Fed Announcements
- BIS Working Papers 1079 — Volume Dynamics Around FOMC

---

### 2. VIX Term Structure Regime Filter

**The case:** VIX futures curve shape predicts subsequent equity returns. Works as an overlay/filter on any strategy.

**How it works:**
- **Backwardation** (near-term VIX > long-term): Market stress. Subsequent S&P 500 returns are significantly positive (contrarian buy signal).
- **Contango** (normal state): No significant timing signal.
- **Extreme contango:** Complacency. Reduce exposure.

**Evidence:** Macrosynergy research shows statistically significant positive equity returns following backwardation signals.

**Data:** VIX futures from vixcentral.com or CBOE (free). FRED has VIX spot.

**Trade frequency:** 5-15 signals/year as overlay.

**Main risk:** Backwardation can persist during crashes (buying into falling knife).

---

## Tier 2: Strong Evidence

### 3. Sector Rotation Momentum

**The case:** Monthly rebalance into top-performing sectors captures momentum premium that persists due to institutional herding and narrative effects.

**Evidence:**
- 3.6% annual alpha over 15 years (Fidelity)
- Sharpe ratio ~0.73 (roughly 2x benchmark)
- 5% excess returns per annum from country/industry momentum (Quantpedia)

**Implementation:**
- Monthly: rank sector ETFs (XLK, XLE, XLF, XLV, XLI, XLC, XLRE, XLU, XLB, XLP, XLY) by 6-12 month momentum
- Buy top 2-3 sectors, avoid/short bottom sectors
- All ETFs available on Alpaca

**Trade frequency:** Monthly rebalance (~12 trades/year per position)
**Data needed:** Price data only (free via Alpaca)
**Main risk:** Momentum crashes (sudden sector reversals)

---

### 4. Post-Earnings Announcement Drift (PEAD)

**The case:** Stocks with large earnings surprises continue drifting in the surprise direction for 60-90 days. One of the oldest and most persistent anomalies in finance.

**Evidence:**
- 5.1% risk-adjusted return over 3 months (Garfinkel, Hribar, Hsiao 2024)
- UCLA Anderson Review (2025) confirms PEAD is "alive and well"
- Strongest in small/mid-caps with less analyst coverage

**Implementation:**
- Identify stocks with large positive earnings surprises (top SUE decile)
- Buy after earnings, hold 60 days
- 20-50 opportunities per quarter during earnings season

**Data needed:** Earnings data (free from Alpaca, Alpha Vantage, or Financial Modeling Prep)
**Main risk:** Requires stock-level analysis, not just ETF trading. Individual stock risk.

---

### 5. Credit Spread Regime Filter

**The case:** High-yield credit spreads are a leading indicator of equity market stress. Widening spreads predict drawdowns.

**Implementation:**
- Monitor ICE BofA US High Yield OAS (FRED series: BAMLH0A0HYM2)
- Compare to 20-day or 50-day moving average
- Widening = reduce equity exposure / tighten stops
- Narrowing = increase exposure / widen stops

**Data:** Entirely free via FRED API. Daily updates.
**Trade frequency:** Position changes monthly or quarterly.
**Main risk:** Slow-moving signal. Better for avoiding drawdowns than generating alpha.

---

## Tier 3: Worth Exploring

### 6. Crypto Momentum on Alpaca
- Crypto markets are demonstrably less efficient than equities
- Momentum and mean reversion signals are stronger
- Alpaca supports BTC/USD, ETH/USD
- Limitation: no shorts on crypto via Alpaca

### 7. News Sentiment as Filter
- Alpaca News API (free) + FinBERT (open source) for sentiment scoring
- Research shows up to 50% returns over 28 months with sentiment signals (Arxiv 2025)
- Best as a filter on other strategies, not standalone
- Requires NLP infrastructure

### 8. Opening Range Breakout (Filtered)
- 60-min ORB historically: 89.4% win rate, but effectiveness declining
- Requires additional filters (volume, VIX regime, gap size)
- Well-known strategy, edge eroding

---

## Tier 4: Not Recommended

- **Social media sentiment (Reddit/X):** WSB attention reduces returns (-8.5%). Contrarian signal only, too noisy.
- **Options flow following:** Information priced in instantly. Supplementary context at best.
- **VWAP mean reversion on liquid ETFs:** This is essentially what our indicator strategies already tried.

---

## Recommended Build Order

### Phase 1: Economic Calendar Integration (1-2 weeks)
1. Set up FRED API (`pip install fredapi`)
2. Integrate EODHD calendar or scrape Investing.com
3. Build scheduler for upcoming NFP, CPI, FOMC, GDP releases
4. Implement "quiet mode" — pause existing bots 30 min before/after major releases
5. Build post-announcement momentum detector (price direction + volume 30 min after)

### Phase 2: VIX + Credit Regime Overlay (1 week)
1. Pull VIX term structure daily
2. Pull HY credit spread from FRED daily
3. Create regime classifier: risk-on / neutral / risk-off
4. Apply as position sizer / filter for all strategies

### Phase 3: Event-Day Options (2-3 weeks)
1. Build volatility crush strategy: sell iron butterflies on SPY before FOMC/CPI/NFP
2. Backtest using historical options data
3. Paper trade for 2-3 months

### Phase 4: Sector Rotation + PEAD (2-3 weeks)
1. Monthly sector momentum ranker
2. Earnings surprise detector
3. Paper trade both

---

## Key Data Sources Summary

| Data | Source | Cost | Python |
|---|---|---|---|
| Macro economic data | FRED | Free | `fredapi` |
| Economic calendar | EODHD | Free tier | REST API |
| Stock/ETF/options prices | Alpaca | Free | `alpaca-py` |
| News + sentiment | Alpaca News API | Free | `alpaca-py` |
| VIX term structure | CBOE / vixcentral | Free | scrape |
| Credit spreads | FRED (BAMLH0A0HYM2) | Free | `fredapi` |
| Earnings data | Alpha Vantage / FMP | Free tier | REST API |

---

## Why Event-Driven Beats Indicators

| Indicator Strategies | Event/Macro Strategies |
|---|---|
| Trade continuously | Trade only at catalysts |
| Signal is public knowledge | Edge is in patience + timing |
| 1000+ trades/year (costs kill) | 20-50 trades/year |
| Competing with HFT | HFT can't exploit multi-day drift |
| Price data only | Multiple data dimensions |
| SPY/QQQ too efficient | Same markets, different timing |
