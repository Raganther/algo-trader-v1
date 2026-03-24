# Observations — Algo Trader V1
*Running insights from the forward testing phase. Graduate to confirmed knowledge when settled.*

---

## Memory system (complete as of Mar 24)
All three hooks live and in sync with global CLAUDE.md: SessionStart, PreToolUse guard (now enforces both memory file changes AND domain file discoverability), PostToolUse OpenBrain audit (now enforces update-in-place before appending). OpenBrain migrated to algo-trader category. docs/dev.md removed — ideas/brainstorming now go directly in observations.md. calibration_notes.md created as first graduated domain file.

---

## Data integrity baseline
- Mar 03–04: gaps (bugs active, acceptable)
- Mar 05 onwards: 100% fill capture
- Mar 16–19: full Alpaca audits — all records matched pm2 logs across all 4 bots
- Mar 20: clean window starts — 18/18 orders matched, all fixes deployed
- Mar 23: 9 trades across all 4 bots, full audit passed. GDX server stop fired in profit (entry $80.05, exit $83.317, +$958 paper). Trail fire confirmed ✅

---

## Trailing stop pattern (Mar 23)
Same-day trades tend to exit via K-signal before the trailing stop can fire in profit — the K-signal (end-of-move reversal) fires at candle close while the trail needs an intrabar reversal. Multi-day holds give the trail time to ratchet far above entry, making an intrabar reversal more likely to hit it first. GDX held 3 days ($80.05 → trail $83.35 → fired $83.317).

---

## Market open fill delays
GLD and SLV first buys on Mar 23 took 3–4 minutes to fill (placed at 13:31 UTC, market open). The 30s pending_fills timeout fired correctly — fills were eventually confirmed. This is normal at open, not a bug. Happens occasionally on other days too.
