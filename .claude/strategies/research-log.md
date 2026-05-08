Status: current | Epistemic: confirmed | Last verified: 2026-05-08

# Research Log — Algo Trader V1

> **Purpose:** Cumulative reasoning across all strategy exploration. Not a results ledger — a record of what was tried, what was learned, and what it implies.
> Read this when deciding what to try next. Individual strategy cards hold the depth; this file holds the synthesis.

---

## HWM Mechanism Falsification Audit — May 8 2026

**Trigger.** May 7 deployed HWM live with the causal claim that the +0.78 Sharpe lift came from being structurally insensitive to a 1-bar polling delay (vs close-anchored which amplifies it into ~0.7 Sharpe of optimism). The "+0.78 ≈ 0.7" coincidence in `trail-anchor-hwm.md:38` is load-bearing — if HWM is just a better signal extractor (not delay-immune), live HWM expectation should still be discounted by ~0.7 Sharpe and the live tripwires anchored to 5.73 are too generous.

**Method.** Falsification audit at `backend/analysis/audit_hwm_delay_sensitivity.py`. `--delay 1` is broken (paper_trader scalar override + ordering bug, not trivially fixable), so used **data-shift preprocessing**: shift OHLCV by 1 bar pre-backtest, re-run with delay=0. Strategy code untouched. Ran 4 cells: (close, hwm) × (shift=0, shift=1) on the long-window 7-bot. Decision rule (set in advance): falsified if `|Δsharpe(hwm)| ≥ 0.5 × |Δsharpe(close)|`.

**Result — H₀ SUPPORTED with caveats.** Δsharpe(close) = 0.42, Δsharpe(hwm) = 0.15. HWM is ~2.8× more delay-resistant than close-anchored, comfortably under the 0.5× threshold. **But only 0.42 of the predicted 0.7 close-anchored artifact reproduced** — data-shift is a coarser model than the real polling delay, which has sub-bar fill-price effects and polling-cadence variance the audit doesn't capture. Live HWM gap is probably ~0.2–0.3 Sharpe, not zero. Per-trade attribution (close vs hwm at shift=0): 3996 common entries, 94% bar-aligned, 6% (240 trades) where HWM exits earlier with **more profit** (+$54k aggregate), 0 where HWM holds longer — clean asymmetric finding consistent with both mechanisms (delay-resistance + better signal extraction). The disambiguation comes from the 2×2: the *additional* Sharpe drop close-anchored takes under shift (0.42 vs HWM's 0.15) is the delay-resistance signature.

**Implications.**
- The "+0.78 ≈ 0.7" identity in `trail-anchor-hwm.md` is overstated; it's a directional rhyme, not a causal identity. Edited the doc to soften the language.
- Live HWM tripwires should anchor at ~5.50 Sharpe (5.73 − ~0.23 buffer), not the bare 5.73. Not yet applied to `live_performance_report.py` — pending strategic call.
- The original "all backtest Sharpes overstate live by ~0.7" rule of thumb in the diagnostic should be read as 0.4–0.7 (audit lower bound = 0.42, original estimate 0.7).
- The mechanism support *strengthens* (does not weaken) the case for keeping HWM live. Pre-audit, +0.78 backtest could have been a backtest-only artifact; audit shows the mechanism is real, just weaker than headline framing implied.

**Files.** `.claude/calibration/audit-hwm-delay-mechanism.md` (full report + 2×2 + per-trade attribution), `.claude/calibration/audit-hwm-delay-mechanism.json` (machine-readable summary), `backend/analysis/audit_hwm_delay_sensitivity.py` (reproducible script). Edited: `trail-anchor-hwm.md` (caveat banner + softened language), `live-vs-backtest-iau-diagnostic.md` (magnitude refined "0.5–1.0" → "0.4–0.7"), `research-roadmap.md` (rows updated).

---

## Live-vs-Backtest Diagnostic + HWM Trail Anchor — May 7 2026

**Trigger.** Live perf report at 14 trading days showed metals four roughly tracking backtest, except IAU which diverged sharply (backtest +$384, live −$196). Drilled in to find the cause.

**Method.** Ran portfolio backtest over the same Apr 15 → May 7 window with same params, compared trade-by-trade against live `live_trade_log` + Alpaca closed-order history.

**Finding 1 — Backtest is structurally optimistic by ~0.7 Sharpe.** The backtest evaluates signals at bar Close with effective delay=0; live polls Alpaca every ~60s, so live's effective execution timing is ~1 bar after each bar Close. The phase shift propagates through `trail_after_bars=10` (trail activates on a different bar) and the close-anchored trail formula uses each bar's Close as reference (different bar = different reference Close = different trail level). On choppy price action where prices wobble around the trail level, live's stop fires while backtest's doesn't. Apr 23 IAU short was the smoking gun: same entry $89.05 in both, backtest let it run to K-exit at $88.00 (+$274), live got whipsawed at trail stop $89.10 (−$14). Wider trail (2.5 ATR) tested — does NOT mitigate (long-window Sharpe 4.95 → 4.33, DD 3.41% → 4.07%). The issue is structural to the trail formula's bar-Close anchoring, not parameter-tunable. **Implication:** all validated-edges Sharpes (GLD 2.48 etc.) overstate live by ~0.7. CLAUDE.md guidance "size for Sharpe 1.0–1.5 on metals" was correct intuition; this provides the mechanism.

**Finding 2 — HWM trail anchor closes the gap (Path 2 shipped).** New `trail_anchor` parameter on `stoch_rsi_mean_reversion.py` with values `'close'` (default — byte-identical to legacy) or `'hwm'` (anchors trail to trade's high-water-mark: highest High since entry for longs, lowest Low for shorts). HWM is intrinsic to the trade's price action, structurally insensitive to bar timing. **Long-window 7-bot result: Close +424.09% / 4.95 / 3.41% vs HWM +517.41% / 5.73 / 3.05%.** ΔSharpe +0.78, ΔDD −0.36pp, all 7 symbols improve, no regressions. The +0.78 lift ≈ the 0.7 estimated delay artifact, suggesting HWM in live should approximately recover the gap. **Why it works:** HWM fixes two problems at once — (a) timing-sensitivity (different bar = different Close = different trail) AND (b) noisy signal (bar Close is variable; trade's actual best price is invariant). The improvements compound.

**Implications across the project.**
- All headline backtest Sharpe figures should be read as close-anchored with ~0.7 live optimism. Live expectations subtract this.
- Spot/ETF Sharpe gap interpretation revised: both backtests have the delay artifact, so it can't explain a backtest-vs-backtest gap. The "ETF microstructure premium" hypothesis from `long-window-validation.md` remains open but is now decoupled from the live-deployment sizing question.
- Live forward-test tripwires anchored to backtest − 0.7. Sharpe<0.5 at 30d / <1.5 at 60d / <2.0 at 90d → degraded.
- Validated-edges Sharpe table needs eventual re-run with HWM for canonical reference.
- Pending strategic decisions: (1) flip live bots to `trail_anchor: hwm`, (2) flip strategy default `close → hwm`, (3) re-run per-asset Sharpe table, (4) test interaction with cap-shrink and small-capital configurations.

**Files.** `.claude/calibration/live-vs-backtest-iau-diagnostic.md` (full diagnosis), `.claude/strategies/trail-anchor-hwm.md` (HWM A/B + decision matrix), `backend/strategies/stoch_rsi_mean_reversion.py` (`trail_anchor` parameter), `backend/analysis/live_performance_report.py` (corrected tripwires).

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

## Regime-Segmented Diagnostic — Apr 23 2026

**Tried:** Tagged validated StochRSI Enhanced 15m trades with the previous completed daily regime at entry. Scope was deliberately narrow: current forward-test assets only (`GLD`, `IAU`, `SLV`, `GDX`), current validated strategy only (`StochRSIMeanReversion`), 2020–2025 window, long/short split. Full artifact: `.claude/strategies/regime-stochrsi-diagnostic.md`. Regenerate with `python3 -m backend.analysis.stochrsi_regime_performance`.

**Result:** Partial gradient, not a clean regime switch.

| Aggregate bucket | Long Sharpe | Short Sharpe | Read |
|------------------|-------------|--------------|------|
| RANGING | 6.55 | 6.67 | Strongest and most consistent |
| TRENDING_UP | 3.27 | 3.36 | Still profitable, weaker than ranging |
| TRENDING_DOWN | 3.39 | 1.90 | Not a clean skip signal |
| HIGH_VOL | 2.01 | 3.35 | Mixed; long side uneven by symbol |

**Why:** The core edge remains an intraday mean-reversion / trailing-stop payoff shape, not a pure regime bet. Daily regime still matters: RANGING gives the cleanest oscillator behaviour, while HIGH_VOL creates noisy long-side outcomes in SLV/GDX. But TRENDING_UP and even TRENDING_DOWN are not uniformly bad, because the strategy can still capture sharp reversions within those macro states.

**What this does *not* prove:** This was not run on SPY, QQQ, IWM, S&P futures, XLE, EventSurprise, or other previously tested strategy families. The early SPY/QQQ/IWM rejection still stands until those exact assets/strategies are rerun regime-segmented. Regime analysis has not resurrected them yet.

**Implication:** For current metals bots, regime is a candidate high-conviction sizing/filter input, especially favouring RANGING and treating HIGH_VOL long exposure cautiously. It does not justify broad live regime-aware sizing by itself. Phase 2 is now well-defined: rerun previously rejected strategies/assets by regime to test whether aggregate failure hid regime-specific edges.

**Follow-up portfolio replay:** `python3 -m backend.analysis.regime_sizing_portfolio` tested simple regime multipliers on the four-metals closed-trade portfolio. Baseline stayed best on daily Sharpe (4.27). Conservative sizing reduced max DD by ~$90 but gave up ~$4,041 P&L; aggressive and high-vol-only were also worse on Sharpe. Result: do **not** build broad regime-aware live sizing from this evidence. Regime remains useful as context or a narrow filter candidate, not a portfolio sizing layer.

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

**Result (estimated — pre-Apr-4 fix; rerun deferred, see `research-roadmap.md` → Deferred / Rerun):**

| Asset | Full Sharpe | Long-Only Sharpe | Verdict |
|-------|------------|------------------|---------|
| GLD | 2.47 | ~1.80 | Weaker without shorts |
| IAU | 1.97 | ~1.20 | Meaningfully weaker |
| SLV | 2.41 | ~3.10 | Better long-only |
| GDX | 2.58 | ~1.65 | Weaker without shorts |

**Why:** SLV (silver) has stronger long-side asymmetry than the others — silver mean-reverts more sharply from oversold conditions. GLD, IAU, GDX benefit from both sides. Long-only removes all short trades, which contribute meaningfully to the full edge on three of four assets.

**Implication:** Short trading is required for the full validated edge on GLD/IAU/GDX. SLV is viable long-only. Short trading is deferred until whole-share quantity sizing is implemented (Alpaca rejects fractional short sells). Long-only figures rerun deferred — tracked in `research-roadmap.md` → Deferred / Rerun.

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

**Status:** Validated, queued as 5th bot candidate — gated on correlation-aware sizing per roadmap.

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

**Validated params backtests include shorts:** The headline Sharpe figures (GLD 2.47, IAU 1.97, SLV 2.41, GDX 2.58) are full long+short. Long-only validated Sharpe figures are estimates (GLD ~1.80, IAU ~1.20, SLV ~3.10, GDX ~1.65). Rerun with corrected engine deferred — tracked in `research-roadmap.md` → Deferred / Rerun.

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
- **K-exit win rate: 76%** (updated Apr 10, 67 completed trades) — confirms entry + K-exit has genuine alpha in live conditions. Slight dip from 80% as some K-exits on choppy days closed near entry. Still strongly positive.
- **TS win rate: ~17%** (updated Apr 10, 67 completed trades) — by design at test params. 0.5 ATR trail fires on noise before position moves. Not informative about the validated strategy.
- **K/TS split: approximately 50/50** — matches backtest post-fix.
- **GDX consistently weakest** (initially 42%, recovered to 50% after Apr 6 active day — 3 trades including 2 K-exit winners) — partly regime (oil spike, mining cost margin compression during Iran conflict), partly structural (extra beta layer).
- **Correlated simultaneous entries:** GLD/IAU/SLV enter within seconds multiple times per week. With 2% risk per trade, 3 simultaneous entries = 6% portfolio in one correlated move. Requires correlation-aware position sizing before real money.
- **Market open is most active window** (13:30–14:15 UTC). Most profitable K-exit days start here. Whether persistent edge or regime-specific bounce pattern is unknown — test as explicit time-of-day filter post-calibration.
- **Single multi-day hold (GDX +3.267) outperformed 49 other trades combined.** Validated params (trail after 10 bars) are designed to capture this pattern more often. The validated strategy has a fundamentally different character from the test params.

**Stop slippage characterised (updated Apr 8, 33 stop exits):** Mean ~$0.025/share, median $0.010/share, 100% negative direction. New outlier Apr 6: GLD -$0.297 — largest in dataset, on a high-volatility day. Mean is skewed by outliers; median ($0.010) is more reliable. Slippage can spike significantly on volatile sessions. Backtest assumes $0. Known bias — will cause slight P&L overstatement in Layer 4. Add `stop_slippage` param after Layer 3 confirms bias on larger sample — tracked in roadmap → Calibration.

**What this phase confirmed:** Both server-side exit mechanics work (stop loss + trailing stop). Execution audit integrity 100% across all 12 days checked. The infrastructure is sound.

**What remains unconfirmed (as of Apr 8):** Trail at validated params. The test params trail is not the edge — it's a noise-driven stop. The real trail (2.0 ATR, after 10 bars) is what lets winners run. It has never fired live. *(Resolved Apr 20: validated trail fired in profit on SLV, GLD, IAU — see roadmap Resolved section.)*

**Overall position (Apr 8):** Two of three strategy components confirmed live (entry signal + K-exit, both exit mechanics). One component unconfirmed (trail at validated params). One regime tested (metals bull, 2024–2025 best historical years). Test params only — validated params never run live. Apr 20 calibration confirms the backtest engine; validated params forward test confirms the full edge.

---

## Forgotten Testing Surface Audit — Apr 27 2026

**Tried:** Inventoried `backend/research.db` to map all historical experiments against the strategy domain files. Found a far broader testing surface than the `.claude/strategies/` directory documents.

**Result:** 5,380 experiments and 606 test runs spanning 13 symbols and 4 strategy implementations. Most date from Feb 11–12 2026 — pre-fix, pre-validated-recipe, pre-regime-lens. Domain files cover GLD/IAU/SLV/GDX/XLE + EventSurprise. The DB also tested:

| Symbol | Strategy/TF | Best Sharpe | Best Return | Trades | Documentation status |
|--------|-------------|-------------|-------------|--------|---------------------|
| XBI (biotech) | StochRSI 15m | 1.18 | +23.5% | 1,072 | One-line mention in GLD card ("Sweep positive 0.90 1h") — no domain file |
| TLT (20Y bonds) | StochRSI 1h | 0.85 | +10.7% | 1,359 | Same — no domain file |
| OIH (oil services) | StochRSI 1h | 1.05 | +40.9% | 451 | Not mentioned anywhere |
| XOP (oil & gas explorers) | StochRSI 1h | 0.55 | +11.4% | 404 | Not mentioned |
| SPY/QQQ/IWM/DIA | StochRSI 1h | 0.20–0.63 | — | — | Documented as dead end in this file |
| GLD | DonchianBreakoutStrategy 15m | 1.50 | +129.3% | 3,226 | Not mentioned (only Composable's MACD/Donchian mix is) |
| GLD | MACDBollingerStrategy | 0.23–0.46 | — | — | Not mentioned |

**Why these results may not be definitive any more:**
1. **Apr 4 stop-check fix** — corrected engine changed Sharpe by ±0.07 on metals, +0.17 on GDX. Old rejections were on a buggy engine.
2. **Validated recipe** (OB80/OS15, 2.0 ATR trail after 10 bars, skip Monday, ADX 20 filter) was developed mid-Feb after most of these tests ran. They used older parameter combos.
3. **Extended data window** — all DB tests end Feb 12 2026. We now have through Apr 27 — 11 weeks of additional out-of-sample including the Apr 22 metals selloff and the bar-completion-guard era.
4. **Regime-aware lens** — Apr 23 partial-gradient diagnostic shows aggregate-Sharpe-near-zero is consistent with "works in RANGING, cancels in TRENDING." SPY/QQQ/IWM rejection at aggregate Sharpe 0.20–0.63 may hide RANGING-only edges. Same logic for the energy variants and TLT.

**Why it matters:** The "validated edge is precious metals + energy at 15m" claim rests on having actually checked the alternatives with current best practices. We haven't. Three of the candidates (XBI, OIH, DonchianBreakout on metals) sit in the 1.0–1.5 Sharpe band — close enough to the 2.0 quality bar that a corrected-engine + better-params + longer-window rerun could plausibly push them across.

**Implication:** There's a meaningful body of work to revisit before declaring the strategy library complete. Action items captured in `research-roadmap.md` → "Strategy Validation" (forgotten-asset retests) and "Regime-First Research Programme" Phase 2 (broad-index regime resurrection).

**What this audit is NOT:** an indictment of past testing. The Feb sweep was the right exploration breadth at the time. The gap is just that we never circled back to revalidate the borderline candidates after the engine fixes. With a calibrated engine and 11 weeks of forward-test confirmation, the cost-benefit on revisiting them has flipped.

---

## Forgotten Asset Reruns — Apr 28 2026 Result

**Tried:** Applied the validated StochRSI Enhanced 15m recipe (OB80/OS15, ADX 20, 2.0 ATR trail after 10 bars, skip Monday) to the four borderline-candidate assets identified in the Apr 27 audit: XBI (biotech), OIH (oil services), TLT (bonds), XOP (oil & gas explorers). All four had been tested at 1h timeframe with old non-validated params in Feb 2026 and shown Sharpe 0.55–1.18 — close to but below the 2.0 quality bar. Hypothesis: corrected engine + validated recipe + extended data window would push some across.

**Result:**

| Asset | Old (1h, Feb) | New (15m validated, Apr 28) | Verdict |
|-------|---------------|----------------------------|---------|
| OIH | Sharpe 1.05 / +40.9% | **+146.53% / 2.95% DD / 589 trades / 42% WR** | ⭐ Top tier — highest single-asset return ever tested |
| XOP | Sharpe 0.55 / +11.4% | +90.34% / 3.29% DD / 629 trades / 42% WR | Strong pass |
| XBI | Sharpe 1.18 / +23.5% | +84.75% / 2.44% DD / 602 trades / 43% WR | Strong pass |
| TLT | Sharpe 0.85 / +10.7% | +20.87% / 1.16% DD / 866 trades / 40% WR | Rejected — below quality bar |

**Why three passed and one didn't:** The same structural pattern that made the metals work (commodity-linked, sector-equity beta amplification, intraday range-bound at 15m) applies to oil services, oil E&P, and biotech. All four are volatile, news-driven, sector-specific assets with natural intraday mean-reversion behaviour. **TLT is structurally different** — bonds at 15m are driven by rate-curve dynamics, not range-bound microstructure. Mean-reversion is overwhelmed by rate-trend continuation, exactly the same failure mode that killed StochRSI on broad equity indices (SPY/QQQ/IWM). This is a useful **negative result**: the StochRSI 15m edge is not universal — it requires assets with natural range-bound microstructure, not assets where macro-trend dominates.

**Why this matters more than the metals correction:** Today's discovery roughly **doubles the validated strategy universe.** Before: 5 candidates (4 metals + XLE). After: 8 candidates (5 + OIH/XOP/XBI). The portfolio expansion is structurally important because:
- **OIH is the new highest-return asset** by absolute number (+146% vs SLV's +144%).
- **XBI is largely uncorrelated** with metals or energy — the most useful diversifier identified, directly relevant to the Critical Path correlation-aware-sizing question.
- **XOP/OIH/XLE** all validate the same energy-sector edge — proves the pattern generalises within a sector, not just to one specific ETF.

**What this is NOT:** validated for deployment. Each candidate has had **one backtest** on the full 2020 → Apr 27 2026 window. The cross-cutting learning is explicit: walk-forward is the generalisation test. Single-period numbers are the first gate, not the last. None of OIH/XOP/XBI gets to a paper bot until 4/4 walk-forward windows + Sharpe computation are complete.

**Implication:** Don't celebrate yet, but the strategy library just got a lot more interesting. Walk-forward queue (next major work) plus Phase 2 regime-segmented broad-index resurrection (still open, may unlock more) are now the two biggest sources of additional candidates.

**Apr 28 follow-up — WF validation complete.** All 3 candidates (OIH/XBI/XOP) passed 4/4 walk-forward windows. OIH range +35–57% per window, XBI +17–39%, XOP +25–40%. Win rates stable 41–47% across all 12 sub-period tests. The edge generalises across COVID, post-COVID, 2022 bear, 2023 recovery, and 2024–2025 bull regimes. Status on each card promoted from "candidate" to "validated." Still pending: Sharpe computation (CLI gap, affects all 9 validated assets), cross-correlation among XLE/OIH/XOP (likely overlap), correlation of XBI vs metals (diversification claim). The validated bot universe is now **8 assets** (4 metals + XLE + OIH + XOP + XBI), and the strategy library is empirically denser than any prior point in the project.

---

## Held-Out Generalisation Test — Apr 28 2026

**Tried:** Ran the validated recipe (15m, OB80/OS15, 2.0 ATR trail after 10 bars, skip Mon, ADX 20) on 12 novel assets across diverse driver classes — assets we had **no prior signal on**. Three categories: (A) sector ETFs we'd never tested (XLF/XLV/XLI/XLK/KRE), (B) genuinely different drivers (UUP currency, GBTC bitcoin, EWZ emerging market, ITA defense), (C) **predicted failures** (VXX volatility, ARKK growth, TQQQ 3× leveraged Nasdaq). The hypothesis was that the strategy works on liquid sector ETFs but fails on trend-dominated assets — a boundary check rather than another expansion.

**Result: every single asset passed.** Including all three predicted failures.

| Asset | Driver class | Return | DD | Trades | WR | Predicted | Actual |
|-------|--------------|--------|-----|--------|----|-----------| -------|
| VXX | Volatility | **+200.92%** | 4.33% | 729 | 44% | should fail | extreme pass |
| TQQQ | 3× leveraged tech | +187.88% | 6.58% | 705 | 41% | should fail | extreme pass |
| ARKK | Disruptive growth | +98.20% | 3.48% | 539 | 41% | should fail | pass |
| XLK | Tech sector | +82.73% | 2.08% | 629 | 45% | should pass | pass |
| KRE | Regional banks | +76.20% | 1.68% | 596 | 45% | should pass | pass |
| EWZ | Brazil emerging | +52.86% | 2.49% | 523 | 44% | uncertain | pass |
| GBTC | Bitcoin | +48.59% | 2.75% | 216 | 49% | uncertain | pass |
| ITA | Defense | +32.22% | 1.92% | 379 | 39% | uncertain | pass |
| XLI | Industrials | +26.67% | 1.80% | 666 | 43% | should pass | pass |
| XLV | Healthcare | +22.66% | 1.35% | 728 | 43% | should pass | pass |
| XLF | Financials | +22.01% | 2.60% | 618 | 40% | should pass | pass |
| UUP | US dollar | +10.02% | 0.76% | 557 | 41% | uncertain | marginal |

**Why this is destabilising rather than just exciting:** The whole point of the held-out test was to find the boundary. If everything passes, either (a) the strategy is universally robust on liquid ETFs with sufficient volatility — a much stronger claim than we'd previously made — or (b) the test design isn't actually distinguishing real edge from artefact. Both interpretations need to be taken seriously.

**The three artefact risks:**
1. **Long-bias / regime artefact.** 2020–2026 was a sustained bull market for almost all risk assets. Even VXX shorts win because volatility declined on average over the period. The strategy may be implicitly riding equity-correlated beta, not capturing a structural mean-reversion edge. The honest control would be intraday data from the 2007–2010 bear or the dot-com 2000–2003 era — but Alpaca's intraday history doesn't reach back that far.
2. **Survivorship bias.** The 12 assets are all liquid survivors of the past 6 years. Failed SPACs, delisted ETFs, and crashed-then-recovered names aren't in the set. The strategy might fail on the assets that didn't survive.
3. **Recipe over-robustness.** If the validated recipe is so generic that any volatile liquid ETF produces +10–200% over 6 years, it might not be capturing a *specific* mean-reversion edge — it might just be a long-vol strategy with a sensible exit rule. That's still useful, but it's a different claim from what we've been making.

**The single most informative follow-up:** re-run SPY/QQQ/IWM/DIA/TLT with the validated recipe. Cross-cutting learning #10 below claims the strategy "fails on broad equity indices (SPY/QQQ/IWM)" — but that finding came from **old params on the broken engine**. We never re-tested with the validated recipe. If they pass too, the boundary thesis is broken and we need a new mental model. If they still fail, the boundary is real and the held-out result is the strongest validation we've ever produced.

**What this is NOT:** a green light to deploy any of the 12 held-out assets. They have one backtest each. The interpretation is unresolved. Until the SPY/QQQ retest answers the boundary question, treat all 12 as pending — interesting data points, not validated edges. **The cross-cutting learning #10 below is now in question and should be marked as such until resolved.**

**Implication:** The next session-defining work is the boundary verification (5 more backtests, 5 minutes of compute). After that, depending on the result, either an expansion of how we think about the strategy universe, or a confirmation that we found a genuine sector-specific edge.

---

## Boundary Verification — Apr 28 2026

**Tried:** Re-ran SPY/QQQ/IWM/DIA on the validated recipe (15m, OB80/OS15, 2.0 ATR trail after 10 bars, skip Mon, ADX 20, dynamic_adx false), 2020-07-27 → 2026-04-27 (Alpaca's 15m horizon for these symbols). TLT was already covered by the Apr 28 forgotten-asset audit (rejected, +20.87% / 1.16% DD / 866 trades / 40% WR — bonds dominated by rates dynamics, not microstructure mean-reversion).

**Result: all 4 broad equity indices pass the positive-return gate.**

| Asset | Return | Max DD | Trades | Win Rate | Ann. Return |
|-------|--------|--------|--------|----------|-------------|
| IWM | **+57.42%** | 1.43% | 655 | 46% | ~9.4%/yr |
| DIA | +27.32% | 2.56% | 639 | 40% | ~4.4%/yr |
| QQQ | +27.17% | 2.19% | 733 | 40% | ~4.4%/yr |
| SPY | +21.94% | 2.02% | 655 | 40% | ~3.6%/yr |

Year-by-year (per yearly DB rows): SPY/QQQ/DIA all show every full year positive except QQQ 2021 (-0.65%) and DIA 2023 (-1.35%) — both shallow (<3% DD). IWM positive every year except 2026 partial (-0.49% on 45 trades). 2022 was the strongest year for all four (bear-market regime favoured the mean-reversion edge).

**Interpretation: the boundary thesis is illusory.** Cross-cutting learning #10's claim that the strategy "fails on broad equity indices (SPY/QQQ/IWM)" was driven by old params on the broken stop-check engine, never re-tested with the validated recipe. With current params + healthy engine, all four broad indices are profitable on the same window where the metals/energy assets produced 40–146%. IWM (1.43% DD, 46% WR) is the cleanest of the four — DD-adjusted profile is competitive with the validated lineup.

**But — returns are lower than the validated names.** SPY at +22% / 5.7yr (~3.6%/yr) is the weakest result we've seen on a passing asset; IWM at +57% / ~9.4%/yr is mid-pack but well below SLV/GDX/OIH territory. Possible readings:
1. **Microstructure edge is universal but stronger on volatile sector/commodity ETFs.** Broad indices have lower intraday volatility → smaller mean-reversion amplitude → lower per-trade edge → lower aggregate return. Same edge, scaled down.
2. **Beta-amplification reading.** The metals/energy returns aren't pure StochRSI alpha — they're StochRSI signal × asset volatility. Apply the same recipe to a calmer asset (SPY) and you get a smaller number, not because the edge is weaker but because the underlying daily range is smaller.

These two readings are nearly the same statement and consistent with cross-cutting learning #8 ("asset-specific beta layers change drawdown, not the edge"). The strategy isn't asset-class-specific — it's a 15m mean-reversion edge that scales with asset volatility, modulo the bond exception (TLT — rates dynamics overwhelm microstructure).

**What this resolves:**
- Cross-cutting learning #10 updated: boundary is on **driver class** (rates-driven assets fail), not **asset class** (equities vs commodities). Bonds out, everything else liquid+volatile-enough is in.
- The held-out 12/12 result is no longer ambiguous between "real edge" and "test-design failure" — combined with broad indices also passing, the through-line is consistent: the strategy works on liquid ETFs whose 15m bar moves contain mean-reversion structure. The artefact risks (long-bias, survivorship, recipe over-robustness from research-log Apr 28 entry) remain valid concerns and aren't dismissed by this result, but the simpler explanation — broad microstructure edge — now fits the data.

**What this does NOT resolve:**
- Whether SPY/QQQ/IWM/DIA returns are high enough to clear a quality bar for deployment. ~3.6–9.4%/yr is below the metals/energy lineup. Needs Sharpe to compare on a DD-adjusted basis (Sharpe computation is the open code task).
- Long-bias / regime artefact (the 2020–2026 bull-market window concern from the held-out entry) is still untested. Need older intraday data or a synthetic stress test.
- Walk-forward for SPY/QQQ/IWM/DIA. Single-run pass is necessary not sufficient — same gate as OIH/XBI/XOP had to clear. Lower priority than getting the validated 8 to real money, but worth queueing.

**Next implications for the project:**
- The strategy library's universe just expanded again, but with diminishing edge per added asset. Adding SPY to the lineup at +22%/5.7yr isn't competitive vs already-validated +144% SLV, except for diversification arguments. The right question is no longer "does it work on X?" but "where does it work *best*, and how do we size correlated bets?"
- Critical path is unchanged: correlation-aware sizing for the existing 7-bot lineup is still the gate to real money. Adding more assets without correlation sizing makes the tail risk worse, not better.

---

## Sharpe Verification — Apr 28 2026

**Tried:** Extended `backend/engine/backtester.py` to compute annualised Sharpe from the bar-level equity history (resampled to daily, std/mean × √252). Added a print line in `backend/runner.py`. Re-ran all 8 validated assets full-strategy + 4 metals long-only + 4 boundary indices on the extended 2020 → Apr 27 2026 window. Same recipe across all runs (`dynamic_adx:false`).

**Result:**

| | Asset | Return | DD | Trades | WR | Sharpe |
|---|---|---|---|---|---|---|
| Full | GLD | 45.13% | 1.22% | 504 | 43% | **2.48** ✓ |
| Full | SLV | 131.04% | 2.00% | 522 | 47% | **2.46** ✓ |
| Full | GDX | 133.27% | 2.01% | 582 | 46% | **2.46** ✓ |
| Full | OIH | 146.06% | 2.96% | 586 | 42% | **2.33** ✓ |
| Full | XLE | 85.70% | 3.27% | 565 | 45% | **2.30** ✓ |
| Full | XBI | 84.87% | 2.44% | 601 | 43% | **2.18** ✓ |
| Full | XOP | 91.65% | 3.29% | 627 | 42% | 1.98 (at bar) |
| Full | IAU | 39.34% | 1.32% | 493 | 40% | 1.95 (under) |
| LO | GLD | 34.98% | 0.51% | 336 | 47% | **2.57** ✓ |
| LO | SLV | 90.77% | 1.14% | 326 | 49% | **2.47** ✓ |
| LO | GDX | 79.87% | 1.21% | 375 | 47% | 1.89 |
| LO | IAU | 29.41% | 1.06% | 306 | 39% | 1.86 |
| Idx | IWM | 57.42% | 1.43% | 655 | 46% | **2.30** ✓ |
| Idx | DIA | 27.32% | 2.56% | 639 | 40% | 1.83 |
| Idx | QQQ | 27.17% | 2.19% | 733 | 40% | 1.45 |
| Idx | SPY | 21.94% | 2.02% | 655 | 40% | 1.36 |

**What this resolves:**
- The 2.0 quality bar is now measurable. **6 of 8 validated lineup clear cleanly** (GLD, SLV, GDX, OIH, XLE, XBI). XOP at 1.98 is at the bar; IAU at 1.95 falls just under and is the weakest of the metals on a DD-adjusted basis.
- Old card claims for GLD (2.47), SLV (2.41), and IAU (1.97) were close to the verified values. **GDX claim 2.58 was too high** (verified 2.46). **XLE claim 2.06 was too low** (verified 2.30).
- **GLD and SLV long-only Sharpes exceed full-strategy** (2.57 vs 2.48; 2.47 vs 2.46). Shorts hurt DD-adjusted return on these two — they reduce equity volatility less than they reduce mean return. GDX and IAU show the opposite pattern (long-only Sharpe drops), suggesting shorts contribute meaningfully on the higher-beta metals.
- **IWM is the only broad index that clears the bar** (2.30 ✓). SPY (1.36), QQQ (1.45), DIA (1.83) are profitable but DD-adjusted profile is below the metals/energy lineup. Returns scale with underlying volatility per learning #8 — calmer assets produce smaller Sharpes at similar trade counts.

**What this does NOT resolve:**
- Sharpe is computed from a daily-resampled equity curve, not on per-trade returns. Both are standard, but they differ — daily resampling treats overnight gaps as bar moves; per-trade Sharpe weights by trade count. The 2.0 bar across the project's history was applied without specifying which — keep this as the canonical method going forward.
- WF Sharpe is not yet computed per window. Full-period Sharpe ≥ 2.0 doesn't guarantee per-window Sharpe ≥ 2.0; some sub-periods will be lower. Worth running once the WF runner is touched again.
- IAU at 1.95 raises a small question about whether it should remain in the validated lineup at the same status as the others. Currently kept because (a) live forward test is running, (b) the gap to 2.0 is within Sharpe noise on a 6-year window, (c) WF is 4/4. A judgement call rather than a hard rejection.

**Implication for next steps:**
- Quality bar is now applicable to all future candidate decisions. The held-out 12 + boundary 4 = 16 single-run passers can now be ranked DD-adjusted before committing WF compute to any of them.
- For the 7-bot live lineup: nothing changes — they're already deployed. But knowing the Sharpe distribution makes the correlation-aware-sizing build more concrete: when GLD/IAU/SLV all enter together, the IAU leg is the lowest-quality contributor by DD-adjusted return.

---

## Edge Question — Test 1: Buy-and-Hold Comparison (Apr 28 2026)

**Tried:** Built `backend/analysis/buy_and_hold_comparison.py` to compute B&H return, max drawdown, and annualised Sharpe (daily-resampled close × √252) for all 12 tested assets over 2020-07-27 → 2026-04-27 — same window and Sharpe convention as the strategy backtests. Compared directly to verified strategy figures.

**Result:**

| Symbol | B&H Return | B&H DD | B&H Sharpe | Strat Return | Strat DD | Strat Sharpe | Δ Sharpe | DD ratio |
|---|---|---|---|---|---|---|---|---|
| GLD | +160.52% | 22.09% | 1.08 | +45.13% | 1.22% | 2.48 | **+1.40** | 18.1× |
| SLV | +234.11% | 39.29% | 0.78 | +131.04% | 2.00% | 2.46 | **+1.68** | 19.6× |
| GDX | +131.20% | 50.79% | 0.60 | +133.27% | 2.01% | 2.46 | **+1.86** | 25.3× |
| IAU | +424.16%* | 21.03% | 0.80 | +39.34% | 1.32% | 1.95 | +1.15 | 15.9× |
| XLE | +66.68% | 55.31% | 0.47 | +85.70% | 3.27% | 2.30 | **+1.83** | 16.9× |
| OIH | +229.72% | 45.66% | 0.72 | +146.06% | 2.96% | 2.33 | **+1.61** | 15.4× |
| XBI | +15.35% | 64.04% | 0.24 | +84.87% | 2.44% | 2.18 | **+1.94** | 26.2× |
| XOP | +227.34% | 39.70% | 0.75 | +91.65% | 3.29% | 1.98 | +1.23 | 12.1× |
| SPY | +121.16% | 25.22% | 0.90 | +21.94% | 2.02% | 1.36 | +0.46 | 12.5× |
| QQQ | +155.18% | 35.54% | 0.83 | +27.17% | 2.19% | 1.45 | +0.62 | 16.2× |
| IWM | +87.64% | 33.17% | 0.60 | +57.42% | 1.43% | 2.30 | **+1.70** | 23.2× |
| DIA | +84.95% | 21.88% | 0.80 | +27.32% | 2.56% | 1.83 | +1.03 | 8.5× |

\*IAU +424% is anomalous (GLD is +161% on the same metal). Likely the daily-bar split-adjustment inconsistency previously noted in `research-roadmap.md`. Sharpe is still consistent with the rest of the metals.

**Headlines:**
- **Strategy beats B&H on every single asset.** Δ Sharpe is positive everywhere, range +0.46 (SPY) to +1.94 (XBI), median ~+1.4.
- **Every B&H Sharpe is below the 2.0 quality bar** (range 0.24 to 1.08). Passive holding doesn't clear the bar we hold the strategy to.
- **DD protection is 8.5×–26.2×** across the board. Even the worst case (DIA, 8.5×) is meaningful.
- **Strategy beats B&H on raw return for 3 assets** (GDX +133% vs +131%, XLE +86% vs +67%, XBI +85% vs +15%) — these aren't smoothing wrappers, they're outperforming on the absolute number too.
- **Smallest gaps are on broad indices** (SPY +0.46, QQQ +0.62, DIA +1.03) — consistent with our learning #8 "edge scales with volatility." Calmer assets show less framework edge over B&H.
- **XBI is the most striking case:** B&H Sharpe 0.24, strategy Sharpe 2.18. The framework converts a basically-uninvestable asset (biotech is high-vol with no clear long drift in this window — only +15% over 6 years) into a Sharpe-2 contributor.

**What this resolves:** Test 1 cleanly passes the decision rule. The framework adds genuine risk-adjusted value over passive holding on every asset in this regime. **Story 1 (real risk-adjusted alpha) survives; Story 2 (smoothing wrapper) is partially refuted.** "Partially" because:
- The result holds on Sharpe, where the framework dominates.
- The result holds on raw return *for some assets but not others* — on SPY/QQQ/DIA/SLV/IAU/OIH/XOP, B&H made meaningfully more money. The framework trades absolute return for DD-adjusted return. That's a real edge but it's an edge of a specific kind: smoothing + selective participation, not "we make more money than buying and holding."
- The result is still within a 2020–2026 bull market. Test 3 (synthetic inversion) is what tests whether the edge survives outside this regime.

**Implication for next tests:** Proceed to Test 2 (fully-random ablation). The framework adds value over B&H — we now want to know how much of that value remains when we strip out the K-cross exit too, isolating the trail+stop+sizing+ADX+min-hold core.

**Implication for project framing:** When describing the strategy, the honest claim is "framework converts asset volatility into risk-adjusted return at very low DD" — not "we predict mean-reversion." The Sharpe gap over B&H is the metric to lead with, not the absolute return.

---

## Edge Question — Test 2: Fully-Random Ablation (Apr 28 2026)

**Tried:** Added `random_exit_prob` parameter to `StochRSIMeanReversionStrategy` mirroring the existing `random_entry_prob`. With both set, the strategy uses the same RNG to fire entries (Bernoulli per flat bar, p=0.15) and exits (Bernoulli per in-position bar after min-hold, p=0.05 — calibrated to produce trade counts comparable to validated). Stop loss + trailing stop unchanged. ADX filter, skip-Mon, sizing, 25% notional cap, 10-bar min-hold all unchanged. This isolates the framework's contribution with **zero signal information** anywhere in the strategy.

**Calibration (GLD):**
- ep=0.03 → 546 trades, Sharpe 2.81
- ep=0.05 → 553 trades, Sharpe 2.32 *(closest to validated 504; chosen for the batch)*
- ep=0.10 → 573 trades, Sharpe 2.02

Sharpe is robust across the exit-rate range. Framework Sharpe doesn't depend on calibration choice within reason.

**Result (random_entry_prob=0.15, random_exit_prob=0.05, seed=42):**

| Asset | Validated Sharpe | Random-Entry Only | **Fully-Random** | Δ vs Validated |
|---|---|---|---|---|
| GLD | 2.48 | 2.46 | **2.32** | -0.16 |
| SLV | 2.46 | 2.04 | **2.64** | **+0.18** |
| GDX | 2.46 | 2.05 | **2.57** | **+0.11** |
| QQQ | 1.45 | 1.99 | **2.28** | **+0.83** |

**Headlines:**
- **Fully-random matches or exceeds validated on 3 of 4 assets.** Only GLD shows a modest deficit (-0.16); SLV, GDX, and QQQ are all higher than validated.
- **Every fully-random Sharpe is ≥ 2.0.** The framework alone — with no signal information whatsoever — clears the quality bar on every asset tested.
- **The StochRSI entry + K-cross exit signals are at best neutral and at worst slightly net-negative** versus a fully-random control. Across these four assets the average Sharpe is 2.45 fully-random vs 2.21 validated — random is **higher on average**.
- This goes further than the Apr 28 random-entry-only test. That test still kept K-cross exits (which use real K values). This one removes the last signal-dependent piece. The fact that Sharpe goes *up* on most assets with the K-exit removed is the strong claim here: the K-cross exit signal isn't carrying useful information either, and may actually be triggering exits that hurt more than they help.

**What this resolves:**
- **The framework alone IS the edge.** ATR stop, trailing stop after 10 bars, ADX-ranging filter, 2% fixed-risk sizing, 25% notional cap, and 10-bar min-hold together produce Sharpe ≥ 2.0 on every tested asset, with no signal information of any kind. This is a clean, falsifiable, and now empirically-confirmed claim.
- **The StochRSI signal is decorative or worse.** On 3 of 4 assets, removing it improves Sharpe. The "edge" we documented across the project as "StochRSI mean-reversion at 15m" was a misattribution — what we measured was a *position-management framework* that the signal happened to be sitting on top of.
- **Cross-cutting learning #11 (added Apr 28) is now upgraded from "framework is doing most of the work" to "framework is doing all of the work, signal is at best neutral."**

**What this does NOT resolve:**
- The bull-market regime question. Framework alone produces Sharpe 2.0+ on a 2020–2026 bull-market window — but does it also do that outside this regime? Test 3 (synthetic price inversion) is the next test.
- Why the framework works. The fact that it produces Sharpe 2.0+ from random entries + random exits is striking. Plausible mechanism: the trail-after-10-bars + 25% cap creates positive expectancy by *truncating losses sharply via the fixed ATR stop while letting winners run via the trail*. That's a structural asymmetry that doesn't need any signal — random entries on a slightly-trending asset, with that asymmetry, will produce positive Sharpe. Granular ablations (no-trail, no-ADX, no-min-hold individually) would attribute exactly which framework component is load-bearing — but for the deployment decision the bigger question is settled.
- Why GLD shows -0.16 specifically. GLD might be the one asset where the StochRSI signal contributes a small genuine edge — or it might be RNG noise. Worth a multi-seed sweep on GLD specifically before claiming "signal helps GLD."

**Implication for live bots:** The 7 paper bots are running a strategy where the signal contributes nothing on average. They could be replaced with random-entry/random-exit bots and likely produce equal or better Sharpe. **This is not a reason to change anything immediately** — the signal isn't *hurting* either, and the live bots are validating execution mechanics regardless of edge attribution. But for any future deployment decision, "we use StochRSI mean-reversion" should be replaced with "we use a position-management framework with the validated parameters" as the honest description.

**Implication for next research:** Test 3 (synthetic inversion) becomes more important, not less. If the framework alone produces Sharpe 2.0+ from random signals, the regime-dependence question is the only remaining edge-attribution question. If the framework also produces Sharpe 2.0+ on inverted prices, then we know the framework is capturing volatility, not direction. If it doesn't, then the framework has real directional edge that depends on positive drift.

---

## Edge Question — Test 3: Synthetic Price Inversion (Apr 28 2026)

**Tried:** Added `--invert-prices` flag to `backend/runner.py`. The flag reflects OHLC around the close-mean pivot (`new_x = 2 * pivot - x`) and swaps high ↔ low to keep high ≥ low. ATR, volatility, and bar shape are preserved; direction is flipped. Ran the validated recipe on inverted GLD (positive control — highest validated Sharpe) and inverted SPY (boundary asset — low Sharpe, broad index, suspected direction-agnostic).

Sanity check: first 5 bars of GLD inverted by hand — `high ≥ low` preserved, original "below the mean" prices become "above the mean" and vice versa. Math verified.

**Result:**

| Asset | Original Return | Original DD | Original Sharpe | Inverted Return | Inverted DD | Inverted Sharpe | Δ Sharpe |
|---|---|---|---|---|---|---|---|
| GLD | +45.13% | 1.22% | **2.48** | +85.54% | 6.84% | **0.85** | **-1.63** |
| SPY | +21.94% | 2.02% | **1.36** | +25.45% | 2.29% | **1.53** | +0.17 |

**Headlines:**
- **GLD has real directional edge.** Inverted Sharpe collapses from 2.48 → 0.85. Inverted return is actually HIGHER (+85.54% vs +45.13%) but DD is **5.6× worse** (6.84% vs 1.22%). The framework still produces positive expectancy on inverted GLD, but the favourable risk-adjusted profile depends on the actual direction of price movement.
- **SPY is essentially direction-agnostic.** Inverted Sharpe 1.53 vs original 1.36 — within Sharpe noise; if anything slightly better. The framework's behaviour on SPY doesn't depend on the rising-tide tendency of the actual data.
- **The two assets are telling different stories.** The metals edge depends on regime. The broad-index edge does not.

**Mechanism — why GLD shows direction-dependence and SPY doesn't:**
- GLD's 2020–2026 window is a strong, sustained bull market with relatively low volatility. The framework's trail-after-10-bars rule lets winners run; in a bull regime that asymmetry is amplified because winners genuinely persist. Flip the direction and the long-side trail is now riding *against* the underlying drift; positions that would have ratcheted up now whipsaw, hitting stops with worse fills. The 5.6× DD increase is exactly this: the framework is designed for "let winners run" and on inverted gold the runs go the wrong way.
- SPY's 15m microstructure is different — even within a bull market, intraday SPY has more two-sided action, more mean-reversion within trend, and proportionally lower drift per bar. The framework's edge here is largely volatility capture (the ATR stop and trail are calibrated to bar-volatility, which doesn't care which direction) — flipping the direction doesn't change the volatility structure, so Sharpe holds.

**Reconciliation with the GLD card's Feb 27 daily-bar bear-market test:**
- Daily-bar GLD 2012–2015 (gold bear): Strategy +6.0% / 1.41% DD / Sharpe 0.50. B&H -34.9% over the same window.
- Daily-bar GLD 2007–2011 (gold bull): Strategy +21.7% / 4.15% DD / Sharpe 1.06.
- Pattern: bull-regime Sharpe ~2× bear-regime Sharpe. Today's inversion test (which is also a "bear-like" condition) shows similar magnitude collapse (2.48 → 0.85, ~3× drop). **Two independent tests now point to "metals framework Sharpe is regime-dependent."**

**What this resolves:**
- **The metals deployment is implicitly a long-volatility-on-precious-metals bet.** The framework has real edge but that edge depends on continued metals strength. If gold enters a sustained bear (like 2011–2015), live performance will be materially worse than the 2.46 backtest Sharpe suggests.
- **Broad-index deployment (IWM at Sharpe 2.30) is more regime-robust.** The framework's edge on equity indices appears to be genuine volatility capture, not direction-dependent.
- **The framework is universal in producing Sharpe ≥ 2 (Test 2), but the magnitude of that Sharpe varies with regime on directional assets.** The two facts aren't contradictory: framework alone is the edge; on directional assets the magnitude of that edge is regime-amplified.

**What this does NOT resolve:**
- Whether OIH/XBI/XOP/XLE behave like GLD (regime-dependent) or like SPY (regime-agnostic). Likely most are GLD-like — they're sector ETFs in trending sectors during the test window — but per-asset confirmation needs running.
- The exact Sharpe one should expect in a different regime. Inversion is a proxy, not a direct measurement of bear-market performance. The Feb 27 daily-bar bear test gives one data point (~½ the bull Sharpe); this inversion gives another (~⅓ the bull Sharpe). True bear-regime intraday performance is between these, modulo regime-specific structure that neither test captures.
- Whether a hedge or regime-detector could correct this. If we knew when we were in a metals bear, we could downsize or skip. But we don't have a real-time regime classifier validated to that purpose; the existing regime card is descriptive, not predictive.

**Implication for live bots:**
- Don't size the metals bots assuming Sharpe 2.46. Internal expected Sharpe for sizing/risk should be closer to 1.0–1.5 to account for regime variation. The current 2% risk per trade with 25% notional cap is conservative enough that this isn't an immediate issue, but **any push to scale up sizing for the metals bots needs to budget regime-dependence into the math.**
- IWM is now a more attractive deployment candidate than its raw Sharpe suggests. Sharpe 2.30 with regime-agnostic behaviour is more robust than Sharpe 2.48 with regime-dependence.
- The bond rejection (TLT) earlier this week makes more sense: TLT is rates-driven AND directionally stable in the test window. The framework's edge requires either real volatility or directional drift to capture; TLT had neither in a way the framework could exploit.

---

## Edge Question — Synthesis (Apr 28 2026)

**Three tests, three resolutions:**

| Test | Question | Result |
|---|---|---|
| 1 — Buy-and-Hold | Does the strategy add risk-adjusted value over passive holding? | **YES on all 12 assets.** Δ Sharpe +0.46 to +1.94, DD protection 8.5×–26.2×. |
| 2 — Fully-Random Ablation | Is the StochRSI signal the source of edge, or is it the framework? | **Framework, not signal.** Random entries + random exits with the same framework match or beat validated Sharpe on 3 of 4 assets. |
| 3 — Synthetic Inversion | Is the framework direction-agnostic, or does it depend on the bull-market regime? | **Asset-dependent.** GLD direction-dependent (Sharpe 2.48 → 0.85 inverted). SPY direction-agnostic (1.36 → 1.53). |

**The honest, post-resolution model of what we built:**

The system is a **position-management framework** consisting of: ATR stop loss, trailing stop ratcheting after 10 bars, ADX-ranging entry filter, 2% fixed-risk position sizing, 25% notional cap, skip-Mon, 10-bar minimum hold. This framework, applied to any reasonably liquid intraday-volatile asset, converts asset volatility into risk-adjusted return more efficiently than passive holding (Test 1). It does this without needing any signal — random entries and random exits produce comparable Sharpe (Test 2). The "StochRSI mean-reversion" entry and exit logic that we built around the framework is at best decorative; on average across 4 assets it slightly hurts.

The framework's edge is regime-dependent on directional assets and regime-agnostic on lower-drift assets (Test 3). On metals like GLD, the high Sharpe (2.48) depends meaningfully on the actual direction of price movement — invert the direction and Sharpe collapses to 0.85. On SPY, Sharpe is unchanged by inversion. The implication: the metals deployment is implicitly a directional bet on continued metals strength; the broad-index deployment (IWM) is more regime-robust.

**What this means for the project:**

1. **The 7 paper bots are real edge, but a smaller and more specific edge than we documented.** They produce Sharpe 2.0+ on backtest *because the framework works*, not because the StochRSI signal predicts mean-reversion. They depend on continued metals strength to maintain that backtest Sharpe in live conditions.

2. **The "validated edges across 8 assets" framing is overstated.** What's validated is one framework, applied to 8 assets, with 6 of them clearing Sharpe 2.0 in a 2020–2026 bull market. The framework is the edge; the per-asset Sharpe variations reflect each asset's volatility profile and regime.

3. **The strategy library is smaller than we thought.** "StochRSI Enhanced" isn't a strategy in the sense we documented — it's `Framework v1` plus a misattributed signal. The actual research surface is: alternative framework parameters, regime-aware sizing for the framework, additional framework variants (different stop / trail / filter logic).

4. **Real-money deployment posture:**
   - **Conservative path:** keep the current paper bots running, size for Sharpe 1.0–1.5 expected (not 2.46), prioritise IWM over more metals on the next deployment because it's regime-robust. Continue the Critical Path technical items (correlation-aware sizing, ATR sizing, late-session guard).
   - **Aggressive path:** increase sizing now based on backtest Sharpe. **Not recommended** — the inversion result shows backtest Sharpe overstates expected live Sharpe in a regime change.

5. **Future research questions worth asking:**
   - Which framework component is load-bearing? Granular ablations (no-trail / no-ADX / no-min-hold) would attribute exactly. Now diagnostic, not gating, because the framework attribution itself is settled.
   - Can a real-time regime detector + dynamic sizing convert Test 3's regime-dependence into regime-aware deployment? Existing regime work is descriptive; a predictive component would be new.
   - Is there an actual signal that adds value over the framework? The StochRSI doesn't. Other indicators or composable signals might. Lower priority than understanding the framework, but the question is now well-posed.
   - Does the framework break or hold on assets with neither volatility nor drift? TLT failed; that was driver-class (rates). What other assets have similar profiles?

**Status of the cross-cutting learnings as of Apr 28 evening:**
- #10 (mean-reversion is general microstructure) — **revised: framework is general, signal is irrelevant.**
- #11 (framework is doing most of the work) — **upgraded: framework is doing all of the work, signal is at best neutral, and framework has direction-dependence on metals.**

The Apr 28 finding chain (held-out 12/12 → boundary 4/4 → Sharpe verification → random-entry control → fully-random ablation → buy-and-hold → inversion) was a single multi-day arc of empirically reframing the project. The framework is real. The signal isn't. The edge depends on regime for some assets and not others. That's the model now.

---

## Random-Entry Control — Apr 28 2026

**Tried:** After the boundary verification + Sharpe sweep made the strategy look suspiciously general ("works on almost everything"), ran a discriminator: replace the StochRSI entry signal with random Bernoulli draws (calibrated to match validated trade frequency, p=0.15 per flat bar, seed=42, 50/50 long/short). Keep all other logic identical — ADX filter, skip-Mon, 2% risk sizing, 25% notional cap, ATR stop, trailing stop after 10 bars, K-cross exit, min-hold. Added `random_entry_prob` param to `StochRSIMeanReversionStrategy`. Compared random-entry Sharpe to validated Sharpe on 6 representative assets.

**Result:**

| Asset | Validated Sharpe | Random Sharpe | Δ | Validated Return | Random Return |
|---|---|---|---|---|---|
| GLD | 2.48 | **2.46** | -0.02 | 45.13% | 45.31% |
| SLV | 2.46 | 2.04 | -0.42 | 131.04% | 96.55% |
| GDX | 2.46 | 2.05 | -0.41 | 133.27% | 109.22% |
| IWM | 2.30 | 1.65 | -0.65 | 57.42% | 42.35% |
| SPY | 1.36 | 1.13 | -0.23 | 21.94% | 18.55% |
| QQQ | 1.45 | **1.99** | **+0.54** | 27.17% | 49.39% |

GLD swept across p=0.08/0.15/0.25/0.40 (Sharpe 2.02 / 2.46 / 2.43 / 2.47) — the random-entry Sharpe is robust to the probability choice, not a calibration artefact.

**What this resolves (negative finding):**
- The StochRSI mean-reversion entry signal is **not the primary source of edge**. Across 6 assets the entry contributes between -0.65 and +0.54 Sharpe over a random-entry baseline. On GLD it contributes essentially zero. **On QQQ it actively hurts** — random entries Sharpe 1.99 vs validated 1.45. The "edge" we've been documenting is mostly the position-management framework: ATR stop, trailing stop after 10 bars, ADX-ranging filter, skip-Mon, fixed-risk sizing, K-cross exit, 10-bar min-hold.
- The mental model "the strategy works because StochRSI extremes mean-revert" is largely wrong. The honest model is closer to: "in ranging regimes (ADX < 20), liquid ETFs at 15m have enough microstructure for a 2.0-ATR trailing stop with 2% risk per trade and a 10-bar min-hold to capture positive expectancy from any reasonably timed entry, and a K-cross provides a noise-tolerant exit." The entry signal at most tilts that small.
- This explains the held-out test result. If the entry signal isn't doing the work, then "everything passes" was inevitable as long as the asset has enough volatility for the trail to capture profits and the ADX filter to gate trending periods. The recipe is generic *because the signal isn't load-bearing*, not because we found a universal mean-reversion edge.

**What this does NOT resolve:**
- **Exits are still informed.** K-cross exit uses real K values; only entries are randomised. A fully clean control would randomise both. But stop-loss and trailing stop are pure-price and account for the majority of exits, so the result is still informative.
- **Long-bias / regime artefact remains open.** Random entries with positive expectancy in a 6-year bull market is exactly the pattern we'd expect if we're capturing equity beta. To distinguish from real microstructure edge we still need either pre-2020 intraday data or a synthetic stress test.
- **What in the framework is doing the work** is now the open question. Candidates ranked by likelihood: (1) trailing stop after N bars in profit — captures extended moves; (2) ADX filter — only trades when range-bound, avoiding trend continuation losses; (3) min-hold + K-cross exit — protects against premature signal exits; (4) 25% notional cap — bounds tail risk. Need ablations to attribute.
- **Asset-specific signal quality.** SLV/GDX/IWM show real (~0.4–0.65) entry contribution; GLD shows zero; QQQ shows negative. The signal isn't worthless everywhere — it's just much smaller than we thought, and it's negative on at least one validated-class asset.

**Implication for live bots:**
- The 7 paper bots aren't necessarily wrong — they're producing real returns from a real framework. But **what we thought was driving the returns isn't what's driving them.** The implications:
  - Future "does the strategy work on X?" tests are nearly meaningless until we understand which framework component is load-bearing. We'll keep finding "yes" because the framework keeps working.
  - Walk-forward tests so far validate the framework, not the signal. Same conclusion: WF passes don't tell us what's actually generalising.
  - Correlation-aware sizing (real-money critical path) is unaffected — that's a position-management concern, not an entry-signal concern.
  - The Apr 4 "stop-check fix" being load-bearing makes more sense now: the trail is doing most of the work, so a bug in stop ordering would have outsized impact.

**Implication for research direction:**
- The next concrete experiments are framework ablations, not more asset tests:
  1. **No trail** — fixed stop only. If Sharpe collapses, the trail is the edge.
  2. **No ADX filter** — accept all regimes. If Sharpe collapses, the ranging-regime constraint is the edge.
  3. **No min-hold** — exit immediately on K-cross. If Sharpe survives, min-hold isn't load-bearing.
  4. **No K-cross exit (stop-only)** — pure price-based exit. Tests whether the K signal carries any exit information.
  5. **Fully random (random entries + random exits + stop only)** — establishes the baseline for the trail+stop+sizing framework alone.
- Order: 5 → 1 → 2 → 4 → 3. Each is one parameter change, ~3 minutes per asset.

**Honest summary:** the held-out 12/12 + boundary 4/4 + Sharpe verification looked like a strategy library win. Combined with this random-entry control, the more accurate read is: **we have a strong position-management framework that we built around what we thought was the signal, and the framework is what's actually working.** That's still a project asset — the framework is real, deployable, and live in 7 paper bots — but it requires recasting how we describe and extend the strategy.

---

## Cross-Cutting Learnings

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

**6. Current sizing is equal capital allocation, not risk-based.**
The bot splits account equity equally across symbols (~25% per position) and deploys the full amount. Risk per trade is not fixed — it varies with ATR on the day (stop distance × position size). A more rigorous approach — ATR-based position sizing — would work backwards from a fixed max risk (e.g. 1% of account) and calculate share count from stop distance. This keeps risk per trade constant regardless of volatility. Not currently implemented — it's a post-calibration enhancement. Also relevant: at $99k paper balance, whole-share sizing is essentially as precise as fractional (1 GLD share = 0.44% of account). The case for fractional shares is at real-money starting capital (€100) where whole shares are impractical.

**7. Correlation is a sizing problem, not a signal problem.**
GLD/IAU/SLV have the same signal because they track the same underlying. Running all three simultaneously isn't three independent bets — it's one bet with 3x size. Correlation-aware position sizing (reduce per-trade risk when 3+ correlated bots in simultaneously) is required before real money. But before implementing sizing logic, run the portfolio correlation analysis (see Open Research Agenda) — the data may show the compounding loss risk is less severe than the theoretical maximum, or that GDX's structural divergence provides natural diversification.

**8. Asset-specific beta layers change drawdown, not the edge.**
GDX = gold beta + mining equity beta. XLE = energy beta. Higher volatility assets produce higher DD with the same Sharpe — not a bug, a property of the underlying. Don't retune params to lower DD on volatile assets; accept the DD or size smaller.

**9. Forward test param design involves a trade-off between trade volume and trail observation.**
Aggressive params (tight OB/OS, short hold, tight trail) generate high trade volume — useful for verifying execution mechanics quickly. But a trail of 0.5 ATR after 1 bar fires on noise constantly, so you never observe the trail doing what the validated strategy depends on. Three weeks of aggressive params confirmed all infrastructure and exit mechanics, but produced almost no meaningful TS exits — the two exceptions (GDX +3.267, GLD +3.706) only occurred because late-session entries forced overnight holds that accidentally mimicked validated params behaviour. For future strategy forward tests: use aggressive params only for the mechanics verification phase, then switch to validated params as soon as infrastructure is confirmed. Design the two phases explicitly rather than running aggressive params for the entire forward test window.

**11. The position-management framework is doing most of the work, not the StochRSI signal (Apr 28).**
Random-entry control (Bernoulli draws calibrated to validated trade frequency, all other logic identical) produces Sharpes within 0.05–0.65 of validated across 6 assets, and *beats* validated on QQQ (+0.54). On GLD random ≈ validated (Sharpe 2.46 vs 2.48). The edge lives in the framework: 2.0-ATR stop, trailing stop after 10 bars, ADX-ranging filter, skip-Mon, 2% fixed-risk sizing, 25% notional cap, K-cross exit, 10-bar min-hold. The StochRSI entry signal contributes a small asset-dependent tilt — not the dominant effect we'd assumed. This re-frames learning #10: the strategy generalises because the framework generalises, not because StochRSI mean-reversion is universal. Implication: future "does it work on X?" tests are uninformative until ablations identify which framework component is load-bearing. (Caveat: K-cross exit still uses real K — exits aren't fully randomised in this control. Pure-price stop/trail account for majority of exits, so the result is informative but not airtight.)

**10. Mean-reversion at 15m is a general microstructure pattern; boundary is on driver class, not asset class.**
Works on precious metals (GLD/IAU/SLV/GDX), energy (XLE/OIH/XOP), biotech (XBI), tech (XLK/QQQ), banks (KRE/XLF), industrials (XLI/DIA), healthcare (XLV), defense (ITA), dollar (UUP), Brazil EM (EWZ), bitcoin (GBTC), growth (ARKK), volatility (VXX), 3× leveraged Nasdaq (TQQQ), and broad indices (SPY/QQQ/IWM/DIA — verified Apr 28 with validated recipe; previous "fails on broad indices" finding was old params + broken engine). The earlier "Commodities yes, Broad indices no" framing was wrong — it was an asset-class boundary that turned out to be illusory. **The real boundary is on driver class:** assets where intraday price action is dominated by rates/curve dynamics rather than microstructure (TLT, bonds generally) fail. Returns scale with underlying volatility — calmer assets like SPY produce smaller returns at similar DD-adjusted profiles, consistent with learning #8 (beta scales DD, not edge). For deployment decisions the question shifts from "does it work on X?" to "where is the edge highest per unit of correlation already in the portfolio?"

---

## Open Research Agenda

Sequenced by dependency and priority. Critical path: **1 → 2 → 3 → 6**. Items 4 and 5 run in parallel during the validated params forward test window. Items 7–10 are expansion after real money is running.

---

### Critical path — required before real money

1. **Calibration — run Mon/Tue Apr 14–15** — don't wait until Apr 20. Gate: overnight GLD/SLV/GDX positions close first. Run backtest comparison over clean window (~70–75 trades, sufficient for execution layer validation). See calibration-notes.md for commands and layered framework.

2. **Whole-share sizing + short broker code** — implement immediately after calibration passes. Position sizing: `floor(risk_budget / stop_distance) = whole shares`. Broker code: audit `live_broker.py` for direction-aware stop placement, trail ratcheting, and exit order type on the short side. Short signal code already exists and is blocked — unblock once sizing is in place. No intermediate parameter phase needed to verify short mechanics.

3. **Switch to validated params with shorts enabled** — OB 80/OS 15, hold 10, trail 2.0 ATR after 10 bars, skip Monday. Deploy immediately after item 2. Starts the second clean window (confirms trail component) and the short verification window simultaneously. Expected ~3–4 short trades/week across 4 symbols — 2 weeks sufficient to confirm short mechanics. Short verification is simpler than long mechanics verification at launch (4 things to verify vs 7+): short fills correctly, stop above entry, trail ratchets downward, exit closes cleanly.

4. **Rerun all stale backtests (parallel with forward test)** — long-only and full Sharpe for all 4 symbols, year-by-year tables, flagged as pre-Apr-4-fix estimates in strategy domain files. Run with corrected engine post-calibration. Informs real money sizing and symbol prioritisation.

5. **Portfolio correlation analysis (parallel with forward test)** — run all 4 symbols simultaneously on validated params, 5-year backtest, shared timeline. Tally joint outcomes: all win / all lose / mixed, split by year. Purpose: determine empirically whether 6% theoretical worst-case exposure is a real risk, and whether GDX's structural divergence provides natural diversification. Do before implementing sizing logic.

6. **Correlation-aware sizing + late-session entry guard** — implement once correlation analysis gives the empirical picture. Late-session guard (block/halve size within ~30 min of close) is the simpler piece. Sizing mechanism decided after analysis. Both are pre-real-money gates.

7. **First real money deployment** — gate: calibration passed + trail confirmed + short mechanics confirmed + sizing implemented. Start with one symbol, minimal capital. Scale to all four once running cleanly.

---

### Expansion — after real money running

7. **XLE as 5th bot** — validated, ready to deploy. Lower priority than getting core 4 bots running at real money. Deploy after sizing logic is confirmed on existing bots.

8. **Time-of-day filter** — market open (13:30–14:15 UTC) is consistently the most active and most profitable window. Test as explicit param: does restricting entries to the open window improve Sharpe or reduce it? Post-calibration backtest experiment.

9. **Overnight / multi-day hold variant** — GDX +3.267 multi-day trade outperformed 49 others combined. Validated params partially capture this. Worth designing an explicit variant with tighter entry conditions, wider trail, longer min_hold — targeting multi-day momentum continuation rather than intraday mean reversion.

10. **EventSurprise paper test** — CPI-miss signal (86% WR, ~3 trades/year) needs live verification. Low frequency but clean signal. Run as a 5th or 6th bot alongside StochRSI after core strategy is confirmed at real money.

11. **Sector ETF expansion** — apply StochRSI 15m to XLF, XLK, XLV, TLT. Same params, no retuning. Filter: Sharpe ≥ 2.0, WF 4/4, multi-asset confirmation.

12. **Regime classification + enhancements** — **BUILT (Apr 10).** Classifier implemented (`backend/indicators/regime.py`, `scripts/analyse_regimes.py`). Findings, sizing framework, downstream enhancement roadmap, and regime backtest plan all documented in `.claude/strategies/regime-analysis.md`. Next step post-calibration: build the shared-timeline portfolio runner (needed for both correlation analysis and regime backtest), then tag trades with entry regime to validate sizing rationale empirically.

13. **Regime frontend (Stage 3 chart)** — visualisation layer on top of the regime engine. 5-year price chart with background shading by regime, trade entry/exit markers overlaid (Stage 2), live panel showing current regime + duration + transition probability. Comes after Stage 2 (trade overlays).
