# Research: Strategy Direction & Alternative Approaches

> Last updated: 2026-02-10

## Context

After extensive backtesting with corrected cost model (`--spread 0.0003 --delay 0`), all indicator-only strategies on liquid US ETFs collapsed:

| Strategy | Before Fix | After Fix | Root Cause |
|---|---|---|---|
| QQQ 5m StochRSI | 44.9% | 0.99% | delay=1 phantom profit |
| IWM 15m StochRSI | 19.8% | -1.13% | delay=1 phantom profit |
| QQQ 4h Donchian | 22.6% | -6.38% | delay=1 phantom profit |
| SPY 15m StochRSI | 54.36% | -8.61% | delay=1 phantom profit |
| SwingBreakout (daily, triple confirm) | N/A | -0.01% to +1.39% | No alpha to begin with |
| MACD+Bollinger QQQ 1h | N/A | +1.03% ann. | Marginal, not worth trading |
| RegimeGatedStoch SPY 1h | N/A | +2.01% ann. | Marginal |
| RegimeGatedStoch BTC 1h | N/A | +1.74% ann. | Small positive (less efficient market) |

**Conclusion:** Public indicators (RSI, MACD, Bollinger, Donchian) on SPY/QQQ/IWM cannot generate alpha after realistic costs. These markets are too efficient and the signals too widely known.

**Key insight:** The edge for retail isn't in WHAT you trade, but WHEN and WHY you trade.

---

## Live Trading Validation (Feb 5-10, 2026)

### Confirmation: 100+ live trades match corrected backtests

After running 3 bots (SPY 5m, QQQ 15m, IWM 5m) in EXTREME mode (50/50 thresholds) for 5 days:

**SPY sample round-trips:**
| Buy | Sell | Per-share P&L |
|-----|------|--------------|
| $695.49 | $694.24 | -$1.25 |
| $695.37 | $695.37 | ~$0.00 |
| $694.14 | $693.39 | -$0.75 |
| $689.78 | $689.59 | -$0.19 |

Pattern: trades are essentially random around breakeven, bid-ask spread eats any theoretical edge.

**Updated slippage data (70+ trades):**
| Symbol | Trades | Avg Slippage | Fill Delay |
|---|---|---|---|
| SPY | 39+ | 0.024% | ~1 sec |
| QQQ | 7+ | 0.049% | ~1 sec |
| IWM | 24+ | 0.029% | ~1 sec |

**Key finding:** Live results are consistent with corrected backtest showing ~0% returns. The backtester with `--spread 0.0003 --delay 0` is now a **trustworthy tool** — any strategy showing meaningful profit under these settings has a real chance of working live.

### The delay=1 bug explained

In `backtester.py`, the execution override is set AFTER `on_data()` already executed the order:
1. Previous iteration set `override_price = data[N]['Open']`
2. Current iteration: `strategy.on_data(N)` runs → sees bar N's Close → broker fills at bar N's Open (the override)
3. Current iteration then sets override for N+1

Result: strategy sees the Close price and decides to trade, but fills at the Open of the same bar. On mean reversion with 1000+ trades/year, this timing shift creates phantom profit that compounds massively. With `delay=0`, orders fill at Close (matching live behavior), and all profit disappears.

---

## Untested Indicator-Based Directions

The backtester is now accurate. These areas haven't been explored and could potentially yield results:

### 1. Less Efficient Assets
- **Sector ETFs:** XLE (energy), XBI (biotech), XHB (homebuilders) — less institutional coverage
- **Small-cap ETFs:** IJR, IWO — wider spreads but potentially more signal
- **Emerging markets:** EEM, VWO — less efficient, more momentum persistence
- **Why it might work:** SPY/QQQ are the most efficient markets. Less traded ETFs have wider spreads but signals may still have edge after costs

### 2. Volume-Based Indicators
- **OBV (On-Balance Volume):** Measures buying/selling pressure — NOT in current codebase
- **VWAP:** Volume-weighted average price — NOT implemented
- **Volume profile:** Price levels with highest trading volume
- **Why it might work:** Everything tested so far uses only OHLC price data. Volume carries fundamentally different information about supply/demand

### 3. Multi-Timeframe Confluence
- Take 5m StochRSI signals ONLY when daily trend aligns (e.g. price above 200 SMA)
- Or: use weekly Donchian direction to filter 15m mean reversion entries
- **Why it might work:** Single-timeframe signals are noisy. Multi-TF confirmation reduces false signals

### 4. Crypto Markets
- RegimeGatedStoch on BTC showed +1.74% annualised — small but positive
- Crypto is demonstrably less efficient than US equities
- Limitation: Alpaca doesn't support crypto shorts
- **Why it might work:** Less institutional competition, 24/7 trading, higher volatility

### Assessment
Expected probability of finding meaningful alpha (>5% annually) on indicator-only strategies:
- On SPY/QQQ/IWM: **Very low** (~5%) — exhaustively tested, all collapsed
- On sector/small-cap ETFs: **Low-moderate** (~15-20%) — untested, slightly less efficient
- On crypto: **Moderate** (~25%) — less efficient, but long-only constraint limits potential
- With volume indicators: **Low** (~10%) — volume data is also public, but at least it's different information

These are worth testing as quick experiments (1-2 days each) given the backtester is now trustworthy, but expectations should be calibrated accordingly.

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
