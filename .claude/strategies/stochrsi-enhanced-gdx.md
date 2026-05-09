Status: current | Epistemic: headline confirmed; framework IS the edge (signal decorative); metals direction-dependent (regime risk) | Last verified: 2026-04-28

# StochRSI Enhanced — GDX 15m

> **May 9 2026 update — re-run under `adx_filter_mode='entry_only'`: GDX Sharpe 2.46 → 1.46 (close-anchored, single-symbol). FAILS the 2.0 quality bar by a wide margin.** ΔSharpe **−1.00** — GDX (with XBI) is the heaviest bug-beneficiary. Most of GDX's "validated edge" was the ADX-bug letting trades run through high-ADX regimes without exit. Buggy 2.46 figure preserved below as historical reference. **Live impact mitigated** by HWM (+~0.4 Sharpe) and partial bug-escape via server-side stops + ADX dips, but per-asset standalone GDX is now well below the quality bar. See `calibration-journal.md` §2 May 9 entry. Live tripwire anchor revised to ~4.0 ±0.5 (portfolio-level).
>
> **May 7 2026 caveat (now superseded by May 9 above for magnitude).** Sharpe figures below were close-anchored backtests with apparent ~0.7 Sharpe live-vs-backtest gap. May 9 bug-fixed re-run is the current source of truth.

> **Strategy file:** `backend/strategies/stoch_rsi_mean_reversion.py`

> **Apr 28 2026 status update — framework attribution finding.**
>
> Verified Sharpe (Apr 28): **2.46** full-strategy / **1.89** long-only — *full-strategy Sharpe exceeds long-only on GDX; shorts contribute meaningfully here, unlike on GLD/SLV.* Headline returns/DD on this card remain accurate.
>
> Random-entry control (tested directly on GDX): replacing the StochRSI entry trigger with random Bernoulli draws (p=0.15, seed=42), keeping all other logic identical, produces Sharpe **2.05** vs validated **2.46**. The StochRSI entry contributes ~0.41 Sharpe — real but a minority of the total edge. The bulk of the Sharpe comes from the position-management framework (2.0 ATR stop, trailing stop after 10 bars, ADX ranging filter, 2% fixed-risk sizing, 25% notional cap, K-cross exit, 10-bar min-hold).
>
> What this means: the metrics below are correct as a record of *what the validated recipe produces on GDX*. The interpretation "StochRSI mean-reversion is the edge on GDX" is **partially correct** — the entry signal contributes meaningfully but the framework is the primary driver. See `research-log.md` → "Random-Entry Control — Apr 28 2026" for full data.

## Knowledge

### Validated Parameters

Same params as GLD 15m — no tuning needed, transferred directly.

| Param | Code name | Value |
|---|---|---|
| RSI period | `rsi_period` | 7 |
| Stoch period | `stoch_period` | 14 |
| Overbought | `overbought` | 80 |
| Oversold | `oversold` | 15 |
| ADX threshold | `adx_threshold` | 20 |
| ADX filter ON | `skip_adx_filter` | false |
| ATR stop | `sl_atr` | 2.0 |
| Trailing stop | `trailing_stop` | true |
| Trail ATR mult | `trail_atr` | 2.0 |
| Trail after bars | `trail_after_bars` | 10 |
| Min hold | `min_hold_bars` | 10 |
| Skip days | `skip_days` | [0] (Monday) |

#### Backtest command:
```bash
python3 -m backend.runner backtest --strategy StochRSIMeanReversion --symbol GDX --timeframe 15m \
  --start 2020-01-01 --end 2025-12-31 --source alpaca --spread 0.0003 --delay 0 \
  --parameters '{"rsi_period":7,"stoch_period":14,"overbought":80,"oversold":15,"adx_threshold":20,"skip_adx_filter":false,"sl_atr":2.0,"trailing_stop":true,"trail_atr":2.0,"trail_after_bars":10,"min_hold_bars":10,"skip_days":[0]}'
```

### Performance Summary (verified Apr 27 2026)

- **Full-period return (2020 → Apr 27 2026):** +132.91%, **Max drawdown:** 2.01%, **Trades:** 581, **Win rate:** 46%
- **Comparable 2020–2025 sub-window:** ~+127% (compounded from yearly), 541 trades
- **Sharpe:** *needs recompute* — previous +2.58 figure is from same Apr 4 transcription pattern as GLD
- **Holdout test (2024–2025):** +31.7%, Sharpe 2.27 — pre-fix, directionally valid

> **Apr 27 2026 correction:** GDX is the asset **least affected** by the transcription errors — today's verified figures (~+127% / 541 trades on 2020–2025) are within 3% of the card's claimed +129.8% / 540 trades. The 2020–2025 trade count matches almost exactly. Engine itself healthy. The 2026 YTD figure (+1.54% / 40 trades / 2.60% DD) is notably weaker than GDX's strong historical years — consistent with live observations that GDX has been the laggard during the post-Apr-22 selloff. **Pre-Apr-4:** +114.1% / 2.02% DD / 539 trades. **Apr 4 (close to verified):** +129.8% / 2.02% DD / 540 trades. **Apr 27 verified:** ~+127% / 2.96% DD (worst year 2025) / 541 trades on 2020–2025; +132.91% / 2.01% DD / 581 trades on extended window.

### Year-by-Year (verified Apr 27 2026)

| Year | Return | DD | Trades |
|---|---|---|---|
| 2020 | +5.21% | 1.66% | 54 *(partial — starts Jul)* |
| 2021 | +15.80% | 1.59% | 96 |
| 2022 | +22.67% | 2.08% | 94 |
| 2023 | +11.57% | 2.96% | 92 |
| 2024 | +8.59% | 3.59% | 85 |
| 2025 | +25.39% | 3.13% | 120 |
| 2026 (YTD to Apr 27) | +1.54% | 2.60% | 40 |

2025 was strongest (+25.39%), 2024 weakest (+8.59%) — flipped from earlier card claim. 2026 YTD is weak (+1.54%) consistent with live observation that GDX has been the laggard since the Apr 22 selloff.

### Key Findings

**Why it works:** GDX (gold miners ETF) is a leveraged proxy to gold — miners move 2-3× gold's daily moves due to operating leverage. The same mean-reversion oscillations exist at 15m, but with larger amplitude.

**Highest absolute return of the four** (+129.8% vs GLD +39.22%, SLV +97.96%, IAU +32.7%) due to the leveraged nature of miners. Drawdown is similar to SLV (2.02%) — acceptable.

**2024 was the weakest year** (Sharpe 1.06) — GDX had some idiosyncratic miner-specific volatility. Still positive. 2025 was the strongest (Sharpe 3.52).

**Idiosyncratic risk note:** Unlike GLD/SLV which track metal prices directly, GDX can decouple from gold due to mining company factors (costs, strikes, management). This is the main risk vs GLD — monitored via the walk-forward results.

### Thesis Validation

GDX passing 4/4 walk-forward windows confirms the precious metals thesis extends to leveraged gold exposure. The mean-reversion structure is robust enough to survive the added noise from mining company fundamentals.

### Long-Only Baseline (verified Apr 28 2026)

Live bots run both long and short since Apr 13. This long-only figure is the **practical floor**.

| Metric | Full Strategy | Long-Only |
|--------|--------------|-----------|
| Return (2020 → Apr 27 2026) | +132.91% | **+79.87%** |
| Max Drawdown | 2.01% | **1.21%** (smoother) |
| Trades | 581 | **375** (~35% fewer) |
| Win Rate | 46% | **47%** |
| Sharpe | *recompute* | *recompute* (prior estimate ~1.65 was unverified) |

**Return drop:** −40%. **DD improvement:** −0.80%. Largest absolute return loss of the four but still strongly profitable long-only.

**Year-by-year long-only (verified Apr 28 2026):**

| Year | Return | DD | Trades |
|---|---|---|---|
| 2020 | +3.28% | 1.50% | 35 *(partial)* |
| 2021 | +4.69% | 1.90% | 62 |
| 2022 | +11.58% | 2.29% | 60 |
| 2023 | +7.83% | 2.90% | 60 |
| 2024 | +7.65% | 2.22% | 58 |
| 2025 | +18.98% | 2.30% | 75 |
| 2026 (YTD to Apr 27) | +6.30% | 4.76% | 25 |

2025 was strongest (+18.98%), 2020 weakest. 2026 YTD has the highest single-period DD (4.76%) — reflects GDX's particular sensitivity to the Apr 22 selloff. Old estimate (~+75%) was close — only ~5 percentage points pessimistic.

**Implication:** Shorts add ~+53 percentage points on GDX over the test period — the largest absolute short-side contribution of any asset. The leveraged miner structure means GDX moves more in both directions, so shorts capture proportionally more.

### Forward Testing

gdx-test bot running on cloud with aggressive params (OB 60/OS 40, 3-bar hold/trail after 1 bar, 0.5 ATR). All 4 exit mechanics confirmed — including trailing stop FIRING in profit (Mar 23: entry $80.05, trail ratcheted to $83.35, server stop fired intrabar @ $83.317, +$958 paper). See `CLAUDE.md` and `.claude/calibration/calibration-journal.md`.

Backtest prediction for test params (Dec 2025 – Mar 2026): +2.45%, 69 trades, 59% WR.
