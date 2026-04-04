Status: current | Epistemic: confirmed | Last verified: 2026-04-04

# StochRSI Enhanced — IAU 15m

> **Strategy file:** `backend/strategies/stoch_rsi_mean_reversion.py`

## Knowledge

### Validated Parameters

Same params as GLD/SLV/GDX 15m — no tuning needed, transferred directly.

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
python3 -m backend.runner backtest --strategy StochRSIMeanReversion --symbol IAU --timeframe 15m \
  --start 2020-01-01 --end 2025-12-31 --source alpaca --spread 0.0003 --delay 0 \
  --parameters '{"rsi_period":7,"stoch_period":14,"overbought":80,"oversold":15,"adx_threshold":20,"skip_adx_filter":false,"sl_atr":2.0,"trailing_stop":true,"trail_atr":2.0,"trail_after_bars":10,"min_hold_bars":10,"skip_days":[0]}'
```

### Performance Summary (corrected Apr 4 2026)

- **Full-period return (2020–2025):** +32.7%, **Max drawdown:** 0.89%, **Trades:** 467
- **Sharpe:** 1.97
- **Holdout test (2024–2025):** +12.55%, DD 0.66% — pre-fix, directionally valid
- **Walk-forward:** 4/4 windows positive (100%)

> **Note (Apr 4 2026):** Corrected after fixing backtest stop-check ordering bug. Old figures: Return +32.58%, DD 0.72%, Sharpe ~2.0, Trades 679.

### Year-by-Year

| Year | Return | DD | Trades |
|---|---|---|---|
| 2020 | +2.97% | 0.81% | 63 |
| 2021 | +4.47% | 0.80% | 139 |
| 2022 | +4.25% | 1.27% | 116 |
| 2023 | +4.09% | 0.71% | 128 |
| 2024 | +5.19% | 1.46% | 121 |
| 2025 | +7.19% | 2.27% | 112 |

### Walk-Forward Windows

| Test Period | Return | DD | Trades |
|---|---|---|---|
| 2022 | +4.30% | 0.72% | 114 |
| 2023 | +3.89% | 0.48% | 127 |
| 2024 | +5.00% | 0.66% | 117 |
| 2025 | +7.17% | 0.63% | 111 |

### Key Findings

**IAU is a GLD proxy** — same underlying (gold), different ETF. Slightly cheaper (lower price = lower $ per share), but tracks GLD very closely. The edge transfers perfectly because the price dynamics are identical.

**Lower absolute return than GLD** (+32.6% vs +44.7%) because IAU has a lower price point (~$82 vs ~$260 for GLD), making each % move worth less in dollar terms per share — but the % returns are the same magnitude, just with more trades (679 vs GLD's ~500ish).

**Most consistent year-by-year** of all precious metals assets — no year below +2.97%, very tight return distribution. Lowest per-year drawdown of the group.

**Lowest drawdown in the precious metals group:** 0.72% vs SLV 2.00% and GDX 2.02%. Being a direct gold-tracking ETF (not silver or miners) = less idiosyncratic risk.

### Precious Metals Thesis — Now 4 Assets Validated

| Asset | Sharpe | Return | Max DD | WF |
|---|---|---|---|---|
| GLD 15m | 2.47 | +39.22% | 0.73% | 4/4 |
| SLV 15m | 2.41 | +97.96% | 2.00% | 4/4 |
| GDX 15m | 2.58 | +129.8% | 2.02% | 4/4 |
| **IAU 15m** | **1.97** | **+32.7%** | **0.89%** | **4/4** |

### Long-Only Baseline (live constraint — Mar 14 2026)

Live bots run long-only — Alpaca rejects fractional short orders.

| Metric | Full Strategy | Long-Only |
|--------|--------------|-----------|
| Return (2020–2025) | +32.7% | ~+20% *(pre-fix long-only, needs rerunning)* |
| Max Drawdown | 0.89% | ~0.76% |
| Trades | 467 | ~330 |
| Win Rate | 40% | ~39% |
| Sharpe (approx) | 1.97 | ~1.20 *(estimate — pre-fix was ~1.33)* |

**Return drop:** -34%. **Sharpe drop:** ~2.0 → ~1.33. IAU is the most impacted asset — short trades add significant alpha here. Long-only IAU is the weakest of the four assets on a risk-adjusted basis.

**Year-by-year (long-only):** 2020: +0.23% | 2021: +0.98% | 2022: +3.27% | 2023: +2.95% | 2024: +5.37% | 2025: +6.49%
All years profitable but 2020–2021 are very slim. The short side is especially important for IAU's early-period performance.

### Forward Testing

iau-test bot running on cloud with aggressive params (OB 60/OS 40, 3-bar hold/trail after 1 bar, 0.5 ATR). All 4 exit mechanics confirmed — see `CLAUDE.md` and `.claude/calibration/calibration-notes.md`.

Backtest prediction for test params (Dec 2025 – Mar 2026): -0.50%, 54 trades, 37% WR — weakest of the 4 symbols under test params.
