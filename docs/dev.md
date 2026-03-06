# Algo Trader V1 — Dev Notes

> Read on demand only. Not loaded on cold start.

## Ideas Backlog

Ideas are hypotheses to test. Once tested, results go into the relevant strategy file and the idea is removed.

### High Priority

**#20 Portfolio Manager — Dynamic Cross-Bot Position Sizing**
Run all 4 validated 15m strategies with a shared 20% risk budget. Each bot queries live account before sizing. True compounding — account grows, bets grow.
- Build `backend/broker/portfolio_manager.py`
- Update each bot's entry logic to call PortfolioManager before sizing
- Test on paper with all 4 bots simultaneously

### Medium Priority

**#16 EventSurprise on SLV and TLT**
CPI surprises should drive SLV same direction as GLD. TLT directly rate-sensitive.
Run EventSurprise (CPI-only) on SLV 15m. Run EventSurprise (CPI + FOMC) on TLT 15m.

**#17 StochRSI + EventSurprise Combination on GLD**
On CPI days, StochRSI might fire opposite to expected CPI move. Test blackout filter or confluence filter.

**#21 Price Action Charts + Regime Analysis Dashboard**
Pull 15m data for GLD/SLV/GDX/IAU. Build frontend charts with trade overlays. Classify regimes (trending/ranging). Analyse strategy performance per regime.

**#2 Regime-Adaptive Strategy Rotation**
Detect current market regime, deploy historically best strategy for that regime.

**#8 Multi-Timeframe Confirmation**
Combine 15m and 1h StochRSI signals on GLD. Only enter when both show oversold simultaneously.

### Lower Priority

**#1 Drawdown Duration Analysis** — Build distributions of drawdown episodes per strategy.
**#6 Position Sizing / Leverage Optimisation** — Kelly Criterion approach. GLD DD only 0.69% — room to size up.
**#10 IG Spread Betting Integration** — Phase 1-2 built. Remaining: integrate IGBroker with runner.py.
**#11 Time-of-Day Filtering** — Analyse which hours produce best win rate on 15m strategy.
**#12 Limit Order Entries** — Place limit slightly below signal bar close for better avg entry.
**#13 Volatility-Scaled Position Sizing** — Scale position size inversely to ATR.
**#18 Overnight Orchestrator on Cloud** — Run discovery engine on algotrader2026 at zero extra cost.
**#19 Full Cloud Migration** — Move frontend + backend to cloud. Needs e2-medium upgrade (~$27/mo).
**#3 Pairs Trading** — Trade spread between GLD/SLV or GLD/IAU.
**#4 Beta Hedging** — When long GLD, short proportional SLV/IAU to neutralise directional exposure.
**#5 Portfolio Diversification** — Find edges on assets uncorrelated with gold (TLT, XLE).
**#9 Cross-Asset Signal Confirmation** — Only enter when GLD + SLV + IAU all show oversold simultaneously.

## Completed Plans

### Filing System Migration — 2026-03-06
Migrated from old `.claude/` structure to new five-file system.
- New `CLAUDE.md` at project root (auto-loaded)
- New `scripts/git-save.sh` (includes push to origin)
- New `memory/MEMORY.md` (auto-generated, last 10 saves)
- New `memory/plan.md` (active plan)
- New `docs/dev.md` (this file — ideas + archive)
- Old files preserved in `.claude/` for reference
