Status: current | Epistemic: headline confirmed; framework IS the edge (signal decorative); metals direction-dependent (regime risk) | Last verified: 2026-05-10

# StochRSI Enhanced — IAU 15m

> **May 10 2026 update — portfolio-level test confirms IAU's role: KEEP IN LINEUP.** Adding IAU to a 4-bot lineup (Run A → Run B in `portfolio-runner-lineup-selection.md`) lifts portfolio Sharpe 3.79 → 3.87 (+0.08). IAU contributes net positive diversification despite standalone Sharpe 1.88. The 2.0 per-asset bar is a candidate-addition screen, not a prune threshold.
>
> **May 9 2026 update — re-run under `adx_filter_mode='entry_only'`: IAU Sharpe 1.95 → 1.88 (close-anchored, single-symbol). Still below 2.0 (was already).** ΔSharpe −0.07 — IAU was the smallest bug-beneficiary, indicating its prior figure was honest. Buggy 1.95 figure preserved below as historical reference. See `calibration-journal.md` §2 May 9 entry. Live tripwire anchor revised to ~4.0 ±0.5 (portfolio-level).

> **Strategy file:** `backend/strategies/stoch_rsi_mean_reversion.py`

> **Apr 28 2026 status update — framework attribution finding.**
>
> Verified Sharpe (Apr 28): **1.95** full-strategy (just under the 2.0 quality bar) / **1.86** long-only. IAU is the weakest of the metals on a DD-adjusted basis. Headline returns/DD on this card remain accurate.
>
> Random-entry control was **not run directly on IAU** (tested on GLD/SLV/GDX/SPY/QQQ/IWM — see `research-log.md` → "Random-Entry Control — Apr 28 2026"). On the metals tested directly, random entries with the same framework produce Sharpe within 0.02–0.42 of validated. The cross-asset pattern strongly suggests the StochRSI entry signal is a small contributor here too and the framework is doing most of the work — but per-asset attribution is unverified.
>
> What this means: the metrics below are correct as a record of *what the validated recipe produces on IAU*. The interpretation "StochRSI mean-reversion is the edge on IAU" is under review pending direct random-entry test or framework ablations.

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

### Performance Summary (verified Apr 27 2026)

- **Full-period return (2020 → Apr 27 2026):** +40.05%, **Max drawdown:** 1.31%, **Trades:** 705, **Win rate:** 41%
- **Comparable 2020–2025 sub-window:** ~+32.2% (compounded from yearly), 679 trades
- **Sharpe:** *needs recompute* (CLI doesn't print Sharpe — previous +1.97 figure is suspect from same Apr 4 transcription as GLD)
- **Holdout test (2024–2025):** +12.55%, DD 0.66% — pre-fix, directionally valid

> **Apr 27 2026 correction:** Today's verified rerun produces 679 trades / ~+32.2% on the 2020–2025 window. The card previously claimed 467 trades / +32.7% from the Apr 4 transcription. **The return figure was approximately right; the trade count was wrong by ~45%.** Same pattern as GLD — the Apr 4 "post-fix" trade count appears to have been a transcription error. Engine itself is healthy (Apr 4 stop-check fix in place, see GLD card for full investigation). The pre-Apr-4 IAU trade count was 679 — today's number matches it exactly, meaning the fix produces effectively no change in trade count for IAU (it suppresses false same-bar stop fires, which IAU sees few of). **Pre-Apr-4:** +32.58% / 0.72% DD / 679 trades. **Apr 4 transcription (suspect):** +32.7% / 0.89% DD / 467 trades. **Apr 27 verified:** ~+32.2% / 1.31% DD / 679 trades on 2020–2025.

### Year-by-Year (verified Apr 27 2026)

| Year | Return | DD | Trades |
|---|---|---|---|
| 2020 | +3.11% | 0.81% | 63 *(partial — starts Jul)* |
| 2021 | +4.66% | 0.80% | 139 |
| 2022 | +4.23% | 1.26% | 116 |
| 2023 | +4.06% | 0.71% | 128 |
| 2024 | +5.21% | 1.44% | 121 |
| 2025 | +7.34% | 2.24% | 112 |
| 2026 (YTD to Apr 27) | +5.19% | 3.01% | 26 |

### Walk-Forward Windows

| Test Period | Return | DD | Trades |
|---|---|---|---|
| 2022 | +4.30% | 0.72% | 114 |
| 2023 | +3.89% | 0.48% | 127 |
| 2024 | +5.00% | 0.66% | 117 |
| 2025 | +7.17% | 0.63% | 111 |

### Key Findings

**IAU is a GLD proxy** — same underlying (gold), different ETF. Slightly cheaper (lower price = lower $ per share), but tracks GLD very closely. The edge transfers perfectly because the price dynamics are identical.

**Lower absolute return than GLD** (+32.7% vs +39.22%) because IAU has a lower price point (~$82 vs ~$260 for GLD), making each % move worth less in dollar terms per share — but the % returns are the same magnitude, just with fewer trades (467 vs GLD's 465 — nearly identical).

**Most consistent year-by-year** of all precious metals assets — no year below +2.97%, very tight return distribution. *(Year-by-year table pre-fix — trade counts will differ slightly)*

**Highest drawdown in the gold ETFs:** 0.89% vs GLD 0.73% (both post-fix). Still excellent. (Pre-fix DD was 0.72%; the fix surfaced a marginally wider drawdown as intrabar checks were corrected.)

### Precious Metals Thesis — Now 4 Assets Validated

| Asset | Sharpe | Return | Max DD | WF |
|---|---|---|---|---|
| GLD 15m | 2.47 | +39.22% | 0.73% | 4/4 |
| SLV 15m | 2.41 | +97.96% | 2.00% | 4/4 |
| GDX 15m | 2.58 | +129.8% | 2.02% | 4/4 |
| **IAU 15m** | **1.97** | **+32.7%** | **0.89%** | **4/4** |

### Long-Only Baseline (verified Apr 28 2026)

Live bots run both long and short since Apr 13. This long-only figure is the **practical floor**.

| Metric | Full Strategy | Long-Only |
|--------|--------------|-----------|
| Return (2020 → Apr 27 2026) | +40.05% | **+26.09%** |
| Max Drawdown | 1.31% | **0.68%** (much smoother) |
| Trades | 705 | **467** (~34% fewer) |
| Win Rate | 41% | **40%** |
| Sharpe | *recompute* | *recompute* (prior estimate ~1.20 was unverified) |

**Return drop:** −35%. **DD improvement:** −0.63% (much lower). IAU is the **asset most reliant on shorts** — removing them loses the most relative return.

**Year-by-year long-only (verified Apr 28 2026):**

| Year | Return | DD | Trades |
|---|---|---|---|
| 2020 | +0.38% | 1.23% | 44 *(partial)* |
| 2021 | +1.03% | 0.72% | 89 |
| 2022 | +3.28% | 1.30% | 80 |
| 2023 | +2.93% | 0.74% | 86 |
| 2024 | +5.35% | 1.10% | 76 |
| 2025 | +7.41% | 2.18% | 74 |
| 2026 (YTD to Apr 27) | +2.56% | 1.51% | 18 |

All years profitable but 2020–2021 are very slim (+0.38% / +1.03%). Shorts are structurally important for IAU's early-period performance — explains why the live bots have run IAU short multiple times in the recent tape. Old estimate (~+20%) was too pessimistic by ~6 percentage points.

### Forward Testing

iau-test bot running on cloud with aggressive params (OB 60/OS 40, 3-bar hold/trail after 1 bar, 0.5 ATR). All 4 exit mechanics confirmed — see `CLAUDE.md` and `.claude/calibration/calibration-journal.md`.

Backtest prediction for test params (Dec 2025 – Mar 2026): -0.50%, 54 trades, 37% WR — weakest of the 4 symbols under test params.
