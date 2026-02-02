# Testing Standards

## Why Realistic Settings Matter

Backtests without spread/delay are **overly optimistic** and don't reflect real trading costs.

### Example Impact:
- **Without costs:** 96% return over 6 years
- **With costs:** 65% return over 6 years
- **Difference:** 31% (almost 1/3 of profits!)

---

## Recommended Settings

### Stocks (SPY, QQQ, IWM, AAPL, etc.)
```bash
--spread 0.0001   # 1 basis point (0.01%)
--delay 1         # Next bar execution
--source alpaca   # Consistent data source
```

**Why these values:**
- Spread: Liquid stocks have very tight spreads (~1bp)
- Delay: Realistic order execution takes 1 bar minimum
- Source: Alpaca provides consistent, reliable data

### Crypto (BTC/USD, ETH/USD)
```bash
--spread 0.0002   # 2 basis points (more volatile)
--delay 1         # Next bar execution
--source alpaca
```

**Why these values:**
- Spread: Crypto has slightly wider spreads
- Higher volatility = more slippage

### Forex (GBPJPY, EURUSD, USDJPY)
```bash
--spread 0.0002   # ~2 pips for major pairs
--delay 1         # Next bar execution
--source csv      # Often using CSV data for forex
```

**Why these values:**
- Spread: Major pairs have 2-3 pip spreads typically
- Forex data often comes from broker CSVs

---

## Quick Usage

### Option 1: Use realistic-test.sh (Automatic)
Automatically detects asset type and applies correct settings:

```bash
bash scripts/realistic-test.sh backtest \
  --strategy StochRSIMeanReversion \
  --symbol SPY \
  --timeframe 15m \
  --start 2020-01-01 \
  --end 2025-12-31
```

### Option 2: Manual (Explicit Control)
```bash
bash scripts/test-and-sync.sh backtest \
  --strategy StochRSIMeanReversion \
  --symbol SPY \
  --timeframe 15m \
  --start 2020-01-01 \
  --end 2025-12-31 \
  --spread 0.0001 \
  --delay 1 \
  --source alpaca
```

---

## What Each Setting Does

### Spread
**What it is:** The difference between buy price (ask) and sell price (bid)

**Example:**
- Market shows: $100.00
- You buy at: $100.01 (ask)
- You sell at: $99.99 (bid)
- Cost: $0.02 per round trip

**Impact:** With 1,000 trades/year, even 1bp spread = significant cost

### Execution Delay
**What it is:** Time between signal generation and order fill

**Options:**
- `--delay 0`: Instant fill at current bar close (UNREALISTIC)
- `--delay 1`: Fill at next bar open (REALISTIC)

**Why it matters:**
- Real orders take time to execute
- Price can move between signal and fill
- More conservative = more reliable backtest

### Data Source
**What it is:** Where historical price data comes from

**Options:**
- `alpaca`: Live API data (recommended for stocks/crypto)
- `csv`: Local files (recommended for forex)

**Why it matters:**
- Different sources may have different data
- Consistent source = comparable results
- Alpaca data is well-maintained and reliable

---

## Migration Plan

### Old Tests (No Spread/Delay)
Your existing tests (Iterations 1-10) likely used:
- Spread: 0 ❌
- Delay: 0 ❌
- Results: Overly optimistic

### New Tests (Realistic)
All future tests should use:
- Spread: 0.0001-0.0002 ✅
- Delay: 1 ✅
- Results: Realistic and tradeable

### Recommendation
Rerun your top strategies with realistic settings to get accurate performance estimates.

---

## Example: Before vs After

### IWM Strategy
**Old Test (v1 - No costs):**
- Return: 96.29%
- Win Rate: 54.2%
- Max DD: 11.79%

**New Test (v2 - With costs):**
- Return: 65.21%
- Win Rate: 56.7%
- Max DD: 12.52%

**Impact:** -31% return due to realistic costs

**Conclusion:** Still profitable, but more accurate!

---

## Quick Reference

```bash
# Stocks - Use this command:
bash scripts/realistic-test.sh backtest --strategy [NAME] --symbol [STOCK] --timeframe 15m --start 2020-01-01 --end 2025-12-31

# Crypto - Use this command:
bash scripts/realistic-test.sh backtest --strategy [NAME] --symbol BTC/USD --timeframe 1h --start 2024-01-01 --end 2024-12-31

# Matrix Research - Use this command:
bash scripts/realistic-test.sh matrix --strategy [NAME] --pairs SPY,QQQ,IWM --years 2020-2025 --timeframes 15m,1h
```

---

## Best Practices

1. ✅ Always use realistic settings for final validation
2. ✅ Test on out-of-sample data (forward testing)
3. ✅ Compare results across multiple years
4. ✅ Track reality gap (backtest vs live performance)
5. ❌ Don't optimize on same data you test on
6. ❌ Don't trust single-year results
7. ❌ Don't ignore trading costs

---

Last Updated: 2026-02-02
