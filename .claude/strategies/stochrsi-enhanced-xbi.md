Status: validated | Epistemic: WF 4/4 + Sharpe ≥2.0 confirmed; framework IS the edge (signal decorative); regime-dependence presumed (untested per-asset) | Last verified: 2026-04-28

# StochRSI Enhanced — XBI 15m (Validated — Diversifier)

> **May 9 2026 update — re-run under `adx_filter_mode='entry_only'`: XBI Sharpe 2.18 → 1.18 (close-anchored, single-symbol). FAILS the 2.0 quality bar by a wide margin.** ΔSharpe **−1.00** — XBI (with GDX) is the heaviest bug-beneficiary. Most of XBI's "validated edge" was the ADX-bug letting trades run through high-ADX regimes without exit. Buggy 2.18 figure preserved below as historical reference. **Live impact mitigated** by HWM (+~0.4 Sharpe) and partial bug-escape, but per-asset standalone XBI is now well below the quality bar — re-evaluate "diversifier" framing once portfolio-level entry_only re-runs land. See `calibration-journal.md` §2 May 9 entry. Live tripwire anchor revised to ~4.0 ±0.5 (portfolio-level).
>
> **May 7 2026 caveat (now superseded by May 9 above for magnitude).** Sharpe figures below were close-anchored backtests with apparent ~0.7 Sharpe live-vs-backtest gap. May 9 bug-fixed re-run is the current source of truth.

> **Strategy file:** `backend/strategies/stoch_rsi_mean_reversion.py`

> **Apr 28 2026 status update — framework attribution finding.**
>
> Verified Sharpe (Apr 28): **2.18** full-strategy ✓ (clears 2.0 quality bar). Headline returns/DD on this card remain accurate.
>
> Random-entry control was **not run directly on XBI** (tested on GLD/SLV/GDX/SPY/QQQ/IWM — see `research-log.md` → "Random-Entry Control — Apr 28 2026"). On the assets tested directly, random entries with the same framework produce Sharpes within 0.02–0.65 of validated. The cross-asset pattern strongly suggests the StochRSI entry signal contributes a small per-asset tilt and the framework is doing most of the work — but per-asset attribution on XBI is unverified.
>
> What this means: the metrics below are correct as a record of *what the validated recipe produces on XBI*. The diversifier claim (XBI is biotech, uncorrelated with metals/energy) was always about *correlation*, not signal source — that claim is unaffected by the random-entry finding. But the interpretation "StochRSI mean-reversion is the edge on XBI" is under review pending direct random-entry test or framework ablations.
> **Status:** Discovered Apr 28 2026 during forgotten-asset audit. **Walk-forward 4/4 windows positive (Apr 28).** Sharpe and cross-correlation analysis still pending.

## Knowledge

### Validated Parameters

Same recipe as all other StochRSI Enhanced bots — no retuning.

| Param | Value |
|---|---|
| rsi_period | 7 |
| stoch_period | 14 |
| overbought | 80 |
| oversold | 15 |
| adx_threshold | 20 |
| skip_adx_filter | false |
| sl_atr | 2.0 |
| trailing_stop | true |
| trail_atr | 2.0 |
| trail_after_bars | 10 |
| min_hold_bars | 10 |
| skip_days | [0] (Monday) |

#### Backtest command:
```bash
python3 -m backend.runner backtest --strategy StochRSIMeanReversion --symbol XBI --timeframe 15m \
  --start 2020-01-01 --end 2026-04-28 --source alpaca --spread 0.0003 --delay 0 \
  --parameters '{"rsi_period":7,"stoch_period":14,"overbought":80,"oversold":15,"adx_threshold":20,"skip_adx_filter":false,"sl_atr":2.0,"trailing_stop":true,"trail_atr":2.0,"trail_after_bars":10,"min_hold_bars":10,"skip_days":[0]}'
```

### Performance Summary (verified Apr 28 2026)

- **Full-period return (2020 → Apr 27 2026):** **+84.75%**, **Max drawdown:** 2.44%, **Trades:** 602, **Win rate:** 43%
- **Sharpe:** *needs computing*

XBI was previously a "Sweep positive" 1h candidate (Sharpe 0.90–1.18, +23.5% / 1,072 trades). Moving to 15m + validated recipe **3.6× the total return**. Same pattern as the metals — the 1h baseline was the floor, not the ceiling.

### Year-by-Year (verified Apr 28 2026)

| Year | Return | Max DD | Trades |
|---|---|---|---|
| 2020 | +3.88% | 2.17% | 42 *(partial — starts Jul)* |
| 2021 | +12.16% | 2.43% | 126 |
| 2022 | +26.19% | 2.84% | 96 *(biotech volatility year)* |
| 2023 | +10.26% | 2.56% | 108 |
| 2024 | +7.87% | 2.81% | 106 |
| 2025 | +4.63% | 2.55% | 100 |
| 2026 (YTD to Apr 27) | +0.58% | 1.28% | 24 |

**2022 standout** (+26.19%) — biotech had its highest-volatility year of the window. **2025–2026 weakening** (+4.63% / +0.58%) — biotech sector entered a quieter regime. This is the **softest tail** of any candidate — worth watching whether the edge has degraded or just paused.

### Context

- **Asset:** XBI = SPDR S&P Biotech ETF — equal-weighted basket of biotech firms. Different from IBB (cap-weighted) — XBI gives smaller biotechs more exposure, hence higher volatility.
- **Driver class:** Biotech is news-driven (FDA decisions, clinical trial results, M&A). High intraday volatility, high range-bound behaviour at 15m.
- **Why it likely works:** Biotech's high event-driven volatility produces frequent oversold/overbought oscillations. Same mean-reversion mechanism as the metals, applied to a completely different sector.
- **Diversification value:** Biotech is largely uncorrelated with metals or energy. Adding XBI to the portfolio could reduce overall correlation risk — directly addressing the "Critical Path: correlated 4-symbol overnight gap" concern in the roadmap.

### Cross-Asset Comparison

XBI sits in the middle tier:

| Asset | Return | Max DD | Trades |
|---|---|---|---|
| OIH | +146.53% | 2.95% | 589 |
| SLV | +144.26% | 2.00% | 581 |
| GDX | +132.91% | 2.01% | 581 |
| XOP | +90.34% | 3.29% | 629 |
| **XBI** | **+84.75%** | **2.44%** | **602** |
| XLE | +80.42% | 3.27% | 570 |
| GLD | +49.83% | 1.18% | 728 |
| IAU | +40.05% | 1.31% | 705 |

### Walk-Forward Validation (Apr 28 2026)

| Window | Period | Return | Max DD | Trades | Win Rate |
|--------|--------|--------|--------|--------|----------|
| 1 | 2020 → mid 2022 | +39.10% | 2.41% | 212 | 47% |
| 2 | mid 2022 → 2025 | +31.91% | 1.65% | 364 | 42% |
| 3 | 2020 → 2021 | +17.07% | 1.97% | 166 | 46% |
| 4 | 2022 → 2023 | +35.36% | 2.43% | 203 | 44% |

**4/4 windows positive.** Returns +17% to +39% — wider spread than OIH/XOP, with W3 (2020–2021) being notably weaker. Win rates stable 42–47%. The 2020–2021 softness is a real signal: biotech mean-reversion was weakest during the post-COVID stimulus period — possibly because the entire sector was trending strongly upward (mean-reversion fails in trends). Consistent with the "ranging-asset" thesis and not a deal-breaker.

### Required Validation Before Deployment

- [x] Walk-forward 4-window test — **4/4 pass**
- [ ] Sharpe computation (CLI gap)
- [ ] Correlation analysis vs metals (the diversification claim is plausible but unverified)
- [ ] Investigate the 2025–2026 weakening: temporary regime, structural change, or warning sign?
- [ ] Regime-segmented analysis — particularly important given the W3 softness

### Significance

XBI is the **diversifier candidate**. It's not the highest-return option but it's likely the one with lowest correlation to the existing bot lineup. If it walks forward cleanly, it's a strong addition specifically for **portfolio-level risk reduction** — the most pressing remaining gate before real money.
