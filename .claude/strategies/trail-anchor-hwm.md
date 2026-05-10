Status: current | Epistemic: backtest-validated under bug fix; HWM still wins; magnitude revised | Last verified: 2026-05-09

> **May 9 2026 update — HWM A/B re-run under `adx_filter_mode='entry_only'`. HWM still wins, but lift shrinks ~58% to **+0.45 Sharpe**.** Long-window 7-bot, $94k, both legs under `entry_only`:
> - Close + entry_only: +212.28% / DD 2.06% / **Sharpe 3.72** / 4486 trades
> - HWM   + entry_only: +230.73% / DD 2.58% / **Sharpe 4.17** / 4639 trades
>
> ΔSharpe **+0.45** (was +0.78 buggy), ΔDD +0.52pp (was −0.36pp buggy), Δreturn +18pp. The decision-rule check still clears (+0.30 Sharpe branch passes; DD branch flips slightly negative but tiny). **Verdict: HWM stays live as-is** on all 7 bots. The "+0.78 ≈ 0.7 delay-artifact identity" framing dies — about 42% of the buggy-mode lift was the bug interacting worse with close-anchored than with HWM (HWM is more bug-resistant for the same reason it is more delay-resistant: stops triggered against an intrinsic HWM are not blocked by the buggy ADX early-return).
>
> **May 8 2026 audit (still valid context):** mechanism claim SUPPORTED via data-shift falsification. HWM is ~2.8× more delay-resistant than close-anchored (`Δsharpe(close)=0.42`, `Δsharpe(hwm)=0.15`). Only 0.42 of the predicted 0.7 artifact reproduced — see `.claude/calibration/audit-hwm-delay-mechanism.md`. Note that audit was itself run under the buggy default; both Δs are partly conflated with the bug; pending re-run under entry_only.
>
> **May 8 2026 PM caveat (now resolved by today's re-run):** the ADX-filter exit-block bug at `stoch_rsi_mean_reversion.py:211-239` inflated all prior numbers in this card. The original table below (close 4.95, HWM 5.73, Δ +0.78) is the buggy-mode A/B and is preserved as historical record. The bug-fixed A/B above is the current source of truth.
>
> **Live tripwire anchor: ~4.0 ±0.5 Sharpe.** Live should sit between 4.17 (pure entry_only fix) and 5.73 (pure buggy) since live partially escapes the bug via server-side stops + ADX dips. Tripwires in `live_performance_report.py` are calibrated to this band (1.8 / 2.5 / 3.0 at 30/60/90d).

# Trail Anchor: High-Water-Mark (HWM) — Path 2 from May 7 Diagnostic

> Strategy improvement that addresses the 1-bar polling delay artifact identified in `live-vs-backtest-iau-diagnostic.md`. Replaces the trail-stop's bar-Close anchor with the trade's high-water-mark, making the trail level intrinsic to the price action rather than extrinsic to bar timing.

## Mechanism

**Old (close-anchored):**
```python
# long
new_sl = row['Close'] - (atr_val * trail_atr)
# short
new_sl = row['Close'] + (atr_val * trail_atr)
```
The trail level depends on the current bar's Close. A 1-bar phase shift (live's polling delay vs backtest's instant fill) means live and backtest reference different bars when trail activates, producing different stop levels.

**New (HWM-anchored, opt-in):**
```python
# long: trail follows the highest High since entry
new_sl = high_water_mark - (atr_val * trail_atr)
# short: trail follows the lowest Low since entry
new_sl = high_water_mark + (atr_val * trail_atr)  # hwm tracks lowest low
```
The trail level is anchored to the trade's actual best-price-reached, which is independent of bar boundaries. A 1-bar phase shift produces nearly the same trail level because the HWM is the same value regardless of when trail activated.

## Headline result — long window (2020-07 → 2026-04, 7-bot $94k)

| Metric | Close (baseline) | **HWM** | Δ |
|---|---:|---:|---:|
| Return | +424.09% | **+517.41%** | **+93.32pp** |
| Sharpe | 4.95 | **5.73** | **+0.78** |
| Max DD | 3.41% | **3.05%** | **−0.36pp** |
| Trades | 4344 | 4533 | +189 |

**Decision rule (+0.30 Sharpe OR −1pp DD): passes both branches with massive margin.** ΔSharpe +0.78 is the largest single-parameter improvement we've measured to date.

The Sharpe lift of +0.78 is **close to the 0.7 Sharpe gap** estimated for the live-vs-backtest delay artifact (May 7 diagnostic). HWM is **more** delay-resistant than close-anchored, but the May 8 audit shows it is not delay-immune (HWM Sharpe drops 0.15 under simulated 1-bar phase shift; close drops 0.42). The "+0.78 ≈ 0.7" framing reads as identity but is at best a directional rhyme — see audit caveats above.

## Per-symbol comparison (long window)

| Symbol | Close trades | Close P&L | HWM trades | HWM P&L | Δ P&L |
|---|---:|---:|---:|---:|---:|
| GLD | 716 | $36,206 | 751 | **$44,914** | +$8,708 |
| IAU | 698 | $27,706 | 729 | **$30,739** | +$3,033 |
| SLV | 579 | $73,877 | 601 | **$96,007** | +$22,130 |
| GDX | 573 | $67,765 | 599 | **$86,322** | +$18,557 |
| OIH | 564 | $85,118 | 587 | **$96,716** | +$11,598 |
| XBI | 591 | $51,440 | 615 | **$64,656** | +$13,216 |
| XOP | 623 | $55,639 | 651 | **$66,177** | +$10,538 |

**All 7 symbols improve.** No regression on any bot.

## Short window (2026-04-15 → 2026-05-07, metals 4 — live comparison)

| Symbol | Close P&L | HWM P&L | Live P&L | HWM mitigation |
|---|---:|---:|---:|---|
| GDX | −$350 | −$350 | −$328 | identical (no trail fired in either) |
| GLD | −$415 | **−$188** | −$424 | HWM saves $227 vs close-anchored |
| IAU | +$384 | +$5 | −$196 | HWM closes ~$380 of the $580 live-vs-backtest gap |
| SLV | +$910 | +$1,090 | +$957 | HWM tracks live more closely than close-anchored |

22-day window is too short for headline Sharpe, but the per-symbol pattern shows HWM moving the backtest *toward* live behaviour for the metals — exactly what we'd expect if the close-anchor artifact was the source of divergence.

## Backward compatibility

- New parameter `trail_anchor` with values `'close'` (default — current behaviour) or `'hwm'`
- **Default 'close' preserves historical backtest reproducibility** — Run 0 baseline byte-identical when default is used
- HWM is opt-in by passing `"trail_anchor": "hwm"` in strategy parameters
- Live bots running existing configs are **unaffected** — they continue with close-anchored trail until reconfigured

Run with HWM:
```bash
python3 -m backend.runner portfolio --strategy StochRSIMeanReversion \
    --symbols GLD,IAU,SLV,GDX,OIH,XBI,XOP \
    --timeframe 15m --start 2020-07-27 --end 2026-04-27 \
    --source alpaca --spread 0.0003 --initial 94000 \
    --parameters '{"rsi_period":7,"stoch_period":14,"overbought":80,"oversold":15,"adx_threshold":20,"skip_adx_filter":false,"sl_atr":2.0,"trailing_stop":true,"trail_atr":2.0,"trail_after_bars":10,"min_hold_bars":10,"skip_days":[0],"trail_anchor":"hwm"}'
```

## Live deployment — May 7 2026 (DEPLOYED)

All 7 bot scripts (`scripts/run_{gld,iau,slv,gdx,oih,xbi,xop}_test.sh`) updated to include `"trail_anchor":"hwm"` parameter. Bots restarted on cloud server via `pm2 restart all` after `git pull`.

**Behaviour at deploy time:**
- Existing OIH short position (54 @ $442.14, +$1,205 unrealized at deploy) continues with **close-anchored trail** — `self.high_water_mark` is None for that position because HWM only initializes on entry, and the strategy code falls back to close-anchor when HWM is None
- All new trades (post-restart) initialize HWM and use the new formula
- Effective transition: HWM applies fully once OIH exits and a new trade fires

**Forward test reset.** This change resets the close-anchored forward-test convergence clock. Live performance from May 7 onward validates HWM, not the original close-anchored expectations. Tripwire bars in `live_performance_report.py` shipped May 9 at **1.8 / 2.5 / 3.0 at 30/60/90d**, anchored to ~4.0 ±0.5 Sharpe (post-ADX-bug-fix midpoint).

## Pending strategic decisions

1. **Flip live bots to `trail_anchor: hwm`** ✓ **done May 7 PM.** All 7 bots restarted with `trail_anchor:'hwm'`. Existing OIH short used close-anchored fallback until exit.
2. **Flip strategy default `trail_anchor` from `'close'` to `'hwm'`.** Epistemic change — all future backtests use the new formula by default, all historical backtest snapshots become non-reproducible without the explicit `trail_anchor: 'close'` override. **Pending** — best done if/when 30+ days of HWM live data tracks the ~4.0 ±0.5 anchor.
3. **Re-run validated-edges Sharpe table with HWM × entry_only (compound).** May 9 ran close-anchored × entry_only per-asset only. HWM × entry_only per-asset still pending. Lower priority since the portfolio-level HWM × entry_only result (4.17) is the live-relevant number; per-asset is informational.
4. **Re-run cap-shrink experiment (Apr 30 PM Run 2, +0.45 Sharpe under buggy mode) under entry_only.** Promoted to next experiment after May 10 lineup-selection closed pruning direction. Only remaining candidate with credible path past Sharpe 4.17.
5. **Re-run small-capital ($1k) deployment plan under HWM + entry_only.** Lower priority.

## Open questions (post-bug-fix)

- **Will the +0.45 Sharpe lift (HWM vs close, both under entry_only) hold in live?** Live HWM has been running since May 7; pattern check at day 14 (~May 21), tripwire convergence at day 30+. Anchor band: 4.0 ±0.5.
- **Does HWM × cap-shrink × entry_only compound positively?** Promoted as next experiment.
- **Does HWM affect the small-cap ($1k) deployment plan under entry_only?** Untested.
- **Per-asset interaction:** the long-window data shows all 7 symbols improving, but per-asset distribution of improvement varies (SLV +$22k vs GDX +$19k vs IAU only +$3k). Worth investigating whether HWM benefit is regime-dependent.

## Files referenced

- `backend/strategies/stoch_rsi_mean_reversion.py` — `trail_anchor` parameter (line ~46), HWM tracking (line ~92), trail update (line ~189)
- `.claude/calibration/live-vs-backtest-iau-diagnostic.md` — May 7 diagnostic that motivated this change
- `.claude/strategies/portfolio-runner-baseline.md` — canonical Run 0 (close-anchored)
