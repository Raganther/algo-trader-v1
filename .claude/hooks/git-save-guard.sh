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
CHANGED=$(git -C "$CLAUDE_PROJECT_DIR" diff HEAD --name-only -- .claude/memory/plan.md .claude/memory/observations.md 2>/dev/null)

if [ -z "$CHANGED" ]; then
  echo "⚠️  BLOCKED: .claude/memory/plan.md and .claude/memory/observations.md are unchanged since last commit."
  echo "   Update these files before running git save."
  exit 1
fi

# Check 2: any new domain files in .claude/ must be listed in CLAUDE.md
CLAUDE_MD="$CLAUDE_PROJECT_DIR/CLAUDE.md"
UNLISTED=""

# Find all files in .claude/ excluding hooks/, settings files, openbrain-category, and core memory files
while IFS= read -r -d '' file; do
  relative="${file#$CLAUDE_PROJECT_DIR/}"
  # Skip hooks, settings, openbrain-category, and core memory files
  if echo "$relative" | grep -qE "^\.claude/hooks/|^\.claude/settings|^\.claude/openbrain-category|^\.claude/memory/plan\.md|^\.claude/memory/observations\.md|^\.claude/memory/gitlog\.md"; then
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
for core in ".claude/memory/plan.md" ".claude/memory/observations.md" ".claude/memory/gitlog.md"; do
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

# Check 4: Graduation Candidates section in observations.md must be empty
OBSERVATIONS="$CLAUDE_PROJECT_DIR/.claude/memory/observations.md"
if [ -f "$OBSERVATIONS" ]; then
  IN_SECTION=0
  HAS_CANDIDATES=0
  while IFS= read -r line; do
    if echo "$line" | grep -q "^## Graduation Candidates"; then
      IN_SECTION=1
      continue
    fi
    if [ $IN_SECTION -eq 1 ]; then
      if echo "$line" | grep -q "^## "; then
        break
      fi
      if echo "$line" | grep -qE "[^[:space:]]"; then
        HAS_CANDIDATES=1
        break
      fi
    fi
  done < "$OBSERVATIONS"

  if [ $HAS_CANDIDATES -eq 1 ]; then
    echo "⚠️  BLOCKED: observations.md has pending Graduation Candidates."
    echo "   Graduate them to a .claude/[domain]/ file, or explicitly clear the section before saving."
    exit 1
  fi
fi

exit 0
