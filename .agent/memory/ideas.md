# Strategy Ideas & Concepts

> Running log of ideas discussed during sessions. Reference back when ready to explore or implement.

---

## 1. Drawdown Duration Analysis
*Discussed: 2026-02-11*

Analyse historical drawdown episodes (start, trough, recovery, depth, duration) from stored equity curves. Build distributions per strategy/asset.

**Applications:**
- Confidence intervals — "80% of drawdowns recover within 15 days"
- Circuit breaker — if drawdown exceeds 95th percentile duration, reduce size or go flat
- Regime detection — drawdowns outlasting historical distribution suggest the edge has decayed

**Key insight:** Yearly bucketing misses drawdowns spanning year boundaries. Treat each drawdown as a single event regardless of calendar.

**Data source:** Equity curves already stored in `experiments` table.

---

## 2. Regime-Adaptive Strategy Rotation
*Discussed: 2026-02-11*

Meta-strategy that detects the current market regime and deploys the historically best-performing strategy for that regime.

**Approach:**
1. Label historical periods retroactively (trending up/down, range-bound, high/low vol) using ADX, ATR, SMA
2. Score each strategy's performance per regime
3. Live: detect current regime, deploy the winning strategy

**Simpler practical versions:**
- Drawdown-based decay detector — switch/pause when drawdown duration is statistically anomalous
- Volatility scaling — size positions inversely to ATR (high vol = smaller positions)
- Dual strategy paper race — run two strategies on paper, only execute the one with positive recent equity slope

**Challenges:** Regime transitions are slow/noisy, small samples per regime, overfitting risk multiplies with switching rules.

---

## 3. Pairs Trading / Statistical Arbitrage
*Discussed: 2026-02-11*

Trade the spread between correlated assets rather than directional price. When spread deviates from historical mean, go long the cheap one and short the expensive one.

**Candidate pairs (from existing data):**
- GLD / SLV (gold ETFs)
- GLD / IAU (same underlying, different ETF)
- XLE / XOP (energy sector)
- SPY / QQQ (broad market)

**Why it's attractive:**
- Spread is stationary (mean-reverts by construction) — more robust than price-based mean reversion
- Direction-neutral — macro events affect both legs equally
- Regime-resistant — not betting on direction, only on correlation holding

**Implementation needs:**
- New `PairsStrategy` class managing two positions simultaneously
- Or extend backtester for multi-asset strategies
- Spread calculation + z-score entry/exit signals

---

## 4. Beta Hedging Existing Strategies
*Discussed: 2026-02-11*

When StochRSI goes long GLD, simultaneously short proportional SLV/IAU to neutralise directional gold exposure. Only exposed to StochRSI's timing alpha, not gold's direction.

**Benefit:** Stop losses no longer triggered by macro gold drops unrelated to the signal quality.

**Requirement:** Same multi-asset backtester capability as pairs trading.

---

## 5. Portfolio-Level Diversification
*Discussed: 2026-02-11*

Run uncorrelated strategies simultaneously on different assets. Combined equity curve is smoother than any individual strategy.

**Example portfolio:**
- StochRSI mean reversion on GLD (range-bound gold)
- Donchian breakout on TLT (trending bonds)
- Mean reversion on XLE (range-bound energy)

**Key metric:** Correlation of drawdown periods across strategies. If drawdowns don't overlap, portfolio drawdown is much shallower and shorter.

**Already possible:** Run multiple bots on cloud today. The experiments DB tells us which strategy/asset combos are uncorrelated.

---

## 6. Frontend Dashboard Rebuild
*Discussed: 2026-02-11*

Delete current frontend, rebuild to visualise experiments DB. Key views:

- **Heatmap** — asset x timeframe, colored by best Sharpe
- **Validation funnel** — sweep → filtered → validated → passed
- **Drawdown distribution plots** — per strategy/asset, histogram of duration + depth with percentile markers
- **Equity curve overlay** — compare top N validated strategies
- **Parameter sensitivity** — scatter plot of param values vs Sharpe per strategy/asset
- **Discovery timeline** — cumulative experiments, are we still finding new edges?

**Data source:** All reads from `research.db` directly.

---

## 7. Position Sizing / Leverage Optimisation
*Discussed: 2026-02-12*

GLD 15m strategy has backtested max drawdown of only 1.7% — room to increase position size for higher returns.

**Kelly Criterion approach:**
- Calculate optimal fraction of capital to risk per trade based on win rate (47%) and avg win/loss ratio
- Full Kelly is too aggressive — use fractional Kelly (0.25-0.5x) for safety

**Practical scaling:**
| Sizing | Est. Max Drawdown | Est. Annual Return |
|--------|-------------------|-------------------|
| 1x     | 1.7%              | 2-7%              |
| 2x     | ~3.4%             | 4-14%             |
| 3x     | ~5.1%             | 6-21%             |

**Caution:** Backtested drawdowns understate live drawdowns (gap risk, slippage, black swans). Start at 1.5-2x, validate live, scale up gradually.

---

## 8. Gold Sector Amplification (GDX)
*Discussed: 2026-02-12*

GDX (gold miners ETF) moves 2-3x gold's daily moves due to operating leverage. Use GLD StochRSI signal but execute on GDX for amplified returns without margin.

**Steps:** Backtest StochRSI on GDX with same params → compare Sharpe/drawdown to GLD → if edge transfers, deploy.

**Risk:** Miners have idiosyncratic risk (management, costs, strikes) that can decouple from gold.

---

## 9. Multi-Timeframe Confirmation
*Discussed: 2026-02-12*

Combine 15m and 1h StochRSI signals on GLD. Only enter when both timeframes show oversold simultaneously.

**Expected benefits:**
- Higher win rate (filter out noise trades from 47% baseline)
- Larger per-trade return
- Fewer trades (reduced costs)

**Implementation:** New strategy class that reads two data feeds. Moderate effort.

---

## 10. Cross-Asset Signal Confirmation
*Discussed: 2026-02-12*

When GLD, SLV, and IAU all show oversold StochRSI simultaneously, trade with 2-3x normal size. Correlated assets confirming = higher conviction.

**Simpler version:** Just check GLD + SLV agreement before entry.

---

## 11. Spread Betting / IG API Integration
*Discussed: 2026-02-12*

**Problem:** €100 starting capital too small for Alpaca (GLD = $180/share, whole shares only).

**Solution:** Spread betting via IG (or similar):
- Tax-free profits in Ireland
- Trade gold directly at €0.50/point — €100 is workable
- Same gold edge, same StochRSI signals
- IG has REST API for automation
- Scale gradually: €0.50/point → €1 → €5

**Implementation:** Adapt execution layer from Alpaca API to IG API. Strategy logic / indicators / signals unchanged — only the broker interface changes.

**Other small-account options considered:**
- Forex via OANDA (micro/nano lots, good API, but taxable)
- CFDs (fractional exposure, taxable)
- Crypto on Alpaca (fractional, but no validated edge yet)

**Verdict:** Spread betting on gold via IG is most compelling path for small accounts in Ireland (tax-free + validated edge + small minimums).

---

## 12. Forex Strategy Discovery
*Discussed: 2026-02-12*

If adapting to a forex broker (OANDA), run the discovery engine on forex pairs. StochRSI mean reversion may work on ranging pairs.

**Candidate pairs:** EUR/CHF (range-bound), AUD/NZD, EUR/GBP
**Avoid:** Trending pairs like GBP/JPY, USD/JPY

**Advantage:** 24/5 market = more 15m bars = more trades = more data.

---

*Last updated: 2026-02-12*
*Add new ideas as they come up during sessions*
