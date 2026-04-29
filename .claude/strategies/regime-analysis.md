Status: current | Epistemic: classification confirmed; strategy-implication column revised Apr 29 with long-window evidence | Last verified: 2026-04-29

# Regime Analysis — Algo Trader V1

> **Purpose:** Market regime classification, statistics, and implications for strategy sizing and risk management.
> Read when: designing regime-aware sizing, interpreting live performance, planning regime-gated enhancements.

> **Apr 29 2026 update — regime preference re-ranked from real history.** The 18-cell HistData spot-proxy backtest (`long-window-validation.md`) shows:
> - **Strongest = sustained directional moves (bull or bear).** XAGUSD 2009–11 bull Sharpe +2.59; XAGUSD 2013–15 bear +2.04. Direction does not matter — character does.
> - **Decent in chop / recovery (~+1.5 Sharpe consistently).** Not the strongest, contrary to the original "mean reversion works cleanly in RANGING" framing.
> - **Weakest in regime transitions / sharp-top / violent collapse.** XAGUSD 2011 peak → 2012 = +0.80 (worst); XAUUSD 2011 peak → 2012 = +0.86; WTIUSD 2014–16 oil collapse = +1.11 with 5.51% DD.
>
> The "Strategy implication" column below is updated to reflect this. The Apr 28 framework-attribution finding stands: the position-management framework is doing the work, not the StochRSI signal. The Apr 29 addition: the framework's edge is biggest where there's a sustained move for the trailing stop to ride, smallest where regime is changing rapidly.

> **Apr 28 2026 caveat — framework attribution finding.** Regime classification, statistics, and transition probabilities below are objective price-action measurements and remain valid. However, sections that interpret regime through the lens of "StochRSI mean-reversion" should be re-read with the Apr 28 finding in mind: the StochRSI entry signal contributes only a small fraction of total Sharpe (`research-log.md` → "Random-Entry Control — Apr 28 2026"). Interpretations like "oversold bounces are cleaner in TRENDING_UP" are likely *framework × volatility* effects rather than *signal × regime* effects. The methodology is sound; some causal claims need re-grounding.

---

## What is a Regime?

A market regime is the prevailing character of price action over a sustained period. Four regimes defined:

| Regime | Definition | Strategy implication (revised Apr 29) |
|--------|-----------|---------------------|
| RANGING | ADX < 25, ATR normal | Decent — ~+1.5 Sharpe in real chop windows. Not the strongest regime despite the strategy name. |
| TRENDING_UP | ADX > 25, close > 200 SMA | **Strongest** — sustained bull = +2.0 to +2.6 Sharpe. Trailing stop rides the move. |
| TRENDING_DOWN | ADX > 25, close ≤ 200 SMA | **Also strongest** when the bear is sustained, not crashing — XAGUSD 2013–15 bear gave Sharpe +2.04. The original "dangerous long-only" framing was wrong; shorts and the framework handle real bears well. |
| HIGH_VOL | ATR > 1.5× its 50-bar rolling mean | **Weakest, especially during regime transitions.** Sharp-top / post-peak collapse hits Sharpe 0.8–1.1 with elevated DD. The actually-dangerous regime for the live lineup. |

HIGH_VOL takes priority over TRENDING — a volatile trending session is classified HIGH_VOL.

**The under-served regime label is "TRANSITION" / "POST-PEAK".** The current 4-label classifier mixes this case into HIGH_VOL or TRENDING_DOWN, but neither isolates it. Building a transition-detector (e.g. recent ATR spike + cross of 200-SMA opposite to prior trend, with elevated ADX) is the highest-leverage regime-engineering item — it would tag the worst environment for the bots specifically. Tracked in `research-roadmap.md` → Regime-Aware Sizing + Regime-Aware Asset Rotation.

**The classifier's highest-leverage application is asset rotation, not sizing.** The Apr 23 regime-sizing portfolio diagnostic showed broad regime multipliers do NOT improve drawdown-adjusted performance (baseline daily Sharpe 4.27 beats all variants). Apr 29 evidence reframes this: the bigger lift is using the regime classifier as an **asset-selection signal** across a wider universe — pause bots whose asset is in TRANSITION, activate bots whose asset is in sustained TRENDING. This is the strategic direction tracked in `research-roadmap.md` → "Regime-Aware Asset Rotation"; cheapest first step is a 30-asset observational scan with no live changes.

---

## Implementation

- **Module:** `backend/indicators/regime.py` — `classify_regime(df)` takes OHLC DataFrame, returns Series of regime labels. `regime_stats(regimes)` computes duration statistics.
- **Data:** Daily bars stored in `price_data_daily` table in `research.db`. Two sources merged: Yahoo Finance (GLD from Nov 2004, IAU from Jan 2005, SLV/GDX from Apr–May 2006) and Alpaca IEX (Jul 2020 onward). Alpaca is authoritative for the overlap period — Yahoo rows deleted where Alpaca rows exist for the same date. To extend/refresh: `python3 scripts/fetch_price_data_yfinance.py` (Yahoo, full history) or `python scripts/fetch_price_data.py --timeframe 1d --symbols GLD,IAU,SLV,GDX --start 2020-01-01` (Alpaca, recent only).
- **Analysis script:** `python scripts/analyse_regimes.py` — runs classifier, prints overall distribution, year-by-year breakdown, and transition matrix.
- **Parameters:** ADX period 14, SMA period 200, ATR period 14, ADX threshold 25, ATR vol lookback 50 bars, ATR vol multiplier 1.5×.

---

## Findings — GLD/IAU/SLV/GDX Daily (2004–2026)

*Extended dataset: Yahoo Finance back to ETF inception (GLD Nov 2004, IAU Jan 2005, SLV/GDX Apr–May 2006) merged with Alpaca from Jul 2020. 2091 daily bars per symbol. SMA(200) requires 200 bars to initialise — early years (2004–2005 for GLD, earlier for others) show inflated RANGING% as a result; treat pre-2007 as partially unreliable for regime distribution but valid for transition statistics once SMA is initialised.*

### Overall regime distribution (~20 years)

| Symbol | Bars | RANGING% | TRENDING_UP% | TRENDING_DOWN% | HIGH_VOL% |
|--------|------|----------|-------------|----------------|-----------|
| GLD | 2091 | 58.9% | 27.6% | 7.8% | 5.7% |
| IAU | 2091 | 60.4% | 28.8% | 3.1% | 7.7% |
| SLV | 2091 | 62.8% | 21.5% | 11.2% | 4.5% |
| GDX | 2091 | 79.6% | 11.2% | 3.4% | 5.8% |

**RANGING remains dominant at 59–80%.** GDX is structurally more ranging than the others (79.6%) — its trend regimes are shorter and less frequent. SLV has the highest TRENDING_DOWN exposure (11.2%) reflecting silver's higher volatility and sharper bear cycles.

> **2026 SLV HIGH_VOL note:** SLV is showing 27.7% HIGH_VOL in 2026 vs GLD's 17.0% (both per the extended-history classifier). Silver's naturally higher volatility makes the fixed 1.5× ATR HIGH_VOL threshold more sensitive for SLV. Consider symbol-specific ATR thresholds before deploying live regime-aware sizing — tracked in `research-roadmap.md` → Regime-Aware Sizing.

### Average regime duration (trading days)

| Symbol | RANGING avg | RANGING max | TRENDING_UP avg | HIGH_VOL avg |
|--------|------------|------------|----------------|-------------|
| GLD | 36.2 | 244 | 17.0 | 9.2 |
| IAU | 43.6 | 199 | 18.8 | 10.0 |
| SLV | 38.6 | 199 | 15.0 | 11.8 |
| GDX | 87.6 | 230 | 13.0 | 17.3 |

GDX ranging periods average 87 days — more than double the others. This reflects its structurally different character as a mining equity: it spends long stretches consolidating and has shorter, sharper trend episodes. HIGH_VOL periods are short across all symbols (9–17 days avg) — they resolve quickly.

### Year-by-year regime distribution — GLD

| Year | RANGING% | UP% | DOWN% | HIGH_VOL% |
|------|----------|-----|-------|-----------|
| 2020 | 95.6% | 0.7% | 3.7% | 0.0% |
| 2021 | 60.4% | 11.2% | 28.4% | 0.0% |
| 2022 | 66.2% | 14.2% | 13.4% | 6.2% |
| 2023 | 35.8% | 57.6% | 1.2% | 5.4% |
| 2024 | 60.2% | 34.2% | 0.0% | 5.6% |
| 2025 | 49.0% | 38.2% | 0.0% | 12.8% |
| 2026 | 30.4% | 46.4% | 6.2% | 17.0% |

*2020 shows 95.6% RANGING because SMA(200) was still initialising on the Alpaca dataset (data starts Jul 2020, only ~130 bars by year end). Treat 2020 as unreliable for regime distribution.*

**Key pattern:** TRENDING_DOWN dominated 2021 (gold gave back COVID gains). TRENDING_UP emerged strongly from 2023 onward as the metals bull began. 2026 is the most extreme year — 46.4% TRENDING_UP and 17.0% HIGH_VOL simultaneously, driven by the Iran conflict macro event.

### Transition matrices (% probability on regime exit)

**GLD:**

| From → | TRENDING_UP | TRENDING_DOWN | HIGH_VOL | RANGING |
|--------|------------|--------------|---------|---------|
| RANGING | 64.7% | 32.4% | 2.9% | — |
| TRENDING_UP | — | 15.2% | 36.4% | 48.5% |
| TRENDING_DOWN | 12.5% | — | 0.0% | 87.5% |
| HIGH_VOL | 76.9% | 0.0% | — | 23.1% |

**GDX:**

| From → | TRENDING_UP | TRENDING_DOWN | HIGH_VOL | RANGING |
|--------|------------|--------------|---------|---------|
| RANGING | 57.9% | 21.1% | 21.1% | — |
| TRENDING_UP | — | 23.5% | 17.6% | 58.8% |
| TRENDING_DOWN | 62.5% | — | 0.0% | 37.5% |
| HIGH_VOL | 28.6% | 0.0% | — | 71.4% |

Full matrices for all symbols: `python3 scripts/analyse_regimes.py`

**Key transitions:**
- **HIGH_VOL → TRENDING_UP: 77% (GLD), 75% (IAU), 50% (SLV), 29% (GDX).** Volatility spikes strongly precede uptrends in GLD/IAU. GDX is weaker — HIGH_VOL more often resolves back to RANGING (71%) for mining equities.
- **RANGING → TRENDING_UP: 55–68% across all symbols.** When ranging breaks, it breaks upward more often than downward.
- **TRENDING_DOWN → RANGING: 88% (GLD).** Downtrends almost always resolve back to ranging, not to uptrend directly. Mean reversion after a downtrend, not immediate reversal.
- **Current regime implication (as of 2026-04-22):** We are in HIGH_VOL. Based on GLD history, 77% probability the next regime is TRENDING_UP. Average HIGH_VOL duration is 9 days — if we're already several days in, resolution is likely soon. *(Point-in-time snapshot — rerun `analyse_regimes.py` for current classification.)*

---

## Implications for Strategy

### 1. Regime confirms structural edge

59–63% RANGING for GLD/IAU/SLV (79% for GDX) across 20 years is the foundation of Sharpe 2.47. This is not a recent artefact — it's a persistent market structure property of these ETFs. The ADX filter already partially gates on this, but the regime classifier quantifies it explicitly and enables more granular control.

### 2. Regime-dependency explains live performance

2023–2026 are the most TRENDING_UP years in the 20-year dataset. Long-only mean reversion in a bull uptrend = oversold bounces are cleaner and more frequently profitable. The live K-exit win rate of 76% is consistent with operating in the most favourable regime historically. This is not evidence the edge disappears in other regimes — but it will be weaker in a neutral RANGING environment and dangerous in TRENDING_DOWN.

**The second clean window caveat:** switching to validated params now means the forward test will also run in TRENDING_UP/HIGH_VOL — not in a typical RANGING environment. The confirmed Sharpe 2.47 is built across all regimes. We won't observe the strategy in a pure RANGING environment until the market returns to one. This is not a reason to delay — it's a reason to maintain realistic expectations about what the second window confirms.

### 3. Validated params timing aligns well with the current regime

The validated trail (2.0 ATR, after 10 bars) is far better suited to the current HIGH_VOL/TRENDING_UP environment than test params. A wider trail survives intraday noise that constantly stops out the 0.5 ATR trail. Switching to validated params now means entering the likely post-HIGH_VOL TRENDING_UP resolution with the right tool — long holds in an uptrend are exactly what the validated strategy captures.

### 4. HIGH_VOL is the regime to protect against

- 2026 HIGH_VOL is 17% for GLD — well above the 5.7% historical average
- The two largest slippage outliers in the live dataset (-$0.297, -$0.140) both occurred on high-volatility days
- TS exits cluster on high-volatility days — tight trail fires on noise
- HIGH_VOL resolves to TRENDING_UP 77% of the time for GLD/IAU — halve size (don't skip entirely); the following uptrend is worth participating in
- Average HIGH_VOL duration: 9 days — these periods resolve quickly
- Action: halve position size during HIGH_VOL regime

### 5. TRENDING_DOWN is rare but dangerous for long-only

- 7.8% of GLD days historically, nearly absent since 2023
- In a downtrend, oversold often means momentum continuation, not reversal
- TRENDING_DOWN resolves back to RANGING 88% of the time (GLD) — not directly to TRENDING_UP. Mean reversion after the downtrend, not an immediate reversal.
- Action: skip entries or reduce to 0.5% risk during TRENDING_DOWN

### 6. Regime duration as a real-time risk signal

Current regime length vs historical average tells you where you are in the cycle:
- Young ranging (< avg duration): low risk of flip, full size
- Old ranging (> avg duration): statistically overdue, reduce size
- Very old ranging (> 2× avg duration): elevated flip risk, further reduce

Average ranging duration: 36 days (GLD), 44 days (IAU), 39 days (SLV), 88 days (GDX). A new ranging period has typically 5–12 weeks of runway before flip risk rises meaningfully.

### 7. Post-HIGH_VOL transition as a supplementary signal

HIGH_VOL → TRENDING_UP 77% of the time for GLD. The first bars of a new uptrend after a volatility spike are often strong. This could be a supplementary entry signal for a trend-following variant alongside the mean-reversion strategy. Speculative — requires backtesting before use.

### 8. Regime sizing adds value — but needs portfolio validation before live use

The Apr 23 diagnostic tagged validated-params StochRSI trades with previous-completed daily regime at entry. Result: partial gradient. RANGING is strongest on aggregate Sharpe, HIGH_VOL long exposure is uneven, and TRENDING_DOWN is not a clean skip signal. See `.claude/strategies/regime-stochrsi-diagnostic.md`; regenerate with `python3 -m backend.analysis.stochrsi_regime_performance`.

Portfolio replay of simple regime multipliers did **not** justify broad live regime sizing. Baseline daily Sharpe 4.27 beat conservative 4.15, aggressive 4.00, and high-vol-only 4.19; conservative reduced max DD by only ~$90 while giving up ~$4,041 P&L. See `.claude/strategies/regime-sizing-portfolio-diagnostic.md`; regenerate with `python3 -m backend.analysis.regime_sizing_portfolio`.

Implication: keep regime as dashboard/context and a possible narrow high-conviction filter. Do not implement broad live regime sizing unless a future full shared-timeline portfolio runner shows materially better drawdown-adjusted performance.

---

## Regime-Aware Sizing Framework (proposed — not yet implemented)

| Regime | Regime age | Proposed risk per trade |
|--------|-----------|------------------------|
| RANGING | < avg duration | 2.0% (full) |
| RANGING | > avg duration | 1.5% |
| TRENDING_UP | Any | 1.5% |
| TRENDING_DOWN | Any | 0.5% or skip |
| HIGH_VOL | Any | 0.5% or skip |

This works alongside correlation-aware sizing — the two are independent dimensions. Correlation sizing controls how much risk is taken across simultaneous positions; regime sizing controls how much risk is taken in any given market environment.
