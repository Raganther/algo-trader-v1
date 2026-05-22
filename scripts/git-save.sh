#!/bin/bash
# git-save.sh — commit, sync with remote, regenerate memory/gitlog.md, deploy to GCP
# Usage: ./scripts/git-save.sh "commit message"

set -e

if [ -z "$1" ]; then
  echo "Usage: ./scripts/git-save.sh \"commit message\""
  exit 1
fi

# Always operate from the project root, regardless of where the script was called from
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

# Check if a remote is configured
HAS_REMOTE=false
if git remote | grep -q .; then
  HAS_REMOTE=true
fi

# 1. Context-aware checklist (non-blocking — shown before commit for review)
CHANGED=$(git diff --name-only HEAD 2>/dev/null; git diff --cached --name-only 2>/dev/null)
WARNINGS=""

echo "$CHANGED" | grep -q "backend/strategies/trend_framework.py" && \
  WARNINGS="${WARNINGS}\n  [strategy] Strategy logic changed — update relevant trend-framework-*.md domain files."

echo "$CHANGED" | grep -q "backend/engine/live_broker.py" && \
  WARNINGS="${WARNINGS}\n  [live_broker] Live broker changed — update CLAUDE.md Current Status and MEMORY.md if a new bug was fixed."

echo "$CHANGED" | grep -q "backend/engine/alpaca_trader.py" && \
  WARNINGS="${WARNINGS}\n  [alpaca_trader] Alpaca API wrapper changed — update alpaca-mcp.md and CLAUDE.md if behaviour changed."

echo "$CHANGED" | grep -qE "scripts/run_.*\.sh" && \
  WARNINGS="${WARNINGS}\n  [bot scripts] Bot scripts changed — is CLAUDE.md Run Commands bot table still accurate?"

echo "$CHANGED" | grep -q "CLAUDE.md" && \
  WARNINGS="${WARNINGS}\n  [CLAUDE.md] CLAUDE.md changed — does your commit message explain why?"

echo "$CHANGED" | grep -q "research-roadmap.md" && \
  WARNINGS="${WARNINGS}\n  [roadmap] Roadmap changed — have any newly settled items been promoted to the relevant domain file?"

echo "$CHANGED" | grep -qE "trend-framework-(gld|iau|slv|gdx|xle)\.md" && \
  WARNINGS="${WARNINGS}\n  [strategy domain] Strategy domain file changed — is CLAUDE.md Validated Edges table still accurate?"

echo "$CHANGED" | grep -q "backend/engine/backtester.py" && \
  WARNINGS="${WARNINGS}\n  [backtester] Backtester changed — update calibration-notes.md if calibration methodology or results are affected."

if [ -n "$WARNINGS" ]; then
  echo ""
  echo "── Domain update checklist ─────────────────────────────────"
  printf "%b\n" "$WARNINGS"
  echo "─────────────────────────────────────────────────────────────"
  echo ""
fi

# 2. Stage all changes and commit
git add -A
git commit -m "$1" ${2:+-m "$2"}

# 3. Pull from remote to rebase our commit on top of any remote changes
if [ "$HAS_REMOTE" = true ]; then
  echo "↓ Pulling from remote..."
  if ! git pull --rebase; then
    echo "⚠ Pull failed — check for conflicts ('git rebase --abort' to cancel)"
    echo "  Changes committed locally. Skipping push."
    HAS_REMOTE=false
  fi
fi

# 4. Regenerate .claude/memory/gitlog.md from last 15 git log entries
MEMORY_FILE=".claude/memory/gitlog.md"

cat > "$MEMORY_FILE" << 'HEADER'
# Recent Git History

> Auto-generated on git save. Do not edit manually.

HEADER

git log -15 --pretty=format:"----%n**%as** — %s%n%b" --stat >> "$MEMORY_FILE"

echo "" >> "$MEMORY_FILE"

# 5. Stage the updated memory file and amend
git add "$MEMORY_FILE"
git commit --amend --no-edit

echo ""
echo "✓ Committed: $1"
echo "✓ .claude/memory/gitlog.md updated with last 15 saves (full detail)"

# 6. Push to remote
if [ "$HAS_REMOTE" = true ]; then
  echo ""
  echo "↑ Pushing to remote..."
  if ! git push; then
    echo "⚠ Push failed — changes saved locally, not synced to remote"
  else
    echo "✓ Pushed to origin main"
  fi
fi

# 7. Deploy to GCP — pull latest on cloud server
GCP_REPO="~/algo-trader-v1"
if [ "$HAS_REMOTE" = true ] && command -v gcloud &>/dev/null; then
  echo ""
  echo "↓ Deploying to GCP (algotrader-us)..."
  if gcloud compute ssh "algotrader-us" --zone "us-east1-b" --command "git -C ${GCP_REPO} pull" 2>/dev/null; then
    echo "✓ GCP algotrader-us up to date"
  else
    echo "⚠ GCP deploy failed — run manually: gcloud compute ssh algotrader-us --zone us-east1-b --command 'git -C ${GCP_REPO} pull'"
  fi
fi
