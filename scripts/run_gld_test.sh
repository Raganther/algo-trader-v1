#!/bin/bash
# TEMPORARY — aggressive params to test trailing stop / min hold / skip Monday piping
# Delete this bot once mechanics are verified
cd /home/alistairelliman/algo-trader-v1
python3 -m backend.runner trade \
  --strategy StochRSIMeanReversion \
  --symbol GLD \
  --timeframe 15m \
  --paper \
  --parameters '{"rsi_period":7,"stoch_period":14,"overbought":60,"oversold":40,"adx_threshold":50,"skip_adx_filter":false,"sl_atr":2.0,"dynamic_adx":false,"trailing_stop":true,"trail_after_bars":3,"trail_atr":2.0,"min_hold_bars":3,"skip_days":[0]}'
