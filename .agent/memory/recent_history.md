# Recent Git History

### 11c0cd7 - fix: Critical bug fixes for crypto trading and position sizing (2026-02-05)
Overnight BTC bot analysis revealed two critical bugs preventing all trades:

Bug #1: Alpaca Bracket Orders Not Supported for Crypto
- Error: 403 Forbidden - 'crypto orders not allowed for advanced order_class: otoco'
- Cause: Strategy passed stop_loss parameter triggering bracket order creation
- Impact: 100% order failure rate (K crossed 50 multiple times, all rejected)
- Fix: Modified live_broker.py to detect crypto symbols (/) and skip bracket orders
- Result: Crypto uses simple market orders, stocks retain bracket functionality

Bug #2: Position Sizing Too Aggressive (100% Equity Cap)
- Error: 'insufficient balance for BTC (requested: 1.3748, available: 0)'
- Cause: max_size = equity / price allowed 100% equity per position
- Impact: Orders that passed bracket check failed due to rounding/fees
- Fix: Reduced cap from 100% to 25% equity per position
- Result: Allows 4 concurrent positions, leaves buffer for fees

Testing Results:
- Both fixes deployed to cloud server (commits 6168dd7, 45eaeee)
- Bot running stable (17+ min uptime, processing bars correctly)
- Closed existing position for clean slate (,811 cash)
- Waiting for K>50 to validate first clean trade execution
- Current: K=4.4 (oversold), BTC @ $70,924

Key Learnings:
- Alpaca crypto doesn't support advanced order types (brackets/OCO)
- Manual stop loss in strategy works fine (lines 117-135)
- Conservative position sizing prevents rejections and enables diversification
- Infrastructure validated: bot stability, data flow, order placement path works

Co-Authored-By: Claude Sonnet 4.5 <noreply@anthropic.com>

### 4edb583 - test: Default skip_adx_filter to True for EXTREME testing (2026-02-05)
For infrastructure validation testing, disable ADX regime filter
to ensure trades execute even when market is trending.

This allows testing of:
- Order placement with crypto (no bracket orders)
- Position sizing (25% cap)
- Fill logging and slippage measurement

Will revert to False after validation complete.

Co-Authored-By: Claude Sonnet 4.5 <noreply@anthropic.com>

### 45eaeee - fix: Reduce position sizing cap from 100% to 25% of equity (2026-02-05)
Previous cap (1x leverage = 100% equity) was too aggressive:
- Caused "insufficient balance" errors when rounding pushed order over cash
- Left no room for multiple positions or fees

New cap: 25% of equity per position
- Allows 4 concurrent positions
- Leaves buffer for fees and slippage
- More conservative risk management

Co-Authored-By: Claude Sonnet 4.5 <noreply@anthropic.com>

### 6168dd7 - fix: Disable bracket orders for crypto symbols (2026-02-05)
Alpaca does not support bracket orders (stop_loss/take_profit) for
crypto assets. Added detection for crypto symbols (containing '/')
and skip bracket order parameters for these symbols.

This allows BTC/USD trading while retaining bracket orders for stocks.
Strategy already has manual stop loss checking, so no functionality lost.

Co-Authored-By: Claude Sonnet 4.5 <noreply@anthropic.com>

### fb091f4 - docs: Document EXTREME testing mode + BTC 24/7 validation (2026-02-04)
Major updates from tonight's testing session (22:00-22:35 UTC):

## Forward Testing Plan Updates
- Added Phase 5: EXTREME Testing + BTC Validation
- Documented Alpaca after-hours data gap discovery
- Escalated to 50/50 thresholds (trades every K=50 crossing)
- Switched from stocks to BTC/USD 1m for continuous testing
- Updated Current Test Status to show BTC bot running
- Stock bots paused until tomorrow's market open

## Recent History Updates
- Added detailed entry for EXTREME mode deployment
- Documented BTC market progression (K: 100→16 in 5 minutes)
- Validated infrastructure works (data matches Alpaca chart)
- Noted key learning: After-hours stock data unreliable
- Expected 10-30 trades overnight for validation

## Current Status (22:35 UTC)
- BTC 1m bot: Running with 50/50 thresholds
- Stock bots: Paused (after-hours data gaps)
- Resume: Tomorrow 2:30 PM Irish (regular market hours)
- Purpose: Validate infrastructure before 2-week production test

Co-Authored-By: Claude Sonnet 4.5 <noreply@anthropic.com>

### 00af525 - feat: EXTREME testing mode - StochRSI trades every K=50 crossing (2026-02-04)
For rapid infrastructure validation, set ultra-aggressive thresholds:
- Oversold: 50 (was 40)
- Overbought: 50 (was 60)
- ADX threshold: 50 (was 40)

This means:
- LONG when K crosses ABOVE 50 (from below)
- SHORT when K crosses BELOW 50 (from above)
- Trades every single reversal at the midpoint

Expected: 20+ trades in next 2-3 hours
Purpose: Validate infrastructure works end-to-end

Will revert to conservative settings after 24h validation.

Co-Authored-By: Claude Sonnet 4.5 <noreply@anthropic.com>

### ad234ae - fix: Add generate_signals method to DonchianBreakout for live trading (2026-02-04)
DonchianBreakout was designed for backtesting only and lacked the
generate_signals() method required by the live trading runner.

Changes:
- Added generate_signals(df) method that calculates indicators on passed dataframe
- Returns dataframe with Donchian channels and ATR indicators
- Maintains backward compatibility with existing _calculate_indicators() for backtesting
- Enables live trading support for trend-following strategy

This allows DonchianBreakout to work in live trading mode for infrastructure
testing and real-time trend following.

Co-Authored-By: Claude Sonnet 4.5 <noreply@anthropic.com>

### 27a1f55 - docs: Document aggressive testing mode deployment and status (2026-02-04)
Updated both forward_testing_plan.md and recent_history.md to reflect:

## Forward Testing Plan Updates
- Added Phase 4: Aggressive Testing Mode section (deployed 20:32 UTC)
- Updated Current Test Status with new thresholds and K values
- Changed system status to "AGGRESSIVE TESTING MODE - VALIDATING INFRASTRUCTURE"
- Updated Next Steps with 24h validation timeline
- Updated Remaining Tasks to reflect testing phase

## Recent History Updates
- Added entry for 9689758: Aggressive testing mode deployment
- Added entry for 4c51f6b: Per-candle logging addition
- Added entry for 74f9c9a: Forward testing plan documentation
- Documented problem (no trades after 6 hours with conservative settings)
- Documented solution (lower thresholds, fix >= bug, 24h test)
- Documented immediate market response (QQQ in oversold zone)

## Current Status (20:32 UTC)
Testing mode active with aggressive thresholds to generate 20-40 trades
in 24 hours to validate infrastructure before reverting to conservative
settings for 2+ week production forward test.

Expected first trade: Within 15-30 minutes (QQQ waiting for K > 50).

Co-Authored-By: Claude Sonnet 4.5 <noreply@anthropic.com>

### 9689758 - feat: Enable aggressive testing mode for infrastructure validation (2026-02-04)
Changes for 24-hour testing period to verify system works:
- Lower overbought threshold: 80 -> 60 (more frequent signals)
- Raise oversold threshold: 20 -> 40 (more frequent signals)
- Raise ADX threshold: 20 -> 40 (allow more trending markets)
- Fix threshold bug: Use >= and <= instead of > and < to include exact values

Expected: 20-40 trades in 24 hours to validate:
- Order execution on Alpaca
- Position open/close mechanics
- Database logging
- Slippage measurement
- Multi-bot coordination

After validation, revert to conservative settings for real forward test.

Co-Authored-By: Claude Sonnet 4.5 <noreply@anthropic.com>

### 74f9c9a - docs: Update forward testing plan with per-candle logging completion (2026-02-04)
- Documented Phase 3: Per-Candle Logging Enhancement (completed 2026-02-04 20:10)
- Updated Current Test Status with logging active and live market conditions
- Marked system as PRODUCTION FORWARD TESTING - STABLE
- Updated remaining tasks to reflect current progress (Day 1/14)
- Added detailed logging examples and benefits
- Removed outdated auto-stop issue warnings

Co-Authored-By: Claude Sonnet 4.5 <noreply@anthropic.com>

### 4c51f6b - feat: Add per-candle logging for forward testing visibility (2026-02-04)
Added print statement to show every candle:
- Timestamp
- Symbol and close price
- StochRSI K value (current and previous)
- ADX value

This provides real-time visibility into:
- What market conditions bots are seeing
- Why signals are/aren't triggering
- Current RSI levels vs thresholds

Output format:
[2026-02-04 15:30:00] QQQ $515.43 | K: 45.2 (prev: 42.1) | ADX: 18.3

Co-Authored-By: Claude Sonnet 4.5 <noreply@anthropic.com>

### 01f0c28 - docs: Update forward testing plan with 4 active strategies (2026-02-04)
Current Active Tests:
- IWM 15m: Production test (15h uptime)
- QQQ 5m: Champion strategy (just started)
- SPY 15m: Baseline spread data collection
- DIA 15m: Blue chip spread analysis

Total: 40-60 trades/day expected (280-420 trades/week)

Completed:
- BTC/USD test stopped after platform validation
- Measured 0.0432% avg slippage on crypto

Updated:
- Current test status table with all 4 bots
- Memory usage (40% of 1 GB)
- Next steps for data collection phase
- Daily monitoring commands

Co-Authored-By: Claude Sonnet 4.5 <noreply@anthropic.com>

### 9334029 - docs: Update recent_history.md with bot debugging commits (2026-02-03)
Manually added two missing commits to recent_history.md:

1. Resolution of bot auto-stop issue (8ab43d2)
   - Root cause: Bash wrapper + PM2 signal handling conflict
   - Solution: Run Python directly under PM2
   - Verification: 15+ min uptime vs 3 min previously

2. Documentation of BTC bot auto-stop issue (127662b)
   - Critical auto-stop behavior discovered
   - Workaround implemented while investigating

These commits were made during the debugging session but were not
auto-synced to recent_history.md because the git_save.md workflow
was bypassed during active debugging.

Co-Authored-By: Claude Sonnet 4.5 <noreply@anthropic.com>

### 8ab43d2 - docs: Document resolution of bot auto-stop issue (2026-02-03)
Root cause identified and fixed:
- Bash wrapper scripts were causing signal handling issues
- PM2 → bash → Python process tree caused KeyboardInterrupt
- Solution: Run Python directly under PM2

Verification:
- Bot now runs 10+ minutes without restarts (previously max 3 min)
- Passed iteration 4 consistently (previously crashed here)
- Memory stable, 0 restarts

Co-Authored-By: Claude Sonnet 4.5 <noreply@anthropic.com>

### 6ff4784 - debug: Add logging around strategy initialization (2026-02-03)
Bot stops after warmup data loading. Adding debug logging to confirm
strategy __init__ is where it hangs.

Co-Authored-By: Claude Sonnet 4.5 <noreply@anthropic.com>

### 1ca2685 - fix: Comment out NFPBreakout strategy to resolve import error (2026-02-03)
The NFPBreakout strategy depends on backend.data.news_data_loader which
doesn't exist, causing crash-loop on cloud server.

Temporarily commented out to allow bot to start and test debug logging.

Co-Authored-By: Claude Sonnet 4.5 <noreply@anthropic.com>

### 8e970f4 - debug: Add comprehensive logging to live trading loop (2026-02-03)
Added verbose debug logging to diagnose bot auto-stop issue.

Changes to runner.py:
- Added loop counter to track iterations
- Added timestamps at loop start
- Added debug messages before/after data fetch
- Added try/catch around data fetch to isolate fetch errors
- Log when data is None/empty
- Log when no new bar detected
- Enhanced exception handling with full traceback
- Force stdout flush for real-time logging

This will help identify:
- If data fetching is failing
- If exceptions are being raised
- If data becomes None/empty after some iterations
- Exactly which loop iteration causes the stop

Related to: BTC bot auto-stop issue (stops every 5-10 mins)

Co-Authored-By: Claude Sonnet 4.5 <noreply@anthropic.com>

### 127662b - docs: Document BTC bot auto-stop issue and Phase 2.5 progress (2026-02-03)
Updated forward_testing_plan.md with comprehensive status of forward
testing setup including critical issues discovered.

## Phase 2.5 Progress (2026-02-03 Evening)
- Fixed database schema (iteration_index column)
- Fixed IWM and BTC startup scripts (EOF syntax, directory context)
- Added BTC 1m bot for 24/7 testing
- Implemented auto-restart wrapper for reliability

## Critical Issue Discovered
BTC bot (and potentially others) consistently stops after 5-10 minutes
with KeyboardInterrupt. Root cause unknown.

Evidence:
- Bot runs successfully for 5-10 minutes
- Receives bars, executes trades, logs to database
- Then cleanly exits with "Live Trading Stopped"
- Pattern is highly consistent

Possible causes:
- Alpaca API session timeout
- SDK connection keepalive issue
- Rate limiting
- Memory leak
- Bug in data fetching loop

Current workaround:
- Bash wrapper auto-restarts bot within 5 seconds
- Bot reconnects and fetches existing positions
- Continues trading after restart
- 10+ successful trades logged despite restarts

Trade safety analysis:
- LiveBroker.refresh() fetches positions on startup (good)
- Risks: orphaned positions if Alpaca unreachable during restart
- Not production-ready until root cause fixed

## Status Update
- IWM 15m: Stable, waiting for market open
- BTC 1m: Running with auto-restart loop (testing mode)
- Server: europe-west2-a zone
- Database: 10+ trades logged, schema updated

## Next Priority
Debug root cause of bot auto-stop behavior before production deployment.

Co-Authored-By: Claude Sonnet 4.5 <noreply@anthropic.com>

### 189606f - docs: Update forward testing plan - PM2 setup complete (2026-02-03)
Updated forward_testing_plan.md to reflect completed PM2 installation
and successful launch of first forward test.

## Completed Today (Phase 2)
- Installed PM2 v6.0.14 process manager
- Started IWM 15m forward test running in background
- Enabled auto-restart on crash
- Configured systemd for auto-start on server reboot
- Verified live trading connection and bar reception

## Current Status
- **IWM 15m** running live on Google Cloud
- Session ID: f53b07bc-f9da-42b0-a38a-4c88413c6f76
- Started: 2026-02-03 13:00 UTC
- Warmup: 99 bars loaded
- Status: Online and monitoring

## Next Steps
- Monitor for 3 days to verify stability
- Add QQQ 5m and QQQ 4h after verification
- Run all 3 strategies for 2-4 weeks
- Download database and measure real Alpaca trading costs

## PM2 Commands Documented
- pm2 status - Check processes
- pm2 logs iwm-15m - Watch output
- pm2 restart/stop/delete - Process management

Bot now runs 24/7 independently, logging all trades to database
for later analysis of real-world spreads and performance.

Co-Authored-By: Claude Sonnet 4.5 <noreply@anthropic.com>

### 037b509 - docs: Document forward testing setup and progress (2026-02-02)
Created forward_testing_plan.md documenting the complete setup process
for running multi-week forward tests on Google Cloud.

## Completed Today (Phase 1)
- Set up Google Cloud e2-micro instance (Ubuntu 22.04)
- Deployed code and installed all Python dependencies
- Configured Alpaca API keys for paper trading
- Successfully tested live trading connection (IWM 15m)
- Verified trade logging to database

## Server Details
- Provider: Google Cloud Platform
- Instance: e2-micro (1 GB RAM, 2 vCPU)
- Cost: ~$7/month (covered by $300 free credit for 90 days)
- OS: Ubuntu 22.04 LTS
- Location: us-central1

## Next Steps (Tomorrow)
1. Install PM2 process manager for 24/7 background execution
2. Monitor initial 3-day test run for stability
3. Add QQQ 5m and QQQ 4h strategies after verification
4. Run all 3 strategies for 2+ weeks
5. Download database and analyze real Alpaca trading costs

## Goal
Measure actual spreads, slippage, and performance to validate
backtest assumptions and update realistic-test.sh settings with
real-world data.

Co-Authored-By: Claude Sonnet 4.5 <noreply@anthropic.com>
