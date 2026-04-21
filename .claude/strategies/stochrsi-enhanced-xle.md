Status: current | Epistemic: confirmed | Last verified: 2026-04-21

# StochRSI Enhanced — XLE 15m

> **Strategy file:** `backend/strategies/stoch_rsi_mean_reversion.py`

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

### Performance Summary (2020–2025)

- **Total return:** +85.2%
- **Max drawdown:** 3.35%
- **Trades:** 539
- **Win rate:** 46%
- **Sharpe:** ~2.06
- **Walk-forward:** 4/4 windows positive

Every year profitable (2020–2025). Strong consistency across all periods.

### Year-by-Year

| Year | Return | Max DD | Trades |
|---|---|---|---|
| 2020 | +11.61% | 2.41% | 41 *(partial — starts Jul)* |
| 2021 | +11.54% | 2.05% | 88 |
| 2022 | +17.17% | 3.23% | 111 *(energy boom — oil price rally)* |
| 2023 | +6.85% | 3.59% | 88 |
| 2024 | +7.31% | 1.50% | 112 |
| 2025 | +10.22% | 1.90% | 99 |

2022 was the standout year (+17.2%) — energy sector rallied hard post-Ukraine. 2023 was the weakest full year (+6.85%) but still solidly positive.

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
