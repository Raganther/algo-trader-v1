# Phase 3 — Composable Strategy Results

> **Status:** Complete. 3 validated combos found, not yet deployed.
> **Code:** `backend/optimizer/composable_strategy.py`, `backend/optimizer/building_blocks.py`
> **Run script:** `backend/optimizer/run_composable.py`

## Summary

458 indicator combinations tested on GLD 1h. 10 top candidates by Sharpe sent to full validation. 7 rejected (overfit noise — high Sharpe but low trade count). 3 passed.

## Validated Combos

| Combo | Test Return | WF Pass | Multi-Asset | Trades |
|-------|-----------|---------|-------------|--------|
| RSI extreme + Opposite zone | +0.3% | 75% | 100% (3/3) | 263 |
| MACD cross + Donchian exit + SMA uptrend | +10.9% | 75% | 67% (2/3) | 176 |
| RSI extreme + Trailing ATR 3x | +4.9% | 75% | 67% (2/3) | 252 |

## Key Lesson

High-Sharpe / low-trade combos are almost always overfit. The 7 rejected candidates had impressive in-sample Sharpe ratios but fewer than 50 trades — they were fitting to noise. The 3 that passed all had 150+ trades and moderate (not extreme) Sharpe values.

## Available Building Blocks

Entry signals: RSI extreme, MACD cross, Bollinger touch, Donchian breakout, StochRSI cross
Exit signals: Opposite zone, Donchian exit, Trailing ATR, Time-based
Filters: SMA uptrend/downtrend, ADX trending, CHOP ranging, Volume above average

All composable via `building_blocks.py` — mix and match entry + exit + filter.

---

*Last updated: 2026-02-13*
