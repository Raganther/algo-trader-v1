#!/bin/bash
# PostToolUse hook — fires after git-save.sh
# Enforces three required steps: graduation check, OpenBrain audit, confirmation.

INPUT=$(cat)
COMMAND=$(echo "$INPUT" | python3 -c "import sys,json; d=json.load(sys.stdin); print(d.get('tool_input',{}).get('command',''))" 2>/dev/null)

# Only fire for git-save.sh commands
if [[ "$COMMAND" != *"git-save.sh"* ]]; then
  exit 0
fi

echo "Git save complete. Three steps required before continuing:"
echo ""
echo "STEP 1 — Graduation check:"
echo "Did you confirm or resolve anything in observations.md this session?"
echo "If yes: move it from observations.md to the appropriate .claude/[domain]/ reference file now, then make a follow-up commit."
echo "If no: state that explicitly and proceed to Step 2."
echo ""
echo "STEP 2 — OpenBrain audit:"
echo "Review what was just committed. Propose confirmed/working things as OpenBrain candidates."
echo "Use the project name as category (check .claude/openbrain-category)."
echo "Run list_memories(category='<project>') first — for each candidate:"
echo "  - If it updates an existing entry: propose update_memory(id, new_content), not a new entry."
echo "  - If it is genuinely new: propose remember(content, category)."
echo "Wait for user approval before writing anything."
echo "If no candidates or updates, state that explicitly."
echo ""
echo "STEP 3 — Confirm completion."
echo "State that both graduation and audit are done before resuming other work."

exit 0
