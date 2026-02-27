# StochRSI Enhanced — GDX 15m

> **Status:** VALIDATED (Sharpe 2.41, Feb 27 2026)
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
python3 -m backend.runner backtest --strategy StochRSIMeanReversion --symbol GDX --timeframe 15m \
  --start 2020-01-01 --end 2025-12-31 --source alpaca --spread 0.0003 --delay 0 \
  --parameters '{"rsi_period":7,"stoch_period":14,"overbought":80,"oversold":15,"adx_threshold":20,"skip_adx_filter":false,"sl_atr":2.0,"trailing_stop":true,"trail_atr":2.0,"trail_after_bars":10,"min_hold_bars":10,"skip_days":[0]}'
```

## Performance Summary (validated Feb 27 2026)

- **Full-period return (2020–2025):** +114.1%, **Max drawdown:** 2.02%, **Trades:** 539
- **Sharpe:** 2.41
- **Holdout test (2024–2025):** +31.7%, Sharpe 2.27 — minimal degradation
- **Walk-forward:** 4/4 windows positive (100%)

## Year-by-Year (Walk-Forward Windows)

| Test Period | Return | Sharpe | Trades |
|---|---|---|---|
| 2022 | +18.2% | 2.90 | 93 |
| 2023 | +10.7% | 1.73 | 91 |
| 2024 | +6.5% | 1.06 | 83 |
| 2025 | +23.6% | 3.52 | 117 |

## Key Findings

**Why it works:** GDX (gold miners ETF) is a leveraged proxy to gold — miners move 2-3× gold's daily moves due to operating leverage. The same mean-reversion oscillations exist at 15m, but with larger amplitude.

**Highest absolute return of the three** (+114% vs GLD +44.7%, SLV +105.3%) due to the leveraged nature of miners. Drawdown is similar to SLV (2.02%) — acceptable.

**2024 was the weakest year** (Sharpe 1.06) — GDX had some idiosyncratic miner-specific volatility. Still positive. 2025 was the strongest (Sharpe 3.52).

**Idiosyncratic risk note:** Unlike GLD/SLV which track metal prices directly, GDX can decouple from gold due to mining company factors (costs, strikes, management). This is the main risk vs GLD — monitored via the walk-forward results.

## Thesis Validation

GDX passing 4/4 walk-forward windows confirms the precious metals thesis extends to leveraged gold exposure. The mean-reversion structure is robust enough to survive the added noise from mining company fundamentals.

---

*Last updated: 2026-02-27 (Initial validation — params transferred from GLD, Sharpe 2.41, 4/4 WF)*
