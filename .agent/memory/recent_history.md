# Recent Git History

### fe419ef - fix: Fix KeyError in Donchian stop loss - use correct position dict key (2026-02-06)
Live broker stores entry price as position['price'] but Donchian strategy
was using position['avg_price'] (backtest format). Caused KeyError crash
on every bar when holding a position (204 PM2 restarts).

Fixed both long (line 150) and short (line 163) stop loss lookups.

Co-Authored-By: Claude Opus 4.6 <noreply@anthropic.com>

### 7ba8fad - feat: Implement memory system restructure for reliable context (2026-02-06)
Created new files:
- .claude/claude.md - Session primer (auto-read by Claude at startup)
- .claude/hooks/load-context.sh - SessionStart hook shows recent commits
- .claude/settings.json - Hook configuration

Updated files:
- system_manual.md - Added forward testing/live trading section
  - Cloud server management (PM2, deploy flow)
  - Platform constraints (crypto shorts, whole shares, etc.)
  - Critical bug fixes reference
  - Slippage analysis results
- git_save.md - Simplified workflow, removed non-existent curate_memory.py

Memory architecture:
- claude.md = Quick status + signposts (150 lines)
- system_manual.md = Permanent technical reference
- forward_testing_plan.md = Journey history (unchanged)
- recent_history.md = Auto-generated from commits

Benefits:
- Zero manual context loading on new sessions
- Hook auto-shows last 5 commits + file pointers
- Claude reads claude.md automatically
- Clear separation: status vs reference vs history

Co-Authored-By: Claude Opus 4.5 <noreply@anthropic.com>

### 1317cd7 - docs: Document Phase 8 multi-asset expansion and slippage analysis (2026-02-05)
Phase 8 additions:
- Fixed crypto short selling crash (Alpaca doesn't support crypto shorts)
- Added API error handling in live_broker.py (prevents loop crashes)
- Added IWM 5m bot (StochRSIMeanReversion)
- Added DonchianBreakout IWM 5m bot (trend-following comparison)

Slippage Analysis (20 trades):
- SPY: 0.032% avg slippage (13 trades)
- QQQ: 0.060% avg slippage (4 trades)
- IWM: 0.030% avg slippage (3 trades)

Key finding: Live slippage is within expected range, backtest
assumptions validated. IWM has tightest execution.

Current status: 4 bots active (SPY, QQQ, IWM StochRSI + IWM Donchian)

Co-Authored-By: Claude Opus 4.5 <noreply@anthropic.com>

### d5665f0 - fix: Disable short entries for crypto symbols (2026-02-05)
Alpaca doesn't support crypto short selling. Every short attempt was
crashing the live loop (40 crashes, 57 PM2 restarts). The bot appeared
to work because PM2 kept restarting it and position sync recovered.

Now skips the overbought zone flag for crypto symbols (containing '/')
so short entries are never attempted. Stocks retain full long/short.

Co-Authored-By: Claude Opus 4.5 <noreply@anthropic.com>

### 2df6fd6 - fix: Catch API errors in buy/sell to prevent live loop crashes (2026-02-05)
Alpaca APIError (insufficient balance, rejected orders) was unhandled
in LiveBroker.buy() and sell(). Exception propagated up and crashed
the entire live trading loop, causing PM2 restarts.

Now catches exceptions, logs the rejection, and returns None.
Strategy already guards with `if result is not None:` so position
state stays correct.

Co-Authored-By: Claude Opus 4.5 <noreply@anthropic.com>

### bd7738a - docs: Document Phase 7 bug fixes and multi-asset validation results (2026-02-05)
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

### 3832ae6 - fix: Round all stock orders to whole shares + guard exit state (2026-02-05)
- Round both buy and sell for stocks (not just sells) to prevent
  fractional residuals (buy 35.6 → sell 35 → 0.6 orphan)
- Only reset position state if exit order actually succeeds
- Prevents ghost state where strategy thinks it exited but didn't

Co-Authored-By: Claude Opus 4.5 <noreply@anthropic.com>

### d8e4439 - fix: Round stock sell orders to whole shares (no fractional shorts) (2026-02-05)
Alpaca does not allow fractional short selling for stocks.
Round sell qty to int for non-crypto symbols.

Co-Authored-By: Claude Opus 4.5 <noreply@anthropic.com>

### 4a8ace5 - test: Default skip_adx_filter to True for forward testing validation (2026-02-05)
Avoids need for --parameters JSON via PM2 (which causes quoting
issues with wrapper scripts). Strategy defaults already have
EXTREME thresholds (50/50). Will revert after validation.

Co-Authored-By: Claude Opus 4.5 <noreply@anthropic.com>

### 7633a95 - fix: Use DAY time-in-force for fractional stock orders (2026-02-05)
Alpaca requires fractional stock orders to use DAY (not GTC).
Auto-detect fractional qty for non-crypto symbols and switch TIF.

Co-Authored-By: Claude Opus 4.5 <noreply@anthropic.com>

### 3af74ad - fix: Fix position tracking bugs for live crypto trading (2026-02-05)
- Sync position state with Alpaca on startup (prevents duplicate entries after restart)
- Normalize symbol keys in broker cache (BTCUSD + BTC/USD) so lookups don't silently fail
- Move zone flag logic inside position==0 check (prevents re-triggering while holding)
- Use get_position() for exit sizing (handles symbol format mismatch, returns actual qty)

Co-Authored-By: Claude Opus 4.5 <noreply@anthropic.com>

### 5dd8d99 - fix: Critical bug fixes for crypto trading and position sizing (2026-02-05)
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
