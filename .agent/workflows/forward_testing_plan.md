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

## Progress Update

### ✅ Phase 1: Setup - COMPLETED (2026-02-02)

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

### ✅ Phase 2: PM2 Setup - COMPLETED (2026-02-03)

**Background Process Manager Installed:**
- ✅ Node.js and npm installed
- ✅ PM2 v6.0.14 installed globally
- ✅ IWM 15m forward test started with PM2
- ✅ Process saved to PM2 (`pm2 save`)
- ✅ Auto-startup enabled via systemd
- ✅ Bot survives server reboots

**Current Running Tests:**
- **IWM 15m** (StochRSIMeanReversion)
  - Status: Online
  - Session ID: f53b07bc-f9da-42b0-a38a-4c88413c6f76
  - Started: 2026-02-03 13:00 UTC
  - Warmup: 99 bars loaded

**PM2 Commands Reference:**
```bash
pm2 status              # Check running processes
pm2 logs iwm-15m        # Watch live logs
pm2 logs iwm-15m --lines 100  # Last 100 log lines
pm2 restart iwm-15m     # Restart process
pm2 stop iwm-15m        # Stop process
pm2 delete iwm-15m      # Remove process
```

---

## Next Steps

### 1. Monitor Initial Run (Days 1-3)
- ✅ **Day 1 (Today):** Bot is running, wait for first trades
- ⏳ **Day 2:** Check logs for any trades: `pm2 logs iwm-15m --lines 100`
- ⏳ **Day 3:** Verify stability, check for crashes/errors

**Daily Check Command:**
```bash
# SSH into server
pm2 status
pm2 logs iwm-15m --lines 50
```

### 2. Add Additional Strategies (After 3-Day Stability Test)
Once IWM 15m runs stable for 3 days, add:

```bash
# QQQ 5m (best realistic performer: +44.9%)
pm2 start python3 --name qqq-5m -- -m backend.runner trade --strategy StochRSIMeanReversion --symbol QQQ --timeframe 5m --paper

# QQQ 4h Donchian (realistic: +22.61%)
pm2 start python3 --name qqq-4h -- -m backend.runner trade --strategy DonchianBreakout --symbol QQQ --timeframe 4h --paper

# Save all processes
pm2 save
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

- [x] Install PM2 and start background process ✅ (2026-02-03)
- [ ] Monitor for 3 days to verify stability (In Progress - Day 1/3)
- [ ] Add QQQ 5m and QQQ 4h strategies (After Day 3)
- [ ] Run all 3 strategies for 2+ weeks
- [ ] Download database and analyze results
- [ ] Calculate real Alpaca spreads from trade logs
- [ ] Update realistic-test.sh with measured values
- [ ] Document findings in research insights

---

## Important Notes

### Server Management
- **Never stop the server** - bot runs 24/7 in background
- **Reconnect anytime** via Google Cloud Console → SSH
- **Check status** daily for first week to catch issues early

### What's Being Logged
Every trade captures:
- Signal price (what strategy wanted)
- Fill price (what Alpaca gave)
- Slippage (difference = real cost)
- Timestamp, side (buy/sell), quantity
- Session ID for grouping trades

### Expected Timeline
- **Week 1:** IWM 15m solo run + stability verification
- **Week 2-3:** Add QQQ strategies, all 3 running simultaneously
- **Week 4:** Download database, analyze results, update settings

### How to Download Results (When Ready)
```bash
# From your laptop
gcloud compute scp algotrader2026:~/algo-trader-v1/backend/research.db ~/Downloads/forward_test_results.db --zone=us-central1-a
```

Then analyze locally or merge with backtest database.

---

## Expected Outcome

**Best Case**: Strategies perform close to backtests → Deploy to real money

**Likely Case**: Some strategies fail reality check → Filter to robust ones only

**Worst Case**: All strategies fail → Need better strategy design

**Either way**: We'll know the TRUTH about our strategies before risking real money.

---

*This is a living document. Update as we learn and solve problems.*
