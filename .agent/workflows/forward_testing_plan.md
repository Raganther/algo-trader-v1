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

### 🔧 Phase 2.5: Debugging & BTC Addition - IN PROGRESS (2026-02-03 Evening)

**Issues Found & Fixed:**
- ❌ Database schema missing `iteration_index` column (crash-looping bots)
  - ✅ Fixed: Added column via Python on cloud server
- ❌ IWM startup script had malformed EOF syntax
  - ✅ Fixed: Rewrote `start_iwm.sh` with proper bash syntax
- ❌ PM2 directory context issue causing module import errors
  - ✅ Fixed: All bots now use startup scripts with `cd ~/algo-trader-v1`

**BTC 1m Bot Added (Testing Platform):**
- ✅ Created `start_btc_loop.sh` with auto-restart wrapper
- ✅ Bot runs 24/7 on BTC/USD (trades continuously, not market hours)
- ✅ Generating high-frequency trades for Alpaca integration testing
- ⚠️ **CRITICAL ISSUE DISCOVERED:** Bot stops consistently after 5-10 minutes

### ✅ Critical Issue RESOLVED: Bot Auto-Stop Behavior

**Problem (RESOLVED):**
The BTC bot consistently stopped after 3-4 minutes with `KeyboardInterrupt`:
- Completed iterations 1, 2, 3 successfully ✅
- Then received KeyboardInterrupt at start of iteration 4 ❌
- Happened consistently at ~3 minute mark

**Root Cause Identified:**
- ❌ Bash wrapper scripts (`start_btc_loop.sh`) were causing signal handling issues
- ❌ PM2 managing bash → bash managing Python created problematic process tree
- ❌ Signal propagation (likely SIGHUP/SIGTERM) reached Python as KeyboardInterrupt

**Solution:**
✅ **Run Python directly under PM2** (no bash wrapper)

**Working Command:**
```bash
cd ~/algo-trader-v1
pm2 start 'python3 -u -m backend.runner trade --strategy RapidFireTest --symbol BTC/USD --timeframe 1m --paper' --name btc-1m
pm2 save
```

**Verification (2026-02-03 23:01-23:07):**
```
Loop 1: 23:01:38 - Completed ✅
Loop 2: 23:02:39 - Completed ✅
Loop 3: 23:03:40 - Completed ✅
Loop 4: 23:04:40 - **Completed successfully!** ✅  (Previously crashed here)
Loop 5: 23:05:41 - Completed ✅
Loop 6: 23:06:42 - Completed ✅
Loop 7+: Continuing...
```

**PM2 Status After Fix:**
- Uptime: 10+ minutes (previously max 3 minutes)
- Restarts: **0** (previously constant restarts)
- Memory: Stable at ~115 MB
- CPU: 0%

**Test Methodology Used:**
1. Added debug logging to identify exact crash point
2. Tested bot locally on Mac → worked perfectly (proved code was correct)
3. Compared cloud vs local environments
4. Tested direct SSH execution vs PM2 wrapper vs PM2 direct
5. Isolated bash wrapper as the culprit

**Lesson Learned:**
When using PM2 for long-running Python processes, avoid bash wrappers. PM2 has built-in auto-restart and monitoring - let it manage Python directly.

### Current Test Status (2026-02-04 14:30 UTC)

| Bot | Strategy | Symbol | TF | Status | Uptime | Memory | Purpose |
|-----|----------|--------|----|----|--------|--------|---------|
| **iwm-15m** | StochRSI | IWM | 15m | 🟢 Live | 15h+ | 78.6 MB | Production test (+19.79% realistic) |
| **qqq-5m** | StochRSI | QQQ | 5m | 🟢 Live | 5m | 105.9 MB | ⭐ Champion (+44.9% realistic) |
| **spy-15m** | StochRSI | SPY | 15m | 🟢 Live | 1m | 101.8 MB | Baseline spreads (most liquid) |
| **dia-15m** | StochRSI | DIA | 15m | 🟢 Live | 1m | 102.0 MB | Blue chip spread analysis |

**Platform Status:**
- Total Memory: 388 MB / 958 MB (40% used)
- All bots: 0 restarts ✅
- Server: Running directly under PM2 (no bash wrappers)
- Market: Opening now (9:30 AM ET)

**Expected Trade Volume:**
- QQQ 5m: 15-25 trades/day
- SPY 15m: 8-12 trades/day
- IWM 15m: 8-12 trades/day
- DIA 15m: 6-10 trades/day
- **Total: 40-60 trades/day** (280-420 trades/week)

**Tests Completed:**
- ✅ BTC/USD 1m - Platform validation complete (23 trades, 0.0432% avg slippage measured)
- Stopped after proving infrastructure stability

**Server Details:**
- Location: europe-west2-a (changed from us-central1)
- Instance: algotrader2026
- Access: `gcloud compute ssh algotrader2026 --zone=europe-west2-a`

**Database Status:**
- ✅ 10+ BTC trades logged since 20:38 UTC
- ✅ Schema updated with iteration_index
- ✅ Trades show before/after restart continuity

---

## Next Steps

### 1. Active Data Collection Phase (Weeks 1-2)
- ✅ **Day 1 (2026-02-04):** 4 strategies running, collecting live data
- ⏳ **Days 2-7:** Monitor daily for stability and trade execution
- ⏳ **Week 2:** Continue collection, target 500+ total trades

**Daily Check Commands:**
```bash
# Check all bots status
gcloud compute ssh algotrader2026 --zone=europe-west2-a
pm2 status

# View recent activity
pm2 logs qqq-5m --lines 50
pm2 logs iwm-15m --lines 50

# Quick health check (all bots)
pm2 status | grep -E "online|stopped|errored"
```

**What to Monitor:**
- Bot uptime (should increase daily)
- Restart count (should stay at 0)
- Memory usage (should be stable ~400 MB)
- Error logs (should be empty)

### 2. Database Analysis (After 2 Weeks)
Once we have 500+ trades across all strategies:

```bash
# Download database from server
gcloud compute scp algotrader2026:~/algo-trader-v1/backend/research.db ./research_cloud.db --zone=europe-west2-a

# Analyze spread data
python3 -m backend.analyze_results --live

# Calculate measured spreads by symbol
# Compare to backtest assumptions
# Update realistic-test.sh with real values
```

### 3. Optional: Add More Strategies
If memory/CPU allows and we want more data:

```bash
# QQQ 1m (ultra high frequency - 50-100 trades/day)
cd ~/algo-trader-v1
pm2 start 'python3 -u -m backend.runner trade --strategy StochRSIMeanReversion --symbol QQQ --timeframe 1m --paper' --name qqq-1m
pm2 save

# OR QQQ 4h Donchian (low frequency trend-following)
pm2 start 'python3 -u -m backend.runner trade --strategy DonchianBreakout --symbol QQQ --timeframe 4h --paper' --name qqq-4h
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

**Phase 2: Setup & Debugging**
- [x] Install PM2 and start background process ✅ (2026-02-03)
- [x] Fix database schema (iteration_index) ✅ (2026-02-03)
- [x] Fix startup scripts ✅ (2026-02-03)
- [x] Add BTC bot for testing ✅ (2026-02-03)
- [x] Implement auto-restart wrapper ✅ (2026-02-03)
- [ ] **CRITICAL: Debug bot auto-stop issue** (Next priority)
- [ ] Monitor IWM for 3 days when market opens (In Progress - Day 1/3)

**Phase 3: Production Testing**
- [ ] Fix root cause of bot stopping (required before production)
- [ ] Add QQQ 5m and QQQ 4h strategies (After IWM stability confirmed)
- [ ] Run all 3 strategies for 2+ weeks
- [ ] Download database and analyze results
- [ ] Calculate real Alpaca spreads from trade logs
- [ ] Update realistic-test.sh with measured values
- [ ] Document findings in research insights

---

## Important Notes

### ⚠️ Current System Status
**TESTING MODE - NOT PRODUCTION READY**
- ✅ Bots are running and logging trades
- ✅ Auto-restart wrapper keeps them alive
- ❌ Bot auto-stop issue unresolved (stops every 5-10 mins)
- ❌ Root cause unknown - requires debugging
- **Recommendation:** Use for testing/learning only until root cause is fixed

### Server Management
- **Never stop the server** - bot runs 24/7 in background
- **Reconnect anytime** via Google Cloud Console → SSH or `gcloud compute ssh algotrader2026 --zone=europe-west2-a`
- **Check status** daily for first week to catch issues early
- **Current zone:** europe-west2-a (London region)

### What's Being Logged
Every trade captures:
- Signal price (what strategy wanted)
- Fill price (what Alpaca gave)
- Slippage (difference = real cost)
- Timestamp, side (buy/sell), quantity
- Session ID for grouping trades

### Expected Timeline
- **Week 1 (Current):** Debug bot stability issue, IWM market-hours testing, BTC 24/7 testing
- **Week 2:** Fix root cause, verify stable operation for 72+ hours
- **Week 3-4:** Add QQQ strategies (if stable), run all 3 simultaneously
- **Week 5:** Download database, analyze results, update realistic-test.sh settings

*Timeline extended due to bot auto-stop issue discovery*

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
