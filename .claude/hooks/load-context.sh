#!/bin/bash
# SessionStart hook — surfaces dynamic context on session open

PROJECT_DIR="${CLAUDE_PROJECT_DIR:-$(git rev-parse --show-toplevel 2>/dev/null)}"

echo "=== ALGO TRADER SESSION CONTEXT ==="
echo "Branch : $(git -C "$PROJECT_DIR" branch --show-current 2>/dev/null)"
echo "Commit : $(git -C "$PROJECT_DIR" log -1 --pretty='%h %s (%ar)' 2>/dev/null)"
echo ""

# UTC + IST time anchor
UTC_TIME=$(date -u "+%H:%M UTC")
IST_OFFSET=1  # UTC+1 (IST, after last Sunday of March)
IST_HOUR=$(date -u "+%H")
IST_MIN=$(date -u "+%M")
IST_DISPLAY=$(date -u -v+${IST_OFFSET}H "+%H:%M IST" 2>/dev/null || date -u -d "+${IST_OFFSET} hours" "+%H:%M IST" 2>/dev/null || echo "IST unavailable")
echo "Time   : $UTC_TIME  ($IST_DISPLAY)"
echo ""

# Remind about key files
echo "Cold start — read in order:"
echo "  1. .claude/memory/gitlog.md"
echo "  2. .claude/strategies/research-roadmap.md"
echo ""

# Show recent commits
echo "📋 Recent changes (last 5 commits):"
git -C "$PROJECT_DIR" log --oneline -5 2>/dev/null || echo "  (not in git repo)"
echo ""

# Cloud status
echo "☁️  Cloud status:"
echo "  Server: algotrader-us (us-east1-b)"
echo "  Check bots: gcloud compute ssh algotrader-us --zone=us-east1-b --command=\"pm2 status\""
echo ""

echo "==================================="
exit 0
