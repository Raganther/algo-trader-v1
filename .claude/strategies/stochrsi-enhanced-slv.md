Status: current | Epistemic: confirmed | Last verified: 2026-04-04

# StochRSI Enhanced — SLV 15m

> **Strategy file:** `backend/strategies/stoch_rsi_mean_reversion.py`

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
python3 -m backend.runner backtest --strategy StochRSIMeanReversion --symbol SLV --timeframe 15m \
  --start 2020-01-01 --end 2025-12-31 --source alpaca --spread 0.0003 --delay 0 \
  --parameters '{"rsi_period":7,"stoch_period":14,"overbought":80,"oversold":15,"adx_threshold":20,"skip_adx_filter":false,"sl_atr":2.0,"trailing_stop":true,"trail_atr":2.0,"trail_after_bars":10,"min_hold_bars":10,"skip_days":[0]}'
```

### Performance Summary (corrected Apr 4 2026)

- **Full-period return (2020–2025):** +97.96%, **Max drawdown:** 2.00%, **Trades:** 485
- **Sharpe:** 2.41
- **Holdout test (2024–2025):** +29.9%, Sharpe 2.30 — pre-fix, directionally valid
- **Walk-forward:** 4/4 windows positive (100%)

> **Note (Apr 4 2026):** Corrected after fixing backtest stop-check ordering bug. Old figures: Return +105.3%, DD 2.00%, Sharpe 2.54, Trades 544.

### Year-by-Year (Walk-Forward Windows)

> *Pre-fix data — directionally valid but exact figures will differ after the Apr 4 stop-check correction. Rerun deferred — tracked in `research-roadmap.md` → Deferred / Rerun.*

| Test Period | Return | Sharpe | Trades |
|---|---|---|---|
| 2022 | +23.3% | 4.65 | 82 |
| 2023 | +10.1% | 2.16 | 108 |
| 2024 | +16.6% | 2.28 | 103 |
| 2025 | +11.3% | 2.50 | 101 |

### Key Findings

**Why it works:** Silver shares the same mean-reversion structure as GLD within a precious metals trend. Same macro drivers (CPI, USD, rates) produce the same short-term oscillations. Params transferred without any tuning.

**Higher absolute return than GLD** (+97.96% vs +39.22%) because silver is more volatile — larger moves per trade. This comes with higher drawdown (2.00% vs 0.73%) — still excellent, but 2.7× GLD's DD.

**Baseline (unenhanced) was already Sharpe 1.31.** Enhancement (trailing stop + min hold + skip Monday) improved it to 2.41 — same structural improvement seen on GLD.

### Thesis Validation

This result confirms the **precious metals thesis**: the StochRSI Enhanced edge is not GLD-specific. It is a structural property of precious metals mean-reverting at 15m within a longer-term trend.

### Long-Only Baseline (live constraint — Mar 14 2026)

Live bots run long-only — Alpaca rejects fractional short orders.

| Metric | Full Strategy | Long-Only |
|--------|--------------|-----------|
| Return (2020–2025) | +97.96% | ~+65% *(pre-fix long-only, needs rerunning)* |
| Max Drawdown | 2.00% | ~1.15% |
| Trades | 485 | ~310 |
| Win Rate | 46% | ~47% |
| Sharpe (approx) | 2.41 | ~3.10 *(estimate — pre-fix was ~3.29; long-only SLV still likely best Sharpe of the four)* |

**Return drop:** ~-34%. **But Sharpe likely still IMPROVES:** 2.41 → ~3.10 (estimate). SLV is the outlier — the short trades were adding return but also adding disproportionate risk. Long-only SLV has a better risk-adjusted profile than the full strategy. This is notable: for SLV specifically, running long-only is not a degradation.

**Year-by-year (long-only):** 2020: +5.32% | 2021: +8.43% | 2022: +7.78% | 2023: +7.77% | 2024: +12.74% | 2025: +11.44%
Most consistent year-by-year profile of the four assets. All years strongly positive.

**Implication:** SLV long-only is viable as-is. No urgency to fix short selling for SLV specifically.

### Forward Testing

slv-test bot running on cloud with aggressive params (OB 60/OS 40, 3-bar hold/trail after 1 bar, 0.5 ATR). All 4 exit mechanics confirmed — see `CLAUDE.md` and `.claude/calibration/calibration-notes.md`.

Backtest prediction for test params (Dec 2025 – Mar 2026): +14.25%, 44 trades, 57% WR — strongest of the 4 symbols under test params.

### Overnight Gap Risk (Apr 23 2026)

SLV is the most gap-prone of the 4 symbols (full-history p95 abs gap 3.08%, p99 5.25%, max 13.87% — silver's intraday and overnight volatility runs ~2× gold). First materially-painful live overnight gap: Apr 23 — entry $70.48 Apr 22, GTC stop $70.15 triggered at open Apr 23 and filled at $68.74 (−$1.74/share = −$605 on 347 sh = −0.64% equity). Clean fill vs open print, not slippage; pure gap risk. The −2.41% event falls between p5 and p1 of the historical down-gap distribution. Current 25% notional cap already bounds worst-case p99 loss to ~1.3% equity per symbol — no SLV-specific sizing change needed. See `.claude/calibration/gap-distribution.md` for full distribution tables.
