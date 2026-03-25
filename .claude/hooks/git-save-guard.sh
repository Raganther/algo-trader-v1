#!/bin/bash
# PreToolUse hook — blocks git-save.sh if memory files haven't been updated
# or if new domain files exist in .claude/ that aren't listed in CLAUDE.md

INPUT=$(cat)

COMMAND=$(echo "$INPUT" | python3 -c "import sys,json; d=json.load(sys.stdin); print(d.get('tool_input',{}).get('command',''))" 2>/dev/null)

# Only act on git-save.sh calls
if ! echo "$COMMAND" | grep -q "git-save.sh"; then
  exit 0
fi

# Check 1: memory files must have been modified since last commit
CHANGED=$(git -C "$CLAUDE_PROJECT_DIR" diff HEAD --name-only -- memory/plan.md memory/observations.md 2>/dev/null)

if [ -z "$CHANGED" ]; then
  echo "⚠️  BLOCKED: memory/plan.md and memory/observations.md are unchanged since last commit."
  echo "   Update these files before running git save."
  exit 1
fi

# Check 2: any new domain files in .claude/ must be listed in CLAUDE.md
CLAUDE_MD="$CLAUDE_PROJECT_DIR/CLAUDE.md"
UNLISTED=""

# Find all files in .claude/ excluding hooks/, settings files, openbrain-category, MEMORY.md
while IFS= read -r -d '' file; do
  relative="${file#$CLAUDE_PROJECT_DIR/}"
  # Skip hooks, settings, openbrain-category, MEMORY.md, archive/, workflows/
  if echo "$relative" | grep -qE "^\.claude/hooks/|^\.claude/settings|^\.claude/openbrain-category|MEMORY\.md|^\.claude/archive/|^\.claude/workflows/"; then
    continue
  fi
  # Check if listed in CLAUDE.md
  if ! grep -qF "$relative" "$CLAUDE_MD"; then
    UNLISTED="$UNLISTED\n  $relative"
  fi
done < <(find "$CLAUDE_PROJECT_DIR/.claude" -type f -print0 2>/dev/null)

if [ -n "$UNLISTED" ]; then
  echo "⚠️  BLOCKED: The following .claude/ files are not listed in CLAUDE.md:"
  echo -e "$UNLISTED"
  echo "   Add them to the 'Read on demand' section in CLAUDE.md before saving."
  exit 1
fi

# Check 3: core memory files must be listed in CLAUDE.md
MISSING_CORE=""
for core in "memory/plan.md" "memory/observations.md" "memory/MEMORY.md"; do
  if ! grep -qF "$core" "$CLAUDE_MD"; then
    MISSING_CORE="$MISSING_CORE\n  $core"
  fi
done

if [ -n "$MISSING_CORE" ]; then
  echo "⚠️  BLOCKED: The following core memory files are not listed in CLAUDE.md:"
  echo -e "$MISSING_CORE"
  echo "   Ensure they appear in the Session Start section of CLAUDE.md."
  exit 1
fi

exit 0
