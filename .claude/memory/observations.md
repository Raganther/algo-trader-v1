# Observations — Algo Trader V1
*Running insights from the forward testing phase. Graduate to confirmed knowledge when settled.*

---

## Graduation Candidates
<!-- Entries ready to graduate this session. git-save-guard blocks if non-empty. -->
<!-- Either graduate to .claude/[domain]/ and clear, or explicitly remove if not ready. -->

---

## Memory system (audited Mar 25, compliance pass Mar 26, workflow update Mar 28)
Mar 28 additions:
- Domain file check instruction added to global CLAUDE.md (Workflow section) and project CLAUDE.md (Session Start) — explicit rule to scan domain files before any update, new feature, or bug fix.
- Domain file loop tested in the wild: XLE research used plan mode + domain file review. GLD card revealed XLE 1h was already done; calibration_notes gave the quality bar framing. Loop worked as intended.
- git-save.sh updated: `pull --rebase` added before push — prevents push failures if remote ever gets ahead of local. GitHub repo was already being synced on every save; this is a safety net for edge cases only.

---


Mar 25: hooks synced with global CLAUDE.md. domain files migrated to .claude/[domain]/. archive cleared. .claude/memory/ holds only three core files. OpenBrain category set to algo-trader.
Mar 26 compliance pass against global CLAUDE.md (procedure extracted → .claude/procedures/memory-harness-compliance-audit.md):
- openbrain-audit-reminder.sh updated verbatim: 3 steps → 4 steps, procedure extraction added as Step 2.
- git-save-guard.sh: Check 2 now excludes .claude/procedures/; Check 5 added (blocks if procedure files not in _index.md).
- .claude/procedures/_index.md created (empty, ready for first extraction).
- CLAUDE.md: directory-level pointer (.claude/strategies/) replaced with 7 individual file listings. plan-domain-reminder.sh added to Architecture hooks line.
- All 7 domain files: Status: current added as standard header. Stale "Forward Testing Status" / "Next Steps" sections removed from strategy cards — replaced with brief prose notes referencing CLAUDE.md and calibration_notes.md.

---

## Data integrity baseline
- Mar 03–04: gaps (bugs active, acceptable)
- Mar 05 onwards: 100% fill capture
- Mar 16–19: full Alpaca audits — all records matched pm2 logs across all 4 bots
- Mar 20: clean window starts — 18/18 orders matched, all fixes deployed
- Mar 23: 7 trades across all 4 bots, full audit passed. GLD×2, SLV×2, IAU×2 (all K-signal exits), GDX T2 close via server stop (entered Mar 20, held over weekend). GDX server stop fired in profit (entry $80.05, exit $83.317, +$958 paper). Trail fire confirmed ✅
- Mar 24: 8 trades across all 4 bots, full audit passed. 5 of 8 exits via server stop (choppy market). GLD+IAU stops fired at identical timestamps (15:10 UTC and 18:58 UTC) — correlated assets hit by same intrabar market move simultaneously. All fills matched pm2 logs exactly.
- Mar 25: 1 trade (GDX only). Buy $86.80 → trail updated to $86.49 after 1 bar → server stop fired $86.48 (-$0.32/share, below entry). GLD/IAU/SLV flat. Alpaca audit: 3 records (buy + initial stop canceled + trail stop filled) — confirmed normal pattern for trades with trail update.
- Mar 26: 7 trades (GLD×2, IAU×1, SLV×2, GDX×2). All 4 bots flat EOD. Full Alpaca audit passed. SLV T1 had delayed fill (no stop placed — bug confirmed and fixed same day). Day P&L ~+$237 paper, led by GLD/SLV.
- Mar 27: 3 trades (GLD×1, IAU×1, SLV×1). GDX flat. All 4 bots flat EOD. Full Alpaca audit passed (9/9 records matched). All 3 entries within 31s of each other (18:46 UTC), all 3 exits within 2 min (19:03–19:05 UTC) — correlated metals hit by same move. Trail fired after 1 bar on all 3, exits below entry (same choppy pattern as Mar 25).

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

**Test #1 candidate — XLE 15m (researched Mar 28 2026):** Sharpe 2.06, +85.2%, 3.35% DD, WF 4/4. Same validated params as precious metals, no retuning. Confirms StochRSI mean reversion at 15m is a general microstructure pattern, not precious-metals-specific. Strategy card: `.claude/strategies/stochrsi_enhanced_xle.md`. Forward test starts after Apr 20.

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

## Trailing stop pattern (updated Mar 24)
Same-day trades tend to exit via K-signal before the trailing stop can fire in profit. Multi-day holds give the trail time to ratchet far above entry. Mar 24 added a new data point: in choppy markets, the 0.5 ATR trail activates after 1 bar and sits very close to price — server stop fires frequently, often below entry, before the move has time to develop. 5 of 8 trades exited via server stop on Mar 24. K-signal exits (2 of 8) were the profitable ones.

---

## Two types of slippage — only one is modelled
The backtest models **spread slippage** via `--spread 0.0003` (0.03% bid-ask cost on every order). It does NOT model **stop execution slippage** — the gap between stop price and actual fill when Alpaca converts a triggered stop to a market order intrabar. Live data shows this is small (typically $0.01–0.14/share) but consistent. Will surface in Layer 3 of the Apr 20 calibration comparison (stop fill prices vs backtest). If systematic, worth adding a small stop-slippage assumption to the backtest model.

---

## Market open fill delays (fixed Mar 26)
Fills at market open regularly take 1–4 minutes, exceeding the 30s pending_fills timeout. Previously: fill would eventually confirm via pending_fills, but the server-side stop was never placed — position ran unprotected until the next exit signal. Confirmed on Mar 26: SLV buy at 13:31, filled 13:33, no stop in Alpaca, exited via K-signal at 14:16 (43 min unprotected).
Fixed in live_broker.py: `stop_loss` now stored in pending_fills entry at timeout; `get_new_trades()` places the stop when the fill resolves. Log line: `🛡️ SERVER STOP placed at $X.XX ... [delayed fill]`.
