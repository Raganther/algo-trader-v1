# Research Insights

This file serves as the "Long Term Semantic Memory" for the agent.
It contains curated insights, proven strategies, and failed experiments derived from the "Episodic Memory" (Git History).

## Proven Strategies
<!-- Strategies that have passed verification -->

- Result: +71.0% Total Return, 5.94% Max Drawdown.
- Tested DonchianTrend on SPY (1h). Result: Success (See database for details).
- Tested StochRSIMeanReversion on SPY (5m). Result: +32.95% Total Return (Baseline).
- Tested StochRSIMeanReversion on SPY (5m) with params {'rsi_period': 21, 'stoch_period': 21}. Result: +2.95% Total Return (Too Slow).
- Tested StochRSIMeanReversion on SPY (5m) with params {'rsi_period': 7, 'stoch_period': 7}. Result: +88.5% Total Return (Winner). Note: Underperformed in 2024 (5.3%) but crushed 2022 (24.7%).
- **OPTIMIZED**: StochRSIMeanReversion on SPY (5m) with `adx_threshold=20` (Stricter Range Filter).
    - 2016: +27.8% (vs +5%)
    - 2018: +23.5% (vs -3%)
    - 2020: +27.1% (vs +14.2%)
    - 2021: +6.8% (vs +14.3%) -> Trade-off: Reduced performance in smooth bull markets.
    - 2022: +35.3% (vs +25%)
    - 2024: +10.9% (vs +5%)
    - Conclusion: Stricter ADX filter avoids "fake" mean reversion in medium trends. Drastically improves volatile years, slightly dampens smooth bull years.
- **ADAPTIVE**: StochRSIMeanReversion with Regime Switching (ATR% > 0.12% -> ADX 20, else ADX 30).
    - 2018: +11.6% (Profitable, but less than Static 20's +23.5%)
    - 2021: +11.1% (Recovered from Static 20's +6.8%, close to Original +14.3%)
    - 2022: +20.6% (Profitable, but less than Static 20's +35.3%)
    - Conclusion: The "Goldilocks" solution. Captures upside in Bull Markets (2021) while staying safe in Bear Markets (2018/2022).
- **STRESS TEST (Optimized)**: Added $0.02 Spread (Slippage/Friction).
    - 2022: +6.3% (Collapsed from +35.3%)
    - 2016: -11.0% (Collapsed from +27.8%)
    - **CRITICAL FAILURE**: The strategy trades too frequently (~3500 trades/year). Friction destroys the edge.
    - **Pivot Required**: We must reduce trade frequency or increase average trade duration.
- Tested HybridRegime on GBPJPY (1h) [2002-2024]. Result: Mixed. 2004 (+53%), 2007 (+34%), but 2002 (-24%). Long-term viable but needs optimization.

## Failed Experiments
<!-- Strategies that failed and why, to avoid repeating mistakes -->

- Result: FAILED (-26.06% Return over 5 Years).
- TimeOnly: +60% Return (Failed: Opening Drive volatility is essential)

- Tested DonchianTrend on AAPL (1h) with params {'donchian_period': 50}. Result: -3.54% Total Return, 31.96% Max Drawdown.
- Tested DonchianTrend on SPY (1h) with params {'donchian_period': 50}. Result: -4.8% Total Return, 13.55% Max Drawdown.
- Tested GammaScalping on SPY (5m) with params {'vol_threshold': 0.015}. Result: -1.43% Total Return, 1.61% Max Drawdown.
- Tested GammaScalping on SPY (5m) with params {'rsi_period': 7, 'stoch_period': 7}. Result: -1.0% Total Return, 1.72% Max Drawdown.
- Tested HybridRegime on GBPJPY=X (1h) with params {'adx_threshold': 30}. Result: 0.0% Total Return, 0.0% Max Drawdown.
- Tested HybridRegime on GBPJPY=X (1h) with params {'adx_threshold': 30}. Result: -0.31% Total Return, 0.34% Max Drawdown.
- Tested HybridRegime on GBPJPY=X (1h) with params {'adx_threshold': 20}. Result: -0.38% Total Return, 0.41% Max Drawdown.
- Tested HybridRegime on GBPJPY=X (1h) with params {'rsi_period': 9, 'stoch_period': 9}. Result: -0.34% Total Return, 0.35% Max Drawdown.
## Market Mechanics
<!-- General observations about market behavior (e.g. Volatility, Timeframes) -->

## Invalidated Hypotheses (Corrections)
<!-- Insights that were proven wrong by later data or bug fixes. Move incorrect insights here. -->


## New Insights (Auto-Curated)
- Crucial Insight: Fundamental conflict between ADX < 30 (Range) and TICK > 1.5 (Momentum).










































## New Insights (Auto-Curated)



































- Tested DonchianTrend on EURUSD=X (1h) with params {'donchian_period': 50}. Result: Metrics not found in output.




- Tested GammaScalping on SPY (5m) with params None. Result: Error: Traceback (most recent call last):.



- Tested DonchianTrend on GBPUSD=X (1h) with params None. Result: Error: No data found from Alpaca..










- Tested HybridRegime on GBPJPY=X (1h) with params None. Result: Error: No data found from Alpaca..


- Tested HybridRegime on GBPJPY (1h) with params {'adx_threshold': 30}. Result: Error: No data found from Alpaca..


- Tested HybridRegime on GBPJPY (1h) with params {'adx_threshold': 30}. Result: Error: Traceback (most recent call last):.

















## New Insights (Auto-Curated)
- Note: GammaScalping bug identified (pending fix).
- Tested HybridRegime on GBPJPY (1h) [2020-2024]. Result: Negative (-0.09% to -0.38%). Higher ADX threshold (40) reduced losses, indicating Mean Reversion preference. Sector TICK optimization blocked by missing data.







