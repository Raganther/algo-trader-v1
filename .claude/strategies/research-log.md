Status: current | Epistemic: confirmed | Last verified: 2026-04-08

# Research Log — Algo Trader V1

> **Purpose:** Cumulative reasoning across all strategy exploration. Not a results ledger — a record of what was tried, what was learned, and what it implies.
> Read this when deciding what to try next. Individual strategy cards hold the depth; this file holds the synthesis.

---

## StochRSI 1h Baseline — early 2026

**Tried:** StochRSI mean reversion on GLD, IAU, XLE at 1h timeframe. Standard params — overbought/oversold crossovers, fixed stop, no trailing component.

**Result:**

| Asset | Sharpe | Status |
|-------|--------|--------|
| GLD | 1.44 | Validated |
| IAU | 1.22 | Validated |
| XLE | 1.11 | Validated |

**Why:** StochRSI oscillator identifies genuine oversold/overbought conditions at 1h. ADX filter removes trades during strong trends where mean reversion fails. Positive but not compelling — Sharpe 1.1–1.4 range isn't high enough to justify deployment without further improvement.

**Implication:** Signal exists at 1h. The question is whether it can be improved by tightening timeframe, adding a trailing component, or both. 15m became the next test.

---

## SPY/QQQ/IWM — early 2026

**Tried:** StochRSI mean reversion on major US equity indices (SPY, QQQ, IWM) across 5m–15m timeframes.

**Result:** No alpha. All combinations failed to produce consistent positive returns across walk-forward windows.

**Why:** US equity indices are driven by macro flow and institutional momentum at these timeframes — mean reversion is quickly overwhelmed by trend continuation. The StochRSI OS/OB signal that works on gold (range-bound commodity with genuine mean-reverting behaviour) doesn't translate to equity indices where momentum dominates.

**Implication:** Asset selection matters. Mean reversion at this timeframe requires assets with natural range-bound behaviour. Broad equity indices are not that. Commodities and commodity-linked ETFs are a better hunting ground.

---

## StochRSI Enhanced 15m (GLD) — Feb 26 2026

**Tried:** Moved from 1h to 15m on GLD. Added trailing stop component (trail ATR multiplier, trail_after_bars gate) and min_hold_bars filter. Added ADX threshold and skip Mondays.

**Result:** GLD 15m — Sharpe 2.47, return +39.22%, max DD 0.73%, 465 trades (2020–2025). 4/4 WF pass. *(Corrected Apr 4 — stop-check fix. Pre-fix was Sharpe 2.54.)*

Previous 1h baseline was Sharpe 1.57. Enhancement nearly doubled Sharpe.

**Why the improvements worked:**
- **15m vs 1h:** Intraday noise at 15m gives more entry opportunities with tighter risk. The mean-reversion moves complete faster and more cleanly.
- **Trailing stop:** This is the critical component. 43% win rate sounds poor, but winners are 3–5x larger than losers — the trailing stop lets the position run through noise and captures the extended move. Without it, every trade exits at a fixed point and the edge collapses.
- **ADX filter (20 threshold):** Removes entries during strong trends where the oscillator oversold condition is not mean-reversion — it's momentum continuation. This filter is load-bearing. Without it, trade count roughly doubles and quality collapses.
- **Min hold 10 bars:** Filters noise entries that reverse immediately. Forces the position to stay open long enough for the trailing stop to ratchet.
- **Skip Mondays:** Monday gap-open volatility creates false OS readings. Removing Monday reduces noise trades.
- **Asymmetric OS/OB (80/15):** OS threshold of 15 is deliberately tight — only the deepest oversold conditions trigger entry. This keeps win rate on K-exits high. The asymmetry (80 OB vs 15 OS) reflects a long-only bias and that precious metals have more clean bounce setups than exhaustion setups in the training window.

**Implication:** The three components must work together: entry finds the setup, min_hold lets it breathe, trailing stop captures the move, K-signal closes it cleanly when momentum dies. Removing any one component meaningfully degrades the result.

**Key parameter sensitivity finding (GLD):** trail_atr is the most sensitive param. 2.0 is the validated sweet spot — tighter fires too early on noise, wider captures more but also holds through full reversals.

---

## Multi-Asset Generalisation (IAU, SLV, GDX) — Feb–Mar 2026

**Tried:** Same params as GLD validation — zero retuning — on IAU, SLV, GDX.

**Result:**

| Asset | Sharpe | Return | Max DD | WF |
|-------|--------|--------|--------|----|
| GLD | 2.47 | +39.22% | 0.73% | 4/4 |
| SLV | 2.41 | +97.96% | 2.00% | 4/4 |
| GDX | 2.58 | +129.8% | 2.02% | 4/4 |
| IAU | 1.97 | +32.7% | 0.89% | 4/4 |

All four validated. Every year profitable on all four assets.

**Why:** GLD, IAU, SLV are physically-backed precious metals ETFs tracking gold and silver spot price. Their 15m microstructure is nearly identical — same institutional participants, same hedging flows, same intraday mean-reversion dynamics. GDX adds mining equity beta on top of gold beta (energy costs, operating leverage) which increases volatility and DD but the same mean-reversion pattern holds.

**Key insight — GDX is structurally different:** GDX is a mining equity ETF, not a physical metal holder. It has its own beta layer: when oil prices spike, mining margins compress, and GDX falls harder than gold even in pro-metals regimes. This was confirmed during the Mar 2026 calibration window — GDX underperformed while the backtest predicted it strongest. Not a model error, a regime-specific structural divergence.

**Implication:** The params generalise without retuning across correlated assets. This is the key signal that the edge is a genuine market microstructure phenomenon, not a curve-fit to one asset. But highly correlated assets (GLD/IAU/SLV) will enter simultaneously — this matters for real-money position sizing.

---

## Long-Only vs Full Strategy Analysis — Mar 14 2026

**Tried:** Ran backtests with `long_only:true` on all 4 assets to establish baseline for live bots (which are long-only due to Alpaca fractional short selling restriction).

**Result (estimated — pre-Apr-4 fix, needs rerunning post-Apr-20):**

| Asset | Full Sharpe | Long-Only Sharpe | Verdict |
|-------|------------|------------------|---------|
| GLD | 2.47 | ~1.80 | Weaker without shorts |
| IAU | 1.97 | ~1.20 | Meaningfully weaker |
| SLV | 2.41 | ~3.10 | Better long-only |
| GDX | 2.58 | ~1.65 | Weaker without shorts |

**Why:** SLV (silver) has stronger long-side asymmetry than the others — silver mean-reverts more sharply from oversold conditions. GLD, IAU, GDX benefit from both sides. Long-only removes all short trades, which contribute meaningfully to the full edge on three of four assets.

**Implication:** Short trading is required for the full validated edge on GLD/IAU/GDX. SLV is viable long-only. Short trading is deferred until whole-share quantity sizing is implemented (Alpaca rejects fractional short sells). Long-only figures need rerunning post-Apr-20 with corrected engine.

---

## Composable Strategy Exploration — mid-Feb 2026

**Tried:** Systematic combination of all available building blocks on GLD 1h. 458 indicator combinations tested. Top 10 by Sharpe sent to full validation (walk-forward, multi-asset).

**Result:** 7 of 10 rejected (overfit). 3 passed.

| Combo | Return | WF Pass | Multi-Asset |
|-------|--------|---------|-------------|
| RSI extreme + Opposite zone | +0.3% | 75% | 3/3 |
| MACD cross + Donchian exit + SMA uptrend | +10.9% | 75% | 2/3 |
| RSI extreme + Trailing ATR 3x | +4.9% | 75% | 2/3 |

**Why 7 failed:** High Sharpe with low trade count (<50 trades) = fitting to noise. The backtest has enough degrees of freedom to find combinations that happened to work on 30–40 historical trades without any real signal.

**Critical overfitting heuristic confirmed:** Sharpe is not sufficient. Trade count is the overfitting guard. Anything under ~150 trades should be treated as suspect regardless of Sharpe. The 3 that passed all had 150+ trades and moderate (not extreme) Sharpe.

**Implication:** The composable framework is built and works. The 3 validated combos are not deployed — they're GLD 1h results, lower return potential than the 15m StochRSI edge. The more important output is the validated heuristic: high Sharpe + low trade count = overfit. Apply this to every future experiment.

**Status:** Framework available, combos not deployed. Revisit after full-edge StochRSI validation complete.

---

## EventSurprise — CPI Trading — Feb 17 2026

**Tried:** Trade GLD directionally after CPI/NFP/Unemployment surprises. Delayed entry (1 bar after event), time-based exit (4 bars = 1h), 0.5% stop.

**Result:**

| Config | Return | Max DD | Trades | Win Rate |
|--------|--------|--------|--------|----------|
| CPI-only (misses) | +2.36% | 0.13% | 14 | 86% |
| All events (beats+misses) | +2.95% | 1.10% | 58 | 48% |

**Why CPI works:** CPI misses (inflation below forecast) are genuinely directional for gold — lower inflation = dovish Fed expectation = non-yielding assets rally. The post-bar move develops AFTER the event bar closes (93% correct direction at 1h). Beats are noisy — market has already priced the hawkish scenario partially, reaction is less clean.

**Why NFP is weak:** Jobs data has a more complex relationship with gold — strong jobs = hawkish = gold down, but also = risk-on = dollar up = different dynamic. Signal exists (55% directional accuracy) but not strong enough to trade on its own.

**Key limitation:** Only ~3 CPI-miss trades per year. High win rate but too infrequent to be a primary strategy — it's a complement. The strategy is built and could run as a 5th bot alongside the StochRSI bots on the same symbols.

**Implication:** CPI-miss signal is real. 86% win rate on 14 trades is robust enough to be interesting. Next step is paper testing — the backtest can't verify fill mechanics for event-driven entries (timing is critical). Also worth testing SLV/IAU on the same CPI signal. Low priority until StochRSI calibration is complete.

---

## XLE Generalisation — Mar 28 2026

**Tried:** Same StochRSI Enhanced 15m params on XLE (Energy Select Sector SPDR) — completely different asset class from precious metals.

**Result:** Sharpe ~2.06, return +85.2%, max DD 3.35%, 4/4 WF. Every year profitable.

**Why this matters:** XLE tracks S&P 500 energy companies (oil majors, energy services) — driven by oil prices, not gold. The StochRSI 15m edge works on an asset with completely different underlying drivers and a different investor base. This confirms the edge is a **general intraday mean-reversion pattern** in liquid ETFs, not a precious-metals-specific effect.

**Higher DD on XLE (3.35% vs GLD's 0.73%):** Energy sector is more volatile than gold. Same edge, more volatile underlying = wider drawdowns. This is expected and not a concern — Sharpe still passes.

**Implication:** The hunting ground for new StochRSI 15m candidates is any liquid ETF with natural intraday mean-reversion behaviour. The params don't need retuning per asset — test as-is first, only tune if WF fails. Obvious next candidates: sector ETFs (XLF, XLK, XLV), commodity ETFs (USO, GDX variants), bond ETFs (TLT, HYG).

**Status:** Validated, deployed as 5th bot candidate post-Apr-20 calibration.

---

## Aggressive Params — Long-Only Backtest (Apr 8 2026)

**Context:** The live bots run OB 60/OS 40, trail 0.5 ATR after 1 bar, min hold 3 bars, ADX 50, no Monday skip — deliberately extreme settings to generate ~2× more trades for mechanics verification. The question: do these params have genuine edge, or is the live +3.85% return purely regime-driven?

**Ran:** Long-only backtest on all 4 symbols, 2020–2025 full cycle, same `long_only:true` as bots.

**Result:**

| Symbol | Total Return | Max DD | Trades | Win Rate |
|--------|-------------|--------|--------|----------|
| GLD | +5.17% | 1.55% | 1,616 | 41% |
| IAU | +8.94% | 1.59% | 1,419 | 43% |
| SLV | +17.23% | 4.23% | 1,643 | 44% |
| GDX | +6.81% | 2.65% | 1,711 | 46% |

**Year-by-year pattern — all 4 symbols:**

| Year | GLD | IAU | SLV | GDX |
|------|-----|-----|-----|-----|
| 2020 | -1.08% | -0.34% | -2.66% | -0.22% |
| 2021 | +1.22% | -0.33% | +4.44% | +0.40% |
| 2022 | -0.21% | +1.48% | +1.72% | +0.72% |
| 2023 | +0.47% | +1.73% | +1.51% | +0.63% |
| 2024 | +2.07% | +2.67% | +5.42% | +2.14% |
| 2025 | +2.66% | +3.27% | +5.94% | +3.00% |

**Why profitable despite 41–46% win rate:** Same mechanism as validated params — K-exit winners are larger than TS losses on average. The signal (mean-reversion entry) has real edge even at aggressive thresholds. But the trail at 0.5 ATR fires on noise constantly, capping winners and producing many small losses. The edge is real but thin.

**Why 2024–2025 are best years:** Metals bull market. The strategy is long-only during a sustained uptrend — bounces from oversold conditions in a rising market are cleaner and more frequently profitable. 2020 is worst (COVID volatility — trail fires constantly on extreme intraday swings). This is a regime effect: the strategy is not regime-neutral at aggressive params.

**Comparison to validated params (also long-only, estimated):**

| Symbol | Aggressive (6yr) | Validated long-only (estimated) |
|--------|-----------------|--------------------------------|
| GLD | +5.17% | ~+25% |
| IAU | +8.94% | ~+16% |
| SLV | +17.23% | ~+60% |
| GDX | +6.81% | ~+40% |

Validated params extract 4–8× more return with fewer trades and lower or comparable DD. The difference is not the signal — it's the position management (wide trail, long hold, selective entry).

**Key finding:** The live +3.85% in 13 days (Mar 20–Apr 7) is consistent with 2024–2025 run rates for aggressive params, not an outlier — but it is regime-dependent. 2020 shows negative returns with the same params. The live performance confirms the strategy has edge in the current regime, not across all regimes.

**Validated params backtests include shorts:** The headline Sharpe figures (GLD 2.47, IAU 1.97, SLV 2.41, GDX 2.58) are full long+short. Long-only validated Sharpe figures are estimates (GLD ~1.80, IAU ~1.20, SLV ~3.10, GDX ~1.65). Rerun with corrected engine post-Apr-20 to confirm.

---

## Live Calibration — Key Learnings (Mar 20 – Apr 7 2026)

**What this was:** 50 live paper trades on test params (OB 60/OS 40, 3-bar hold, 0.5 ATR trail). Simultaneous backtest on identical params. Comparison to validate the engine.

**Bugs found during calibration (execution layer):**
- Pre-market signal firing (market hours gate missing)
- Wash trade rejections from orphaned sell orders
- GDX trail update race condition (cancel async, new stop placed before shares freed)
- Overnight stop gap (DAY TIF expiry left position unprotected at open)
- Partial bar at market open (live bot firing on 0–2 min bars — bar-completion guard added)

**Bugs found in backtest engine:**
- Stop-check ordering bug: trailing stop ratcheted with current bar's close, then immediately checked current bar's low against elevated stop → 92% false stop exits. Fix: use pre-ratchet level for intrabar check. Impact: Sharpe 2.54→2.47 (GLD), trade count 710→465.
- Long-only vs full: backtest executing shorts that live bots never could — fundamentally mismatched comparison without `long_only:true`
- Trading hours not applied: backtest processing pre/post-market bars without `trading_hours:[13.5,20]`

**Live signal findings:**
- **K-exit win rate: 76%** (updated Apr 8, 62 trades) — confirms entry + K-exit has genuine alpha in live conditions. Slight dip from 80% as some K-exits on choppy days closed near entry. Still strongly positive.
- **TS win rate: 15%** (updated Apr 8, 62 trades) — by design at test params. 0.5 ATR trail fires on noise before position moves. Not informative about the validated strategy.
- **K/TS split: exactly 50/50** — matches backtest post-fix.
- **GDX consistently weakest** (initially 42%, recovered to 50% after Apr 6 active day — 3 trades including 2 K-exit winners) — partly regime (oil spike, mining cost margin compression during Iran conflict), partly structural (extra beta layer).
- **Correlated simultaneous entries:** GLD/IAU/SLV enter within seconds multiple times per week. With 2% risk per trade, 3 simultaneous entries = 6% portfolio in one correlated move. Requires correlation-aware position sizing before real money.
- **Market open is most active window** (13:30–14:15 UTC). Most profitable K-exit days start here. Whether persistent edge or regime-specific bounce pattern is unknown — test as explicit time-of-day filter post-calibration.
- **Single multi-day hold (GDX +3.267) outperformed 49 other trades combined.** Validated params (trail after 10 bars) are designed to capture this pattern more often. The validated strategy has a fundamentally different character from the test params.

**Stop slippage characterised (updated Apr 8, 33 stop exits):** Mean ~$0.025/share, median $0.010/share, 100% negative direction. New outlier Apr 6: GLD -$0.297 — largest in dataset, on a high-volatility day. Mean is skewed by outliers; median ($0.010) is more reliable. Slippage can spike significantly on volatile sessions. Backtest assumes $0. Known bias — will cause slight P&L overstatement in Layer 4. Add `stop_slippage` param post-Apr-20 if confirmed on larger sample.

**What this phase confirmed:** Both server-side exit mechanics work (stop loss + trailing stop). Execution audit integrity 100% across all 12 days checked. The infrastructure is sound.

**What remains unconfirmed:** Trail at validated params. The test params trail is not the edge — it's a noise-driven stop. The real trail (2.0 ATR, after 10 bars) is what lets winners run. It has never fired live. Second clean window on validated params (post-Apr-20) is the remaining confirmation.

**Overall position (Apr 8):** Two of three strategy components confirmed live (entry signal + K-exit, both exit mechanics). One component unconfirmed (trail at validated params). One regime tested (metals bull, 2024–2025 best historical years). Test params only — validated params never run live. Apr 20 calibration confirms the backtest engine; validated params forward test confirms the full edge.

---

## Cross-Cutting Learnings

These apply across all experiments — read before designing any new test.

**1. Trade count is the overfitting guard.**
Sharpe alone is meaningless. Under 150 trades = probable noise fit. 300+ trades = structurally meaningful. Check this before any result gets taken seriously.

**2. Walk-forward is the generalisation test.**
In-sample Sharpe means almost nothing. A strategy that passes 4/4 WF windows with consistent returns is making a real claim about generalisation. One that doesn't is likely overfit.

**3. Multi-asset is the strategy quality test.**
If params need retuning per asset, the edge is probably asset-specific curve fitting. If identical params work across 4–5 assets, the edge is structural. Always test multi-asset before deployment.

**4. ADX filter is load-bearing for mean-reversion.**
Trading mean-reversion into a trending market is the primary failure mode. ADX 20 threshold separates ranging from trending regime. Without this, trade count doubles and edge collapses. Check this applies to any new mean-reversion variant.

**5. The trailing stop defines the strategy's character.**
A tight trail (0.5 ATR) = noise-driven stop. A wide trail (2.0 ATR, after 10 bars) = position management tool that captures extended moves. These are completely different strategies wearing the same name. Win rate at 43% is acceptable when winners are 3–5x larger — that's the trail working as designed.

**6. Correlation is a sizing problem, not a signal problem.**
GLD/IAU/SLV have the same signal because they track the same underlying. Running all three simultaneously isn't three independent bets — it's one bet with 3x size. Correlation-aware position sizing (reduce per-trade risk when 3+ correlated bots in simultaneously) is required before real money. But before implementing sizing logic, run the portfolio correlation analysis (see Open Research Agenda) — the data may show the compounding loss risk is less severe than the theoretical maximum, or that GDX's structural divergence provides natural diversification.

**7. Asset-specific beta layers change drawdown, not the edge.**
GDX = gold beta + mining equity beta. XLE = energy beta. Higher volatility assets produce higher DD with the same Sharpe — not a bug, a property of the underlying. Don't retune params to lower DD on volatile assets; accept the DD or size smaller.

**8. Mean-reversion at 15m appears to be a general microstructure pattern.**
Works on precious metals (GLD, IAU, SLV, GDX), energy (XLE), and potentially other liquid ETFs. Fails on broad equity indices (SPY/QQQ/IWM) where momentum dominates at these timeframes. The boundary seems to be: does the asset have natural range-bound behaviour at intraday resolution? Commodities and commodity-linked ETFs: yes. Broad indices: no.

---

## Open Research Agenda

Ranked by expected value given current knowledge:

1. **Validated params forward test (post-Apr-20)** — confirm trail component in live conditions. Required gate before real money.
2. **Whole-share quantity sizing + short trading** — enables full edge on GLD/IAU/GDX. Significant Sharpe improvement.
3. **XLE forward test (5th bot)** — confirms generalisation to non-precious-metals asset in live conditions.
4. **Time-of-day filter** — market open (13:30–14:15 UTC) is consistently most active. Test as explicit param in backtest: does restricting entries to the open window improve Sharpe or reduce it?
5. **Sector ETF expansion** — apply StochRSI 15m to XLF, XLK, XLV, TLT. Same params, no retuning. Filter: Sharpe ≥ 2.0, WF 4/4, multi-asset.
6. **Overnight / multi-day hold variant** — the GDX +3.267 multi-day trade outperformed 49 others. Validated params partially capture this. Worth designing an explicit overnight hold strategy variant — possibly tighter entry conditions, wider trail, longer min_hold — that deliberately targets multi-day momentum continuation rather than intraday mean reversion.
7. **EventSurprise paper test** — CPI-miss signal (86% WR) needs live verification. Low frequency (~3/yr) but clean signal. Run as 5th or 6th bot alongside StochRSI.
8. **Portfolio correlation analysis** — run all 4 symbols simultaneously on validated params over the full 5-year backtest, align trades on a shared timeline, and tally outcomes of simultaneous positions: all win / all lose / mixed, split by year. This is read-only analysis — no strategy changes, no sizing changes. Purpose: determine empirically how often the theoretical worst case (3× simultaneous full-stop loss) actually occurs, and whether GDX's structural divergence from GLD/IAU/SLV provides natural diversification in practice. Year-by-year split is important — 2022 bear metals regime may show very different correlation behaviour from 2024–2025 bull. This analysis informs whether sizing logic is needed and at what scale. Requires a shared-timeline runner (simpler than full portfolio backtester — read-only, no execution logic). Do this before implementing sizing logic.

9. **Correlation-aware sizing algorithm** — design and implement position sizing logic that reduces per-trade risk when correlated bots are simultaneously in. Exact mechanism (fixed total exposure cap, scaling function, or K-value stagger) to be decided after portfolio correlation analysis confirms the severity. Required before real money. Late-session entry guard (block/halve size when signal fires within ~30 min of close, as DAY stops expire before providing protection) is the simpler companion mechanism — testable with the existing single-symbol engine, no portfolio runner needed.
