#!/bin/bash
# PreToolUse hook — fires before Write tool calls
# Enforces lowercase-hyphenated naming convention for .claude/*.md files

INPUT=$(cat)
FILE=$(echo "$INPUT" | python3 -c "import sys,json; d=json.load(sys.stdin); print(d.get('tool_input',{}).get('file_path',''))" 2>/dev/null)

# Only act on .claude/ .md files
if ! echo "$FILE" | grep -q "/.claude/"; then
  exit 0
fi
if [[ "$FILE" != *.md ]]; then
  exit 0
fi

BASENAME=$(basename "$FILE" .md)

# Exempt: hooks/, memory/, _index.md
if echo "$FILE" | grep -qE "/.claude/(hooks|memory)/"; then
  exit 0
fi
if [ "$BASENAME" = "_index" ]; then
  exit 0
fi

# Check naming convention: lowercase letters, digits, hyphens — no uppercase, underscores, spaces, leading digit
if ! echo "$BASENAME" | grep -qE "^[a-z][a-z0-9-]*$"; then
  echo "⚠️  BLOCKED: Domain file name '$BASENAME.md' does not follow the lowercase-hyphenated convention."
  echo "   Use: lowercase letters, digits, hyphens only. No uppercase, underscores, spaces, or leading digits."
  echo "   Example: strategy-results.md, not StrategyResults.md or strategy_results.md"
  exit 1
fi

exit 0
