#!/bin/bash
# PostToolUse hook — fires after Edit or Write tool calls
# If plan.md was modified and lacks "Domain files consulted", reminds Claude to review domain files.

INPUT=$(cat)
FILE=$(echo "$INPUT" | python3 -c "import sys,json; d=json.load(sys.stdin); print(d.get('tool_input',{}).get('file_path',''))" 2>/dev/null)

# Only fire for plan.md edits
if [[ "$FILE" != *"plan.md" ]]; then
  exit 0
fi

# Check if plan is active (not "No active plan")
if grep -q "No active plan" "$FILE" 2>/dev/null; then
  exit 0
fi

# Check if Domain files consulted line already exists
if grep -q "Domain files consulted" "$FILE" 2>/dev/null; then
  exit 0
fi

echo "plan.md updated. Before starting work on this plan:"
echo ""
echo "1. Review the 'Read on demand' section in CLAUDE.md for relevant domain files."
echo "2. Read any that apply to this plan."
echo "3. Add a 'Domain files consulted: [list or None]' line at the top of plan.md."
echo ""
echo "This ensures graduated knowledge informs the plan before work begins."

exit 0
