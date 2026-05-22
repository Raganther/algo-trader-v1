Status: current | Epistemic: living journal — status board + timeline + milestones + methodology | Last verified: 2026-05-10

# Calibration Journal — Algo Trader V1

Single living document for the calibration journey. **Status of every component, the timeline of findings, live forward-test milestones + named patterns, the running Layer 3 sample, and the methodology.** New findings get folded in here as they're discovered; long standalone reports live in their own files (referenced from the timeline). Per-trade detail is **not** maintained here — query Alpaca MCP `get_orders` or the cloud `live_trade_log` table for raw trades, see `daily-trade-audit.md` procedure.

> **Live is ground truth. The backtest is the model.** When live and backtest disagree, the default move is to refine the model, not the bots. Strategy changes are a separate lever (e.g. May 7 HWM trail anchor) and warrant explicit justification.

---

## 1. Status board

| Component | Status | Source of truth |
|---|---|---|
| Spread model (`--spread 0.0003`) | **Calibrated** Apr 13 | §6 methodology + Apr 13 snapshot |
| Order mechanics (whole-share, GTC, shorts, sync, wash) | **Calibrated** Apr 13 + ongoing | §6 + cloud `live_trade_log` |
| Stop-fire mechanics (server-side stop, intrabar) | **Calibrated** | Apr 13 snapshot below |
| Layer 3 — stop slippage aggregation | **In progress** — 41/50 fires (Apr 24 refresh; floor not current) | §5 below + cloud `live_trade_log` for refresh |
| Per-cluster slippage | **Pending** — sample too thin | (gated on Layer 3 hitting 50+) |
| 1-bar polling delay artifact | **Identified May 7, magnitude refined May 8, portfolio-level confirmed May 20** — config-matched residual ~$867 over the 5-week verified window; model-fit still pending (`--delay 1` broken) | `live-vs-backtest-iau-diagnostic.md`, `audit-hwm-delay-mechanism.md`, §2 May 20 entry |
| ADX-filter early-return blocks exits | **Quantified May 8 PM; default flipped to `entry_only` May 21** — bug contributes ~50% of return and ~1.23 Sharpe in long-window 7-bot. The fix is now the strategy default; 7 live run scripts pinned to `'all'` so live trading is byte-unchanged pending a deliberate deploy. **HWM A/B + per-asset re-runs May 9; portfolio baseline re-run May 21. Live deploy + cap-shrink/small-cap re-runs still pending.** | §2 timeline May 8 PM / May 9 / May 20 / May 21 entries |
| HWM trail anchor — live tracking | **Day-14 gate PASSED May 20** — HWM-era live P&L (−$300) matches HWM+entry_only backtest (−$310) on the identical tape | `trail-anchor-hwm.md`, §2 May 20 entry |
| Sub-bar fill price variance | **Not characterized** — extractable from `live_trade_log` | (none yet) |
| Overnight gap behavior on stops | **Characterized** Apr 23 incident + `gap-distribution.md` | `gap-distribution.md` |
| Aggregate live Sharpe expectation | **~4.0 ±0.5 (May 9)** — was 5.73 → 5.50 → 4.0 over May 7–9. Tripwires SHIPPED May 9 (bars 1.8/2.5/3.0 at 30/60/90d). | `live_performance_report.py`, §2 May 9 entry |
| Lineup-pruning question (per-asset Sharpe < 2.0 ⇒ prune?) | **Resolved May 10 — NO.** Sharpe monotonic with bot count; per-asset bar is candidate-add screen, not prune threshold. | `portfolio-runner-lineup-selection.md`, §2 May 10 entry |

> **Rule for this table:** numbers live in their source-of-truth file, not here. This row says *what* and *where*, not *how many*. When the Layer 3 sample grows to 45, only update §5; this row stays "in progress" until it crosses 50.

---

## 2. Findings timeline

### Apr 13 2026 — Apr 13 calibration run, Layers 1/2/4 PASS
Entry/exit mechanics, spread model, and aggregate P&L direction all check out for test params over the Mar 20 – Apr 20 window. Layer 3 (slippage) deferred to forward test. Full results in §7 below.

### May 7 2026 — Backtest 1-bar polling delay artifact identified (IAU diagnostic)
14 days of validated-params live data revealed a structural mismatch: backtest evaluates signals at bar Close with delay=0; live polls Alpaca every ~60s, effective delay ≈ 1 bar. The phase shift propagates through `trail_after_bars=10` and the close-anchored trail formula's bar-Close reference, producing different stop-fire bars on identical price paths. Apr 23 IAU short was the smoking gun. **Initial estimate: backtest optimistic by ~0.7 Sharpe.** Full diagnosis: `live-vs-backtest-iau-diagnostic.md`. HWM trail anchor (Path 2) shipped + deployed live same day as the structural fix; `--delay 1` (Path 1) noted as broken in the existing backtester, deferred.

### May 8 2026 (AM) — HWM mechanism falsification audit (magnitude refined)
The "+0.78 Sharpe lift ≈ 0.7 delay artifact" causal claim from May 7 put under formal falsification (data-shift simulation of 1-bar phase shift, since `--delay 1` is broken). **Verdict SUPPORTED** — HWM is ~2.8× more delay-resistant than close-anchored (Δsharpe(close)=0.42 vs Δsharpe(hwm)=0.15). **But only 0.42 of the predicted 0.7 close-anchored artifact reproduced** under simulation; data-shift under-represents real polling delay's sub-bar effects. Practical implications (as understood at this point — superseded by the May 8 PM finding below):
- Close-anchored real artifact range: **0.42 (lower bound) ≤ X ≤ 0.7 (upper bound)**
- HWM live gap likely **~0.2–0.3 Sharpe**, not zero
- Live HWM tripwire anchor recommendation at this point: 5.73 → **~5.50** (later revised again to ~4.0 after the PM ADX-bug finding)
- The "+0.78 ≈ 0.7" framing is a directional rhyme, not a causal identity
- Mechanism support *strengthens* (does not weaken) the case for keeping HWM live

Full audit + 2×2 + per-trade attribution: `audit-hwm-delay-mechanism.md` (with caveat header noting the audit was run under the ADX-bug). Reproducible script: `python3 -m backend.analysis.audit_hwm_delay_sensitivity`.

### May 8 2026 (PM) — ADX-filter early-return blocks mid-trade exits
While investigating why backtest didn't reproduce the live OIH +$22.53 short (May 5 19:47 entry → May 8 13:31 K-exit), found a bug in `backend/strategies/trend_framework.py:211-239`. The ADX filter `if current_adx > self.adx_threshold: return` runs **before** the stop-loss check (line 242), entry block (line 269), and signal-exit blocks (lines 428, 445). When ADX rises above threshold mid-trade, the strategy returns early and **all exits are blocked** — only the trail-update path (line 168-208, before the filter) keeps running.

Effect: positions opened in low-ADX regime cannot exit (via stop or K-signal) once ADX rises above 20 mid-trade. The OIH short opened May 5 at ADX=8.5 with K=23 (clean entry), but ADX rose to 30+ as the down-move accelerated; backtest's exit logic was locked out for the entire May 6-7 window even when K dropped to 0.0 (clear K-exit condition). Empirically confirmed: backtest leaves the position open with `qty=-5` at end of data window.

**Live has two safety nets that mask the bug:**
1. Server-side Alpaca stops fire independently of bot code
2. The K-exit fires when ADX briefly dips below threshold (transient ranging in a trend)

**This is a third backtest-vs-live divergence**, alongside the delay artifact (May 7) and the trade-fire divergence. Direction of impact on aggregate Sharpe is unclear — depends on whether trapped trades are net winners or losers.

**Suggested fix:** move the ADX filter to gate only the entry block, not the whole `on_data` function. Stops and signal-exits should run regardless of ADX state. Single-block code change in `trend_framework.py:211-269`.

**Status:** identified, not fixed. Holding off on the fix because (a) HWM was deployed yesterday and is still being verified, (b) the fix invalidates every prior backtest result (validated edges, portfolio runner, HWM A/B, May 8 audit) until re-run, (c) impact direction needs quantification before committing.

**First quantification audit (May 8 PM, `audit_adx_filter_exit_block.py`):** ran A (current, buggy) vs B (`skip_adx_filter=True`, no ADX filter at all) on long-window 7-bot. **B was substantially worse**: +248.77% / Sharpe 3.24 / DD 4.54% / 10,122 trades vs A's +424.09% / 4.95 / 3.41% / 4,344 trades. ΔSharpe −1.71. **But B is the wrong proxy** — removing the ADX filter from both entries AND exits floods in 5,778 extra losing entries during trends, drowning out any exit-effect signal.

What the audit *did* surface, on the 2,149 trades that fired in both runs:
- 567 trades (26% of common) had different exits → direct fingerprint of the exit-block bug
- ΔP&L on common trades: **−$101,759** (B captured ~$102k LESS than buggy A)
- Per common trade: ~$47/trade extra profit captured by the buggy version

**Counter-intuitive interpretation:** the bug appears to be *helping* aggregate backtest performance, not hurting it. Mechanism: trades enter in low-ADX (ranging) regime, the move accelerates into a trend (ADX rises), bug locks exits during the high-ADX phase, trade rides further than the strategy's exit logic would normally allow, eventually closes when ADX dips. The OIH May 5 short is the canonical example. **Some non-trivial fraction of the validated-edges Sharpes (GLD 2.48 etc.) is bug-derived "let winners run via accidental exit-block."**

**Live partially escapes the bug** via server-side Alpaca stops + K-exits that fire when ADX briefly dips. So live captures *some* of the bug's benefit but not all. **This contributes to the live-vs-backtest gap on top of the delay artifact** — the gap may be larger than the May 7-8 magnitude estimate suggested.

**Audit B inconclusive on bug magnitude.** Need a parameterized fix (gate ADX on entries only, leave exits alone) for clean A-vs-C comparison.

JSON record: `audit-adx-filter-exit-block.json`.

**Second quantification audit (May 8 PM, parameterized fix).** Added `adx_filter_mode` parameter to `trend_framework.py` with values `'all'` (default — legacy buggy behaviour, byte-identical to prior backtests) or `'entry_only'` (proper fix — ADX gate blocks new entries only, stops and signal-exits run regardless). Re-ran long-window 7-bot:

| Metric | A (`'all'` — buggy) | C (`'entry_only'` — fix) | Δ |
|---|---:|---:|---:|
| Return | +424.09% | +212.28% | **−211.81pp** |
| Sharpe | 4.95 | 3.72 | **−1.23** |
| Max DD | 3.41% | 2.06% | **−1.35pp** |
| Trades | 4,344 | 4,486 | +142 |

**The bug is contributing roughly half the headline return and one-quarter of the Sharpe.** Every symbol's per-symbol P&L drops materially (GDX $67k → $25k, OIH $85k → $49k, SLV $74k → $39k, etc.) — the "let winners run via accidental exit-block" effect is structural across the lineup, not concentrated.

**Per existing decision rule** (ship change if ΔSharpe ≥+0.30 OR ΔDD ≥−1pp with ΔSharpe ≥−0.10): fix FAILS catastrophically (ΔSharpe −1.23 vs −0.10 tolerance). **But this isn't an optimization decision — it's correctness.** The buggy version is the wrong model of what the strategy actually does in trending tape; the fix produces an honest backtest.

**Implications for the calibration journey:**
- All validated-edges per-asset Sharpes (GLD 2.48, IAU 1.95, SLV 2.46, GDX 2.46, OIH 2.33, XBI 2.18, XOP 1.98) were computed under this bug — likely overstated by similar magnitude per asset
- HWM A/B (+0.78 Sharpe, 4.95→5.73) was computed under the bug — relative direction probably preserved but magnitude needs re-run
- The May 7-8 "delay artifact" estimate of 0.4–0.7 Sharpe was conflating two effects: the actual polling delay AND the ADX-bug expressing differently in live (where server-side stops + ADX dips partially escape it) vs backtest (where it can't be escaped). True delay artifact magnitude likely smaller than 0.7.
- **Live Sharpe expectation revised:** previously recommended tripwire anchor ~5.50 (HWM-corrected from 5.73). Now realistic live range is **~3.7–4.5** Sharpe, depending on how much of the bug live escapes via safety nets. **Tripwire anchor should drop to ~4.0** as a reasonable midpoint.
- Real-money pilot timeline shifts — the calibrated baseline just dropped meaningfully

**Status:** parameterized fix shipped behind opt-in flag (default preserves legacy behaviour byte-identical, so all prior backtests remain reproducible). Live bots unchanged. Pending: full A/B re-suite (validated edges per asset, HWM A/B, small-cap, cap-shrink) under `'entry_only'`, then strategic decision on flipping default. Treat as a multi-week initiative similar to HWM deploy but bigger blast radius.

---

### May 10 2026 — Lineup-selection experiment under bug-fixed calibration

Three trimmed lineups vs 7-bot HWM+entry_only baseline (Sharpe 4.17). Run A (4-bot best-per-cluster GLD/SLV/OIH/XBI): **3.79**. Run B (5-bot drop GDX+XOP): **3.87**. Run C (6-bot drop GDX): **4.01**. Sharpe monotonic with bot count; each bot adds ~+0.10–0.15 Sharpe via diversification. All trimmed lineups fail the decision rule (Sharpe branch lost; DD branch best 0.13pp, far short of 1pp bar).

**Verdict:** keep the 7-bot lineup. Even per-asset losers GDX (1.46) and XOP (1.32) add net positive at portfolio level. The May 9 per-asset 2.0 Sharpe bar is a candidate-addition screen, not a prune threshold.

**Next experiment promoted:** per-bot cap-shrink under entry_only. Apr 30 PM +0.45 Sharpe finding (4.95 → 5.40 on 8 bots × 12.5%) needs re-validation under bug fix.

Snapshot: `.claude/strategies/portfolio-runner-lineup-selection.md`. Per-asset cards (GDX/XOP/IAU/XBI/OIH) updated with "keep in lineup" banner. Roadmap row "Best-per-cluster 4-bot experiment" status: resolved.

---

### May 9 2026 — Tripwire calibration + HWM A/B + per-asset Sharpe under bug fix

**Tripwire update (`backend/analysis/live_performance_report.py`).** Anchor revised 5.73 → **4.0**, annualised return expectation 0.39 → 0.22, bars 1.5/3.0/4.0 → **1.8/2.5/3.0** at 30/60/90d. Bars sit ~2σ below the anchor's lower edge (3.5) given Sharpe SE ≈ 1/√days (30d ≈ ±0.7, 60d ≈ ±0.5, 90d ≈ ±0.4). DD expectation (3.05%) and win-rate band (41–47%) flagged "provisional" pending refresh under entry_only.

**HWM A/B re-run under `entry_only` (long-window 7-bot, $94k):**

| Metric | Close + entry_only | HWM + entry_only | Δ |
|---|---:|---:|---:|
| Return | +212.28% | +230.73% | +18.45pp |
| Sharpe | 3.72 | **4.17** | **+0.45** |
| Max DD | 2.06% | 2.58% | +0.52pp |
| Trades | 4486 | 4639 | +153 |

**ΔSharpe shrinks from buggy +0.78 → fixed +0.45** (~58% survives bug correction). Decision-rule passes (+0.30 Sharpe branch clears; DD branch flips slightly negative but tiny). **Verdict: HWM stays live as-is.** The "+0.78 ≈ 0.7 delay-artifact identity" framing dies — about 42% of the buggy lift was the bug interacting worse with close-anchored than with HWM (HWM is more bug-resistant for the same reason it is more delay-resistant: stops triggered against an intrinsic HWM are not blocked by the buggy ADX early-return).

**Per-asset Sharpe under `entry_only` (close-anchored, single-symbol, 2020-01 → 2026-04):**

| Asset | Buggy | entry_only | Δ | Clears 2.0? |
|---|---:|---:|---:|---|
| GLD | 2.48 | **2.28** | −0.20 | ✓ |
| SLV | 2.46 | **2.19** | −0.27 | ✓ |
| OIH | 2.33 | 1.91 | −0.42 | ✗ |
| IAU | 1.95 | 1.88 | −0.07 | ✗ (was already) |
| XLE | 2.30 | 1.55 | −0.75 | ✗ |
| GDX | 2.46 | 1.46 | **−1.00** | ✗ |
| XOP | 1.98 | 1.32 | −0.66 | ✗ |
| XBI | 2.18 | 1.18 | **−1.00** | ✗ |

Only **GLD and SLV** clear the 2.0 quality bar at the per-asset close-anchored level. **GDX and XBI** lose the most (−1.00 each — heaviest bug-beneficiaries). Caveats before reading too much in: (a) HWM lift adds ~0.3–0.5 (live runs HWM); (b) live partially escapes the bug via server-side stops + ADX dips; (c) **portfolio Sharpe (4.17 under HWM+entry_only) is much higher than per-asset average** due to cross-asset diversification — the lineup is a portfolio, not 8 standalone bots. Per-asset numbers below 2.0 don't directly invalidate the lineup; they invalidate the "8-of-8 quality candidates" framing.

**Status board updates needed:** "All validated-edges per-asset Sharpes" row should reference the new May 9 column; HWM trail anchor row should reference the +0.45 result; live Sharpe expectation row resolved (4.0 ±0.5 anchor, tripwires now calibrated).

**Outstanding A/B re-runs under `entry_only`:** May 8 delay-mechanism audit, small-cap deployment, cap-shrink experiment, portfolio-runner V2 baseline, cluster-cap V1 — all preserved as historical record but pending refresh before any further strategic use.

---

### May 20 2026 — First portfolio-level matched-window live-vs-backtest comparison (day-14 HWM gate)

The roadmap scheduled a day-14 HWM pattern-detection gate for ~May 21. Ran it: the 7-bot portfolio backtested over the **exact same price tape** as the verified-params forward test (Apr 15 → May 20 2026), three configs, vs live. Reproducer: `scripts/window_backtest.py` (one-off; loads Alpaca recent data or research.db cache, runs `PortfolioRunner` with the live param set, dumps equity + trades to JSON).

**Headline three-way comparison, full Apr 15 → May 20 window:**

| Run | Trades | P&L | Win% | W/L |
|---|---:|---:|---:|---:|
| LIVE (real bots) | 51 | **−$653** | 27.5% | 2.34 |
| Backtest, `adx_filter_mode='all'` (buggy — the config the bots actually run) | 65 | **+$8,978** | 46.2% | 4.53 |
| Backtest, `adx_filter_mode='entry_only'` (bug fixed) | 68 | **+$372** | 42.6% | 1.46 |

**The buggy backtest is worthless as a live predictor.** Same data, same nominal config as the bots, yet +$8,978 vs live −$653. Fixing the bug collapses the *same backtest* from +$8,978 → +$372 — the bug invented ~$8,600 of phantom profit over five weeks. The bug-fixed backtest (+$372) sits right next to live (−$653).

**Why live can't capture the bug even though the bots run `'all'`:** the bug blocks the *strategy's* stop-loss check when ADX is high. Live's server-side Alpaca stop orders fire intrabar regardless of ADX, so live exits where the buggy backtest rides. Live therefore behaves like `entry_only`, not like `'all'` — confirming the May 8 PM "live partially escapes the bug" thesis on real forward-test data. **Decision rule going forward: all deployment-facing backtests use `entry_only`; `'all'` numbers describe an un-tradeable market.**

**Config-matched refinement.** The matched backtest above used HWM throughout, but live ran close-anchored Apr 15–May 6 and HWM only from May 7. Re-running `entry_only` with `trail_anchor='close'` and stitching (close for Apr 15–May 6 + HWM for May 7–20):

- Config-matched bug-fixed backtest: **+$214** · live: **−$653** · residual gap **~$867** over 65 trades.
- **HWM era May 7–20 in isolation: live −$300 vs HWM+entry_only backtest −$310 — a $10 match.** The most recent, cleanly config-matched fortnight shows near-perfect live/backtest agreement.
- The ~$867 residual is concentrated in the Apr 28–May 6 window and is consistent with the documented 1-bar polling-delay artifact + slippage.

**Rolling distribution context.** Full bug-fixed backtest (`entry_only`+HWM, 2020-07→2026-04: +180.56% / Sharpe 3.96 / DD 3.17% / 3,810 trades — consistent with the May 9 long-window 4.17). Rolling **23-trading-day** annualised Sharpe (live window length): median **4.38**, p10 0.19, p5 −0.96, p1 −3.44; **9.1% of all 23-day windows are negative**. Live's −0.62 sits at **~p6.3** — a poor window, ~1-in-16 frequency, not a structural break. Crucially, the bug-fixed backtest *over the identical Apr 15–May 20 tape* scored only Sharpe **+0.61** (~p13): **the regime itself was weak for the strategy.** Five weeks of chop → roughly flat is the correct, expected outcome.

**GLD diagnostic.** GLD is the single largest negative live-vs-backtest contributor: live −$674 vs config-matched bug-fixed backtest +$526 (~$1,200 gap). Trade-level diff: live took repeated long re-entries into the Apr 22–23 gold selloff (4 stopped longs, −$382) and a fast May 5 stop-out (−$50 where the backtest rode +$680). This is the **delay artifact amplified by a sustained down-trend** — counter-trend longs entered one bar late get worse fills and faster stops in a falling tape; GLD trended down hardest (440→417), so it ate the most delay damage. Not a GLD-specific bug. At the portfolio level it is substantially offset (SLV live +$2,237 *beat* the bug-fixed backtest's +$1,168) — per-symbol live-vs-backtest gaps are large and noisy but largely cancel across the lineup.

**Tripwire-calibration insight.** The 30-day tripwire (Sharpe < 1.8) cannot distinguish "bad regime" from "broken edge": the bug-fixed backtest's own 23-day windows fall below 1.8 well over a third of the time, and *this* window scored 0.61 — it would have tripped the wire while perfectly healthy. A single sub-1.8 reading is not diagnostic. Recommend re-anchoring `live_performance_report.py` tripwires to **percentile breaches** of the bug-fixed rolling distribution (sustained below p10/p5) rather than absolute Sharpe levels.

**Net verdict:** the strategy is **not broken and not underperforming a correct backtest** — live tracks `entry_only` within ~$867 over five weeks, and the HWM era matches to $10. The disappointment was measuring live against a *buggy* backtest. The true five-week expectation in this chop regime was ≈ break-even, and that is what live delivered. Strongest evidence to date for flipping the `adx_filter_mode` default to `entry_only`.

---

### May 21 2026 — `adx_filter_mode` default flipped to `entry_only` (code), live pinned

Acting on the May 20 finding: flipped the strategy default `adx_filter_mode` `'all'` → `'entry_only'` at `trend_framework.py:57`. The bug-fixed mode is now what every backtest and the codebase use by default; the legacy buggy `'all'` mode is reachable only by passing it explicitly (to reproduce a pre-May-21 backtest).

**Live trading is byte-unchanged.** All 7 live bot run scripts (`scripts/run_*_test.sh`) were explicitly pinned to `"adx_filter_mode":"all"` in the same change. Flipping the default without pinning would have silently switched the bots to `entry_only` on their next deploy — that is the "live deploy" decision, which is **deliberately deferred** (it changes live behaviour — K-exits would fire in high-ADX regimes — and resets the forward-test clock). The pin holds the bots on their current behaviour until that decision is made; remove it as part of the deploy.

**Portfolio baseline re-run under the new default** (`portfolio-runner-baseline.md` regenerated, 2020-07→2026-04, $94k, close-anchored, cap on): **+212.28% / Sharpe 3.72 / DD 2.06% / 4,486 trades** — down from the buggy +424.09% / 4.95 / 3.41% / 4,344. Reproduces the May 8 PM A-vs-C audit's C-cell figure exactly (consistency check passed).

**Still pending (buggy-`'all'`-mode, not yet re-run):** per-bot cap-shrink experiment, small-capital ($1k) deployment plan, the Apr 30 rotation 4-run study — all numbers in `CLAUDE.md` Current Status and the corresponding domain files remain buggy-mode. The per-asset validated-edges Sharpes (May 9) and HWM A/B (May 9) are already on `entry_only`. Code change only — no git-save / cloud deploy performed.

---

## 3. Live forward-test milestones

> **Bot config (all 7):** OB 80 / OS 15, ADX threshold 20, 10-bar min hold, 2.0 ATR trail after 10 bars, GTC stops, whole-share sizing, shorts enabled, `skip_days:[0]`. GLD/IAU/SLV/GDX deployed Apr 15–16; OIH/XBI/XOP added Apr 28; HWM trail anchor deployed all 7 May 7 PM.

> **Exit types:** `K` = bot K-signal at candle close · `SS` = server-side stop loss · `TS` = trailing stop fired intrabar in profit · `EM` = emergency market exit (gap-through-stop guard, introduced Apr 29)

| Date | Event | Significance |
|---|---|---|
| Apr 15 | First validated-params entry (SLV K-exit, −$207) | Forward test begins |
| Apr 16 | **First short confirmed** — GLD short, 14:17 sell-to-open @ $440.43, K-exit 16:46 @ $439.73 (+$38.50) | Whole-share sizing path validated end-to-end for shorts |
| Apr 20 | **First trail fire in profit** — SLV, entered Apr 16 @ $71.29, trail ratcheted $70.72 → $72.14, server stop fired @ $72.12 (+$283.86) | The mechanism that drives validated-params Sharpe — confirmed live |
| Apr 22→23 | **First overnight gap-through** — SLV, entered $70.48, gapped down, GTC stop @ $70.15 fired at open @ $68.74 (−$605.52) | Closed single-symbol gap-policy item; delta = gap risk, not slippage |
| Apr 23 | **First organic short stop-fire against us** — IAU short @ $89.05, buy-stop fired @ $89.10 (−$13.65) | Closed "awaiting organic short stop" data point |
| Apr 28 | OIH/XBI/XOP bots added (4 → 7 lineup) | Energy + biotech clusters introduced live |
| Apr 29 | **Correlation-aware sizing V1 deployed** | `risk_frac = 0.02 / N` (cluster occupancy discount). First cluster-simultaneous entry that triggers discount: TBD — record N, risk_frac, share count when it happens |
| Apr 29 | **First EM exit** — XBI, entered Apr 28 @ $131.25, gap-through-stop guard fired market exit @ $129.55 (−$313.61) | New exit type `EM` introduced; gap-recovery code path bug surfaced + fixed same session |
| May 7 | **HWM trail anchor deployed live** all 7 bots | Existing OIH short continues with close-anchored fallback (HWM only initializes on entry) |
| May 8 | **Last close-anchored trade closed** — OIH short opened May 5 19:47 @ $442.09 (qty 54), K-exit (market) May 8 13:31 @ $419.56 = **+$22.53/share × 54 = +$1,217** over ~3-day hold. Exit mechanism: K-signal (StochRSI mean-reversion complete), not trail-fire — trail was tracking at ~$443-444 and got canceled when K-exit fired. | Transition point: every new entry from this point forward initializes HWM. Live record is now HWM-only. Signal-driven capture on a sustained move (~5% OIH drop over the hold) — the trail backed it up but didn't fire. |
| TBD | First HWM live entry | TBD — record date, symbol, exit type when it fires |

---

## 4. Named patterns

**GLD stop-cycle whiplash (observed Apr 23).** Choppy regime + 2.0 ATR trail produces ≥3 entry→stop cycles in one session, all losses. Apr 23: 3 GLD entries within ~3 hours, each stopped within 30–60 min ($-1.42, $-1.51, $-1.34/share). Validated-params behaviour, not a bug — the cost of running mean-reversion in chop with a tight trail. Worth flagging if it repeats often enough to suggest a regime gate.

**Stop-slippage sign asymmetry (observed Apr 20–23).** Sell-stops on long positions slip mostly negative (fill below stop level). Buy-stops on short covers / long sell-stops at trail-ratchet slip mostly positive (fill above stop level). The "100% negative" framing from early calibration didn't hold — direction is side-dependent.

**Gap-through-stop bug pattern (observed + fixed Apr 29).** Bot's gap-recovery code path can cancel a valid GTC stop at session re-open, then fail to re-place if the new stop level would be "wrong-side" of current price (Alpaca rejects). Fixed by `runner.py:943-983` breach-check guard. Symptom to watch for: any future bot session that logs `[LOOP] 🚨 Stop $X already breached by price $Y` — the guard is doing its job, but the underlying root cause (`pending_stop_order_id` becoming None despite live GTC stop) is unresolved.

---

## 5. Layer 3 — stop slippage running sample

**Last refresh:** Apr 24 2026. **Sample at refresh:** 41 fires (33 calibration window + 8 forward-test through Apr 24).

**Stats at last refresh:** mean −$0.0247/share, median −$0.0134/share. Consistent with prior calibration (median $0.010, mean $0.025). 3 of 8 most recent fires are positive (sign asymmetry — see §4).

**Target:** 50 intraday fires before deciding whether to bake `stop_slippage` into the backtest. **Probably already crossed** — Apr 25 → today is ~10 trading days unlogged. Refresh requires running `daily-trade-audit.md` over Apr 25 → today and counting filled stop orders. Treat the "41" figure as a floor, not the current count.

**Most recent fires (Apr 20–23):**

| Date | Symbol | Side | Stop $ | Fill $ | Slippage |
|------|--------|------|--------|--------|----------|
| Apr 20 | GLD | sell-stop (long) | 440.10 | 440.05 | -0.0500 |
| Apr 20 | IAU | sell-stop (long) | 90.18 | 90.18 | +0.0044 |
| Apr 20 | SLV | sell-stop (long, TS) | 72.14 | 72.12 | -0.0200 |
| Apr 22 | IAU | buy-stop (short cover) | 89.23 | 89.24 | +0.0100 |
| Apr 23 | GLD | sell-stop (long) | 433.67 | 433.61 | -0.0650 |
| Apr 23 | GLD | sell-stop (long) | 433.19 | 433.11 | -0.0800 |
| Apr 23 | IAU | buy-stop (short cover) | 89.09 | 89.10 | +0.0100 |
| Apr 23 | GLD | sell-stop (long) | 433.21 | 433.20 | -0.0069 |

---

## 6. Methodology

### What calibration is

The test params (OB 60/OS 40, ADX 50, 3-bar hold, 0.5 ATR trail) were a calibration *instrument* — high trade count to surface bugs and validate engine layers — not a trading strategy. By running the same params in backtest and live simultaneously, we verify whether the backtest engine faithfully models reality. **Validated params + HWM trail are the actual deployed strategy.**

### How to run a live-vs-backtest comparison

```bash
# Backtest over same window as live, with full lead-in for indicator warmup
python3 -m backend.runner backtest --strategy TrendFramework --symbol GLD \
  --timeframe 15m --start 2026-01-01 --end 2026-04-20 --source alpaca \
  --spread 0.0003 --delay 0 \
  --parameters '{"rsi_period":7,"stoch_period":14,"overbought":60,"oversold":40,"adx_threshold":50,"skip_adx_filter":false,"sl_atr":2.0,"dynamic_adx":false,"trailing_stop":true,"trail_atr":0.5,"trail_after_bars":1,"min_hold_bars":3,"skip_days":[],"trading_hours":[13.5,20],"long_only":true}'

# Pre-window baseline (subtract to isolate the comparison window)
# Same command with --end <window-start>
```

**REQUIRED for test-params calibration runs:**
- `"trading_hours":[13.5,20]` — live bot only processes bars during 13:30–20:00 UTC. Without this, backtest processes pre/post-market bars and inflates trade counts.
- `"long_only":true` — pre-Apr-15 live bots couldn't execute shorts (fractional share guard). Without this, backtest doubles trade count vs live. Not needed for validated-params comparisons (shorts now work).

**Why the lead-in matters:** backtest needs ~50 bars of warmup before indicators are valid. Starting from Jan 1 ensures warmup completes before the comparison window opens.

### Layered comparison framework

| What you compare | What it confirms |
|---|---|
| Trade count | Signal generation faithful — indicators, bar timing, entry/exit logic match |
| Entry/exit prices (trade by trade) | Whether the spread assumption reflects reality |
| Stop fill prices vs backtest | How accurately backtest models intrabar server-side stop execution |
| Aggregate P&L | Overall model accuracy |

Stop if a layer fails before proceeding to the next.

**Caveats:**
- Paper fills ≠ real-money fills — Alpaca paper simulates at market price
- Calibration is a snapshot — valid for the market conditions during the test window only
- Need ~80–100 trades for P&L comparison to be statistically meaningful

### Two types of slippage — only one is currently modelled

Spread slippage modelled (`--spread 0.0003`). Stop execution slippage not modelled — live shows $0.00–$0.14/share, typically under $0.05. Tracked in §5 above. Will fold into backtest model if Layer 3 sample at 50+ shows systematic deviation from the implicit zero assumption.

### Calibration integrity — signal vs execution layer

Bug fixes applied during testing are in the execution layer (order placement, fill confirmation, stop management, DB logging). None touched signal generation (StochRSI thresholds, ADX check, bar timing). The calibration comparison is asking only: "when strategy thresholds are met, does a trade fire?" — identical in backtest and live. Fixes made mechanics reliable; they didn't change what the strategy does.

One marginal factor: delayed fills at market open (3–4 min on some symbols) can briefly desync bot state, potentially missing a signal the backtest would catch. This is noise, not systematic drift.

### Live observation framework — what to look for

While the 7 bots run, four measurements convert time-passing into real-money confidence:

1. **Live Sharpe vs backtest Sharpe — per cluster.** Once ~3 months of trades accumulated (target: late Jul 2026), per-cluster live Sharpe vs backtest expectation. **Portfolio-level anchor: ~4.0 ±0.5** (May 9 revision after ADX-bug quantification). Per-cluster backtest expectations under bug fix are not yet measured cleanly (only standalone per-asset entry_only numbers exist: GLD 2.28, SLV 2.19, etc. — single-symbol, close-anchored). Decision rule: live within 30% of portfolio anchor = sound; live < 2.0 = something material mis-modelled. Surface in `live-performance-report.md` once per-cluster split is built.
2. **Slippage tracking** — quarterly aggregate. If consistently above the model's ~$0.013/share median, backtest Sharpe is overstated by ~ (live − model) × annual stop count × position size / equity.
3. **Regime check** — sustained bear / sideways during the window is data we have nowhere else. Apr 28 framework-attribution finding predicts the framework is *strong* in sustained directional moves and *weak* in transitions.
4. **Correlated-entry frequency** — how often 3+ peers in the same cluster enter within 30 min. Theoretical concern from `gap-distribution.md`; live frequency tells us whether the worst case is rare or common.

---

## 7. Apr 13 2026 — Test-params calibration full results (CLOSED)

> **Status: CLOSED 2026-04-13.** Layers 1/2/4 PASS (commit `dbeea79`). Bots subsequently moved to validated params + HWM (May 7). Future calibration is a new initiative tracked in `research-roadmap.md`.

### Mar 20 – Apr 13 (18 trading days)

Backtest (`trading_hours:[13.5,20]`, `long_only:true`, `dynamic_adx:false`) vs live Alpaca log (75 confirmed trades). Clean window = full (Jan 1 – Apr 14) minus pre-window baseline (Jan 1 – Mar 20).

| Symbol | Backtest trades | Live trades | Ratio | BT return (clean) | BT win rate (full) |
|--------|----------------|-------------|-------|-------------------|--------------------|
| GLD    | 20             | 19          | 1.05x | +1.03%            | 58%                |
| IAU    | 18             | 18          | 1.00x | +0.55%            | 44%                |
| SLV    | 19             | 19          | 1.00x | +2.98%            | 49%                |
| GDX    | 18             | 19          | 0.95x | +2.28%            | 54%                |
| **Total** | **75**      | **75**      | **1.00x** | —             | —                  |

**Layer 1 — Signal: PASS.** Trade counts match exactly in aggregate.

**Layer 2 — Entry/Exit Prices: PASS on aligned trades.** Aligned intraday trades match within ±$0.3 (slightly above the 0.03% spread, attributable to 1-bar market-order fill timing desync). Multi-day trade divergence investigated and confirmed as cumulative drift, not a structural model gap. Overnight stop persistence is symmetric between backtest and live (`backtester.py` has no session-boundary logic; `runner.py:934` re-places DAY stop with same in-memory `current_sl`).

**Layer 3 — Stop slippage: deferred** (sample 33 fires at Apr 13, expanded to 41 by Apr 24 — see §5).

**Layer 4 — Aggregate P&L: PASS with caveat.**
- Live portfolio P&L (Mar 19 close → Apr 13 close): **+$4,543 / +4.82%** ($94,353 → $98,896)
- Backtest sum-of-symbols on $40k isolated capital: +$684 / +1.71%
- Live is **~2.8× backtest** — explained by shared-capital multi-bot stacking, not a model bug. Backtest runs each symbol on isolated $10k; live runs 4 bots sharing ~$94k pool, each sizing at 25% cap of the *full* pool, so total deployment can stack to 100%. Expected effective deployment 2–3× backtest depending on correlated-entry frequency. Observed 2.8× is in range; direction matches.
- Rigorous aggregate validation requires shared-capital portfolio backtester (shipped Apr 30 PM as `backend/engine/portfolio_runner.py`).

### Apr 13 calibration regime context

The Mar 20 – Apr 20 window coincided with an extreme regime — Operation Epic Fury (Iran, Feb 28) triggered metals volatility, gold flash-crashed Mar 19 (-6.9%), recovered partially through April. GDX underperformed GLD by ~12pp on oil-driven mining margin compression — structural, not a model error.

Implications: execution layer (spread, slippage, bar timing) is regime-independent and the calibration of those parameters is valid. Signal layer was forward-tested under conditions outside the 2020–2025 training sample; weaker-than-predicted results don't necessarily indicate a backtest bug.

---

## 8. Historical snapshots (pre-Apr-13, archived for reference)

### Mar 5–16 (11 trading days) — preliminary

Backtest (Jan 1 lead-in, `long_only=True`) vs live DB:

| Symbol | Backtest trades | Live trades | Backtest return |
|--------|----------------|-------------|----------------|
| GLD    | 8              | 10          | -0.27%          |
| IAU    | 5              | 8           | -0.32%          |
| SLV    | 10             | 10          | -0.36%          |
| GDX    | 6              | 8           | -0.66%          |

Too early for conclusions — repeated successfully at Apr 13.

### Mar 20–27 (8 trading days) — preliminary, INVALIDATED

Run without `long_only:true`; backtest counted shorts that live couldn't execute. The 1.3x ratio was an artefact, not a signal-generation gap. **Do not use as a calibration reference.**

### Mar 20–Apr 2 (12 trading days) — corrected mid-point

Backtest (`trading_hours:[13.5,20]`, `long_only:true`) vs live MCP audit (48 confirmed trades). Ratio ~0.90x — gap confirmed as partial-bar market-open effect (Apr 3 finding): live fires on 1–2 min bars at 13:30 open; backtest uses complete 15-min bars. P&L direction aligned. Closed with the full Apr 13 run above.

### Mar 20 – Apr 7 (13 trading days) — live equity curve

Pulled Apr 8 via `get_portfolio_history` MCP. **+$3,626 (+3.85%) over 13 trading days** ($94,353 → $97,837). Three big up days (Mar 23, Mar 31, Apr 2) account for +$4,612. Max single-day DD: -$605 (Mar 30). Apr 7 includes open GLD position (+$735 unrealized). Regime note: 2024–2025 is the best-performing period in aggressive-params backtest — clean equity curve partly reflects that.

---

## Per-trade ledger archive

Per-trade detail for the Mar 20 – Apr 20 calibration window is preserved at `archive/calibration-window-mar-apr.md`. Frozen, no maintenance. For ongoing per-trade analysis (Apr 15+), query Alpaca MCP `get_orders` or the cloud `live_trade_log` table directly using `daily-trade-audit.md`.
