#!/bin/bash
cd /home/alistairelliman/algo-trader-v1
python3 -m backend.runner trade \
  --strategy StochRSIMeanReversion \
  --symbol GLD \
  --timeframe 15m \
  --paper \
  --parameters '{"rsi_period":7,"stoch_period":14,"overbought":80,"oversold":15,"adx_threshold":20,"skip_adx_filter":false,"sl_atr":2.0}'
