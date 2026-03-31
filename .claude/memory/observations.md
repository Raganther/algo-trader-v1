# Observations — Algo Trader V1
*Running insights from the forward testing phase. Graduate to confirmed knowledge when settled.*

---

## Graduation Candidates
<!-- Entries ready to graduate this session. git-save-guard blocks if non-empty. -->
<!-- Either graduate to .claude/[domain]/ and clear, or explicitly remove if not ready. -->

---

## Memory system (audited Mar 25, compliance pass Mar 26, workflow update Mar 28, full migration Mar 30)
Mar 28 additions:
- Domain file check instruction added to global CLAUDE.md (Workflow section) and project CLAUDE.md (Session Start).
- git-save.sh: `pull --rebase` added before push.
- OpenBrain auto-backup confirmed working.

Mar 30 migration (global CLAUDE.md updated spec):
- git-save-guard.sh: added `agents/` exclusion to Check 2; added Check 6 (blocks if modified domain files missing `Epistemic:` or `Last verified:` headers).
- domain-naming-guard.sh: new hook, PreToolUse Write — enforces lowercase-hyphenated naming for `.claude/*.md` files.
- settings.json: registered domain-naming-guard.sh under PreToolUse Write.
- All 8 domain files: headers extended to `Status: current | Epistemic: confirmed | Last verified: YYYY-MM-DD` (dates from git log per file).
- CLAUDE.md pointers: reformatted to "read when X" trigger conditions.
- All 8 domain files renamed underscores → hyphens (e.g. `stochrsi_enhanced_gld.md` → `stochrsi-enhanced-gld.md`). All cross-references updated across CLAUDE.md, plan.md, observations.md, and 4 strategy cards.
- Procedures extracted: `memory-harness-migration.md` and `daily-trade-audit.md` added to `.claude/procedures/`.

---


Mar 25: hooks synced with global CLAUDE.md. domain files migrated to .claude/[domain]/. archive cleared. .claude/memory/ holds only three core files. OpenBrain category set to algo-trader.
Mar 26 compliance pass against global CLAUDE.md (procedure extracted → .claude/procedures/memory-harness-compliance-audit.md):
- openbrain-audit-reminder.sh updated verbatim: 3 steps → 4 steps, procedure extraction added as Step 2.
- git-save-guard.sh: Check 2 now excludes .claude/procedures/; Check 5 added (blocks if procedure files not in _index.md).
- .claude/procedures/_index.md created (empty, ready for first extraction).
- CLAUDE.md: directory-level pointer (.claude/strategies/) replaced with 7 individual file listings. plan-domain-reminder.sh added to Architecture hooks line.
- All 7 domain files: Status: current added as standard header. Stale "Forward Testing Status" / "Next Steps" sections removed from strategy cards — replaced with brief prose notes referencing CLAUDE.md and calibration-notes.md.

---

## Data integrity baseline
- Mar 03–04: gaps (bugs active, acceptable)
- Mar 05 onwards: 100% fill capture
- Mar 16–19: full Alpaca audits — all records matched pm2 logs across all 4 bots
- Mar 20: clean window starts — 9/9 DB records matched Alpaca. 4 intraday trades (SLV TS, GLD K, IAU K, GDX T1 TS) + GDX T2 overnight hold (exits Mar 23).
- Mar 23: 13/13 matched. 7 trades: GLD×2 K, SLV×2 K, IAU×2 K, GDX T2 TS (trail fire in profit confirmed ✅). Profitable day.
- Mar 24: 16/16 matched. 8 trades: 6 of 8 exits via TS (choppy). GLD+IAU simultaneous stop fires at 15:10 and 18:58 UTC — correlated intrabar moves.
- Mar 25: 2/2 matched. 1 trade (GDX only). TS below entry.
- Mar 26: 14/14 matched. 7 trades. SLV T1 delayed fill — no stop placed (pending_fills bug, fixed same day). 4 K-exits, 3 TS.
- Mar 27: 6/6 matched. 3 trades (GLD, IAU, SLV — GDX flat). All TS, all entries within 31s, all exits within 1:06. Correlated metals.

**Full per-trade detail (entry/exit prices, stop levels, slippage) now in `.claude/calibration/live-trade-log.md`.**

---

## Post-calibration research process (planned, Mar 27)
Once the Apr 20 calibration passes, the backtester becomes a validated instrument. The intended workflow going forward:

**Three-phase research loop:**
1. **Research** — run backtests freely. Filter for Sharpe > 2, max DD < 3%, walk-forward passes.
2. **Validate** — for anything that clears the filter, run a 4–8 week forward test. Compare live results to backtest prediction. Goal is prediction accuracy, not profit.
3. **Deploy** — if forward test passes, deploy with real money.

**Execution layer vs signal layer:**
The Apr 20 calibration validates the *execution layer* — spread, stop slippage, bar timing. These corrections apply universally to any indicator or asset. A new strategy still needs its own forward test to validate its *signal layer* (the indicator logic itself). The hierarchy of confidence:
- Same strategy, new time period: highest confidence
- Same strategy, different correlated asset: high
- Same strategy, very different asset: medium (execution fine, signal behaviour unknown)
- Different indicator, same assets: medium (execution applies, signals untested)
- Different indicator, different assets: low until forward tested

**Rolling validation idea:** run short (4–8 week) forward tests on different assets and strategies after calibration. Each successful prediction (backtest and live agree on direction/magnitude) adds confidence in the engine. Don't need to be profitable — just predictable. Lock calibration params after Apr 20; don't tweak to fit each new test (that's curve-fitting the calibration).

**Test #1 candidate — XLE 15m (researched Mar 28 2026):** Sharpe 2.06, +85.2%, 3.35% DD, WF 4/4. Same validated params as precious metals, no retuning. Confirms StochRSI mean reversion at 15m is a general microstructure pattern, not precious-metals-specific. Strategy card: `.claude/strategies/stochrsi-enhanced-xle.md`. Forward test starts after Apr 20.

---

## Preliminary calibration check (Mar 27)
Backtest run with aggressive test params + `trading_hours:[13,20]` over Mar 20–27 vs live Alpaca results:

| Symbol | Backtest trades | Backtest return | Live trades |
|--------|----------------|-----------------|-------------|
| GLD | 11 | +0.05% | ~8–9 |
| IAU | 8 | -0.08% | ~7–8 |
| SLV | 10 | -0.27% | ~8–9 |
| GDX | 11 | -0.81% | ~7–8 |
| Total | 40 | | ~31 confirmed |

**Finding: no red flags.** 1.3x trade count inflation and P&L direction matching (both near-zero/slightly negative). Choppy week confirmed in both engines — trail fires after 1 bar, exits near or below entry across all 4 symbols.

**Hours filter barely helps:** `trading_hours:[13,20]` reduces Jan–Mar aggregate from 156→139 for GLD (only 11%). The bulk of the Jan–Mar difference in trade rate vs live is market regime — Jan–Feb had more oscillation (K crossing oversold/overbought more frequently) vs March precious-metals bull run with extended overbought periods.

**For Apr 20 calibration:** always add `"trading_hours":[13,20]` to backtest params. This is the only systematic correction required. Residual 30% over-prediction is acceptable; caused by hours filter including 13:00–13:29 bars (live gate starts at 13:30) plus minor execution timing differences.

---

## "Phantom sell" — blocked short entry (confirmed Mar 27)
Every day, all 4 bots log `⚠️ SELL skipped: no open position — ignoring duplicate exit signal` once during the session. This is NOT a duplicate exit — it's a **blocked short entry attempt**.

What happens: K spends time above overbought (60) → `in_overbought_zone = True`. When K later drops below 50, the strategy's short entry logic fires `self.sell()` with a `stop_loss`. `live_broker.sell()` blocks it (fractional short selling unsupported) and prints the misleading warning. `in_overbought_zone` resets to False (line 295) — no further attempts that session.

State stays clean after it. No bad trades. Fires once per overbought zone crossing.
Two issues: (1) warning message says "duplicate exit" when it's a "blocked short entry" — misleading. (2) `self.current_sl` gets set to the short stop value before the sell is blocked — stale but harmless (overwritten on next long entry, and stop loss check requires `position == 'long'`).
Both resolve naturally when whole-share sizing is implemented and shorts re-enabled.

---

## Trade log analysis (Mar 20–31)
Full analysis co-located with data in `.claude/calibration/live-trade-log.md`. Key headline: K-exits 76% win rate vs TS exits 14% across 43 trades. GDX underperforming vs backtest prediction. Correlated simultaneous entries = 6% portfolio exposure — needs position sizing adjustment before real money.

---

## Trailing stop pattern (updated Mar 31)
Same-day trades tend to exit via K-signal before the trailing stop can fire in profit. Multi-day holds give the trail time to ratchet far above entry. Mar 24: in choppy markets, the 0.5 ATR trail activates after 1 bar and sits very close to price — server stop fires frequently, often below entry. 5 of 8 trades exited via server stop on Mar 24; K-signal exits (2 of 8) were the profitable ones.

Mar 31 (strong rally day): opposite pattern — 5 of 7 K-exits, all profitable. GLD/IAU/SLV K-exited in profit; GDX (against metals trend) both exited via server stop near entry. Confirms K-exits are the profitable exits when momentum is sustained.

**Overnight stop timing (SLV T3, Mar 31):** DAY TIF stop expired 20:00 UTC as expected. New stop placed at 21:10 UTC (after bot restart at 20:09 UTC) — $67.50 vs expected $67.42. Documented mechanism says stop re-placed on first market-hours bar (13:30 UTC next day), so 21:10 UTC placement is unexpected. Hypothesis: position sync on restart triggers a trailing stop update on the last processed bar even outside market hours. Position IS protected. Investigate before Apr 20.

---

## Two types of slippage — only one is modelled
The backtest models **spread slippage** via `--spread 0.0003` (0.03% bid-ask cost on every order). It does NOT model **stop execution slippage** — the gap between stop price and actual fill when Alpaca converts a triggered stop to a market order intrabar. Live data shows this is small (typically $0.01–0.14/share) but consistent. Will surface in Layer 3 of the Apr 20 calibration comparison (stop fill prices vs backtest). If systematic, worth adding a small stop-slippage assumption to the backtest model.

---

## Market open fill delays (two fixes applied)
Fills at market open regularly take 1–4 minutes, exceeding the 30s pending_fills timeout.

**Fix 1 (Mar 26):** server-side stop was never placed for delayed fills — position ran unprotected until the next exit signal. Fixed: `stop_loss` stored in pending_fills entry; `get_new_trades()` places the stop when fill resolves. Log: `🛡️ SERVER STOP placed at $X.XX ... [delayed fill]`.

**Fix 2 (Mar 30):** entry metadata (`entry_time`, `entry_hour`, `entry_dow`, `atr_at_entry`) was silently dropped for delayed fills. Root cause: `set_entry_metadata()` attaches to `new_trades[-1]`, but on delayed fills `new_trades` is empty at call time (order still in pending_fills). Fixed: metadata stored in `_pending_entry_metadata[symbol]`; `get_new_trades()` pops and attaches it when the fill resolves. No more `⚠️ Warning: set_entry_metadata` log line.
