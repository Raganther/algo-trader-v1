### 2fca3c2 - docs: Document Phase 7 bug fixes and multi-asset validation results (6 seconds ago)

## Phase 7: Position Tracking Bug Fixes (2026-02-05)

7 critical bugs found and fixed during live BTC/SPY/QQQ testing:

1. Position state lost on restart (strategy.position=0 on init)
   - Fix: Sync with Alpaca after strategy init in runner.py
2. Zone flags re-trigger while holding (duplicate entries)
   - Fix: Move zone logic inside position==0 check
3. Symbol format mismatch BTCUSD vs BTC/USD (exits fail silently)
   - Fix: Store both formats in broker position cache
4. Exit qty lookup uses wrong method (returns None)
   - Fix: Use get_position() which handles both formats
5. Fractional stock orders need DAY TIF
   - Fix: Auto-detect and switch TimeInForce
6. No fractional short selling for stocks + residual positions
   - Fix: Round ALL stock orders to whole shares
7. Exit state not guarded on order failure (ghost flat state)
   - Fix: Only reset position if order returns non-None

## Validation Results
- BTC: 3+ clean round-trips (entry + exit filling correctly)
- SPY: 2 clean round-trips (35 whole shares, no residuals)
- QQQ: Running, waiting for 15m signals
- All trades verified against Alpaca order history

## Files Modified
- backend/runner.py (position sync on startup)
- backend/strategies/stoch_rsi_mean_reversion.py (zone guard, exit guard, get_position)
- backend/engine/live_broker.py (symbol normalization)
- backend/engine/alpaca_trader.py (whole shares, DAY TIF)

Co-Authored-By: Claude Opus 4.5 <noreply@anthropic.com>

---
### 3832ae6 - fix: Round all stock orders to whole shares + guard exit state (42 minutes ago)

- Round both buy and sell for stocks (not just sells) to prevent
  fractional residuals (buy 35.6 → sell 35 → 0.6 orphan)
- Only reset position state if exit order actually succeeds
- Prevents ghost state where strategy thinks it exited but didn't

Co-Authored-By: Claude Opus 4.5 <noreply@anthropic.com>

---
### d8e4439 - fix: Round stock sell orders to whole shares (no fractional shorts) (3 hours ago)

Alpaca does not allow fractional short selling for stocks.
Round sell qty to int for non-crypto symbols.

Co-Authored-By: Claude Opus 4.5 <noreply@anthropic.com>

---
### 4a8ace5 - test: Default skip_adx_filter to True for forward testing validation (3 hours ago)

Avoids need for --parameters JSON via PM2 (which causes quoting
issues with wrapper scripts). Strategy defaults already have
EXTREME thresholds (50/50). Will revert after validation.

Co-Authored-By: Claude Opus 4.5 <noreply@anthropic.com>

---
### 7633a95 - fix: Use DAY time-in-force for fractional stock orders (3 hours ago)

Alpaca requires fractional stock orders to use DAY (not GTC).
Auto-detect fractional qty for non-crypto symbols and switch TIF.

Co-Authored-By: Claude Opus 4.5 <noreply@anthropic.com>

---
### 3af74ad - fix: Fix position tracking bugs for live crypto trading (5 hours ago)

- Sync position state with Alpaca on startup (prevents duplicate entries after restart)
- Normalize symbol keys in broker cache (BTCUSD + BTC/USD) so lookups don't silently fail
- Move zone flag logic inside position==0 check (prevents re-triggering while holding)
- Use get_position() for exit sizing (handles symbol format mismatch, returns actual qty)

Co-Authored-By: Claude Opus 4.5 <noreply@anthropic.com>

---
### 5dd8d99 - fix: Critical bug fixes for crypto trading and position sizing (7 hours ago)

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

---
### 4edb583 - test: Default skip_adx_filter to True for EXTREME testing (8 hours ago)

For infrastructure validation testing, disable ADX regime filter
to ensure trades execute even when market is trending.

This allows testing of:
- Order placement with crypto (no bracket orders)
- Position sizing (25% cap)
- Fill logging and slippage measurement

Will revert to False after validation complete.

Co-Authored-By: Claude Sonnet 4.5 <noreply@anthropic.com>

---
### 45eaeee - fix: Reduce position sizing cap from 100% to 25% of equity (9 hours ago)

Previous cap (1x leverage = 100% equity) was too aggressive:
- Caused "insufficient balance" errors when rounding pushed order over cash
- Left no room for multiple positions or fees

New cap: 25% of equity per position
- Allows 4 concurrent positions
- Leaves buffer for fees and slippage
- More conservative risk management

Co-Authored-By: Claude Sonnet 4.5 <noreply@anthropic.com>

---
### 6168dd7 - fix: Disable bracket orders for crypto symbols (9 hours ago)

Alpaca does not support bracket orders (stop_loss/take_profit) for
crypto assets. Added detection for crypto symbols (containing '/')
and skip bracket order parameters for these symbols.

This allows BTC/USD trading while retaining bracket orders for stocks.
Strategy already has manual stop loss checking, so no functionality lost.

Co-Authored-By: Claude Sonnet 4.5 <noreply@anthropic.com>

---
### fb091f4 - docs: Document EXTREME testing mode + BTC 24/7 validation (18 hours ago)

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

---
### 00af525 - feat: EXTREME testing mode - StochRSI trades every K=50 crossing (18 hours ago)

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

---
### ad234ae - fix: Add generate_signals method to DonchianBreakout for live trading (18 hours ago)

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

---
### 27a1f55 - docs: Document aggressive testing mode deployment and status (20 hours ago)

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

---
### 9689758 - feat: Enable aggressive testing mode for infrastructure validation (20 hours ago)

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

---
### 74f9c9a - docs: Update forward testing plan with per-candle logging completion (20 hours ago)

- Documented Phase 3: Per-Candle Logging Enhancement (completed 2026-02-04 20:10)
- Updated Current Test Status with logging active and live market conditions
- Marked system as PRODUCTION FORWARD TESTING - STABLE
- Updated remaining tasks to reflect current progress (Day 1/14)
- Added detailed logging examples and benefits
- Removed outdated auto-stop issue warnings

Co-Authored-By: Claude Sonnet 4.5 <noreply@anthropic.com>

---
### 4c51f6b - feat: Add per-candle logging for forward testing visibility (20 hours ago)

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

---
### 01f0c28 - docs: Update forward testing plan with 4 active strategies (26 hours ago)

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

---
### 9334029 - docs: Update recent_history.md with bot debugging commits (2 days ago)

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

---
### 8ab43d2 - docs: Document resolution of bot auto-stop issue (2 days ago)

Root cause identified and fixed:
- Bash wrapper scripts were causing signal handling issues
- PM2 → bash → Python process tree caused KeyboardInterrupt
- Solution: Run Python directly under PM2

Verification:
- Bot now runs 10+ minutes without restarts (previously max 3 min)
- Passed iteration 4 consistently (previously crashed here)
- Memory stable, 0 restarts

Co-Authored-By: Claude Sonnet 4.5 <noreply@anthropic.com>

---