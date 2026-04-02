# Procedure: Memory Harness Migration

**When to apply:** when the global CLAUDE.md spec is updated and a project needs to be brought into compliance. Also run when setting up a new project and the spec has evolved since the last setup.

## Steps

1. **Read global CLAUDE.md hooks section** — identify the canonical hook list, check counts, and note any spec changes since last migration.

2. **Diff hooks against project** — for each hook named in the spec:
   - Does the file exist in `.claude/hooks/`?
   - Is it registered in `.claude/settings.json` under the correct event and matcher?
   - Does the script content match the spec (verbatim where required)?

3. **Diff git-save-guard checks** — count the checks in the spec vs the script. For any new checks, implement them at the end of the guard before `exit 0`.

4. **Check domain file headers** — the spec defines the required header line. For each file in `.claude/[domain]/`:
   - Does it have `Status:`, `Epistemic:`, and `Last verified:` fields?
   - Use `git log -1 --format="%as" -- <file>` for the honest `Last verified` date.
   - Use `confirmed` for independently verified knowledge, `assumed` for worked-when-tried-not-re-verified.

5. **Check CLAUDE.md domain file pointers** — each pointer must be "read when X" trigger-condition format, not "contains Y" content summary. Rewrite any that describe content rather than trigger.

6. **Git save** — all changes in one commit. The new check 6 in git-save-guard will enforce headers on future domain files automatically.

## Example (Mar 30 2026)
- Added `agents/` exclusion to Check 2
- Added Check 6 (Epistemic/Last verified enforcement)
- Created `domain-naming-guard.sh` + registered in settings.json
- Extended 8 domain file headers from `Status: current` to full three-field format
- Reformatted 8 CLAUDE.md pointers from content summaries to "read when X"

## Example (Apr 2 2026 — v3 migration)
- `plan.md` eliminated — active steps distributed to domain file `## Plan` sections and `observations.md` Active Work
- `plan-domain-reminder.sh` deleted, removed from `settings.json` PostToolUse hooks
- `git-save-guard.sh`: Check 1 narrowed (observations.md only), Check 3 narrowed (observations.md + gitlog.md only), Check 4 (Graduation Candidates) removed, checks renumbered 5→4 and 6→5
- `openbrain-audit-reminder.sh`: Step 1b (domain files from plan.md) removed; Step 1a updated to v3 staging contract (KEEP-STAGING / CREATE-DOMAIN / REMOVE)
- `load-context.sh`: plan.md removed from session start output
- `CLAUDE.md`: plan.md removed from Session Start read order, plan-domain-reminder.sh removed from hooks description
- 10 domain files restructured: status header moved to line 1, `## Knowledge` section added wrapping all content, existing `##` sections demoted to `###`, `*Last updated:*` footers removed
- File-specific Plan/Open Questions added: xle.md (Plan.Active), calibration-notes.md (Plan.Active + Plan.Research), event-surprise.md (Plan.Research), alpaca-mcp.md (Open Questions)
- `observations.md` rewritten to v3 format: Active Work + Staging sections only
