# Active Plan — Filing System Migration
Started: 2026-03-07

## Steps
1. [ ] Merge `.claude/CLAUDE.md` detail into root `CLAUDE.md` (bugs, status, validated params, next steps)
2. [ ] Delete `.claude/CLAUDE.md`
3. [ ] Add missing sections to `docs/dev.md` (remove Decisions Log — not in new template)
4. [ ] Move `memory/plan.md` content to `docs/dev.md` Completed Plans when done
5. [ ] Delete `.claude/memory/recent_history.md`
6. [ ] Delete `.claude/memory/ideas.md`
7. [ ] Delete `scripts/update_memory.sh`
8. [ ] Git save

## Notes
- `.claude/memory/system_manual.md` and `.claude/memory/strategies/` are kept — referenced from root CLAUDE.md as on-demand reference files
- Root `CLAUDE.md` already matches the new template structure, just needs the detail filled in
- After this migration, only `./scripts/git-save.sh` is used — never `update_memory.sh`
