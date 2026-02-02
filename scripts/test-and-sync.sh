#!/bin/bash

# test-and-sync.sh
# Wrapper script that runs backtests and automatically updates memory files
# Usage: bash scripts/test-and-sync.sh [runner command] [runner arguments]
# Example: bash scripts/test-and-sync.sh backtest --strategy StochRSI --symbol SPY --timeframe 1h --start 2024-01-01 --end 2024-12-31

set -e  # Exit on error

echo "🚀 Starting test-and-sync workflow..."
echo ""

# Store the command for logging
COMMAND="$*"

# Run the test via runner.py
echo "📊 Step 1/3: Running backtest..."
echo "Command: python3 -m backend.runner $COMMAND"
echo "─────────────────────────────────────────────────────────"
python3 -m backend.runner "$@"

# Check if the test succeeded
if [ $? -eq 0 ]; then
    echo ""
    echo "✅ Backtest completed successfully!"
    echo ""

    # Update research insights
    echo "📝 Step 2/3: Updating research insights..."
    echo "─────────────────────────────────────────────────────────"
    python3 -m backend.analyze_results --write

    if [ $? -eq 0 ]; then
        echo ""
        echo "✅ Research insights updated!"
        echo ""

        # Update git history
        echo "📚 Step 3/3: Updating git history..."
        echo "─────────────────────────────────────────────────────────"
        bash .agent/scripts/update_memory.sh

        if [ $? -eq 0 ]; then
            echo ""
            echo "✅ Git history updated!"
            echo ""
            echo "═══════════════════════════════════════════════════════"
            echo "🎉 All memory files synchronized!"
            echo "═══════════════════════════════════════════════════════"
            echo ""
            echo "Updated files:"
            echo "  • backend/research.db (database)"
            echo "  • .agent/memory/research_insights.md"
            echo "  • .agent/memory/recent_history.md"
            echo ""
            echo "💡 Tip: Run 'git status' to see changes, then commit with:"
            echo "   git add ."
            echo "   git commit -m \"test: [describe your test]\""
        else
            echo "⚠️  Warning: Git history update failed (non-critical)"
        fi
    else
        echo "❌ Error: Failed to update research insights"
        exit 1
    fi
else
    echo ""
    echo "❌ Error: Backtest failed"
    exit 1
fi
