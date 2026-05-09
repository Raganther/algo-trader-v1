Status: current | Epistemic: headline confirmed; framework IS the edge (signal decorative); metals direction-dependent (regime risk) | Last verified: 2026-04-28

# StochRSI Enhanced — XLE 15m

> **May 9 2026 update — re-run under `adx_filter_mode='entry_only'`: XLE Sharpe 2.30 → 1.55 (close-anchored, single-symbol). FAILS the 2.0 quality bar.** ΔSharpe −0.75. Buggy 2.30 figure preserved below as historical reference. XLE is not currently deployed live (XOP/OIH cover energy); this is informational only. See `calibration-journal.md` §2 May 9 entry. Live tripwire anchor revised to ~4.0 ±0.5 (portfolio-level).
>
> **May 7 2026 caveat (now superseded by May 9 above for magnitude).** Sharpe figures below were close-anchored backtests with apparent ~0.7 Sharpe live-vs-backtest gap. May 9 bug-fixed re-run is the current source of truth.

> **Strategy file:** `backend/strategies/stoch_rsi_mean_reversion.py`

> **Apr 28 2026 status update — framework attribution finding.**
>
> Verified Sharpe (Apr 28): **2.30** full-strategy. Headline returns/DD on this card remain accurate.
>
> Random-entry control was **not run directly on XLE** (tested on GLD/SLV/GDX/SPY/QQQ/IWM — see `research-log.md` → "Random-Entry Control — Apr 28 2026"). On the assets tested directly, random entries with the same framework produce Sharpes within 0.02–0.65 of validated; on QQQ random *beats* validated. The cross-asset pattern strongly suggests the StochRSI entry signal contributes a small per-asset tilt and the framework (2.0 ATR stop, trailing stop after 10 bars, ADX ranging filter, 2% fixed-risk sizing, 25% notional cap, K-cross exit, 10-bar min-hold) is doing most of the work — but per-asset attribution on XLE is unverified.
>
> What this means: the metrics below are correct as a record of *what the validated recipe produces on XLE*. The interpretation "StochRSI mean-reversion is the edge on XLE" is under review pending direct random-entry test or framework ablations.

## Knowledge

### Validated Parameters

Same params as GLD/IAU/SLV/GDX — no retuning. Cross-asset generalisation thesis confirmed.

| Param | Value |
|---|---|
| rsi_period | 7 |
| stoch_period | 14 |
| overbought | 80 |
| oversold | 15 |
| adx_threshold | 20 |
| skip_adx_filter | false |
| sl_atr | 2.0 |
| dynamic_adx | false |
| trailing_stop | true |
| trail_atr | 2.0 |
| trail_after_bars | 10 |
| min_hold_bars | 10 |
| skip_days | [0] (Monday) |

### Performance Summary (verified Apr 27 2026)

- **Full-period return (2020 → Apr 27 2026):** +80.42%, **Max drawdown:** 3.27%, **Trades:** 570, **Win rate:** 45%
- **Comparable 2020–2025 sub-window:** ~+81% (compounded from yearly), 545 trades
- **Sharpe:** *needs recompute* — previous +2.06 figure is unverified
- **Walk-forward:** 4/4 windows positive

XLE figures are **close to the previous card claim** (+85.2% / 539 trades / 3.35% DD). The Apr 21 update appears to have been roughly accurate, unlike the Apr 4 transcription on the metals cards. Small downward revision (+85.2% → +80.42%) likely reflects: (1) the Apr 22 metals/energy correlation (XLE 2026 YTD is -0.46%, see year-by-year), (2) extended window adding the Apr selloff. Engine itself healthy.

### Year-by-Year (verified Apr 27 2026)

| Year | Return | Max DD | Trades |
|---|---|---|---|
| 2020 | +11.53% | 2.39% | 41 *(partial — starts Jul)* |
| 2021 | +11.40% | 2.03% | 88 |
| 2022 | +17.54% | 3.19% | 111 *(energy boom — oil price rally)* |
| 2023 | +6.06% | 3.56% | 91 |
| 2024 | +5.30% | 1.49% | 115 |
| 2025 | +10.41% | 1.86% | 99 |
| 2026 (YTD to Apr 27) | -0.46% | 2.23% | 25 |

2022 was the standout year (+17.54%) — energy sector rallied hard post-Ukraine. 2023–2024 weaker (+6.06% / +5.30%). 2026 YTD is **negative** (-0.46%) — first negative year-fragment in the dataset, reflecting the Apr 22 selloff impact on energy.

### Walk-Forward Validation (Mar 28 2026)

| Window | Period | Return | Max DD | Trades | Win Rate |
|--------|--------|--------|--------|--------|----------|
| 1 | 2020–mid 2022 | +36.4% | 1.26% | 184 | 49% |
| 2 | mid 2022–2025 | +33.3% | 3.35% | 353 | 44% |
| 3 | 2020–2021 | +24.9% | 1.26% | 127 | 50% |
| 4 | 2022–2023 | +25.2% | 3.35% | 199 | 42% |

4/4 windows positive. Consistent returns across all splits. DD spikes in windows including 2022–2023 (volatile energy sector) but within acceptable range.

### Context

- **Asset:** XLE = Energy Select Sector SPDR (S&P 500 energy companies — oil majors, energy services)
- **Correlation:** Oil prices, not gold — deliberately different from precious metals thesis assets
- **Data:** 37,237 bars, Jul 2020 – Mar 2026 (Alpaca IEX)
- **Validated:** Mar 28 2026 as Rolling Validation Test #1 candidate

### Cross-Asset Comparison

| Asset | Sharpe | Return | Max DD | WF |
|---|---|---|---|---|
| GLD | 2.47 | +39.22% | 0.73% | 4/4 |
| SLV | 2.41 | +97.96% | 2.00% | 4/4 |
| GDX | 2.58 | +129.8% | 2.02% | 4/4 |
| IAU | 1.97 | +32.7% | 0.89% | 4/4 |
| **XLE** | **~2.06** | **+85.2%** | **3.35%** | **4/4** |

XLE sits above IAU on Sharpe but below GLD/SLV/GDX. Still passes the quality bar (Sharpe ≥ 2.0, WF 4/4). The higher DD reflects energy sector volatility vs gold's safe-haven stability. *(Precious metals figures corrected Apr 4 — stop-check ordering fix)*

### Significance

XLE is in a completely different sector from the four precious metals ETFs. Its inclusion confirms that StochRSI mean reversion at 15m is a **general market microstructure pattern**, not a precious-metals-specific effect. Same params, different asset class, consistent results.
