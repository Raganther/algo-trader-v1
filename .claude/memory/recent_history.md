# Recent Git History

### 191fd43 - docs: Update claude.md with full Feb 14 session findings (2026-02-14)
Updated:
- IG status: Phase 1-2 complete, demo data limits documented
- Fractional shares: enabled on Alpaca (min $1 order)
- Where We Left Off: revised strategy — Alpaca over IG for now
- Checklist: 4 new completed items, 4 updated next steps
- Decision: stay on Alpaca, use fractional shares for small-capital real trading

### 7c5c212 - feat: Enable fractional share trading on Alpaca (2026-02-14)
Changed int(qty) to round(qty, 4) in AlpacaTrader.place_order().
Enables trading with small accounts (e.g. €100 buying 0.05 shares of GLD at $460).
Alpaca supports fractional shares down to $1 minimum order.

Previously: int(qty) rounded 0.05 → 0 shares (couldn't trade)
Now: round(qty, 4) keeps 0.05 shares (valid fractional order)

### b5e51e4 - fix: IGBroker order placement — currency, expiry, and arg fixes (2026-02-14)
Fixed 3 issues found during demo testing:
1. create_open_position requires all positional args (not just kwargs)
2. Gold CFD uses currency_code='USD' not 'GBP' (added CURRENCY_MAP)
3. CFD demo account needs expiry='-' not 'DFB' (spread bet expiry)

Order flow verified end-to-end on IG demo:
- Connect ✅, Place order ✅, Get deal ref ✅, Confirm deal ✅
- Final rejection 'MARKET_CLOSED_WITH_EDITS' = expected (Saturday)

### 40e000c - feat: Add IGBroker for live trading + hour filter for strategy (2026-02-14)
New: backend/engine/ig_broker.py
- Matches LiveBroker interface (buy, sell, place_order, get_position, refresh, etc.)
- Uses trading-ig create_open_position() with deal confirmation
- Handles stop distance calculation, position tracking, trade logging
- EPIC_MAP for Gold/Silver/Forex symbols

Modified: backend/runner.py
- Added --source ig|alpaca to trade command
- Auto-selects IGBroker+IGDataLoader when --source ig

Modified: backend/strategies/stoch_rsi_mean_reversion.py
- Added trading_hours parameter (committed earlier)

Usage: python3 -m backend.runner trade --strategy StochRSIMeanReversion --symbol GLD --source ig --timeframe 15m --paper

### 42d5e5f - feat: Add trading_hours filter to StochRSI strategy (2026-02-14)
Adds 'trading_hours' parameter (e.g. [14, 21] for NYSE hours 14:30-21:00 UTC).
Entries blocked outside specified hours, exits always allowed (same pattern as skip_days).
Default: empty list (no filtering - backward compatible).

Verified: Alpaca GLD Jan-Feb 2026 — 50 trades with filter vs 56 without, same 2.04% return.
Key use case: restrict IG 24hr Gold to NYSE hours only to replicate GLD-validated conditions.

### cd4c6a9 - refactor: Reorganize .claude/ into memory/, workflows/, archive/ (2026-02-14)
Final structure:
  .claude/claude.md (master primer)
  .claude/memory/ (system_manual, ideas, recent_history)
  .claude/workflows/ (git_save - active)
  .claude/archive/ (edge_enhancement, forward_testing, strategy_discovery - completed)

Updated all path references in claude.md, update_memory.sh, load-context.sh, git_save.md

### adafde5 - refactor: Move memory files from .agent/memory/ to .claude/ (2026-02-14)
Consolidates all memory/context files under .claude/:
- Moved ideas.md, recent_history.md, system_manual.md
- Updated update_memory.sh output path
- Updated claude.md file references
- Updated load-context.sh hook
- Updated git_save.md workflow

All memory now lives in .claude/ alongside claude.md

### e08e71b - chore: Clean up memory files, update claude.md with IG integration (2026-02-14)
Deleted:
- .agent/memory/research_insights.md (RETIRED, contaminated with delay=1 results)
- .agent/memory/research.md (outdated, findings already in claude.md)

Updated claude.md:
- Added IG integration status line
- Updated 'Where We Left Off' to Feb 14 (IG Phase 1 complete)
- Added IG backtest command to Quick Commands
- Cleaned Read These Files section (3 memory + 3 workflow files)
- Updated Next Steps with IG milestones (3 checked, 2 remaining)
- Removed references to deleted files

### ea83500 - feat: Add --source ig to runner.py for IG data backtesting (2026-02-14)
Phase 1 of IG integration:
- Added 'ig' as third data source option (alongside csv/alpaca) in backtest, matrix, and trade commands
- Added IG data loading branches in run_backtest() and worker_task()
- Added GLD/SLV/IAU ETF ticker → IG Gold/Silver CFD epic mappings
- Updated Gold epic from DFB (CS.D.USCGC.TODAY.IP) to CFD (CS.D.CFDGOLD.CFDGC.IP) which works on demo

Verification: Ran 'backtest --source ig --symbol GLD --timeframe 15m' with Enhanced StochRSI params.
Result: -1.85% return, 148 trades, 60% win rate, 2.42% max DD over 6 weeks of IG demo Gold data.
Strategy executes correctly on IG data — no changes needed to strategy code.

### 4f9e37d - fix: Patch IGDataLoader date format and epic resolution (2026-02-14)
Fixes for IG Demo API interaction:
- Reverted date format to ISO 8601 (YYYY-MM-DDTHH:MM:SS) which prevents error.malformed.date
- Added datetime object passing to trading-ig for robustness
- Updated _process_df to prioritize 'bid'/'ask' mid-price calculation over 'last' (which was NaN for CFDs/Gold)
- Updated test script to use dynamically discovered epic from search
- Updated memory files (ideas.md, system_manual.md) to reflect working status

Verification:
- Successfully fetched 93 rows of Gold 15m data on Demo account

### ea719c6 - feat: Add IG spread betting data loader (2026-02-14)
New files:
- backend/engine/ig_loader.py: IGDataLoader class mirroring AlpacaDataLoader interface
  for fetching historical OHLCV data from IG REST API (gold, forex, indices)
- backend/engine/test_ig_loader.py: Quick test script for IG API connection

Changes:
- .env: Added IG_API_KEY, IG_USERNAME, IG_PASSWORD, IG_ACC_TYPE (demo)
- ideas.md: Added idea #18 documenting IG spread betting integration
  motivation (Kelly sizing on small accounts, tax-free in Ireland)
- system_manual.md: Added IG loader usage docs and API reference

Status: IGDataLoader built and tested. Authentication works on demo
but IG demo environment has no instruments/price data provisioned
(search returns 0, price history returns 500 error). Emailed IG support.
Code will work once IG resolves demo provisioning or live KYC approved.

Key technical details:
- Uses trading-ig Python library (pip install trading-ig)
- Epics: CS.D.USCGC.TODAY.IP (Gold), CS.D.EURUSD.MINI.IP (EUR/USD)
- Resolutions: 1Min, 5Min, 15Min, 1H, 4H, D
- REST API for history/orders, Streaming (Lightstreamer) for live prices

Co-Authored-By: Claude Opus 4.5 <noreply@anthropic.com>

### 0700679 - fix(broker): add set_entry_metadata to LiveBroker to prevent crash on trade (2026-02-13)

### 8e0dac0 - test: Add temporary aggressive-params test bot for piping verification (2026-02-13)
OB 60/OS 40, ADX 50, trail after 3 bars, min hold 3 bars.
Generates high trade frequency to verify trailing stop, min hold,
and skip_days mechanics are working in live paper trading.
Delete after verification.

Co-Authored-By: Claude Opus 4.6 <noreply@anthropic.com>

### d44665c - feat: Deploy enhanced GLD 15m strategy (Sharpe 2.42) (2026-02-13)
Skip Monday + trailing stop (2x ATR after 10 bars) + min hold 10 bars.
Replaces baseline params (Sharpe 1.57) with validated enhanced version.

Co-Authored-By: Claude Opus 4.6 <noreply@anthropic.com>

### 0558c89 - feat: Edge enhancements — trailing stop + min hold take Sharpe from 1.57 to 2.42 (2026-02-13)
Trade analysis revealed three key leaks in GLD 15m StochRSI:
- Stop losses were 100% losers (199 trades, -$1,219 total)
- Short-duration trades (1-5 bars, 72% of trades) were breakeven noise
- Monday trades had near-zero edge (128 trades, +$23 total)

Enhancements added to StochRSIMeanReversion (all optional, off by default):
- skip_days: filter entries on specified days (e.g. [0] for Monday)
- trailing_stop + trail_after_bars + trail_atr: move stop to lock in profits
- min_hold_bars: prevent signal exits before N bars held

Enriched trade records (entry_time, exit_reason, atr_at_entry, direction,
entry_hour, entry_dow) for diagnostic analysis. Added set_entry_metadata()
to PaperTrader, exit_reason passthrough in Strategy base class.

A/B sweep results (18 variants vs baseline):
- Skip Monday: Sharpe +0.12 (removes dead trades)
- Trail 2x ATR after 20 bars: Sharpe +0.41 (best single enhancement)
- Trail 2x/5bar + Hold 5: Sharpe 2.30 (+0.73, best combo)
- Skip Mon + Trail 2x/10bar + Hold 10: Sharpe 2.42 (+0.72)

Full validation — ALL 4 variants PASSED (holdout + walk-forward + multi-asset):
- Best: Skip Mon + Trail 2x/10bar + Hold 10 → Sharpe 2.42
- Holdout: +16.4% (train +18.6%, only 2.2% degradation)
- Walk-forward: 4/4 windows positive (100%)
- Multi-asset: GLD +38%, SLV +92%, IAU +31%

Key insight: Enhancements performed BETTER on unseen data. Trailing stop
is structural (not curve-fitting) — generalises across gold assets.

New files:
- backend/optimizer/trade_analysis.py — diagnostic backtest + trade slicing
- backend/optimizer/enhancement_sweep.py — A/B sweep framework

Co-Authored-By: Claude Opus 4.6 <noreply@anthropic.com>

### b065f82 - docs: Add edge enhancement plan and update session context (2026-02-13)
New file: .agent/workflows/edge_enhancement_plan.md
- 5-phase plan to improve validated edges (GLD 15m Sharpe 1.66)
- Phase 1: Enrich trade records (entry time, exit reason, ATR at entry)
- Phase 2: Diagnostic analysis (time-of-day, vol regime, exit patterns)
- Phase 3: Build targeted filters based on analysis findings
- Phase 4: A/B sweep (~50 variants vs baseline)
- Phase 5: Stack winners + validate through walk-forward

Key finding: backtester doesn't store entry timestamps or exit reasons,
needs enrichment before analysis can begin.

Updated ideas.md with 5 new ideas (#13-17): time-of-day filtering,
exit optimisation, limit order entries, vol-scaled sizing, news blackout.

Updated claude.md: GLD 15m bot deployed (replaced 1h), validation run
in progress (150 candidates), edge enhancement as next priority.

Raised validation candidate limit from 50 to 150 in run_overnight.py
to cover all unvalidated symbol/TF combos in a single run.

Co-Authored-By: Claude Opus 4.6 <noreply@anthropic.com>

### 29d2cfc - feat: Switch GLD bot from 1h to 15m (Sharpe 1.66, best validated edge) (2026-02-13)
GLD 15m params: RSI 7, Stoch 14, OB 80, OS 15, ADX 20, ATR stop 2x
Replaces GLD 1h (Sharpe 1.44) with higher-edge 15m strategy.

Co-Authored-By: Claude Opus 4.6 <noreply@anthropic.com>

### b63e070 - docs: Update with GLD 15m validation results and new strategy ideas (2026-02-13)
- GLD 15m StochRSI (Sharpe 1.66) validated as best edge — yearly returns 2-7%
- 5,300+ experiments, 90 validated passes across GLD/IAU/XLE
- Added ideas #7-12: position sizing, GDX amplification, multi-TF confirmation,
  cross-asset signals, spread betting/IG API for small accounts, forex discovery
- Updated next steps: explore IG API for €100 starting capital

Co-Authored-By: Claude Opus 4.6 <noreply@anthropic.com>

### a91cf41 - feat: Add scan/medium grid modes, symbol filtering, and ideas log (2026-02-12)
- Added --scan (11 combos), --medium (972 combos) grid tiers for faster iteration
- Added --symbols and --timeframes CLI filters to focus runs on promising targets
- Added --skip-sweep and --skip-validation flags for independent pass execution
- Fixed --quick not respecting explicit --max-hours override
- Pass 4 now loads winners from DB when skipping validation
- Enabled verbose output during sweeps for progress visibility
- Created .agent/memory/ideas.md for future strategy concepts (drawdown analysis,
  regime rotation, pairs trading, beta hedging, portfolio diversification, dashboard)
- Updated claude.md with ideas.md reference (DO NOT auto-read)

Co-Authored-By: Claude Opus 4.6 <noreply@anthropic.com>

### de52b94 - feat: Add overnight strategy discovery orchestrator (2026-02-11)
Single script (run_overnight.py) chains all discovery phases for
unattended overnight runs. 4 passes: broad sweep across priority-
ordered asset/TF combos → filter promising candidates from DB →
validate via holdout/walk-forward/multi-asset → expand winners to
adjacent timeframes and related assets.

Features:
- TimeBudget class with global time limit (default 10h)
- --quick mode for smoke testing (reduced grids, <1h)
- --skip-composable to skip slow composable sweeps
- skip_tested=True everywhere for crash recovery
- Per-sweep error handling (logs and continues)
- Priority targets: GLD other TFs, gold-correlated (SLV/IAU/GDX),
  XLE/XBI/TLT, broad market (SPY/QQQ/IWM/DIA)
- Final report with timing, new experiments, validation results,
  and top 10 all-time performers

No existing files modified — wires existing Phase 0-3 APIs together.

Co-Authored-By: Claude Opus 4.6 <noreply@anthropic.com>
