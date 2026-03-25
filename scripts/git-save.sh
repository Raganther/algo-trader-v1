#!/bin/bash
# git-save.sh — commit, regenerate .claude/memory/gitlog.md, push to origin
# Usage: ./scripts/git-save.sh "commit message"

set -e

if [ -z "$1" ]; then
  echo "Usage: ./scripts/git-save.sh \"commit message\""
  exit 1
fi

# 1. Stage all changes and commit
git add -A
git commit -m "$1" ${2:+-m "$2"}

# 2. Regenerate .claude/memory/gitlog.md from last 8 git log entries
MEMORY_FILE=".claude/memory/gitlog.md"

cat > "$MEMORY_FILE" << 'HEADER'
# Recent Git History

> Auto-generated on git save. Do not edit manually.

HEADER

git log -8 --pretty=format:"----%n**%as** — %s%n%b" --stat >> "$MEMORY_FILE"

echo "" >> "$MEMORY_FILE"

# 3. Stage and amend
git add "$MEMORY_FILE"
git commit --amend --no-edit

# 4. Push to origin
git push origin main

echo ""
echo "✓ Committed: $1"
echo "✓ .claude/memory/gitlog.md updated with last 8 saves (full detail)"
echo "✓ Pushed to origin main"
