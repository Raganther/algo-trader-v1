# Arbitrage & Automation Concepts

> Research notes from Apr 11 2026 discussion. Captures arbitrage types and automation patterns
> for future development and business idea evaluation. Not yet on the critical path.

---

## What Arbitrage Actually Is

### Loose definition (statistical edge)
Exploit a mispricing (information asymmetry or statistical divergence) before it closes.

```
Market price ≠ True value
         ↑
    Your information / model is better
         ↑
    Edge exists until information becomes symmetric
```

The edge always decays as data becomes commoditised. Durable edges live where **data is hard
to get, hard to process, or hard to act on** — not just hard to find.

### True arbitrage (strict definition)
Two independent systems pricing the same thing differently. You buy on A and sell on B
simultaneously — the profit is locked in regardless of where price moves next.

```
System A  →  price of X = P1
System B  →  price of X = P2  (P2 > P1)
→  Buy on A, sell on B simultaneously
→  Profit = P2 - P1 - transaction costs
→  No directional risk if both legs fill
```

**Three hard requirements for true arbitrage:**
1. Two independent systems with conflicting prices for the same thing
2. Simultaneous execution on both legs (one leg alone = directional risk)
3. Edge must exceed total transaction costs (fees, spread, transfer, latency)

**Key distinction from our current trading system:**
- Our trader uses **one platform (Alpaca)** and predicts *directional price movement*
- That is a statistical edge, not true arbitrage
- True arbitrage requires the second platform — the discrepancy lives *between* systems

---

## True Arbitrage — Domain by Domain

### Sports Betting — Most Accessible
- **System A:** Betfair exchange (peer-to-peer odds)
- **System B:** Traditional bookmaker (Paddy Power, Bet365)
- **The gap:** Same match, different implied probabilities across bookmakers
- **How to find it:** Scrape 50+ bookmakers in real time. When sum of implied probabilities
  across all outcomes < 100%, a guaranteed profit window exists. Calculate stakes accordingly.
- **Execution:** Place both bets simultaneously before odds shift
- **Edge killer:** Bookmakers ban winning accounts. Arb bettors get limited to €2 stakes within weeks.
- **Big data angle:** Real-time odds scraping, instant alert when window opens, auto-stake calculator
- **Viability:** Yes — works until account gets flagged. Multiple accounts extend runway.

---

### Cryptocurrency — Most Alive True Arb Today
- **System A:** Coinbase (BTC price = $50,000)
- **System B:** Binance, Kraken, OKX (BTC price = $50,150)
- **The gap:** 0.1–0.5% price differences persist because capital transfer between exchanges
  takes time (withdrawal limits, blockchain confirmation delays)
- **Execution:** Pre-fund both exchanges. Detect gap via WebSocket feeds. Execute both legs
  within milliseconds.
- **Edge killer:** Withdrawal fees, transfer delays, exchange downtime
- **Big data angle:** Simultaneous WebSocket feeds from 10+ exchanges, sub-second gap detection
- **Viability:** Genuinely buildable at retail scale — unlike stock markets, crypto arb hasn't
  been fully competed away. Most viable true arb opportunity available today.

---

### Retail / E-commerce — Geographic Price Arbitrage
- **System A:** US Amazon or clearance retailer (product at $40)
- **System B:** EU/UK Amazon or eBay (same product at €60)
- **The gap:** Regional pricing differences due to distribution, tax, availability, information lag
- **Execution:** Buy on A, list on B — not instant but low risk if product is non-perishable
- **Edge killer:** Amazon marketplace rules, account bans, import duties, return costs, shipping time
- **Big data angle:** Scrape prices across regions, calculate margin after all costs, flag profitable SKUs
- **Viability:** Yes — semi-automated, slow arbitrage. Margins thin but scalable with data.

---

### Energy — Transmission Arbitrage
- **System A:** Electricity price in Region A (e.g. windy Scotland, oversupply, near-zero or
  negative prices)
- **System B:** Electricity price in Region B (e.g. London, high demand, higher price)
- **The gap:** Grid transmission constraints prevent instant price equalisation between regions
- **Execution:** Own assets on both sides — generation/storage in A, load/export in B
- **Retail version:** Battery storage + real-time tariff switching (Octopus Agile publishes
  30-min ahead prices). Charge when cheap, discharge/export when expensive.
- **Big data angle:** Real-time grid data (National Grid ESO public API), weather forecasting,
  demand modelling, half-hourly price feeds
- **Viability:** Yes at small scale with hardware (battery, immersion diverter). Large scale
  requires grid assets.

---

### Currency — Triangular Arbitrage
- **System A/B/C:** Three currency pairs that form a loop
- **Example:** EUR → USD → GBP → EUR — if exchange rates misaligned, end up with more EUR
- **The gap:** Three exchanges pricing pairs slightly differently simultaneously
- **Edge killer:** Closes in milliseconds in liquid FX — institutional HFT owns this completely
- **More viable:** Emerging market currencies, smaller crypto exchanges, illiquid pairs
- **Viability:** No at retail in liquid FX. Possible in crypto cross-pairs.

---

### Insurance / Risk Pricing
- **System A:** Insurance company pricing a risk at premium X (using inferior model)
- **System B:** Reinsurance market pricing the same risk at Y
- **The gap:** Your model of underlying risk is better than both — you intermediate
- **Real world:** Catastrophe bond market, Lloyd's syndicates do this at scale
- **Big data angle:** Weather models, actuarial tables, satellite imagery for property risk scoring
- **Viability:** No without regulatory licence and significant capital. Research interest only.

---

### Labour / Staffing — Slow Arbitrage
- **System A:** Employer paying market rate in City A (Dublin €80k)
- **System B:** Talent available in City B at same skill, lower cost (Eastern Europe €30k)
- **The gap:** Geographic information asymmetry — employer doesn't know talent exists at that price
- **Your role:** Staffing agency, outsourcing firm, or remote-first company capturing the spread
- **Edge killer:** Closes as remote work normalises global salary visibility
- **Viability:** Business model, not a trade — but structurally identical to two-platform arb

---

### Real Estate — Information Arbitrage
- **System A:** Local market pricing property at X (information-poor buyers, slow data)
- **System B:** Sophisticated investor's model valuing same property at Y using better data
- **The gap:** Planning applications, infrastructure investment, school ratings, demographic shifts
  not yet priced into local market
- **Execution:** Slow — months not seconds. Capital locked during reversion.
- **Big data angle:** Planning portal scraping, transport investment maps, rental yield databases
- **Viability:** Yes but slow. Edge is in data advantage, not speed.

---

## Viability Summary

| Domain | True arb? | Retail viable? | Speed required | Edge killer |
|--------|-----------|---------------|----------------|-------------|
| Crypto exchange | Yes | Yes | Milliseconds | Transfer delays, fees |
| Sports betting | Yes | Yes (short) | Seconds | Account bans |
| Retail/ecommerce | Slow | Yes | Hours/days | Rules, duties |
| Energy tariff | Yes | Yes (hardware) | Minutes | Hardware cost |
| FX triangular | Yes | No | Microseconds | HFT dominance |
| Insurance/risk | Yes | No | N/A | Regulation, capital |
| Labour/staffing | Slow | As business | Weeks/months | Market normalisation |
| Real estate | Slow | Yes | Months | Capital lock-up |

---

## The Universal Architecture (Two-Platform Version)

```
┌─────────────────────────────────────┐
│  DATA LAYER                         │
│  - Live feed from System A          │
│  - Live feed from System B          │
│  - Gap detection (A ≠ B)            │
│  - Historical data for backtesting  │
└──────────────┬──────────────────────┘
               │ gap detected + costs checked
┌──────────────▼──────────────────────┐
│  EXECUTION LAYER                    │
│  - Act on System A  ─┐ simultaneously│
│  - Act on System B  ─┘              │
│  - Log both fills                   │
│  - Alert if one leg fails           │
└─────────────────────────────────────┘
```

**The algo trader is one half of this** — it has the data layer and execution layer for
one platform. Adding true arbitrage means:
1. Second data feed (second exchange/platform API)
2. Simultaneous dual execution
3. Leg-failure handling (if one side fills and other doesn't → immediate unwind)

---

## Arbitrage Types — Trading

### 1. ETF Pairs / Statistical Arbitrage
Find two assets with a historically stable ratio. Trade the spread when it deviates, exit on reversion.

**Our candidates:**
- GLD/IAU — same underlying (gold), different fund size. Ratio should be ~10:1 at all times.
- GLD/GDX — gold price vs gold miners (loose but persistent relationship)
- SLV/GLD — gold/silver ratio, mean-reverting over months/years (historically 40–80x)

**Big data angle:** Cointegration testing (Engle-Granger, Johansen) over long history.
Our yfinance data back to 2004 is exactly what you'd use for this.

**Prerequisites not yet built:**
- Short selling (blocked until whole-share sizing done)
- Dual-symbol simultaneous execution runner
- Spread monitoring / cointegration tracking

---

### 2. ETF / NAV Arbitrage
ETFs can briefly trade at premium or discount to their Net Asset Value (the basket of underlying assets).
The premium/discount is publicly published daily.

**Limitation:** Authorized participant mechanism closes gaps in seconds at institutional scale.
Retail size + Alpaca latency = edge gone before you get there. More academic than practical here.

---

### 3. Cross-Timeframe Signal Arbitrage
Not classical arbitrage but exploits information asymmetry across timeframes:
- Daily regime signals leading 15m entries (our regime classifier does this)
- Weekly trend direction gating 15m entries (trade long only when weekly trend is up)

Already partially built via `backend/indicators/regime.py`.

---

### 4. Volatility Arbitrage
Options implied volatility (IV) vs realised historical volatility (HV).
- IV >> HV: sell options premium
- IV << HV: buy it

**Big data angle:** VIX term structure, GLD options chain, IV percentile over rolling windows.
**Limitation:** Requires options access and a different execution model. Alpaca supports options
but we'd need a full rebuild of the position management layer.

---

### 5. Event-Driven / News Arbitrage
Build a model of *expected* market reaction to macro events (CPI, NFP, Fed).
Trade the *surprise delta* — how much actual diverges from consensus.

**Big data angle:** Decades of Bloomberg consensus vs actual releases, cross-asset reaction matrices.
**Already partially built:** `backend/strategies/event_surprise.py` — CPI surprise on GLD,
+2.36% return, 86% win rate over 14 trades. See `.claude/strategies/event-surprise.md`.

---

### 6. Cross-Asset Macro Arbitrage (Relationship Trading)

| Pair | Relationship |
|------|-------------|
| GLD vs DXY (USD index) | Strong inverse — gold rallies when dollar weakens |
| GLD vs TLT (long bonds) | Both safe-haven — correlate in risk-off regimes |
| SLV vs industrial metals (copper) | Silver has industrial demand component |
| GDX vs GLD | Miners = leveraged gold — compressed ratio = miners cheap |

**Big data angle:** Kalman filter for dynamic hedge ratio estimation — the GLD/DXY relationship
shifts with macro regime. Fixed hedge ratios break during regime transitions.

**Data source:** DXY available via yfinance as `DX-Y.NYB`. Already have GLD/SLV/GDX back to 2004.

---

## Arbitrage Types — Outside Trading

The same **signal → act → manage → exit → log** pattern applies far beyond markets.

### Weather / Energy

**Critical distinction — two separate opportunities in weather:**

#### A. Weather Prediction Alpha (one platform, directional bet)
Build a better weather model than the market consensus. Bet on Kalshi/prediction market
outcomes where your model disagrees with the implied probability.

```
Your model:   70% chance of rain in Dublin on Apr 20
Kalshi market: 45% chance of rain  →  implied odds = 2.22
→ Bet YES on rain — positive expected value
→ You could be wrong — this is a statistical edge, not guaranteed profit
```

This is **the same structure as our algo trader** — one platform, better signal, directional
bet with real risk. Not true arbitrage. But viable and buildable now.

**Data sources (all free):**
| Source | What it gives you |
|--------|------------------|
| NOAA | US historical weather, 100+ years, free API |
| Met Éireann | Irish historical data, free |
| ERA5 (Copernicus) | Global atmospheric reanalysis, 1940–present |
| GFS model output | US government forecast, free, updates 4x/day |
| ECMWF ensemble | European model, gold standard for medium-range |

**Where the statistical edge comes from:**
- **Ensemble spread** — GFS/ECMWF run 50+ parallel forecast variants. The spread of those
  runs quantifies forecast uncertainty. Markets price binary outcomes without using this.
- **ENSO regime conditioning** — El Niño years have statistically different temperature and
  rainfall patterns than La Niña years. Same as our regime classifier — condition on the
  current state to get a better base rate than the unconditional market consensus.
- **Mean reversion** — temperatures revert to seasonal norms. Markets overweight recent
  anomalies. A cold snap doesn't predict another cold snap — base rates do.

**Tradeable markets on Kalshi today:**
- Will temperature in [city] exceed X°F on [date]?
- Will it rain more than X inches this month?
- Will this hurricane make landfall in [region]?
- Will [city] have a white Christmas?
- Will this month be above/below average temperature?

**Viability:** Genuinely viable. Weather is more predictable than financial markets
(physics-based, not adversarial). Kalshi markets are relatively new — crowd pricing
hasn't been fully optimised yet. Edge window probably 2–5 years before it compresses.

---

#### B. Weather True Arbitrage (two platforms, simultaneous execution)
Same weather outcome priced differently across two prediction markets simultaneously.

```
Kalshi:     45% chance of rain  →  YES pays 2.22x
Polymarket: 38% chance of rain  →  NO pays 1.61x
→ Bet YES on Kalshi + NO on Polymarket simultaneously
→  Profit regardless of outcome (if gap > fees)
```

This IS true arbitrage — two platforms, locked profit, no directional risk.

**Why it's harder than prediction alpha:**
- Kalshi and Polymarket rarely price the *same granular* weather outcome
- Thin liquidity on both sides simultaneously
- Window closes fast as cross-market scrapers catch up

**Practical approach:** Build prediction alpha first (single platform). Add cross-platform
monitoring as an opportunistic second layer — alert when same outcome appears on both
platforms with a profitable gap.

---

#### C. Energy Tariff Arbitrage (hardware required)
- **System A:** Grid electricity at low price (Octopus Agile publishes 30-min ahead prices)
- **System B:** Battery / hot water storage as the second "platform"
- Charge when cheap, discharge or divert when expensive
- Real-time grid data: National Grid ESO public API
- **Viability:** Yes at small scale with hardware. Large scale needs grid assets.

---

**Weather opportunity hierarchy:**
```
1. Build better weather model (NOAA + ERA5 + ENSO regime conditioning)
       ↓
2. Bet on single platform where model disagrees with market (prediction alpha)
       ↓  works standalone
3. Monitor second platform for same outcomes
       ↓
4. When cross-platform gap appears → true arb on top (opportunistic)
```

### Sports / Prediction Markets
- **Bookmaker odds arb (sure bets):** Three bookmakers price same event differently. Bet all
  outcomes at right stakes → guaranteed profit. Edge closes in minutes as scrapers commoditise it.
- **xG / statistical model arb:** Better shot-quality models than bookmakers = persistent edge
  on match odds. Closes as sports data companies sell the same data to everyone.
- **Prediction markets:** Metaculus superforecasters consistently beat naive prediction markets
  on low-information events. Edge = better prior calibration + faster Bayesian updating.

---

## Polymarket — Statistical Edge Domains

Polymarket is a decentralised global prediction market (Polygon blockchain, USDC currency).
No geographic restrictions like Kalshi. Public API. Accessible from Ireland.
Key filter for viable domains: **rich historical data exists that the crowd isn't fully pricing in.**

### What Makes a Domain Viable on Polymarket

1. Rich public historical data — decades of outcomes to backtest against
2. A quantifiable base rate — probability of X is calculable from history
3. Crowd mispricing — market prices naive consensus, not calibrated statistical model
4. Regime conditioning — some external state shifts the base rate in predictable ways

---

### Domain 1 — Economics / Macro (Build This)
**Data:** FRED database, BLS, BEA — 50+ years of CPI, NFP, GDP, Fed decisions, all free.
Consensus forecasts published before every release (public aggregators).

**Edge:**
- Market prices the consensus. Model prices the *surprise delta* — how often actual beats/misses
  consensus by more than X. Serial correlation in Fed decisions — if held in March, high base rate
  for June. Inflation mean-reverts over cycles — statistically modelable.
- Directly mirrors our `event_surprise.py` strategy, applied to Polymarket instead of GLD price.

**Example markets:** Will CPI exceed X% in April? Will Fed cut in June? Will US enter recession?

**Verdict: Strong. Build alongside weather.**

---

### Domain 2 — Weather (Build This)
See full section above. NOAA, ERA5, ENSO regime conditioning. Best non-trading candidate.

**Verdict: Strong. 2–5 year edge window before market matures.**

---

### Domain 3 — Epidemiology / Public Health
**Data:** CDC, WHO, ECDC — weekly case counts, hospitalisation rates, 20+ years of flu data.
Seasonal patterns are highly statistically regular.

**Edge:**
- Flu season peaks predictable within 3-week window using historical base rates + current trajectory
- Crowd overreacts to early season spikes, underprices late-season tail risk
- ENSO affects flu season severity — same regime conditioning as weather

**Example markets:** Will WHO declare a new emergency? Will flu hospitalisations exceed X?

**Verdict: Medium-strong. Low competition. Requires epidemiology domain knowledge.**

---

### Domain 4 — Sports
**Data:** FBref, Understat, StatsBomb open data — every match result, xG, player stats, injuries.

**Edge:** Better xG model → mispriced match outcomes. Injury information not yet priced.
Home/away form under specific conditions (weather, altitude, travel fatigue).

**Verdict: Medium but crowded. Sophisticated bettors already use xG. Edge decays fast.**

---

### Domain 5 — Technology Milestones
**Data:** Papers With Code (AI benchmarks), semiconductor roadmaps, patent filings.

**Edge:**
- AI capability follows predictable scaling laws (compute × data → capability)
- Historical roadmap slippage rates for chip manufacturing are well-documented
- Researchers with domain expertise consistently beat crowd on milestone timing

**Example markets:** Will GPT-5 release before X? Will AI hit benchmark Y by date Z?

**Verdict: Medium. Requires deep domain expertise. Low competition.**

---

### Domain 6 — Geopolitics / Conflict
**Data:** ACLED (conflict events 1997–present), GDELT (global news, daily), historical ceasefire patterns.

**Edge:** Conflict escalation follows statistical patterns (power laws). Academic models outperform crowd.
**Caveat:** Single unexpected decision breaks any model. High tail risk.

**Verdict: Weak-medium. Too much noise. Avoid until other domains proven.**

---

### Domain 7 — Elections / Politics
**Data:** 100+ years of polling, electoral history, economic voting models.

**Edge:** Systematic polling bias corrections. Economic fundamentals models outperform polls 12+ months out.
**Caveat:** Most competed domain on Polymarket. Billions traded in 2024 US election. Edge very thin.

**Verdict: Avoid. Too crowded.**

---

### Domain 8 — Astronomy / Natural Events (Underexplored)
**Data:** NASA JPL orbital mechanics (deterministic), USGS earthquake frequency, solar cycle records 400yr.

**Edge:**
- Astronomical events are deterministic — crowd misprices certainties
- Earthquake probability in a region is calculable — crowd uses availability bias
- Almost nobody building models here — least competed domain on the platform

**Example markets:** Will solar flare cause X disruption? Will magnitude 7+ quake hit X region?

**Verdict: Niche, thin liquidity — but potentially least competed edge available.**

---

### Polymarket Domain Rankings

| Domain | Data quality | Edge strength | Competition | Verdict |
|--------|-------------|---------------|-------------|---------|
| Economics / macro | Excellent | Strong | Medium | Build this |
| Weather | Excellent | Strong | Low | Build this |
| Epidemiology | Good | Medium-strong | Low | Research |
| Sports | Excellent | Medium | High | Crowded |
| Technology | Good | Medium | Low-medium | Needs expertise |
| Geopolitics | Moderate | Weak-medium | Low | Risky |
| Elections | Excellent | Weak | Very high | Avoid |
| Astronomy | Excellent | Strong (niche) | Very low | Underexplored |

---

### Polymarket vs Kalshi

| | Polymarket | Kalshi |
|--|-----------|--------|
| Regulated | No (decentralised) | Yes (CFTC) |
| Access | Global (grey area for US persons) | Primarily US |
| Currency | USDC (crypto) | USD (bank) |
| Account setup | Crypto wallet (MetaMask) | Traditional KYC |
| API trading | Yes (wallet-based, more complex) | Yes (traditional REST) |
| Weather markets | Limited but growing | Better coverage |
| Liquidity | Higher overall | Lower overall |
| Edge window | Narrowing (high volume) | Still early |

**For Irish access:** Polymarket is the more accessible platform. Kalshi has geographic
restrictions. Onboarding requires: MetaMask wallet → USDC via Coinbase/Kraken → connect to Polymarket.

### Labour / Skills
- **Geographic salary arbitrage:** Hire senior engineers at $120k in lower cost-of-living cities
  vs $200k in San Francisco. Same output, different price. Edge closing as remote work normalises.
- **Skills mismatch arbitrage:** Certain skills underpriced because employers haven't recognised
  value yet. Data science in 2012 was massively underpriced — early movers captured the premium.

### Real Estate
- **Neighbourhood trajectory:** Buy before gentrification signal is obvious. Big data inputs:
  planning applications, business licence filings, school rating trends, new transport links.
- **Short-term rental yield arbitrage:** Long-term lease a property, sublet on Airbnb at higher
  nightly rates. Statistical edge: model occupancy rates by neighbourhood, season, local events.

### Retail / E-commerce
- **Amazon retail arbitrage:** Buy discounted products at physical retailers, resell on Amazon.
  Scaled with big data: scrape prices, barcode scanners in stores, ML model predicts margin.
- **Price dispersion arbitrage:** Same product, different prices across regions or platforms.
  Pharmaceutical grey market imports are the large-scale version of this.

### Healthcare
- **Sepsis early warning:** Watch vitals continuously. Statistical model fires alert when
  trajectory matches sepsis pattern. Clinician acts — system is the signal layer.
- **Clinical trial data arbitrage:** Better statistical model of trial outcomes → price biotech
  acquisition targets more accurately than the market → buy undervalued biotech pre-readout.

### Infrastructure / DevOps
- **Auto-scaling:** Watch CPU/memory/latency. Scale up when threshold breached, scale down when
  normalised. AWS Auto Scaling is an algo trader for compute — identical architecture.
- **Anomaly detection + auto-remediation:** Watch error rates, latency, disk usage. Detect
  statistical deviation from baseline (same as our regime classifier). Auto-restart, page on-call.

### Finance (adjacent to trading)
- **Invoice chasing automation:** Watch due dates vs received. Day 0: invoice. Day +7: reminder.
  Day +14: escalation. Day +30: collections flag. Automated, rule-based, data-logged.
- **Fraud detection:** Watch transaction patterns. Flag statistical deviation from personal
  baseline. Block / challenge with 2FA. Every bank runs this.

---

## The Common Structure

Every example maps to the same components:

| Component | Trader version | General version |
|-----------|---------------|-----------------|
| Data feed | Price bars (Alpaca) | Sensors, APIs, scrapers |
| Signal | StochRSI threshold | Any statistical condition |
| Action | Buy/sell order | Relay, API call, alert, reorder |
| Risk management | Stop loss, position size | Budget cap, rate limiter, human gate |
| Exit | K-signal or stop | Condition reversal |
| Logging | `research.db` | Any database |
| Analysis | Backtesting | Simulation / replay on historical data |

---

## Key Insight: Backtesting as a General Capability

The trader's most transferable capability is **backtesting** — replaying historical data to
validate rules before deploying. Most automation systems have no equivalent. They run on guessed
thresholds with no evidence of whether they work.

An irrigation system that can replay 10 years of weather + soil data to validate its trigger
thresholds is far more powerful than one using a fixed threshold someone guessed.

**The backtest engine (`backend/engine/`) is domain-agnostic at its core:**
- Time-series data in → signal function → action → state tracking → metrics out
- Swapping price bars for sensor readings, and buy/sell for relay/API, is mostly a data layer change
- The statistics (Sharpe-equivalent, drawdown, win rate) translate directly to any domain

---

## Development Candidates (if ever pursued)

Research sequentially, not in parallel. Each Stage 2 PoC is ~1–2 weeks.
Validate one, decide whether to branch to new repo, then move to next.

**Stage gate before branching to own repo:**
- [ ] Edge confirmed in backtest with real historical data
- [ ] Execution API tested and working
- [ ] Platform account access confirmed
- [ ] Risk/sizing model defined
- [ ] Ready to run paper/test mode live

### Trading (this repo — closest to existing codebase)
1. **GLD/IAU pairs trading** — most natural. Data exists. Need: short selling, dual-symbol runner.
2. **Gold/silver ratio mean-reversion** — daily bars, longer hold. Data exists (yfinance 2004+).
3. **GLD vs DXY regime conditioning** — enhance regime classifier with USD data. 1 new data fetch.
4. **Volatility arb on GLD options** — requires options execution layer rebuild. Medium effort.

### Prediction Markets (new repo when ready)
5. **Weather prediction alpha** — NOAA/ERA5 + ENSO regime model → Polymarket/Kalshi. Same
   architecture as trader. Most interesting non-trading candidate. Build first.
6. **Economics / macro prediction alpha** — FRED data + surprise delta model → Polymarket.
   Directly mirrors event_surprise.py. Build alongside or immediately after weather.
7. **Weather true arbitrage** — opportunistic layer on top of #5. Monitor Kalshi + Polymarket
   for same outcome priced differently. Only viable when liquidity exists on both sides.
8. **Epidemiology / public health** — CDC/WHO seasonal data + ENSO conditioning → Polymarket.
   Low competition, good data. Research after weather and economics proven.
9. **Astronomy / natural events** — NASA JPL + USGS data. Least competed domain. Niche.

### Hardware / Infrastructure
10. **Energy tariff arbitrage** — Octopus Agile API + battery/immersion hardware. Reuses backtest
    engine structure for threshold optimisation over historical tariff data.

---

*Last updated: Apr 11 2026 (session 4 — Polymarket domains added: 8 domains ranked by data quality/edge/competition, Polymarket vs Kalshi comparison, Irish access notes, dev candidates restructured with stage gate)*
