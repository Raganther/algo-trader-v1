# StochRSI Enhanced — SLV 15m

> **Status:** VALIDATED (Sharpe 2.54, Feb 27 2026)
> **Strategy file:** `backend/strategies/stoch_rsi_mean_reversion.py`

## Validated Parameters

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

### Backtest command:
```bash
python3 -m backend.runner backtest --strategy StochRSIMeanReversion --symbol SLV --timeframe 15m \
  --start 2020-01-01 --end 2025-12-31 --source alpaca --spread 0.0003 --delay 0 \
  --parameters '{"rsi_period":7,"stoch_period":14,"overbought":80,"oversold":15,"adx_threshold":20,"skip_adx_filter":false,"sl_atr":2.0,"trailing_stop":true,"trail_atr":2.0,"trail_after_bars":10,"min_hold_bars":10,"skip_days":[0]}'
```

## Performance Summary (validated Feb 27 2026)

- **Full-period return (2020–2025):** +105.3%, **Max drawdown:** 2.00%, **Trades:** 544
- **Sharpe:** 2.54
- **Holdout test (2024–2025):** +29.9%, Sharpe 2.30 — minimal degradation
- **Walk-forward:** 4/4 windows positive (100%)

## Year-by-Year (Walk-Forward Windows)

| Test Period | Return | Sharpe | Trades |
|---|---|---|---|
| 2022 | +23.3% | 4.65 | 82 |
| 2023 | +10.1% | 2.16 | 108 |
| 2024 | +16.6% | 2.28 | 103 |
| 2025 | +11.3% | 2.50 | 101 |

## Key Findings

**Why it works:** Silver shares the same mean-reversion structure as GLD within a precious metals trend. Same macro drivers (CPI, USD, rates) produce the same short-term oscillations. Params transferred without any tuning.

**Higher absolute return than GLD** (+105% vs +44.7%) because silver is more volatile — larger moves per trade. This comes with higher drawdown (2.00% vs 0.69%) — still excellent, but 3× GLD's DD.

**Baseline (unenhanced) was already Sharpe 1.31.** Enhancement (trailing stop + min hold + skip Monday) improved it to 2.54 — same ~76% Sharpe improvement seen on GLD.

## Thesis Validation

This result confirms the **precious metals thesis**: the StochRSI Enhanced edge is not GLD-specific. It is a structural property of precious metals mean-reverting at 15m within a longer-term trend.

## Long-Only Baseline (live constraint — Mar 14 2026)

Live bots run long-only — Alpaca rejects fractional short orders.

| Metric | Full Strategy | Long-Only |
|--------|--------------|-----------|
| Return (2020–2025) | +105.3% | +68.3% |
| Max Drawdown | 2.00% | 1.15% |
| Trades | 544 | 336 |
| Win Rate | ~47% | 47% |
| Sharpe (approx) | 2.54 | ~3.29 |

**Return drop:** -35%. **But Sharpe IMPROVES:** 2.54 → ~3.29. SLV is the outlier — the short trades were adding return but also adding disproportionate risk. Long-only SLV has a better risk-adjusted profile than the full strategy. This is notable: for SLV specifically, running long-only is not a degradation.

**Year-by-year (long-only):** 2020: +5.32% | 2021: +8.43% | 2022: +7.78% | 2023: +7.77% | 2024: +12.74% | 2025: +11.44%
Most consistent year-by-year profile of the four assets. All years strongly positive.

**Implication:** SLV long-only is viable as-is. No urgency to fix short selling for SLV specifically.

## Forward Testing Status (as of Mar 10 2026)

slv-test bot running on cloud with aggressive params (OB 60/OS 40, 3-bar hold/trail).

**Backtest prediction for test params (Dec 2025 – Mar 2026):** +14.25%, 44 trades, 57% WR — strongest of the 4 symbols, consistent with silver's higher volatility.

**Mar 09 observation:** Trail ratcheted from $76.15 → $77.23 on a live trade. Bot K-signal exited first at $77.92 before trail could fire. Trailing stop UPDATE confirmed working. Trail FIRING still unconfirmed.

---

*Last updated: 2026-03-14 (Long-only baseline added. Forward testing active.)*
