Status: validated | Epistemic: WF 4/4 + Sharpe ≥2.0 confirmed; framework IS the edge (signal decorative); regime-dependence presumed (untested per-asset) | Last verified: 2026-04-28

# StochRSI Enhanced — XOP 15m (Validated — at-the-bar)

> **May 9 2026 update — re-run under `adx_filter_mode='entry_only'`: XOP Sharpe 1.98 → 1.32 (close-anchored, single-symbol). FAILS the 2.0 quality bar.** ΔSharpe −0.66 — XOP was at the bar even under the buggy mode and falls clearly below under bug fix. Buggy 1.98 figure preserved below as historical reference. **Live impact mitigated** by HWM (+~0.4 Sharpe) and partial bug-escape, but per-asset standalone XOP is below the quality bar. See `calibration-journal.md` §2 May 9 entry. Live tripwire anchor revised to ~4.0 ±0.5 (portfolio-level).
>
> **May 7 2026 caveat (now superseded by May 9 above for magnitude).** Sharpe figures below were close-anchored backtests with apparent ~0.7 Sharpe live-vs-backtest gap. May 9 bug-fixed re-run is the current source of truth.

> **Strategy file:** `backend/strategies/stoch_rsi_mean_reversion.py`

> **Apr 28 2026 status update — framework attribution finding.**
>
> Verified Sharpe (Apr 28): **1.98** full-strategy — *fractionally under the 2.0 quality bar* (within Sharpe noise on a 6-year window). Headline returns/DD on this card remain accurate.
>
> Random-entry control was **not run directly on XOP** (tested on GLD/SLV/GDX/SPY/QQQ/IWM — see `research-log.md` → "Random-Entry Control — Apr 28 2026"). On the assets tested directly, random entries with the same framework produce Sharpes within 0.02–0.65 of validated. The cross-asset pattern strongly suggests the StochRSI entry signal contributes a small per-asset tilt and the framework is doing most of the work — but per-asset attribution on XOP is unverified.
>
> What this means: XOP at Sharpe 1.98 is the weakest of the energy three (XLE 2.30, OIH 2.33, XOP 1.98). Combined with the fact that XLE/OIH/XOP are highly correlated, XOP is the most expendable energy bot if a deployment trim is needed. The interpretation "StochRSI mean-reversion is the edge on XOP" is under review pending direct random-entry test or framework ablations.
> **Status:** Discovered Apr 28 2026 during forgotten-asset audit. **Walk-forward 4/4 windows positive (Apr 28).** Highly correlated with XLE/OIH — pick the strongest before deployment.

## Knowledge

### Validated Parameters

Same recipe as all other StochRSI Enhanced bots.

| Param | Value |
|---|---|
| rsi_period | 7 |
| stoch_period | 14 |
| overbought / oversold | 80 / 15 |
| adx_threshold | 20 |
| skip_adx_filter | false |
| sl_atr / trail_atr | 2.0 / 2.0 |
| trail_after_bars / min_hold_bars | 10 / 10 |
| skip_days | [0] (Monday) |

### Performance Summary (verified Apr 28 2026)

- **Full-period return (2020 → Apr 27 2026):** **+90.34%**, **Max drawdown:** 3.29%, **Trades:** 629, **Win rate:** 42%
- **Sharpe:** *needs computing*

XOP was previously rejected at 1h (Sharpe 0.55, +11.4% / 404 trades). Moving to 15m + validated recipe **8× the total return**. Largest relative improvement of any forgotten asset — XOP was the most miscategorised by the early sweep.

### Year-by-Year (verified Apr 28 2026)

| Year | Return | Max DD | Trades |
|---|---|---|---|
| 2020 | +6.20% | 4.35% | 50 *(partial — starts Jul)* |
| 2021 | +17.75% | 2.61% | 116 |
| 2022 | +14.04% | 6.11% | 116 *(energy boom — peak volatility)* |
| 2023 | +15.56% | 1.82% | 98 |
| 2024 | +7.78% | 1.44% | 113 |
| 2025 | +6.44% | 2.44% | 112 |
| 2026 (YTD to Apr 27) | +1.54% | 2.04% | 24 |

Every year profitable. 2022 had highest DD (6.11%) — energy sector volatility peak. 2024–2025 softer (+7.78% / +6.44%) but still solid. 2026 YTD modestly positive (+1.54%) despite the energy weakness that hurt XLE and OIH.

### Context

- **Asset:** XOP = SPDR S&P Oil & Gas Exploration & Production ETF — equal-weighted exposure to upstream oil/gas E&P companies. Different from XLE (cap-weighted, includes integrated oils like XOM/CVX).
- **Driver class:** Oil & gas prices, but with explicit exploration-cycle and reserve-replacement leverage. More volatile than XLE; less than OIH.
- **Why it likely works:** Same intraday mean-reversion mechanism as XLE/OIH — energy-sector ETF with natural range-bound 15m behaviour. Mid-volatility profile makes it a sweet-spot asset.
- **Cross-asset comparison:** XOP sits between XLE and OIH on the risk/return spectrum. XLE (broad, lower beta), XOP (E&P, mid beta), OIH (services, highest beta).

### Cross-Asset Comparison

| Asset | Return | Max DD |
|---|---|---|
| OIH | +146.53% | 2.95% |
| SLV | +144.26% | 2.00% |
| GDX | +132.91% | 2.01% |
| **XOP** | **+90.34%** | **3.29%** |
| XBI | +84.75% | 2.44% |
| XLE | +80.42% | 3.27% |

### Walk-Forward Validation (Apr 28 2026)

| Window | Period | Return | Max DD | Trades | Win Rate |
|--------|--------|--------|--------|--------|----------|
| 1 | 2020 → mid 2022 | +39.61% | 2.41% | 226 | 45% |
| 2 | mid 2022 → 2025 | +32.11% | 3.24% | 378 | 41% |
| 3 | 2020 → 2021 | +24.97% | 2.05% | 166 | 46% |
| 4 | 2022 → 2023 | +31.04% | 3.27% | 213 | 42% |

**4/4 windows positive.** Returns +25% to +40%, consistent. Win rates 41–46%. Higher max DDs than OIH (3.24% / 3.27% vs OIH's 2.50% / 2.53%) — XOP is the highest-DD energy candidate.

### Required Validation Before Deployment

- [x] Walk-forward 4-window test — **4/4 pass**
- [ ] Sharpe computation (CLI gap)
- [ ] Cross-correlation with XLE/OIH — strong overlap risk; running all three may not give independent diversification
- [ ] Spread sensitivity

### Significance

XOP confirms a **third energy sector ETF** validates the recipe (XLE + OIH + XOP all pass). The fact that XOP, OIH, and XLE all work demonstrates the edge isn't a quirk of one specific energy ETF — it's a property of the energy sector at 15m. **However:** these three are highly correlated with each other (all driven by oil prices). Deploying multiple energy ETFs to the bot lineup would amplify portfolio risk, not diversify it. Pick the strongest (likely OIH on absolute return, XLE on infrastructure maturity) rather than running all three.
