# Procedure: Memory Harness Compliance Audit

**When to apply:** When the global `~/.claude/CLAUDE.md` is updated with new harness requirements, or when setting up a new project and verifying it matches the global spec.

## Steps

1. **Read global CLAUDE.md** — note the current hook specs (step counts, check lists, exclusion patterns, required files).

2. **Audit hooks** — read each hook script and compare against spec:
   - `openbrain-audit-reminder.sh` — confirm step count and procedure extraction step present. Global spec says "copy verbatim".
   - `git-save-guard.sh` — confirm all checks are present. Check exclusion patterns in Check 2 include `procedures/`. Check 5 (procedure files in _index.md) present.
   - `plan-domain-reminder.sh` — confirm it fires on plan.md edits and checks for "Domain files consulted" line.
   - `load-context.sh` — confirm it prints key context files and cloud status.

3. **Audit `settings.json`** — confirm all four hooks are registered (SessionStart, PreToolUse Bash, PostToolUse Bash, PostToolUse Edit+Write).

4. **Audit domain files** — read each file in `.claude/[domain]/`:
   - `Status: current` (or `superseded` / `invalidated`) present as second non-blank line after H1.
   - No plan steps (checkboxes) — those belong in `plan.md`.
   - No stale operational state — remove or update forward-testing snapshots that reference confirmed-but-listed-as-pending mechanics.

5. **Audit `CLAUDE.md` Session Start** — verify each domain file is listed **individually** by full path (e.g. `.claude/strategies/stochrsi_enhanced_gld.md`), not as a directory pointer. Directory pointers (`.claude/strategies/`) do not satisfy the `grep -qF` check in git-save-guard Check 2.

6. **Audit `CLAUDE.md` Architecture** — confirm all hook scripts are named.

7. **Confirm `.claude/procedures/_index.md` exists** — even if empty.

8. **Fix all gaps found**, then git save.

## Example (this project, Mar 26 2026)

Gaps found vs global CLAUDE.md:
- `openbrain-audit-reminder.sh` had 3 steps, missing procedure extraction (Step 2)
- `git-save-guard.sh` missing Check 5, and Check 2 didn't exclude `procedures/`
- `.claude/procedures/` directory and `_index.md` did not exist
- CLAUDE.md listed `.claude/strategies/` as a directory pointer — 6 files behind it were invisible to Check 2
- All 7 domain files had custom status strings ("VALIDATED", "BUILT") instead of standard `Status: current`
- Strategy cards had stale mechanics-pending sections and Next Steps checkboxes

All fixed in one session.
