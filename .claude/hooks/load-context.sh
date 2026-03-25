#!/bin/bash
# SessionStart hook - loads context automatically when Claude Code starts

echo "=== ALGO TRADER SESSION CONTEXT ==="
echo ""

# Show recent commits
echo "📋 Recent changes (last 5 commits):"
git log --oneline -5 2>/dev/null || echo "  (not in git repo)"
echo ""

# Show current branch and status
echo "🌿 Git status:"
BRANCH=$(git branch --show-current 2>/dev/null)
CHANGES=$(git status --porcelain 2>/dev/null | wc -l | tr -d ' ')
echo "  Branch: $BRANCH"
echo "  Uncommitted changes: $CHANGES files"
echo ""

# Remind about key files
echo "📂 Key context files (read in this order):"
echo "  → .claude/memory/gitlog.md (recent git saves)"
echo "  → .claude/memory/plan.md (active steps)"
echo "  → .claude/memory/observations.md (running insights)"
echo ""

# Check if we can reach cloud (quick timeout)
echo "☁️  Cloud status:"
echo "  Server: algotrader2026 (europe-west2-a)"
echo "  Check bots: gcloud compute ssh algotrader2026 --zone=europe-west2-a --command=\"pm2 status\""
echo ""

echo "==================================="
exit 0
