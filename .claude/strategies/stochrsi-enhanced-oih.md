Status: candidate | Epistemic: single-run verified, not walk-forward validated | Last verified: 2026-04-28

# StochRSI Enhanced — OIH 15m (Candidate — Top-Tier)

> **Strategy file:** `backend/strategies/stoch_rsi_mean_reversion.py`
> **Status:** Discovered Apr 28 2026 during forgotten-asset audit. **Single-run figures only — not yet walk-forward validated.** Do not deploy as a bot until WF 4/4 + Sharpe ≥ 2.0 confirmed.

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
python3 -m backend.runner backtest --strategy StochRSIMeanReversion --symbol OIH --timeframe 15m \
  --start 2020-01-01 --end 2026-04-28 --source alpaca --spread 0.0003 --delay 0 \
  --parameters '{"rsi_period":7,"stoch_period":14,"overbought":80,"oversold":15,"adx_threshold":20,"skip_adx_filter":false,"sl_atr":2.0,"trailing_stop":true,"trail_atr":2.0,"trail_after_bars":10,"min_hold_bars":10,"skip_days":[0]}'
```

### Performance Summary (verified Apr 28 2026)

- **Full-period return (2020 → Apr 27 2026):** **+146.53%**, **Max drawdown:** 2.95%, **Trades:** 589, **Win rate:** 42%
- **Sharpe:** *needs computing* — likely top-tier given consistency profile

**OIH is currently the highest-return single asset we've ever tested with the validated recipe** — narrowly above SLV (+144%) and GDX (+133%). Discovery was unexpected: the DB had only 32 prior OIH experiments, all at 1h timeframe with old non-validated params (best old result Sharpe 1.05 / +40.9%). Moving to 15m + validated recipe more than tripled total return.

### Year-by-Year (verified Apr 28 2026)

| Year | Return | Max DD | Trades |
|---|---|---|---|
| 2020 | +14.47% | 1.87% | 32 *(partial — starts Jul)* |
| 2021 | +18.71% | 5.72% | 101 |
| 2022 | +20.33% | 3.71% | 98 |
| 2023 | +21.87% | 1.59% | 112 |
| 2024 | +12.33% | 1.26% | 111 |
| 2025 | +12.33% | 3.19% | 100 |
| 2026 (YTD to Apr 27) | -1.00% | 3.16% | 35 |

**Every full year strongly positive** (+12% to +22%). 2023 was the strongest (+21.87%). 2026 YTD slightly negative (-1.00%) — the only soft period in the dataset, mirrors XLE's negative 2026 partial year (oil/energy sector weakness post-Apr 22).

### Context

- **Asset:** OIH = VanEck Oil Services ETF — oil drillers, equipment manufacturers, services companies (Schlumberger, Halliburton, Baker Hughes, etc.)
- **Driver class:** Oil prices + sector-specific operating leverage (similar to GDX → gold relationship). Higher beta to oil than direct oil ETFs (USO).
- **Why it likely works:** Oil services has natural intraday mean-reversion at 15m — the underlying companies have high operating leverage, so they move sharply on oil headlines, then often retrace within hours. Same structural mean-reversion behaviour as gold miners (GDX) or silver (SLV).
- **Cross-asset comparison:** OIH is to XLE what GDX is to GLD — leveraged sector-equity proxy with amplified moves. Sister ETF to XOP (oil & gas explorers).

### Cross-Asset Comparison

| Asset | Return | Max DD | Trades | Apr 28 verified |
|---|---|---|---|---|
| OIH | **+146.53%** | 2.95% | 589 | ⭐ Highest return |
| SLV | +144.26% | 2.00% | 581 | |
| GDX | +132.91% | 2.01% | 581 | |
| XOP | +90.34% | 3.29% | 629 | |
| XBI | +84.75% | 2.44% | 602 | |
| XLE | +80.42% | 3.27% | 570 | |
| GLD | +49.83% | 1.18% | 728 | |
| IAU | +40.05% | 1.31% | 705 | |

### Required Validation Before Deployment

- [ ] Walk-forward 4-window test (train/test splits 2020–2022 / 2022–2025, 2020–2021 / 2022–2023, 2022–2023 / 2024–2025, etc.)
- [ ] Sharpe computation from equity curve
- [ ] Regime-segmented analysis — does it work in TRENDING_DOWN / HIGH_VOL?
- [ ] Cross-correlation analysis vs current 4 metals — does adding OIH increase or decrease portfolio diversification?
- [ ] Spread sensitivity — what's the breakeven cost?

### Significance

OIH is the **most exciting candidate from the Apr 28 audit**. It validates two structural hypotheses:
1. The StochRSI 15m edge generalises beyond precious metals to other commodity-linked sector ETFs.
2. Sector ETFs with high operating leverage (mining → GDX, oil services → OIH) tend to amplify the underlying mean-reversion edge — same mechanism that makes GDX (+133%) outperform GLD (+50%) on the same params.

Combined with XLE (+80%) and XOP (+90%), this means the validated edge works on **three distinct energy-sector ETFs** — not asset-specific curve fitting.
