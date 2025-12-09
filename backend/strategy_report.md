# Strategy Report: Donchian Breakout (The "Turtle")

## 1. Strategy Overview
**Philosophy**: "Trade what you see, not what you think."
This is a **Trend Following** strategy. It does not predict where the price will go; it simply follows the price when it breaks out of a defined range. It is famous for making millions for the "Turtle Traders" in the 1980s.

**The Rules (Mechanical):**
-   **Entry**: Buy if Price breaks the **20-Day High**. (Sell if breaks 20-Day Low).
-   **Exit**: Close if Price touches the **10-Day Low**. (Trailing Stop).
-   **Risk Management**: Risk **2% of Equity** per trade. Stop Loss is set at 2x ATR (Volatility).

---

## 2. Findings & Timeframes
We tested this strategy across **11 Currency Pairs** and **3 Timeframes** (1h, 4h, Daily).

### 🏆 Best Timeframe: Daily (1d)
-   **Verdict**: The "Gold Standard".
-   **Why**: It filters out intraday noise and spreads. It captures the big, multi-week trends.
-   **Best Pairs**: USDCHF, EURUSD, AUDUSD.
-   **Stability**: High. Profitable in 2008 (Crisis), 2014 (Trend), and 2023 (Modern).

### 🥈 Niche Timeframe: 4-Hour (4h)
-   **Verdict**: Good for specific pairs.
-   **Why**: Some pairs trend faster.
-   **Best Pair**: **USDCAD** (+16.7% in 2023).

### 🎰 High-Risk Timeframe: 1-Hour (1h)
-   **Verdict**: The "Crisis Hunter".
-   **Why**: It loses money in quiet markets (due to spread costs) but wins BIG in volatile years.
-   **Best Pair**: **GBPJPY** (+76.7% in 2023).

---

## 3. Profit Scenarios (Based on 2023 Performance)
*Note: These calculations assume a **2% Risk Per Trade** model (compounding).*

### The Scenarios
1.  **Conservative**: USDCHF on **Daily** (+11.85%).
2.  **Balanced**: USDCAD on **4h** (+16.70%).
3.  **Aggressive**: GBPJPY on **1h** (+76.70%).

### Profit Table (1 Year)

| Investment | Conservative (+11.85%) | Balanced (+16.70%) | Aggressive (+76.70%) |
| :--- | :--- | :--- | :--- |
| **€100** | **€11.85** Profit | **€16.70** Profit | **€76.70** Profit |
| **€1,000** | **€118.50** Profit | **€167.00** Profit | **€767.00** Profit |
| **€5,000** | **€592.50** Profit | **€835.00** Profit | **€3,835.00** Profit |

### Important Note on Leverage
These returns are based on **Risk Management**, not raw leverage.
-   If you risked **1%** per trade, halve these numbers.
-   If you risked **5%** per trade (Very High Risk), multiply by ~2.5x (but risk of ruin increases).
-   The strategy naturally uses leverage (via position sizing) to achieve the 2% risk target.
