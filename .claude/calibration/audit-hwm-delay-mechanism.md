Status: current | Epistemic: backtest-validated falsification, supports H₀ with caveats | Last verified: 2026-05-08

# Audit — HWM Delay-Insensitivity Mechanism Claim

> Falsification audit of the May 7 causal claim that the HWM trail anchor's +0.78 Sharpe lift comes from being structurally insensitive to a 1-bar polling delay (vs the close-anchored trail that amplifies the delay into ~0.7 Sharpe of optimism). Run via `backend/analysis/audit_hwm_delay_sensitivity.py`. JSON record at `audit-hwm-delay-mechanism.json`.

## Headline

**Verdict: SUPPORTED.** HWM's Sharpe drops 0.15 under a 1-bar input data shift; close-anchored drops 0.42 over the same shift. HWM is roughly **2.8× more resistant** to the phase shift than close-anchored, comfortably below the 0.5× falsification threshold. Mechanism claim is consistent with the data.

**Important caveats** in §Limitations below — the audit confirms the *direction* of the claim but not the *magnitude*. The "+0.78 Sharpe lift ≈ 0.7 delay artifact" coincidence in `trail-anchor-hwm.md:38` is not fully reproduced by this simulation, so the live HWM expectation is probably *better than backtest-minus-zero* but probably still *worse than the +5.73 backtest headline*. Interim recommendation: anchor live tripwires conservatively at **HWM-Sharpe minus ~0.2** until more live data accumulates, not the +5.73 figure.

## Reproduce step (Part 1)

Long-window 7-bot portfolio backtest (2020-07-27 → 2026-04-27, $94k) re-runs **byte-perfect** against the figures in `trail-anchor-hwm.md`:

| Anchor | Return | Sharpe | Max DD | Trades | Match |
|---|---:|---:|---:|---:|---|
| close | +424.09% | 4.95 | 3.41% | 4344 | ✓ |
| hwm | +517.41% | 5.73 | 3.05% | 4533 | ✓ |

Per-symbol P&L for HWM matches the per-symbol table in `trail-anchor-hwm.md` line 42 to the dollar (e.g. SLV $96,007, GDX $86,322). Audit proceeds to falsification.

Short-window metals-4 + IAU Apr 23 trade-level reproduce was scoped out — the long-window headline reproduces exactly, and that's the gate the audit plan set.

## Falsification design (Part 2)

`--delay 1` is broken in the existing backtester (`paper_trader.py` scalar override + ordering bug — confirmed in code, would require a real refactor to fix). Instead, the audit injects a 1-bar phase shift via **data-shift preprocessing**: each symbol's OHLCV is shifted by 1 bar before the backtest, so the strategy at row `i` "sees" what was true at row `i−1`. Strategy code, backtester, and PortfolioRunner are untouched. Indicators are recomputed on the shifted data, matching how the strategy normally consumes it.

This simulates a coarser version of live's polling delay: real live is ~60s (sub-bar), data-shift is one full 15m bar. This is **conservative for falsification** — if HWM survives the larger shift, it would also survive the smaller one. The reverse asymmetry is also true: a small Δsharpe(close) here is *not* evidence the live artifact is small, because the simulation under-represents the real delay.

### 2×2 result

|  | shift=0 | shift=1 | Δsharpe |
|---|---:|---:|---:|
| **close** | 4.95 | 4.53 | **+0.42** |
| **hwm** | 5.73 | 5.58 | **+0.15** |

|  | shift=0 (return / DD) | shift=1 (return / DD) |
|---|---:|---:|
| close | +424.09% / 3.41% | +404.36% / 3.50% |
| hwm | +517.41% / 3.05% | +501.67% / 3.01% |

Decision rule: H₀ falsified if `|Δsharpe(hwm)| ≥ 0.5 × |Δsharpe(close)|`.

`|Δsharpe(hwm)| = 0.15`, `0.5 × |Δsharpe(close)| = 0.21` → **0.15 < 0.21 → SUPPORTED**.

HWM's sensitivity to the phase shift is ~36% of close-anchored's, well under the 50% bar.

## Per-trade attribution (Part 3)

Comparing close vs hwm at shift=0, matching trades on `(entry_time, symbol)`:

| Bucket | Trades | P&L |
|---|---:|---:|
| Common (both anchors fired same entry) | 3,996 | — |
| → bar-aligned exit (same exit timestamp+reason) | 3,756 | trivially equal |
| → HWM held shorter (different exit) | 240 | **+$54,326 (HWM)** |
| → HWM held longer | 0 | — |
| HWM-only entries | 537 | +$67,573 (HWM) |
| Close-only entries | 348 | +$34,119 (close) |

**Interpretation.** Roughly 94% of the 3996 common entries exit on the same bar in both runs (no formula difference matters). On the 6% (240 trades) where the trail formula produces different stops, **HWM always exits earlier** with more locked-in profit (+$54k aggregate). HWM never holds longer than close on a common entry — a clean, asymmetric finding.

The split of HWM's total advantage:
- Same-entry exit improvement: ~62% of the lift
- Net extra trades (+189): the rest

That HWM "exits earlier with more profit" is consistent with both delay-immunity *and* better-signal-extraction. The 2×2 disambiguation is what nails it as delay-immunity: at shift=0 close already loses to HWM (the formula effect), but at shift=1 close loses *additional* 0.42 Sharpe while HWM only loses 0.15. The 0.27 Sharpe gap that *opens up* under shift is the delay-resistance signal.

## Limitations

1. **The simulation under-represents the real delay artifact.** Predicted live-vs-backtest Sharpe gap was ~0.7; this audit only reproduces 0.42 of it via data-shift. Possible reasons: (a) data-shift moves both signal-evaluation *and* fill-price by 1 bar in lockstep, while real live splits them (signal stale by ~1 bar, fill at "next bar's price" within the same UTC minute); (b) real polling delay variance is asymmetric and event-driven, not a clean 1-bar shift on every bar. Either way, the audit's `Δsharpe(close) = 0.42` is a *lower bound* on the true artifact. If the real artifact scales similarly across anchors, the live HWM gap could be ~`(0.15 / 0.42) × 0.7 ≈ 0.25`.

2. **Mechanism supported, magnitude not pinned.** This audit confirms HWM is *more* delay-resistant than close-anchored. It does NOT confirm HWM's resistance is total. The +0.15 Sharpe drop under shift indicates real (small) sensitivity. The "Sharpe lift ≈ delay artifact" framing in `trail-anchor-hwm.md:38` is at best a rhyme, not an identity.

3. **Single-window result.** The audit ran on the validated long window (2020-07 → 2026-04). HWM's delay-resistance in regime-shift periods (e.g. March 2020, 2022 metals chop, 2024 melt-up) was not separately stress-tested. Possible HWM resistance is regime-conditional.

4. **Decision rule was set in advance, not tuned.** The 0.5× threshold was the falsification rule from the audit plan, written before the numbers were known. The HWM result clears it (36%) but isn't a blowout. A tighter threshold (e.g. 0.25×) would have falsified.

## What this changes

**Live tripwires.** The current `live_performance_report.py` tripwires anchor against HWM backtest expectation (Sharpe 5.73). Given the audit confirms HWM is more delay-resistant but not delay-immune, **anchor tripwires at ~5.50** (5.73 − 0.23 buffer for residual delay sensitivity + the 0.15 measured here) rather than 5.73. The original close-anchored "minus 0.7" rule of thumb is now retired because (a) close-anchored is no longer the live formula and (b) the audit shows HWM's expected gap is much smaller.

Concrete tripwire updates worth considering (not auto-applied):
- 30d Sharpe < 1.5 → degraded (was 1.0 close-anchored, would be 2.8 if anchored to 5.73 minus a typical 30d noise band; 1.5 is a midpoint)
- 60d Sharpe < 3.0 (was 2.0)
- 90d Sharpe < 4.0 (was 2.5)

**Strategic decisions.** The audit *strengthens* (does not weaken) the case for keeping HWM live and eventually flipping the strategy default `'close' → 'hwm'`. Pre-audit, the +0.78 backtest lift could plausibly have been a backtest-only artifact that wouldn't transfer; this audit shows the underlying mechanism *is* there in some form. Live HWM should outperform live close-anchored — the open question is by how much, not whether.

**Remaining experiments.** Per-symbol Sharpe re-run with HWM, HWM × cap-shrink, HWM × small-cap — all from the May 7 pending-decisions list — are still warranted. None of these is challenged by the audit.

## How to re-run

```bash
set -a && source .env && set +a
python3 -m backend.analysis.audit_hwm_delay_sensitivity
```

Reads from `research.db` price_data cache (deterministic, no Alpaca round-trip). Takes ~3–4 minutes. Writes a JSON record alongside this file at `audit-hwm-delay-mechanism.json`.

## Files referenced

- `backend/analysis/audit_hwm_delay_sensitivity.py` — the audit script
- `backend/strategies/stoch_rsi_mean_reversion.py:174-201` — trail formula (close vs hwm branches)
- `backend/engine/portfolio_runner.py` — shared-timeline runner, used directly (no CLI)
- `backend/engine/correlation_sizing.py` — module flags set explicitly per cell
- `.claude/calibration/live-vs-backtest-iau-diagnostic.md` — finding under audit (Part 1: 1-bar polling delay)
- `.claude/strategies/trail-anchor-hwm.md` — claim under audit (Part 2: +0.78 Sharpe ≈ delay artifact)
- `.claude/calibration/audit-hwm-delay-mechanism.json` — machine-readable summary
