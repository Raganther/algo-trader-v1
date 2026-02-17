#!/bin/bash
# EventSurprise paper bot — trades GLD on CPI surprise direction
# Deploy: pm2 start scripts/run_event_surprise_test.sh --name event-surprise-test

cd "$(dirname "$0")/.."

python3 -m backend.runner trade \
  --strategy EventSurprise \
  --symbol GLD \
  --timeframe 15m \
  --paper \
  --parameters '{
    "event_types": ["CPI m/m", "CPI y/y"],
    "hold_bars": 4,
    "stop_pct": 0.5,
    "entry_delay": 1,
    "risk_pct": 0.02,
    "trade_beats": false,
    "surprise_threshold": 0.5,
    "dedup_minutes": 5
  }'
