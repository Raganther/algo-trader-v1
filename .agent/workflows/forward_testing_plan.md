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

### ⚠️ Critical Issue: Bot Auto-Stop Behavior

**Problem:**
The BTC bot (and potentially others) consistently stops after 5-10 minutes with `KeyboardInterrupt`:
- Receives bars successfully ✅
- Executes trades on Alpaca ✅
- Logs to database ✅
- Then prints "Live Trading Stopped" and exits ❌

**Evidence:**
```
21:12 - BUY executed ✅
21:13-21:18 - Bars received (6 minutes)
21:19 - "Live Trading Stopped" ❌
21:21 - Auto-restart via wrapper ✅
21:24 - SELL executed ✅ (continues working)
```

**Root Cause: UNKNOWN** - Possible causes:
1. Alpaca API session timeout
2. Alpaca SDK connection keepalive issue
3. Rate limiting after X requests
4. Memory leak causing crash
5. Bug in data fetching loop

**Current Workaround:**
- ✅ Bash wrapper script auto-restarts bot within 5 seconds
- ✅ Bot reconnects to Alpaca and fetches existing positions
- ✅ Continues trading after restart
- ⚠️ Band-aid solution, not a fix

**Trade Safety Analysis:**

*Good News:*
- ✅ `LiveBroker.refresh()` fetches existing positions on startup (live_broker.py:52)
- ✅ Bot should reconnect and continue managing open trades
- ✅ Database shows trades before/after restarts (10+ successful trades logged)

*Risks:*
- ⚠️ If Alpaca is unreachable during restart, `refresh()` fails silently
- ⚠️ Orphaned positions could occur if connection fails
- ⚠️ Order execution timing: trade sent → bot crashes → not logged to database
- ⚠️ Not production-ready until root cause is fixed

**Verification:**
Recent database trades show continuous activity despite restarts:
```
21:24 - SELL 76370.14 (after restart)
21:13 - BUY  76666.88 (before restart)
21:09 - SELL 76764.52
21:08 - BUY  76770.90
```

### Current Test Status (2026-02-03 21:30 UTC)

| Bot | Strategy | Symbol | TF | Status | Health | Issue |
|-----|----------|--------|----|----|--------|-------|
| **iwm-15m** | StochRSI | IWM | 15m | 🟡 Idle | Stable | Waiting for market open |
| **btc-1m** | RapidFire | BTC/USD | 1m | 🟡 Running | **Auto-restart loop** | Stops every 5-10 mins |

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
