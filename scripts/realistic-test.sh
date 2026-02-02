#!/bin/bash

# realistic-test.sh
# Wrapper that adds realistic spread/delay based on asset type
# Usage: bash scripts/realistic-test.sh backtest --strategy StochRSI --symbol SPY --timeframe 1h --start 2024-01-01 --end 2024-12-31

set -e  # Exit on error

echo "🎯 Realistic Backtest Wrapper"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# Parse arguments to find symbol
SYMBOL=""
for i in "$@"; do
    if [[ "$prev_arg" == "--symbol" ]]; then
        SYMBOL="$i"
        break
    fi
    prev_arg="$i"
done

# Determine asset type and set appropriate spread
SPREAD="0.0001"  # Default for stocks
ASSET_TYPE="Stock"

if [[ "$SYMBOL" == *"BTC"* ]] || [[ "$SYMBOL" == *"ETH"* ]] || [[ "$SYMBOL" == *"USD"* ]]; then
    SPREAD="0.0002"
    ASSET_TYPE="Crypto"
elif [[ "$SYMBOL" == *"JPY"* ]] || [[ "$SYMBOL" == *"EUR"* ]] || [[ "$SYMBOL" == *"GBP"* ]]; then
    SPREAD="0.0002"
    ASSET_TYPE="Forex"
fi

echo "📋 Detected Asset Type: $ASSET_TYPE ($SYMBOL)"
echo "💰 Applying Realistic Settings:"
echo "   • Spread: $SPREAD ($(echo "$SPREAD * 10000" | bc)bps)"
echo "   • Execution Delay: 1 bar (next bar fill)"
echo "   • Data Source: Alpaca API"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# Build command with realistic defaults
REALISTIC_ARGS=(
    "$@"
    "--spread" "$SPREAD"
    "--delay" "1"
    "--source" "alpaca"
)

# Run via test-and-sync
bash scripts/test-and-sync.sh "${REALISTIC_ARGS[@]}"
