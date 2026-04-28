Status: candidate | Epistemic: single-run verified, not walk-forward validated | Last verified: 2026-04-28

# StochRSI Enhanced — XOP 15m (Candidate)

> **Strategy file:** `backend/strategies/stoch_rsi_mean_reversion.py`
> **Status:** Discovered Apr 28 2026 during forgotten-asset audit. Single-run figures only — not walk-forward validated. Do not deploy until WF 4/4 + Sharpe ≥ 2.0 confirmed.

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

### Required Validation Before Deployment

- [ ] Walk-forward 4-window test
- [ ] Sharpe computation
- [ ] Cross-correlation with XLE/OIH — strong overlap risk; running all three may not give independent diversification
- [ ] Spread sensitivity

### Significance

XOP confirms a **third energy sector ETF** validates the recipe (XLE + OIH + XOP all pass). The fact that XOP, OIH, and XLE all work demonstrates the edge isn't a quirk of one specific energy ETF — it's a property of the energy sector at 15m. **However:** these three are highly correlated with each other (all driven by oil prices). Deploying multiple energy ETFs to the bot lineup would amplify portfolio risk, not diversify it. Pick the strongest (likely OIH on absolute return, XLE on infrastructure maturity) rather than running all three.
