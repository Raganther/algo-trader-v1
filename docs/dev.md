# Algo Trader V1 — Dev Notes

> Read on demand only. Not loaded on cold start.

## Ideas Backlog

Ideas are hypotheses to test. Once tested, results go into the relevant strategy card and the idea is removed.

---

### High Priority

**#20 Portfolio Manager — Dynamic Cross-Bot Position Sizing**
*Discussed: 2026-02-28*

Run all 4 validated 15m strategies (GLD, SLV, GDX, IAU) simultaneously with a shared risk budget and dynamic compounding position sizes.

**Core concept:**
- Total portfolio risk cap: 20% of account at any time across all 4 bots
- Each bot queries the live account before entering — sizes its trade based on remaining budget
- When a position closes, next bet automatically recalculates from current account equity
- Account grows → bets grow. Account shrinks → bets shrink. True compounding.

**Expected performance (blended portfolio):**
- Annualised return: ~14.8%/yr (equal 25% weight per strategy)
- GLD: 8.9%/yr, SLV: 21.1%/yr, GDX: 22.8%/yr, IAU: 6.5%/yr
- On €1,000: ~€1,994 after 5 years. On €10,000: ~€20,000.

**Sizing logic:**
```
Before entry:
  account_equity = GET /v2/account → equity
  open_positions = GET /v2/positions → sum(market_value)
  capital_at_risk = open_positions / account_equity
  remaining_budget = 0.20 - capital_at_risk
  if remaining_budget <= 0: skip entry
  position_size = account_equity × remaining_budget / open_slots_remaining
```

**Architecture — shared PortfolioManager class:**
- All 4 bots import and call it before sizing entries
- Queries Alpaca API for live account state (already available via AlpacaBroker)
- Returns approved position size in dollars
- No inter-process communication needed — Alpaca account IS the shared state

**Correlation caveat:** GLD + IAU + SLV + GDX are all precious metals. In a bad gold week all 4 drawdown simultaneously. Individual DDs of 0.69%–2.02% could combine to 3-6% portfolio drawdown. Still manageable.

**Implementation steps:**
1. Build `backend/broker/portfolio_manager.py`
2. Update each bot's entry logic to call PortfolioManager before sizing
3. Add configurable `max_portfolio_risk` param (default 0.20)
4. Test on paper with all 4 bots simultaneously

---

### Medium Priority

**#16 EventSurprise on SLV and TLT**
*Derived from: EventSurprise strategy card + GLD CPI findings (Feb 27)*

**Thesis:**
- SLV is gold-correlated — CPI surprises should drive SLV in the same direction as GLD
- TLT (bonds) is directly rate-sensitive — CPI misses (dovish signal) should move TLT strongly upward

**Evidence:** GLD CPI-miss trades show 93% directional accuracy, +0.80% avg 1h move. Same macro logic applies to silver and bonds.

**Test plan:**
- Run EventSurprise (CPI-only) on SLV 15m — compare win rate and avg move to GLD
- Run EventSurprise (CPI + FOMC) on TLT 15m — FOMC is highly relevant for bonds
- Parameter space is small (~20 combos) — manual runs, not orchestrator

---

**#17 StochRSI + EventSurprise Combination on GLD**
*Derived from: having two independent edges on the same asset (Feb 27)*

**Problem:** Both strategies currently run independently on GLD. On CPI days, StochRSI might fire a signal in the opposite direction to the expected CPI surprise move.

**Two approaches to test:**
1. **Blackout filter:** On CPI event days, suppress StochRSI entries within ±2h of the release
2. **Confluence filter:** Only take StochRSI entries that align with the expected CPI surprise direction

**Note:** Event blackout was tested on StochRSI alone and *reduced* returns. But combining direction alignment (not just avoidance) hasn't been tested.

---

**#21 Price Action Charts + Regime Analysis Dashboard**
*Discussed: 2026-03-04*

**Motivation:** SLV shows +14.25% with test params over 3 months — but is that the strategy working or just a silver bull run? Need to separate edge alpha from directional beta.

**Core concept:**
1. Pull all historical 15m data from Alpaca for GLD, SLV, GDX, IAU — store locally
2. Build frontend price action charts with trade overlays (entries/exits/stops)
3. Classify market regimes automatically (trending up, trending down, ranging/choppy)
4. Analyse strategy performance per regime — does the edge hold in all conditions?

**Regime classification approaches:**
- ADX > 25 = trending, < 20 = ranging (already in strategy)
- SMA slope (positive/negative/flat)
- Bollinger Band width (high vol / low vol)

**Key questions it would answer:**
- Does StochRSI Enhanced work in downtrends or only uptrends?
- Are losses concentrated in ranging markets?
- Could we pause trading in regimes where the strategy historically underperforms?

**Connects to:** #2 (regime rotation), #11 (time-of-day filtering), #13 (vol-scaled sizing)

---

**#2 Regime-Adaptive Strategy Rotation**
*Discussed: 2026-02-11*

Meta-strategy that detects the current market regime and deploys the historically best-performing strategy for that regime.

**Approach:**
1. Label historical periods retroactively (trending up/down, range-bound, high/low vol) using ADX, ATR, SMA
2. Score each strategy's performance per regime
3. Live: detect current regime, deploy the winning strategy

**Simpler practical versions:**
- Drawdown-based decay detector — switch/pause when drawdown duration is statistically anomalous
- Volatility scaling — size positions inversely to ATR
- Dual strategy paper race — run two strategies on paper, only execute the one with positive recent equity slope

**Challenges:** Regime transitions are slow/noisy, small samples per regime, overfitting risk multiplies with switching rules.

---

**#8 Multi-Timeframe Confirmation**
*Discussed: 2026-02-12*

Combine 15m and 1h StochRSI signals on GLD. Only enter when both timeframes show oversold simultaneously.

**Expected benefits:**
- Higher win rate (filter out noise trades from 43% baseline)
- Larger per-trade return
- Fewer trades (reduced costs)

**Implementation:** New strategy class that reads two data feeds.

---

### Lower Priority

**#1 Drawdown Duration Analysis**
*Discussed: 2026-02-11*

Analyse historical drawdown episodes (start, trough, recovery, depth, duration) from stored equity curves. Build distributions per strategy/asset.

**Applications:**
- Confidence intervals — "80% of drawdowns recover within 15 days"
- Circuit breaker — if drawdown exceeds 95th percentile duration, reduce size or go flat
- Regime detection — drawdowns outlasting historical distribution suggest the edge has decayed

**Key insight:** Yearly bucketing misses drawdowns spanning year boundaries. Treat each drawdown as a single event regardless of calendar.

**Data source:** Equity curves already stored in `experiments` table.

---

**#3 Pairs Trading / Statistical Arbitrage**
*Discussed: 2026-02-11*

Trade the spread between correlated assets. When spread deviates from historical mean, go long the cheap one and short the expensive one.

**Candidate pairs:** GLD/SLV, GLD/IAU, XLE/XOP, SPY/QQQ

**Why attractive:** Spread is stationary by construction — more robust than price-based mean reversion. Direction-neutral — macro events affect both legs equally.

**Implementation needs:** New `PairsStrategy` class managing two positions simultaneously, or extend backtester for multi-asset strategies.

---

**#4 Beta Hedging Existing Strategies**
*Discussed: 2026-02-11*

When StochRSI goes long GLD, simultaneously short proportional SLV/IAU to neutralise directional gold exposure. Only exposed to StochRSI's timing alpha, not gold's direction.

**Benefit:** Stop losses no longer triggered by macro gold drops unrelated to signal quality.

---

**#5 Portfolio-Level Diversification**
*Discussed: 2026-02-11*

Find edges on assets uncorrelated with gold (TLT, XLE) so drawdown periods don't overlap across strategies.

**Key metric:** Correlation of drawdown periods across strategies. If drawdowns don't overlap, portfolio drawdown is much shallower.

---

**#6 Position Sizing / Leverage Optimisation**
*Discussed: 2026-02-12*

GLD 15m strategy has backtested max drawdown of only 0.69% — significant room to increase position size.

**Kelly Criterion approach:** Calculate optimal fraction based on win rate (43%) and avg win/loss ratio. Use fractional Kelly (0.25-0.5x) for safety.

**Practical scaling:**
| Risk per trade | Est. Max Drawdown | Est. Annual Return |
|----------------|-------------------|-------------------|
| 2% (current)   | ~0.7%             | ~7%               |
| 5%             | ~1.7%             | ~17%              |
| 10%            | ~3.5%             | ~35%              |
| 20%            | ~7%               | ~70%              |

**Caution:** Backtested drawdowns understate live drawdowns. Validate live at lower sizing first.

---

**#9 Cross-Asset Signal Confirmation**
*Discussed: 2026-02-12*

When GLD, SLV, and IAU all show oversold StochRSI simultaneously, trade with 2-3x normal size. Correlated assets confirming = higher conviction. Simpler version: just check GLD + SLV agreement before entry.

---

**#10 IG Spread Betting Integration**
*Discussed: 2026-02-12/13*

**Motivation:** Alpaca's minimum trade unit prevents precise Kelly sizing on small accounts (€100). Spread betting via IG allows sub-unit position sizing (e.g. €0.50/point), enabling proper compounding. Profits tax-free in Ireland.

**Current status:** Phase 1-2 built — `IGDataLoader` + `IGBroker` both working. Demo account provisioned.

**Remaining work:**
- Integrate `IGBroker` with `runner.py` via `--source ig` flag
- Live paper test on IG demo account (GLD equivalent: `CS.D.CFDGOLD.CFDGC.IP`)

**Key IG API details:**
- Auth: username + password + API key → CST + X-SECURITY-TOKEN headers
- Demo base: `https://demo-api.ig.com/gateway/deal`
- Resolutions: `1Min`, `5Min`, `15Min`, `1H`, `4H`, `D`

---

**#11 Time-of-Day Filtering**
*Discussed: 2026-02-13*

Gold trades differently at London open vs NY open vs overlap. The 15m strategy fires ~115 trades/year indiscriminately. Analyse which hours produce the best win rate and filter out noise hours.

**Approach:** Run diagnostic backtest, dump all trades with entry hour, bucket by hour, identify dead zones. Then add simple hour guard to strategy (~5 lines).

**Key insight:** This is pure analysis first — zero code needed to identify the signal. Only build if data shows a clear pattern.

---

**#12 Limit Order Entries**
*Discussed: 2026-02-13*

Instead of market order at signal bar close, place limit order slightly below (for longs). Improves average entry by a few cents per trade. Over 700+ trades that compounds.

**Risk:** Some trades won't fill. Need to check if missed trades were winners.

---

**#13 Volatility-Scaled Position Sizing**
*Discussed: 2026-02-13*

Scale position size inversely to ATR. Low vol = larger position (mean reversion works best in calm markets). High vol = smaller position (more noise). ATR already calculated in strategy.

**Different from #6 (Kelly):** Kelly is about overall capital allocation. This adapts size trade-by-trade based on current conditions.

---

**#18 Overnight Orchestrator — Focused Cloud Runs**
*Discussed: 2026-02-27*

Run overnight orchestrator on existing cloud VM (algotrader2026) — VM already running 24/7 for bots, zero extra cost.

**How to run focused:**
```bash
# Precious metals expansion — Tier 1 priority
python -m backend.optimizer.run_overnight \
  --quick --symbols SLV,GDX,IAU --timeframes 15m --skip-composable

# Morning sync
gcloud compute scp algotrader2026:/home/user/algo-trader-v1/backend/research.db \
  ./backend/research.db --zone=europe-west2-a
```

**Key principle:** Use `--quick` (32 combos) to get directional signal. Only run `--medium` (972 combos) if `--quick` shows positive result.

---

**#19 Full Cloud Migration**
*Discussed: 2026-02-28*

Move everything (frontend, backend, DB, bots, overnight orchestrator) to cloud so the system is accessible from any device via browser.

**Architecture:**
- nginx reverse proxy → Next.js frontend (port 3000) + PM2 bots
- SQLite DB stays on server (single source of truth)
- Development via VS Code Remote SSH

**Blockers on current e2-micro:**
- Only 1 GB RAM — too tight for Next.js
- Node.js v12 installed — Next.js requires v18+

**Required upgrade:** e2-medium (~$27/mo, 4 GB RAM). e2-small ($14/mo, 2 GB) is marginal.

**Priority: LOW** — revisit when moving to real-money production phase.

---

## Completed Plans

### #7 Gold Sector Amplification (GDX) — Completed 2026-02-27
Test StochRSI Enhanced on GDX 15m for leveraged gold exposure via miners. **Result:** Validated — Sharpe 2.41, +114.1%, DD 2.02%, 4/4 walk-forward. GDX bot now running.

### #14 IAU 15m Validation — Completed 2026-02-27
Holdout/walk-forward validation on IAU 15m with enhanced params. **Result:** Validated — Sharpe ~2.0, +32.6%, DD 0.72%, 4/4 walk-forward. IAU bot now running.

### Filing System Migration — Completed 2026-03-07
Fully migrated to 5-file system matching global CLAUDE.md.
- Root `CLAUDE.md` is now single source of truth — all detail merged in, `.claude/CLAUDE.md` deleted
- `memory/MEMORY.md` — auto-generated by `git-save.sh` (8 full commits with stats)
- `memory/plan.md` — active plan, one at a time
- `docs/dev.md` — ideas + completed plans archive (this file)
- Retired: `.claude/CLAUDE.md`, `.claude/memory/recent_history.md`, `.claude/memory/ideas.md`, `scripts/update_memory.sh`
- Kept: `.claude/memory/system_manual.md`, `.claude/memory/strategies/` (on-demand reference)
