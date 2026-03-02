# Recent Git History

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

### ce79ac8 - chore: system audit — commit missing iau script, update claude.md (2026-02-26)
- Add scripts/run_iau_test.sh (existed on cloud, never committed to git)
- Update CLAUDE.md: document Feb 26 DAY TIF fix, update next steps
- Audit confirmed: all memory files accurate, codebase matches docs

Co-Authored-By: Claude Sonnet 4.6 <noreply@anthropic.com>

### 4361d59 - fix: fractional stock orders must use DAY not GTC on Alpaca (2026-02-26)
All GLD/IAU orders rejected since Feb 13 with:
'fractional orders must be DAY orders' (code 42210000)

Fix: non-crypto symbols now default to TimeInForce.DAY.
Crypto keeps GTC as before.

Co-Authored-By: Claude Sonnet 4.6 <noreply@anthropic.com>

### eb208c3 - feat: EventSurprise strategy + memory restructure into per-strategy files (2026-02-17)
New strategy: EventSurpriseStrategy trades GLD on CPI/NFP/Unemployment
surprise direction. Loads 83k-row economic calendar, matches events to
bars via bisect, deduplicates co-releases, classifies surprises using
per-event-type std threshold, enters with delayed entry and time-based
exit. CPI-only backtest: 14 trades, 86% win rate, +2.36%, 0.13% DD.
All-events backtest: 58 trades, 48% WR, +2.95%, 1.10% DD.

Memory restructure: moved strategy detail blocks out of claude.md into
per-strategy files under .claude/memory/strategies/. claude.md now has
a Strategy Index table linking to detail files. Slimmed from ~260 to
~210 lines. Updated Git Save Protocol to include strategy memory updates.

New files:
- backend/strategies/event_surprise.py (strategy)
- backend/scripts/event_surprise_analysis.py (initial diagnostic)
- backend/scripts/event_surprise_gaps.py (gap analysis — 5 investigations)
- scripts/run_event_surprise_test.sh (bot launch script)
- .claude/memory/strategies/stochrsi_enhanced_gld.md
- .claude/memory/strategies/event_surprise.md
- .claude/memory/strategies/composable_results.md

Modified:
- backend/runner.py (import, STRATEGY_MAP, default params)
- .claude/claude.md (slimmed, Strategy Index, updated protocol)

Co-Authored-By: Claude Opus 4.6 <noreply@anthropic.com>

### 4c8df74 - feat: Economic calendar integration — event blackout filter for StochRSI (2026-02-17)
Added event blackout filtering to skip entries near high-impact USD events
(FOMC, NFP, CPI, Unemployment Rate). Uses 83k-row economic calendar CSV.

New code:
- DataLoader.get_event_blackout_times() — loads event datetimes filtered by
  currency, impact, and event keywords (NFP/FOMC/CPI/Fed Funds/Unemployment)
- StochRSI event_blackout_hours param — precomputes blackout bar timestamps
  at init for O(1) lookup in on_bar, follows existing skip_days pattern
- Runner --event-blackout N CLI flag for backtest and live trading paths
- backend/scripts/event_trade_analysis.py — diagnostic script

Diagnostic results (1,381 GLD 15m trades, 2020-2025, 385 events):
- ±1h: 81 event trades avg PnL -$1.13 vs +$2.23 clean (event trades are losers)
- But full backtest with blackout ON reduces return (28% → 23% at 1h, 21% at 2h)
- Blunt avoidance filters out some winning trades too
- Feature built and available (off by default, event_blackout_hours=0)
- Foundation for future event-driven strategies (actual vs forecast surprise)

Co-Authored-By: Claude Opus 4.6 <noreply@anthropic.com>
