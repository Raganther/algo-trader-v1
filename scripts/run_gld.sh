#!/bin/bash
cd /home/alistairelliman/algo-trader-v1
python3 -m backend.runner trade \
  --strategy StochRSIMeanReversion \
  --symbol GLD \
  --timeframe 1h \
  --paper \
  --parameters '{"rsi_period":21,"stoch_period":7,"overbought":80,"oversold":15,"adx_threshold":25,"skip_adx_filter":false,"sl_atr":3.0}'
