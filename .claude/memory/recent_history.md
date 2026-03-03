# Recent Git History

### 27a5b8d - fix: add graceful shutdown handler to prevent zombie trades on pm2 restart (2026-03-03)
PM2 sends SIGTERM on restart but old process could linger and place orders.
Now catches SIGTERM/SIGINT, sets shutdown flag, exits within 1 second.
Sleep broken into 1s intervals for fast response. Bar processing skipped
if shutdown requested.

Co-Authored-By: Claude Opus 4.6 <noreply@anthropic.com>

### a697957 - feat: add server-side stop losses for fractional share orders (2026-03-03)
Alpaca doesn't support bracket orders with fractional shares, so stop
losses were silently not being placed. Now we:

1. Place a separate stop sell order after BUY fill (server-side protection)
2. Cancel + replace stop order when trailing stop ratchets up
3. Cancel stop order before signal-based exits
4. Detect when server-side stop fires externally and reset strategy state

This ensures positions are protected even if the bot hangs or data feed stalls.

Co-Authored-By: Claude Opus 4.6 <noreply@anthropic.com>

### 73f4432 - docs: update claude.md — current status, fix outdated info (2026-03-03)
- Updated to reflect 4 test bots (added GDX), removed gld-15m-enhanced
- Fixed fractional shares status (confirmed working, was incorrectly listed as whole shares only)
- Added bugs found/fixed (fetch window, OOM), known issues, server specs
- Added test vs validated params comparison table
- Removed redundant/outdated sections, consolidated reference info

Co-Authored-By: Claude Opus 4.6 <noreply@anthropic.com>

### 2cd7f16 - docs: update recent_history.md (2026-03-02)
Co-Authored-By: Claude Opus 4.6 <noreply@anthropic.com>

### 3b7364a - fix: increase live fetch window from 2 to 7 days (2026-03-02)
The on_bar guard (i < 50) was silently skipping all signal evaluation
because the 2-day fetch only returned ~32 bars of 15m data (especially
over weekends). This meant zero trades fired today despite big moves.
7 days guarantees 50+ bars even over weekends.

Co-Authored-By: Claude Opus 4.6 <noreply@anthropic.com>

### 1535880 - temp: enable Monday trading for testing (2026-03-02)
All 4 test bots (GLD/IAU/SLV/GDX) — skip_days changed from [0] to [] so they trade today.

Co-Authored-By: Claude Opus 4.6 <noreply@anthropic.com>

### 8476d9f - feat: add GDX 15m test bot script (2026-03-02)
4th precious metals bot — same aggressive test params as GLD/IAU/SLV
for mechanics verification before switching to validated params.

Co-Authored-By: Claude Opus 4.6 <noreply@anthropic.com>

### 9e919c6 - docs: add portfolio manager idea (#20) to ideas.md (2026-02-28)
Dynamic cross-bot position sizing across all 4 validated 15m strategies.
20% total risk budget, compounding on account equity, shared PortfolioManager class.
Expected blended return ~14.8%/yr. Natural next step after execution mechanics verified.

Co-Authored-By: Claude Sonnet 4.6 <noreply@anthropic.com>

### 5b0858b - feat: add IAU 15m to frontend registry (2026-02-28)
Links IAU 15m to stochrsi_enhanced_iau.md for detail page notes.

Co-Authored-By: Claude Sonnet 4.6 <noreply@anthropic.com>

### 9a0e08f - feat: validate IAU 15m StochRSI Enhanced — 4th precious metals edge confirmed (2026-02-28)
IAU 15m full validation (Feb 28):
- Full period (2020-2025): +32.58%, DD 0.72%, 679 trades
- Holdout test (2024-2025): +12.55%, DD 0.66% — minimal degradation
- Walk-forward: 4/4 windows positive (2022: +4.3%, 2023: +3.89%, 2024: +5.0%, 2025: +7.17%)
- All 6 individual years positive

Precious metals thesis now confirmed on 4 assets (GLD 2.54, SLV 2.54, GDX 2.41, IAU ~2.0).
IAU has lowest DD of the group (0.72%) and most consistent year-by-year returns.
Also added idea #19 (full cloud migration) to ideas.md.

Co-Authored-By: Claude Sonnet 4.6 <noreply@anthropic.com>

### 82b66b4 - feat: bear market backtest + GLD daily data (2005-2019) (2026-02-27)
Bear market validation (daily bars, Stooq data):
- Strategy stayed positive through entire 2012-2015 bear (-45.6% GLD)
- Full bear period: +6.0% strategy vs -34.9% B&H
- Every individual bear year positive (2013: +3.6%, 2014: +1.2%, 2015: +2.2%)
- Key reason: only ~15% in-market, catches bounces and exits flat

Weakest period: 2012 (transition year, -0.6%) — choppy indecision
Caveat: daily bars only, not 15m. Directionally encouraging.

Data saved: backend/data/gld_daily_2005_2019.csv (3,737 bars)

Co-Authored-By: Claude Sonnet 4.6 <noreply@anthropic.com>

### 4a4f0ac - fix: guard against duplicate exit signals causing short-sell rejections (2026-02-27)
Before placing a SELL order, check that an open position actually exists.
If flat, log a warning and skip — prevents Alpaca rejecting the order as
a short sell when the strategy fires an exit signal on consecutive bars.

Affects all live bots (gld-test, iau-test, slv-test).

Co-Authored-By: Claude Sonnet 4.6 <noreply@anthropic.com>

### 29dbe5e - docs: session update Feb 27 — slv-test deployed, 3 validated edges (2026-02-27)
Bot fleet now: gld-test + iau-test + slv-test (all PAPER, aggressive params)
Waiting for full trade cycle (entry → trail → exit) before switching to validated params.

Validated edges confirmed this session:
- SLV 15m: Sharpe 2.54, 4/4 WF
- GDX 15m: Sharpe 2.41, 4/4 WF
- trail_atr sweep concluded: keeping 2.0 (1.5 marginal on holdout)

Co-Authored-By: Claude Sonnet 4.6 <noreply@anthropic.com>

### 81c9a4c - feat: add slv-test bot script (aggressive params, paper mode) (2026-02-27)

### da71a42 - feat: validate SLV + GDX 15m edges — precious metals thesis confirmed (2026-02-27)
Three validated 15m edges now confirmed:
- GLD 15m: Sharpe 2.54 (existing)
- SLV 15m: Sharpe 2.54 — +105.3%, DD 2.00%, 4/4 WF pass
- GDX 15m: Sharpe 2.41 — +114.1%, DD 2.02%, 4/4 WF pass

Key findings:
- Params transferred from GLD unchanged — no tuning needed
- Confirms thesis: precious metals mean-revert at 15m within a trend
- trail_atr sweep (1.0-2.5) ran: 1.5 marginal vs 2.0 on holdout, keeping 2.0

Files added:
- scripts/run_focused_tests.py — targeted backtest runner
- scripts/run_validation.py — holdout + walk-forward validator
- .claude/memory/strategies/stochrsi_enhanced_slv.md — SLV strategy card
- .claude/memory/strategies/stochrsi_enhanced_gdx.md — GDX strategy card
- frontend/src/lib/registry.ts — SLV + GDX entries added for dashboard notes

Co-Authored-By: Claude Sonnet 4.6 <noreply@anthropic.com>

### 3f5c853 - docs: GLD 15m full audit + strategy memory update (Feb 27) (2026-02-27)
Full audit of best edge — GLD 15m StochRSI Enhanced:
- Data quality: 36,075 bars, Alpaca IEX 1m→15m resampled, clean
- Full period (2020–Feb 2026): 44.7%, DD 0.69%, 710 trades
- Sharpe 2.54 (computed from equity curve daily returns)
- 2026 YTD: +1.16%, 21 trades
- Parameter sensitivity: robust. min_hold=10 critical. trail_atr=1.5 shows +47.5% (worth exploring)
- Spread sensitivity: profitable to 0.22% (7-20× real GLD spread headroom)
- Buy & Hold: 117.5% vs 44.7% (gold bull run), but Sharpe 0.98 vs 2.54, DD 22% vs 0.69%

Updated stochrsi_enhanced_gld.md with full audit tables.
Updated CLAUDE.md: Sharpe 2.42 → 2.54, session summary updated.

Co-Authored-By: Claude Sonnet 4.6 <noreply@anthropic.com>

### 0c1d3e3 - feat: dashboard fixes + memory update — Feb 27 (2026-02-27)
Frontend fixes:
- DB query: when years were run independently (one iteration per year),
  collect all years via per-year MAX subquery instead of picking single best
  iteration (was showing only 2025 for GLD 1h)
- Markdown map: changed to exact Strategy|SYMBOL|TF keys — GLD 15m notes
  no longer leak onto GLD 1h and other strategy pages
- Detail page: uses getMarkdownFile(strategy, symbol, timeframe) for exact lookup

DB changes (research.db — not in git):
- Inserted enhanced GLD 15m experiment (trailing stop + min hold + skip Mon)
  into experiments as passed, Sharpe=2.54 computed from equity curves
- Ran GLD 1h year-by-year backtests 2020-2025 (rsi:21, stoch:7, OB:80, OS:15,
  sl_atr:3.0), stored in test_runs — detail page now shows full 6-year breakdown

Co-Authored-By: Claude Sonnet 4.6 <noreply@anthropic.com>

### 23b34b9 - feat: strategy dashboard — DB-driven auto-generated cards (2026-02-26)
Replaces hard-coded strategy registry with fully automatic card generation.
Any experiment that passes validation (status='passed') with Sharpe ≥ 1.0
gets a card on the index, sorted by Sharpe descending. No manual step needed
when the overnight engine validates a new edge.

- registry.ts: stripped to markdown file map + status thresholds only
- db.ts: getValidatedStrategies() queries experiments table directly;
  auto-picks best iteration from test_runs for year table + equity curve
- page.tsx: reads from DB, splits into Verified (≥1.3) / Promising sections
- StrategyCard: shows symbol, TF, Sharpe, annualised return, max DD from DB
- Detail page: resolves slug via DB lookup, shows stats + notes if md exists
- Threshold: Sharpe ≥ 1.3 = validated badge, ≥ 1.0 = promising badge

Current validated edges (7): GLD 15m, GLD 1h, GLD 1d, SLV 15m, IAU 1h,
XLE 1h, GLD 4h — all StochRSIMeanReversion, auto-surfaced from experiments DB.

Co-Authored-By: Claude Sonnet 4.6 <noreply@anthropic.com>

### f551364 - docs: git save — Feb 26 session (strategy analysis + frontend idea) (2026-02-26)
- Fixed backtest command in CLAUDE.md: wrong param names (min_hold→min_hold_bars, stop_loss_atr→sl_atr, missing skip_adx_filter:false) were silently producing wrong results (5.61%/1996 trades vs 43%/689 trades)
- Re-verified GLD 15m StochRSI Enhanced with correct params: 43.03% total return, 0.69% DD, all 6 years profitable
- Added year-by-year breakdown to stochrsi_enhanced_gld.md (2020-2025, best year 2024 +7.90%)
- Added profit projection table by position sizing (2%→20% risk/trade) for €100/€1000 accounts
- Added WARNING note about silent param fallbacks in strategy memory file
- Updated ideas.md #6: refined frontend rebuild vision — personal strategy reference dashboard, two pages (index + detail), verified strategies sorted by Sharpe, research notes rendered from markdown

### 9992f8f - docs: git save — Feb 26 session (2026-02-26)
- Update claude.md: document DAY TIF fix, system audit findings, next steps
- Stage deletion of .agent/scripts/update_memory.sh (moved to scripts/)

Co-Authored-By: Claude Sonnet 4.6 <noreply@anthropic.com>
