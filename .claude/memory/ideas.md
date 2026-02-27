# Strategy Ideas & Concepts

> Running log of ideas discussed during sessions. Reference back when ready to explore or implement.
> **Format:** Ideas are hypotheses derived from confirmed findings in strategy cards or the experiments DB. Once tested, results go back into the relevant strategy card and the idea is removed.

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

**Current validated edges to combine:**
- StochRSI Enhanced — GLD 15m (Sharpe 2.54)
- StochRSI — GLD 1h (Sharpe 1.44)
- StochRSI — IAU 1h (Sharpe 1.22)
- StochRSI — XLE 1h (Sharpe 1.11)

**Goal:** Find edges on assets uncorrelated with gold (e.g. TLT, XLE) so drawdown periods don't overlap.

**Key metric:** Correlation of drawdown periods across strategies. If drawdowns don't overlap, portfolio drawdown is much shallower.

**Already possible:** Run multiple bots on cloud today. Experiments DB tells us which combos are uncorrelated.

---

## 6. Position Sizing / Leverage Optimisation
*Discussed: 2026-02-12*

GLD 15m strategy has backtested max drawdown of only 0.69% — significant room to increase position size.

**Derived from:** Strategy card — 0.69% DD with 2% risk/trade implies 10-20% risk/trade stays within acceptable DD.

**Kelly Criterion approach:**
- Calculate optimal fraction of capital to risk per trade based on win rate (43%) and avg win/loss ratio
- Full Kelly is too aggressive — use fractional Kelly (0.25-0.5x) for safety

**Practical scaling:**
| Risk per trade | Est. Max Drawdown | Est. Annual Return |
|--------|-------------------|-------------------|
| 2% (current) | ~0.7% | ~7% |
| 5% | ~1.7% | ~17% |
| 10% | ~3.5% | ~35% |
| 20% | ~7% | ~70% |

**Caution:** Backtested drawdowns understate live drawdowns. Validate live at lower sizing first.

---

## 7. Gold Sector Amplification (GDX)
*Discussed: 2026-02-12, prioritised 2026-02-27*

GDX (gold miners ETF) moves 2-3x gold's daily moves due to operating leverage. Use GLD StochRSI signal but execute on GDX for amplified returns without margin.

**Derived from:** Precious metals thesis — same mean-reversion structure as GLD, but with leverage built in.

**Test:** Run StochRSI Enhanced params (RSI 7, Stoch 14, OB 80, OS 15) on GDX 15m. Compare Sharpe/DD to GLD baseline.

**Risk:** Miners have idiosyncratic risk (management, costs, strikes) that can decouple from gold.

---

## 8. Multi-Timeframe Confirmation
*Discussed: 2026-02-12*

Combine 15m and 1h StochRSI signals on GLD. Only enter when both timeframes show oversold simultaneously.

**Expected benefits:**
- Higher win rate (filter out noise trades from 43% baseline)
- Larger per-trade return
- Fewer trades (reduced costs)

**Implementation:** New strategy class that reads two data feeds. Moderate effort.

---

## 9. Cross-Asset Signal Confirmation
*Discussed: 2026-02-12*

When GLD, SLV, and IAU all show oversold StochRSI simultaneously, trade with 2-3x normal size. Correlated assets confirming = higher conviction.

**Simpler version:** Just check GLD + SLV agreement before entry.

---

## 10. IG Spread Betting Integration
*Discussed: 2026-02-12/13*

**Motivation:** Alpaca's minimum trade unit (1 share) prevents precise Kelly sizing on small accounts (€100). Spread betting via IG allows sub-unit position sizing (e.g. €0.50/point), enabling proper compounding. Profits tax-free in Ireland.

**Current status:** Phase 1-2 built — `IGDataLoader` + `IGBroker` both working. Demo account provisioned.

**Remaining work:**
- Integrate `IGBroker` with `runner.py` via `--source ig` flag
- Live paper test on IG demo account (GLD equivalent: `CS.D.CFDGOLD.CFDGC.IP`)

**Key IG API details:**
- Auth: username + password + API key → CST + X-SECURITY-TOKEN headers
- Demo base: `https://demo-api.ig.com/gateway/deal`
- Resolutions: `1Min`, `5Min`, `15Min`, `1H`, `4H`, `D`

---

## 11. Time-of-Day Filtering
*Discussed: 2026-02-13*

Gold trades differently at London open vs NY open vs overlap. The 15m strategy fires ~115 trades/year indiscriminately. Analyse which hours produce the best win rate and filter out noise hours.

**Approach:** Run diagnostic backtest, dump all trades with entry hour, bucket by hour, identify dead zones. Then add simple hour guard to strategy (~5 lines).

**Key insight:** This is pure analysis first — zero code needed to identify the signal. Only build if data shows a clear pattern.

---

## 12. Limit Order Entries
*Discussed: 2026-02-13*

Instead of market order at signal bar close, place limit order slightly below (for longs). Improves average entry by a few cents per trade. Over 700+ trades that compounds.

**Risk:** Some trades won't fill (limit not reached). Need to check if missed trades were winners.

---

## 13. Volatility-Scaled Position Sizing
*Discussed: 2026-02-13*

Scale position size inversely to ATR. Low vol = larger position (mean reversion works best in calm markets). High vol = smaller position (more noise). ATR already calculated in strategy.

**Different from Kelly (#6):** Kelly is about overall capital allocation. This adapts size trade-by-trade based on current conditions.

---

## 14. IAU 15m Full Validation
*Derived from: Feb 27 precious metals expansion*

**Status:** Passed in-sample (Sharpe 2.00, +32.6%, DD 0.72%) but not yet holdout/walk-forward validated.

**Test plan:**
- Run `scripts/run_validation.py` pattern on IAU 15m with enhanced params
- Lower priority than SLV/GDX (Sharpe 2.00 vs 2.54/2.41) but worth confirming

**Note:** GDX 2024 WF window was weakest (Sharpe 1.06) — GDX has some miner-specific noise. IAU being pure gold-tracking may actually be more consistent year-to-year.

---

## 16. EventSurprise on SLV and TLT
*Derived from: EventSurprise strategy card + GLD CPI findings (Feb 27)*

**Thesis:**
- SLV is a gold-correlated asset — CPI surprises should drive SLV in the same direction as GLD
- TLT (bonds) is directly rate-sensitive — CPI misses (dovish signal) should move TLT strongly upward

**Evidence:** GLD CPI-miss trades show 93% directional accuracy, +0.80% avg 1h move. Same macro logic applies to silver and bonds.

**Test plan:**
- Run EventSurprise (CPI-only) on SLV 15m — compare win rate and avg move to GLD
- Run EventSurprise (CPI + FOMC) on TLT 15m — FOMC is highly relevant for bonds
- Parameter space is small (~20 combos) — manual runs, not orchestrator

**Priority: MEDIUM** — extends an existing edge to new assets with clear fundamental justification.

---

## 17. StochRSI + EventSurprise Combination on GLD
*Derived from: having two independent edges on the same asset (Feb 27)*

**Problem:** Both strategies currently run independently on GLD. On CPI days, StochRSI might fire a signal in the opposite direction to the expected CPI surprise move — creating a conflict.

**Two approaches to test:**
1. **Blackout filter:** On CPI event days, suppress StochRSI entries within ±2h of the release
2. **Confluence filter:** Only take StochRSI entries that align with the expected CPI surprise direction

**Note:** Event blackout was tested on StochRSI alone (strategy card) and *reduced* returns. But combining direction alignment (not just avoidance) hasn't been tested.

**Priority: MEDIUM** — interesting but more complex. Do SLV/GDX expansion first.

---

## 18. Overnight Orchestrator — Focused Cloud Runs
*Discussed: 2026-02-27*

**Setup:** Run overnight orchestrator on existing cloud VM (algotrader2026) — VM already running 24/7 for bots, zero extra cost. Pull results back locally with `gcloud compute scp`.

**How to run focused (not wide-net):**
```bash
# Precious metals expansion — Tier 1 priority
python -m backend.optimizer.run_overnight \
  --quick --symbols SLV,GDX,IAU --timeframes 15m --skip-composable

# Morning sync
gcloud compute scp algotrader2026:/home/user/algo-trader-v1/backend/research.db \
  ./backend/research.db --zone=europe-west2-a
```

**Key principle:** Use `--quick` (32 combos/target) to get directional signal. Only run `--medium` (972 combos) if `--quick` shows a positive result. Avoid `--full` until there's strong evidence it will yield something.

---

*Last updated: 2026-02-27 (Major restructure — removed built items (dashboard, event blackout), merged IG duplication, added thesis-driven ideas #14-18 from Feb 27 strategy session)*
*Add new ideas as they come up during sessions*
