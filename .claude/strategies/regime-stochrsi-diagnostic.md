Status: current | Epistemic: confirmed | Last verified: 2026-04-23

# StochRSI Enhanced Performance by Daily Regime

## Knowledge

Window requested: `2020-01-01` to `2025-12-31`. Source: `backend/research.db` intraday `price_data` plus daily `price_data_daily` regimes.

Regime tag uses the previous completed daily bar at the trade entry timestamp, so the diagnostic does not peek at the current day's close/high/low.

Validated params: StochRSI Mean Reversion, 15m, spread `0.0003`, delay `0`, `dynamic_adx:false`, OB/OS `80/15`, ADX `20`, `sl_atr:2.0`, trailing after 10 bars at `2.0 ATR`, `min_hold_bars:10`, skip Monday.

Cells with fewer than 10 trades are flagged as directional-only, not significant.

## Data Coverage

| Symbol | Intraday coverage used |
|--------|------------------------|
| GLD | 2020-07-27 to 2025-12-31 (34,910 bars) |
| IAU | 2020-07-27 to 2025-12-31 (30,753 bars) |
| SLV | 2020-07-27 to 2025-12-31 (35,481 bars) |
| GDX | 2020-07-27 to 2025-12-31 (36,267 bars) |

Closed trades analysed: **1,959**.

## Diagnostic Read

- Metals aggregate shows the clearest Sharpe gradient in `RANGING` for both directions: long `6.55`, short `6.67`.
- `TRENDING_UP` remains profitable, but weaker than `RANGING` on aggregate Sharpe: long `3.27`, short `3.36`.
- `HIGH_VOL` is not uniformly bad, but long-side quality is uneven: SLV long Sharpe `0.26`, GDX long `0.72`, while GLD long is below the significance threshold at 8 trades.
- `TRENDING_DOWN` is not a clean skip signal in this window. Long trades remain profitable on aggregate, and the short side is weaker but not broken.

Decision implication: **partial gradient**. Regime appears useful as a high-conviction sizing/filter input, especially favouring `RANGING` and being cautious with `HIGH_VOL` long exposure, but this diagnostic does not justify a broad live regime-sizing system by itself.

## Per Symbol

### GLD

| Regime | Direction | Trades | Win rate | Sharpe | Avg P&L | Max DD | Note |
|--------|-----------|--------|----------|--------|---------|--------|------|
| RANGING | long | 125 | 44.8% | 3.26 | $9.87 | $70.59 |  |
| RANGING | short | 150 | 44.7% | 3.43 | $5.72 | $65.16 |  |
| TRENDING_UP | long | 59 | 35.6% | 1.14 | $3.53 | $53.83 |  |
| TRENDING_UP | short | 60 | 38.3% | 2.26 | $9.70 | $39.10 |  |
| TRENDING_DOWN | long | 21 | 47.6% | 1.68 | $7.90 | $21.53 |  |
| TRENDING_DOWN | short | 20 | 35.0% | -0.14 | $-0.29 | $45.40 |  |
| HIGH_VOL | long | 8 | 75.0% | 2.05 | $40.73 | $6.85 | directional only |
| HIGH_VOL | short | 22 | 50.0% | 2.00 | $17.44 | $34.03 |  |

### IAU

| Regime | Direction | Trades | Win rate | Sharpe | Avg P&L | Max DD | Note |
|--------|-----------|--------|----------|--------|---------|--------|------|
| RANGING | long | 114 | 36.8% | 2.46 | $6.87 | $112.08 |  |
| RANGING | short | 138 | 44.9% | 2.65 | $4.25 | $53.21 |  |
| TRENDING_UP | long | 55 | 40.0% | 1.73 | $8.91 | $56.23 |  |
| TRENDING_UP | short | 76 | 28.9% | 1.09 | $2.51 | $104.12 |  |
| TRENDING_DOWN | long | 20 | 35.0% | 1.43 | $11.70 | $39.14 |  |
| TRENDING_DOWN | short | 15 | 53.3% | 1.27 | $7.38 | $32.61 |  |
| HIGH_VOL | long | 21 | 38.1% | 1.26 | $17.53 | $42.17 |  |
| HIGH_VOL | short | 28 | 50.0% | 2.27 | $16.68 | $23.61 |  |

### SLV

| Regime | Direction | Trades | Win rate | Sharpe | Avg P&L | Max DD | Note |
|--------|-----------|--------|----------|--------|---------|--------|------|
| RANGING | long | 143 | 46.2% | 4.49 | $25.43 | $98.50 |  |
| RANGING | short | 153 | 45.1% | 3.68 | $16.14 | $116.47 |  |
| TRENDING_UP | long | 52 | 48.1% | 2.45 | $20.19 | $142.62 |  |
| TRENDING_UP | short | 67 | 46.3% | 2.51 | $16.96 | $157.00 |  |
| TRENDING_DOWN | long | 17 | 58.8% | 2.61 | $58.75 | $30.36 |  |
| TRENDING_DOWN | short | 22 | 54.5% | 1.49 | $8.10 | $47.48 |  |
| HIGH_VOL | long | 11 | 27.3% | 0.26 | $5.45 | $157.06 |  |
| HIGH_VOL | short | 20 | 40.0% | 0.76 | $10.82 | $140.60 |  |

### GDX

| Regime | Direction | Trades | Win rate | Sharpe | Avg P&L | Max DD | Note |
|--------|-----------|--------|----------|--------|---------|--------|------|
| RANGING | long | 198 | 48.0% | 3.72 | $23.28 | $226.61 |  |
| RANGING | short | 204 | 46.1% | 4.50 | $21.98 | $264.11 |  |
| TRENDING_UP | long | 42 | 50.0% | 1.94 | $42.55 | $119.50 |  |
| TRENDING_UP | short | 43 | 39.5% | 0.78 | $6.16 | $259.77 |  |
| TRENDING_DOWN | long | 14 | 50.0% | 1.36 | $19.43 | $32.79 |  |
| TRENDING_DOWN | short | 14 | 50.0% | 1.11 | $20.66 | $54.09 |  |
| HIGH_VOL | long | 15 | 40.0% | 0.72 | $9.91 | $124.99 |  |
| HIGH_VOL | short | 12 | 66.7% | 2.30 | $84.43 | $83.88 |  |

## Metals Aggregate

### METALS

| Regime | Direction | Trades | Win rate | Sharpe | Avg P&L | Max DD | Note |
|--------|-----------|--------|----------|--------|---------|--------|------|
| RANGING | long | 580 | 44.7% | 6.55 | $17.69 | $372.55 |  |
| RANGING | short | 645 | 45.3% | 6.67 | $13.02 | $249.24 |  |
| TRENDING_UP | long | 208 | 42.8% | 3.27 | $17.00 | $142.64 |  |
| TRENDING_UP | short | 246 | 37.8% | 3.36 | $8.84 | $329.27 |  |
| TRENDING_DOWN | long | 72 | 47.2% | 3.39 | $23.20 | $55.88 |  |
| TRENDING_DOWN | short | 71 | 47.9% | 1.90 | $8.06 | $85.30 |  |
| HIGH_VOL | long | 55 | 41.8% | 2.01 | $16.41 | $167.96 |  |
| HIGH_VOL | short | 82 | 50.0% | 3.35 | $25.37 | $142.73 |  |
