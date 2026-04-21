#!/bin/bash
# PreToolUse guard — blocks git-save.sh if:
# 1. No .claude/ files or source files have been updated
# 2. New domain files in .claude/ are not listed in CLAUDE.md (hooks/, procedures/, agents/ exempt)
# 3. Core memory file (gitlog.md) is not listed in CLAUDE.md
# 4. New procedure files in .claude/procedures/ are not listed in _index.md
# 5. Domain files written this session are missing Epistemic: or Last verified: headers
# 6. Domain files contain legacy ## Plan or ## Open Questions sections
# 7. Commit message is too vague (< 5 words or single-word type prefix)

INPUT=$(cat)
COMMAND=$(echo "$INPUT" | python3 -c "import sys,json; d=json.load(sys.stdin); print(d.get('tool_input',{}).get('command',''))" 2>/dev/null)

# Only run for git-save.sh commands
if [[ "$COMMAND" != *"./scripts/git-save.sh"* ]]; then
  exit 0
fi

PROJECT_DIR="${CLAUDE_PROJECT_DIR:-$(git rev-parse --show-toplevel 2>/dev/null)}"

# CHECK 1: At least one domain file or source file must be updated
DOMAIN_STATUS=$(git -C "$PROJECT_DIR" status --porcelain -- .claude/ 2>/dev/null \
  | grep -v "^.. \.claude/memory/gitlog\.md" \
  | grep -v "^.. \.claude/memory/observations\.md" \
  | grep -v "^.. \.claude/hooks/" \
  | grep -v "^.. \.claude/settings" \
  | grep -v "^.. \.claude/openbrain-category" \
  | grep "\.md")
SRC_STATUS=$(git -C "$PROJECT_DIR" status --porcelain -- backend/ scripts/ frontend/ CLAUDE.md 2>/dev/null)

if [ -z "$DOMAIN_STATUS" ] && [ -z "$SRC_STATUS" ]; then
  echo >&2 "BLOCKED: No domain files or source files updated since last commit."
  echo >&2 "Update at least one domain file, roadmap item, source file, or CLAUDE.md before saving."
  exit 2
fi

# CHECK 2: New domain files must be listed in CLAUDE.md
NEW_DOMAIN=$(git -C "$PROJECT_DIR" ls-files --others --exclude-standard -- .claude/ 2>/dev/null \
  | grep -v "^\.claude/hooks/" \
  | grep -v "^\.claude/procedures/" \
  | grep -v "^\.claude/agents/" \
  | grep -v "settings\.json" \
  | grep -v "settings\.local\.json" \
  | grep -v "openbrain-category" \
  | grep -v "^\.claude/memory/observations\.md" \
  | grep -v "^\.claude/memory/gitlog\.md")

if [ -n "$NEW_DOMAIN" ]; then
  UNREGISTERED=""
  while IFS= read -r file; do
    FILENAME=$(basename "$file")
    if ! grep -q "$FILENAME" "$PROJECT_DIR/CLAUDE.md" 2>/dev/null; then
      UNREGISTERED="$UNREGISTERED\n  $file"
    fi
  done <<< "$NEW_DOMAIN"

  if [ -n "$UNREGISTERED" ]; then
    echo >&2 "BLOCKED: New domain files not listed in CLAUDE.md:"
    printf >&2 "%b\n" "$UNREGISTERED"
    echo >&2 ""
    echo >&2 "Add each file to CLAUDE.md under 'Read on demand' with a 'read when X' trigger description before saving."
    exit 2
  fi
fi

# CHECK 3: gitlog.md must be listed in CLAUDE.md
if ! grep -q "gitlog\.md" "$PROJECT_DIR/CLAUDE.md" 2>/dev/null; then
  echo >&2 "BLOCKED: .claude/memory/gitlog.md is not listed in CLAUDE.md Session Start section."
  exit 2
fi

# CHECK 4: New procedure files must be listed in _index.md
PROCS_DIR="$PROJECT_DIR/.claude/procedures"
PROCS_INDEX="$PROCS_DIR/_index.md"

if [ -d "$PROCS_DIR" ]; then
  NEW_PROCS=$(git -C "$PROJECT_DIR" ls-files --others --exclude-standard -- .claude/procedures/ 2>/dev/null \
    | grep -v "_index\.md")

  if [ -n "$NEW_PROCS" ] && [ -f "$PROCS_INDEX" ]; then
    UNLISTED=""
    while IFS= read -r file; do
      FILENAME=$(basename "$file")
      if ! grep -q "$FILENAME" "$PROCS_INDEX" 2>/dev/null; then
        UNLISTED="$UNLISTED\n  $file"
      fi
    done <<< "$NEW_PROCS"

    if [ -n "$UNLISTED" ]; then
      echo >&2 "BLOCKED: New procedure files not listed in .claude/procedures/_index.md:"
      printf >&2 "%b\n" "$UNLISTED"
      echo >&2 ""
      echo >&2 "Add each procedure to _index.md with a one-line description before saving."
      exit 2
    fi
  fi
fi

# CHECK 5: Domain files written this session must have Epistemic: and Last verified: headers
CHANGED_DOMAIN=$(git -C "$PROJECT_DIR" diff --name-only HEAD -- '.claude/' 2>/dev/null \
  | grep -v "^\.claude/memory/" \
  | grep -v "^\.claude/hooks/" \
  | grep -v "^\.claude/procedures/_index\.md" \
  | grep -v "settings\.json" \
  | grep -v "openbrain-category" \
  | grep "\.md$")

if [ -n "$CHANGED_DOMAIN" ]; then
  MISSING_HEADERS=""
  while IFS= read -r file; do
    FULL_PATH="$PROJECT_DIR/$file"
    if [ -f "$FULL_PATH" ]; then
      if ! grep -q "Epistemic:" "$FULL_PATH" 2>/dev/null; then
        MISSING_HEADERS="$MISSING_HEADERS\n  $file (missing Epistemic:)"
      elif ! grep -q "Last verified:" "$FULL_PATH" 2>/dev/null; then
        MISSING_HEADERS="$MISSING_HEADERS\n  $file (missing Last verified:)"
      fi
    fi
  done <<< "$CHANGED_DOMAIN"

  if [ -n "$MISSING_HEADERS" ]; then
    echo >&2 "BLOCKED: Domain files written this session are missing required headers:"
    printf >&2 "%b\n" "$MISSING_HEADERS"
    echo >&2 ""
    echo >&2 "Add 'Status: current | Epistemic: confirmed/assumed | Last verified: YYYY-MM-DD' to each file."
    exit 2
  fi
fi

# CHECK 6: Domain files must not contain ## Plan or ## Open Questions sections
if [ -n "$CHANGED_DOMAIN" ]; then
  LEGACY_SECTIONS=""
  while IFS= read -r file; do
    FULL_PATH="$PROJECT_DIR/$file"
    if [ -f "$FULL_PATH" ]; then
      if grep -qE "^## (Plan|Open Questions)" "$FULL_PATH" 2>/dev/null; then
        LEGACY_SECTIONS="$LEGACY_SECTIONS\n  $file"
      fi
    fi
  done <<< "$CHANGED_DOMAIN"

  if [ -n "$LEGACY_SECTIONS" ]; then
    echo >&2 "BLOCKED: Domain files contain legacy ## Plan or ## Open Questions sections:"
    printf >&2 "%b\n" "$LEGACY_SECTIONS"
    echo >&2 ""
    echo >&2 "Domain files contain ## Knowledge only. Move open questions and plans to research-roadmap.md."
    exit 2
  fi
fi

# CHECK 7: Commit message quality — must be meaningful (5+ words, not just a type prefix)
COMMIT_MSG=$(echo "$COMMAND" | sed 's/.*git-save\.sh[[:space:]]*//' | sed 's/^"\(.*\)"$/\1/' | sed "s/^'\(.*\)'$/\1/")
WORD_COUNT=$(echo "$COMMIT_MSG" | wc -w | tr -d ' ')
VAGUE_PATTERN="^(fix|feat|docs|chore|refactor|update|minor|wip|cleanup|changes|misc)\.?$"

if [ "$WORD_COUNT" -lt 5 ] || echo "$COMMIT_MSG" | grep -qiE "$VAGUE_PATTERN"; then
  echo >&2 "BLOCKED: Commit message too vague ($WORD_COUNT words): \"$COMMIT_MSG\""
  echo >&2 ""
  echo >&2 "Good commit messages explain WHAT changed and WHY. Format:"
  echo >&2 "  type: short description of what — reason or context why"
  echo >&2 ""
  echo >&2 "Examples:"
  echo >&2 "  fix: bar-completion guard defers on_bar until 14 min — partial bar at open was generating phantom signals"
  echo >&2 "  feat: add late-session entry guard — GTC stops persist but trade has no room to develop before close"
  echo >&2 "  chore: migrate to harness v4.2 — consolidate open questions into single research-roadmap.md"
  exit 2
fi

exit 0
