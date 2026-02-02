# 🧪 Forward Testing Plan

> **Goal**: Validate backtested strategies with real market execution to measure actual performance and trading costs.

---

## Why Forward Testing?

**Problem**: Our backtests use ESTIMATED trading costs (spread, execution delay).
- Current settings: Guesses based on industry averages
- Unknown: What Alpaca ACTUALLY charges in real fills

**Solution**: Run strategies on Alpaca Paper Trading to measure:
- Real bid-ask spreads
- Real execution slippage
- Real fill delays
- Reality vs backtest performance gap

---

## What We Want to Achieve

### Primary Goal
**Measure real Alpaca trading costs** for our top strategies:
1. StochRSIMeanReversion on QQQ (5m)
2. DonchianBreakout on QQQ (4h)
3. StochRSIMeanReversion on IWM (15m)

### Success Criteria
After 2-4 weeks of paper trading:
- ✅ Know actual average spread per trade
- ✅ Know actual win rate vs backtest prediction
- ✅ Know if strategies survive real execution
- ✅ Update `realistic-test.sh` with measured values

---

## Current System Capabilities

**Already Built**:
- ✅ Paper trading command: `python3 -m backend.runner trade`
- ✅ Live trade logging to database (`live_trade_log` table)
- ✅ Reality Check section in research insights
- ✅ Comparison: Theory (backtest) vs Reality (live)

**Example** (RapidFireTest on BTC/USD):
- Backtest predicted: 66% win rate
- Live reality: 0% win rate → Strategy REJECTED

---

## High-Level Approach

### Phase 1: Setup (Week 1)
- Get cloud server running
- Deploy code to server
- Start ONE strategy for 3-7 days (test run)

### Phase 2: Short Tests (Weeks 2-3)
- Run top 3 strategies for 2 weeks minimum
- Monitor daily, fix issues as they arise
- Collect trade data in database

### Phase 3: Analysis (Week 4)
- Calculate real spreads from trade logs
- Compare backtest vs forward test results
- Update realistic settings with measured data
- Document findings

---

## Key Metrics to Capture

From each forward test, we need:

| Metric | Source | Purpose |
|--------|--------|---------|
| **Signal Price** | Strategy calculation | What we wanted to trade at |
| **Fill Price** | Alpaca execution | What we actually got |
| **Slippage** | Fill - Signal | Real trading cost |
| **Win Rate** | Closed trades | Does strategy actually work? |
| **Return %** | Account equity | Real money performance |

---

## Known Challenges to Solve

1. **Server Availability** - Laptop can't run for weeks
2. **Database Access** - Need to query results while running
3. **Process Monitoring** - Know if it crashes overnight
4. **Data Backup** - Don't lose weeks of results
5. **Multi-Strategy Testing** - Run 3 strategies simultaneously

*We'll tackle each problem incrementally as we build this out.*

---

## Progress Update (2026-02-02)

### ✅ Phase 1: Setup - COMPLETED

**Server Setup:**
- ✅ Google Cloud e2-micro instance created (us-central1)
- ✅ Ubuntu 22.04 LTS installed
- ✅ Python 3.10.12 and dependencies installed
- ✅ Code cloned from GitHub (public repo)
- ✅ Alpaca API keys configured (.env file)
- ✅ Database initialized

**Testing:**
- ✅ Manual test run successful (IWM 15m strategy)
- ✅ Connected to Alpaca Paper Trading
- ✅ Receiving live bars every 15 minutes
- ✅ Trade logging verified

**Server Details:**
- IP: Available via Google Cloud Console
- SSH: Via browser (ssh.cloud.google.com)
- Cost: ~$7/month (covered by $300 free credit for 90 days)

---

## Next Steps (Tomorrow)

### 1. Set Up Background Process (PM2)
```bash
# Install PM2
sudo apt install -y nodejs npm
sudo npm install -g pm2

# Start forward test
pm2 start "python3 -m backend.runner trade --strategy StochRSIMeanReversion --symbol IWM --timeframe 15m --paper" --name "iwm-15m"

# Save and enable auto-restart
pm2 save
pm2 startup
```

### 2. Monitor Initial Run (First 24-48 Hours)
- Check logs daily: `pm2 logs iwm-15m`
- Verify trades are being logged
- Check for errors or crashes

### 3. Add Additional Strategies (After 3-Day Test)
```bash
pm2 start "python3 -m backend.runner trade --strategy StochRSIMeanReversion --symbol QQQ --timeframe 5m --paper" --name "qqq-5m"
pm2 start "python3 -m backend.runner trade --strategy DonchianBreakout --symbol QQQ --timeframe 4h --paper" --name "qqq-4h"
```

### 4. Database Sync Plan
**How data flows:**
- Server database: Forward test results (grows over time)
- Laptop database: Backtest results (static)
- Manual sync: Download server DB after 2 weeks for analysis

**Download command (when ready):**
```bash
# On laptop
gcloud compute scp algotrader2026:~/algo-trader-v1/backend/research.db ~/Downloads/forward_test_results.db --zone=us-central1-a
```

---

## Remaining Tasks

- [ ] Install PM2 and start background process
- [ ] Monitor for 3 days to verify stability
- [ ] Add QQQ 5m and QQQ 4h strategies
- [ ] Run all 3 strategies for 2+ weeks
- [ ] Download database and analyze results
- [ ] Calculate real Alpaca spreads from trade logs
- [ ] Update realistic-test.sh with measured values
- [ ] Document findings in research insights

---

## Expected Outcome

**Best Case**: Strategies perform close to backtests → Deploy to real money

**Likely Case**: Some strategies fail reality check → Filter to robust ones only

**Worst Case**: All strategies fail → Need better strategy design

**Either way**: We'll know the TRUTH about our strategies before risking real money.

---

*This is a living document. Update as we learn and solve problems.*
