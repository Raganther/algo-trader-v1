#!/bin/bash
# PostToolUse hook — fires after git-save.sh
# Enforces four required steps: graduation check, skill extraction, OpenBrain audit, confirmation.

INPUT=$(cat)
COMMAND=$(echo "$INPUT" | python3 -c "import sys,json; d=json.load(sys.stdin); print(d.get('tool_input',{}).get('command',''))" 2>/dev/null)

# Only fire for git-save.sh commands
if [[ "$COMMAND" != *"git-save.sh"* ]]; then
  exit 0
fi

echo "Git save complete. Four steps required before continuing:"
echo ""
echo "STEP 1 — Triage:"
echo ""
echo "a) Observations — for each entry in observations.md, state one of:"
echo "  KEEP     — still evolving, not confirmed"
echo "  GRADUATE — confirmed this session: move to .claude/[domain]/ file, remove from observations.md, update CLAUDE.md pointer, follow-up commit"
echo "  REMOVE   — resolved or stale: delete it"
echo "Also: if you revisited any entry this session, update it in place — do not append a new entry for the same topic."
echo ""
echo "b) Domain files — for each file listed under 'Domain files consulted' in plan.md, state one of:"
echo "  CURRENT     — still accurate, no changes needed"
echo "  UPDATE      — partially changed: edit the file in place"
echo "  SUPERSEDED  — replaced by a better model: add 'Status: superseded' and note what replaced it"
echo "  INVALIDATED — wrong: remove or add 'Status: invalidated' with explanation"
echo "If plan.md has no domain files consulted, skip this check."
echo ""
echo "State your triage explicitly before proceeding to Step 2."
echo ""
echo "STEP 2 — Procedure extraction:"
echo "Review the session's work. Ask: what reusable procedural pattern did we apply that isn't yet named as a procedure?"
echo "A procedure is a repeatable process — how to do a class of task — not a fact (domain file) or a step (plan.md)."
echo "For each candidate, propose: name, when to apply, steps, example from this session."
echo "Wait for user approval before writing. Approved procedures go in .claude/procedures/ with a matching entry in .claude/procedures/_index.md."
echo "If no procedure candidates, state that explicitly."
echo ""
echo "STEP 3 — OpenBrain audit:"
echo "Review what was just committed. Propose confirmed/working things as OpenBrain candidates."
echo "Use the project name as category (check .claude/openbrain-category)."
echo "Run list_memories(category='<project>') first — for each candidate:"
echo "  - If it updates an existing entry: propose update_memory(id, new_content), not a new entry."
echo "  - If it is genuinely new: propose remember(content, category)."
echo "Wait for user approval before writing anything."
echo "If no candidates or updates, state that explicitly."
echo ""
echo "STEP 4 — Confirm completion."
echo "State that triage, procedure extraction, and OpenBrain audit are all done before resuming other work."

exit 0
