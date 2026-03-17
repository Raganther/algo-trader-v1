#!/bin/bash
# PreToolUse hook — blocks git-save.sh if memory files haven't been updated

# Read tool input JSON from stdin
INPUT=$(cat)

# Extract the bash command being run
COMMAND=$(echo "$INPUT" | python3 -c "import sys,json; d=json.load(sys.stdin); print(d.get('tool_input',{}).get('command',''))" 2>/dev/null)

# Only act on git-save.sh calls
if ! echo "$COMMAND" | grep -q "git-save.sh"; then
  exit 0
fi

# Check if memory files have been modified since last commit
CHANGED=$(git -C "$CLAUDE_PROJECT_DIR" diff HEAD --name-only -- memory/plan.md memory/observations.md 2>/dev/null)

if [ -z "$CHANGED" ]; then
  echo "⚠️  BLOCKED: memory/plan.md and memory/observations.md are unchanged since last commit."
  echo "   Update these files before running git save."
  exit 1
fi

exit 0
