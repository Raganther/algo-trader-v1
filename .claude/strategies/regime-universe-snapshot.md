Status: current | Epistemic: snapshot confirmed; rotation-application FALSIFIED Apr 30 PM | Last verified: 2026-04-30

# Regime Universe Snapshot

Daily-bar regime classification across a ~30-asset ETF universe. **Apr 30 PM update:** the original Apr 29 strategic direction this fed into (regime-aware asset rotation) was tested and falsified for the deployed strategy class — see `.claude/strategies/portfolio-runner-rotation-v1.md`. The snapshot still has value as **observational context** (which assets are in which regime today, so live performance can be interpreted in regime terms) and as input to **future strategy-class composition** experiments. It is no longer "the first step toward asset rotation."

- Universe size: 33 (target ~30)
- Classifier: `backend/indicators/regime.py:classify_regime` (defaults: ADX 14 / SMA 200 / ATR 14, ADX threshold 25, ATR vol multiplier 1.5x)
- Persistence window: last 60 bars
- Source: `price_data_daily` (yfinance, auto-fetched if stale > 5 days)

## Today's regime distribution

| Regime | Count | % of universe |
|---|---:|---:|
| RANGING | 26 | 78.8% |
| TRENDING_UP | 7 | 21.2% |
| TRENDING_DOWN | 0 | 0.0% |
| HIGH_VOL | 0 | 0.0% |
| **Favourable (TRENDING)** | **7** | **21.2%** |

**Verdict: BORDERLINE** — 7/33 favourable. Outside the 8–15 selective band but not extreme. Repeat the scan over a week to characterise.

## Per-asset detail

| Symbol | Regime | Days in regime | 60d persistence | Last bar | Bars |
|---|---|---:|---:|---|---:|
| ARKK | RANGING | 14 | 50% | 2026-04-28 | 2888 |
| DIA | RANGING | 11 | 65% | 2026-04-28 | 4104 |
| EEM | RANGING | 26 | 43% | 2026-04-28 | 4104 |
| EFA | RANGING | 11 | 18% | 2026-04-28 | 4104 |
| EWZ | RANGING | 30 | 50% | 2026-04-28 | 4104 |
| GBTC | RANGING | 33 | 62% | 2026-04-28 | 2758 |
| GDX | RANGING | 10 | 50% | 2026-04-28 | 5530 |
| GLD | RANGING | 10 | 70% | 2026-04-28 | 5908 |
| IAU | RANGING | 13 | 72% | 2026-04-28 | 5860 |
| IBB | RANGING | 84 | 100% | 2026-04-28 | 4104 |
| KRE | RANGING | 18 | 63% | 2026-04-28 | 4104 |
| SLV | RANGING | 14 | 82% | 2026-04-28 | 5546 |
| SPY | RANGING | 1 | 48% | 2026-04-28 | 4104 |
| TLT | RANGING | 17 | 87% | 2026-04-28 | 4104 |
| UUP | RANGING | 20 | 70% | 2026-04-28 | 4104 |
| VXX | RANGING | 7 | 35% | 2026-04-28 | 2075 |
| XBI | RANGING | 81 | 100% | 2026-04-28 | 4104 |
| XLB | RANGING | 17 | 28% | 2026-04-28 | 4104 |
| XLE | RANGING | 4 | 7% | 2026-04-28 | 4104 |
| XLF | RANGING | 13 | 35% | 2026-04-28 | 4104 |
| XLI | RANGING | 10 | 17% | 2026-04-28 | 4104 |
| XLP | RANGING | 8 | 13% | 2026-04-28 | 4104 |
| XLU | RANGING | 33 | 75% | 2026-04-28 | 4104 |
| XLV | RANGING | 12 | 75% | 2026-04-28 | 4104 |
| XLY | RANGING | 1 | 35% | 2026-04-28 | 4104 |
| XOP | RANGING | 6 | 10% | 2026-04-28 | 4104 |
| DBA | TRENDING_UP | 37 | 62% | 2026-04-28 | 4104 |
| ITA | TRENDING_UP | 5 | 47% | 2026-04-28 | 4104 |
| IWM | TRENDING_UP | 6 | 42% | 2026-04-28 | 4104 |
| OIH | TRENDING_UP | 2 | 73% | 2026-04-28 | 4104 |
| QQQ | TRENDING_UP | 9 | 22% | 2026-04-28 | 4104 |
| SMH | TRENDING_UP | 5 | 15% | 2026-04-28 | 4104 |
| XLK | TRENDING_UP | 7 | 17% | 2026-04-28 | 4104 |

## Decision rule

Rotation has selection power if 8–15 of the universe are in a favourable (TRENDING_UP or sustained TRENDING_DOWN) regime on a typical day. Persistent <=3 means the universe is too narrow or the regime detector is too strict; persistent >=25 means rotation just always picks 'everything', i.e. no selection lift. Single-day reading is noisy — re-run weekly and compute the rolling distribution before making any architectural call.

## Fetch log

```
GLD: fetched +13 → 5908 bars (last 2026-04-28)
IAU: fetched +13 → 5860 bars (last 2026-04-28)
SLV: fetched +13 → 5546 bars (last 2026-04-28)
GDX: fetched +13 → 5530 bars (last 2026-04-28)
XLE: fetched +4104 → 4104 bars (last 2026-04-28)
OIH: fetched +4104 → 4104 bars (last 2026-04-28)
XOP: fetched +4104 → 4104 bars (last 2026-04-28)
XLF: fetched +4104 → 4104 bars (last 2026-04-28)
XLK: fetched +4104 → 4104 bars (last 2026-04-28)
XLI: fetched +4104 → 4104 bars (last 2026-04-28)
XLV: fetched +4104 → 4104 bars (last 2026-04-28)
XLY: fetched +4104 → 4104 bars (last 2026-04-28)
XLP: fetched +4104 → 4104 bars (last 2026-04-28)
XLU: fetched +4104 → 4104 bars (last 2026-04-28)
XLB: fetched +4104 → 4104 bars (last 2026-04-28)
XBI: fetched +4104 → 4104 bars (last 2026-04-28)
IBB: fetched +4104 → 4104 bars (last 2026-04-28)
SPY: fetched +4104 → 4104 bars (last 2026-04-28)
QQQ: fetched +4104 → 4104 bars (last 2026-04-28)
IWM: fetched +4104 → 4104 bars (last 2026-04-28)
DIA: fetched +4104 → 4104 bars (last 2026-04-28)
KRE: fetched +4104 → 4104 bars (last 2026-04-28)
SMH: fetched +4104 → 4104 bars (last 2026-04-28)
ITA: fetched +4104 → 4104 bars (last 2026-04-28)
ARKK: fetched +2888 → 2888 bars (last 2026-04-28)
EFA: fetched +4104 → 4104 bars (last 2026-04-28)
EEM: fetched +4104 → 4104 bars (last 2026-04-28)
EWZ: fetched +4104 → 4104 bars (last 2026-04-28)
GBTC: fetched +2758 → 2758 bars (last 2026-04-28)
TLT: fetched +4104 → 4104 bars (last 2026-04-28)
UUP: fetched +4104 → 4104 bars (last 2026-04-28)
VXX: fetched +2075 → 2075 bars (last 2026-04-28)
DBA: fetched +4104 → 4104 bars (last 2026-04-28)
```

