#!/bin/bash

PAIRS=("GBPJPY=X" "EURJPY=X" "USDJPY=X")
YEARS=$(seq 2000 2025)

for pair in "${PAIRS[@]}"; do
    for year in $YEARS; do
        echo "Running $pair for $year..."
        python3 -m backend.runner backtest --strategy StochRSIMeanReversion --symbol "$pair" --timeframe 1h --start "$year-01-01" --end "$year-12-31" --spread 0.02 --delay 1
    done
done
