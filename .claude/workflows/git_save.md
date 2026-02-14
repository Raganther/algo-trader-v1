---
description: How to save progress and update project memory
---

# Git Save Protocol

This workflow ensures project memory is synchronized with the codebase on every commit.

## Quick Version

```bash
# 1. Commit with detailed message
git add [files]
git commit -m "type: Short description" -m "Detailed body with context..."

# 2. Auto-generate recent_history.md
./scripts/update_memory.sh

# 3. Amend to include history update
git add .claude/memory/recent_history.md
git commit --amend --no-edit

# 4. Push
git push origin main
```

## Detailed Steps

### 1. Stage Changes
```bash
git add [specific files]
# or
git add .
```

### 2. Commit with Detailed Message

**CRITICAL:** Include research findings, results, and explanations in the commit body.

```bash
git commit -m "type: Short description" -m "Detailed body:
- What was changed
- Why it was changed
- Results or findings
- Next steps if relevant

Co-Authored-By: Claude Opus 4.5 <noreply@anthropic.com>"
```

**Commit Types:**
- `feat` - New feature
- `fix` - Bug fix
- `docs` - Documentation only
- `refactor` - Code change without feature/fix
- `test` - Adding or updating tests

### 3. Update Recent History

```bash
./scripts/update_memory.sh
```

This auto-generates `.claude/memory/recent_history.md` from the last 20 commits.

### 4. Amend Commit to Include History

```bash
git add .claude/memory/recent_history.md
git commit --amend --no-edit
```

### 5. Push

```bash
git push origin main
```

## When to Update Other Files

### `.claude/claude.md` (Session Primer)
Update when:
- Phase changes (e.g., Phase 7 → Phase 8)
- Major milestone reached
- Active bots change
- Critical context changes

### `.claude/memory/system_manual.md` (Technical Reference)
Update when:
- Architecture changes
- New CLI commands added
- New constraints discovered
- One-time after major feature completion

### `.agent/workflows/forward_testing_plan.md` (Forward Test Journey)
Update when:
- New phase begins
- Bug fixes deployed
- Validation results collected
- Status table needs refresh

### `.agent/memory/research_insights.md` (Backtest Results)
**Auto-generated** by `python3 -m backend.analyze_results --write`

Only run manually after backtests, not after forward testing work.

## Deploy to Cloud (After Git Save)

If changes affect running bots:

```bash
gcloud compute ssh algotrader2026 --zone=europe-west2-a --command="cd algo-trader-v1 && git pull && pm2 restart all"
```

---

*Changes don't take effect on cloud until: git push → cloud pull → pm2 restart*
