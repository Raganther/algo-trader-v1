# Observations — Algo Trader V1
*Running insights from the forward testing phase. Graduate to confirmed knowledge when settled.*

---

## Memory system (audited and cleaned Mar 25)
All three hooks live and in sync with global CLAUDE.md. git-save-guard has three checks: (1) memory files modified, (2) domain files listed in CLAUDE.md, (3) core memory files (plan.md, observations.md, MEMORY.md) listed in CLAUDE.md. OpenBrain migrated to algo-trader category. calibration_notes.md created as first graduated domain file.
Mar 25 audit cleanup: deleted .claude/workflows/git_save.md, .claude/memory/MEMORY.md (old relic), and .claude/archive/ (3 completed plan docs). .claude/ is now clean.
Mar 25 migration: domain files moved out of .claude/memory/ into proper domain folders (.claude/strategies/, .claude/calibration/). .claude/memory/ now holds only the three core files (plan.md, observations.md, gitlog.md). CLAUDE.md updated to reflect new paths. This is the correct structure per global CLAUDE.md spec — future graduated files go in .claude/[domain]/, never in .claude/memory/.

---

## Data integrity baseline
- Mar 03–04: gaps (bugs active, acceptable)
- Mar 05 onwards: 100% fill capture
- Mar 16–19: full Alpaca audits — all records matched pm2 logs across all 4 bots
- Mar 20: clean window starts — 18/18 orders matched, all fixes deployed
- Mar 23: 9 trades across all 4 bots, full audit passed. GDX server stop fired in profit (entry $80.05, exit $83.317, +$958 paper). Trail fire confirmed ✅
- Mar 24: 8 trades across all 4 bots, full audit passed. 5 of 8 exits via server stop (choppy market). GLD+IAU stops fired at identical timestamps (15:10 UTC and 18:58 UTC) — correlated assets hit by same intrabar market move simultaneously. All fills matched pm2 logs exactly.

---

## Trailing stop pattern (updated Mar 24)
Same-day trades tend to exit via K-signal before the trailing stop can fire in profit. Multi-day holds give the trail time to ratchet far above entry. Mar 24 added a new data point: in choppy markets, the 0.5 ATR trail activates after 1 bar and sits very close to price — server stop fires frequently, often below entry, before the move has time to develop. 5 of 8 trades exited via server stop on Mar 24. K-signal exits (2 of 8) were the profitable ones.

---

## Two types of slippage — only one is modelled
The backtest models **spread slippage** via `--spread 0.0003` (0.03% bid-ask cost on every order). It does NOT model **stop execution slippage** — the gap between stop price and actual fill when Alpaca converts a triggered stop to a market order intrabar. Live data shows this is small (typically $0.01–0.14/share) but consistent. Will surface in Layer 3 of the Apr 20 calibration comparison (stop fill prices vs backtest). If systematic, worth adding a small stop-slippage assumption to the backtest model.

---

## Market open fill delays
GLD and SLV first buys on Mar 23 took 3–4 minutes to fill (placed at 13:31 UTC, market open). The 30s pending_fills timeout fired correctly — fills were eventually confirmed. This is normal at open, not a bug. Happens occasionally on other days too.
