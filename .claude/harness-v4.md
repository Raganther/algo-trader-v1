Status: current | Epistemic: confirmed | Last verified: 2026-04-23

# Harness v4.2 — Memory & Knowledge Convention

Documents the conventions for this project's knowledge system.

## The three layers

**Domain files** — confirmed, settled knowledge per topic. No speculative content. Read and updated only when something is being promoted from the roadmap. Each file owns one topic; content doesn't leak between files.

**Roadmap** (`.claude/strategies/research-roadmap.md`) — single staging layer for everything in-flight. All open questions, ideas, in-progress experiments, and monitoring items live here. Status labels: `idea | in progress | validated | rejected | monitoring`. When a roadmap item is settled, the confirmed fact is promoted to the relevant domain file and the roadmap item moves to Resolved.

**`CLAUDE.md`** — navigation map and table of contents. Stable facts only: project phase, architecture, run commands, "read when X" file index. Never holds volatile state. Changes rarely — only when architecture, domain file list, or run commands change.

**Session continuity** is carried by `gitlog.md` (auto-regenerated from the last 15 commits with full diff stats + bodies) plus rich commit messages — not by a separate observations file.

## Knowledge lifecycle

```
conversation → roadmap (add open question / idea)
             → roadmap status updated (validated / rejected / monitoring)
             → settled fact promoted to relevant domain file (## Knowledge section)
             → roadmap item moved to Resolved table
```

Domain files never receive speculative content directly. Everything passes through the roadmap first.

## Write order (git save)

```
Roadmap (add/update items) → Domain files (promote settled items) → commit with rich message → CLAUDE.md (only if structure changed)
```

Rich commit messages replace the old observations.md entries. `git-save.sh` regenerates `gitlog.md` from the last 15 commits, so the commit message is what future sessions see.

## Read order (cold start)

```
CLAUDE.md (auto-loaded) + auto-memory MEMORY.md (auto-injected) → gitlog.md (always) → research-roadmap.md (always) → domain files (on demand, via "read when X" triggers)
```

## Domain file format

```markdown
Status: current | Epistemic: confirmed | Last verified: YYYY-MM-DD

# [Title]

## Knowledge
Confirmed facts only. Primary read target. No open questions, no to-dos.
```

Rules:
- `Status | Epistemic | Last verified` header mandatory (enforced by git-save-guard Check 5)
- `## Knowledge` always present
- No `## Plan`, `## Open Questions`, or `## Research` sections — those live in the roadmap (enforced by Check 6)
- Never leave placeholder text in empty sections

## Auto-memory policy

Claude Code maintains a separate auto-memory directory at `~/.claude/projects/<project>/memory/`. Its `MEMORY.md` is auto-injected into every session via `system-reminder`.

**This project's policy:** auto-memory is redirected to the harness. The auto-memory `MEMORY.md` is a pointer index only — no duplicate content. Platform gotchas and bug patterns that are non-obvious and cross-session are kept there. Do not write project strategy or roadmap content into the auto-memory directory. The harness is the authoritative store.

## git-save-guard checks (enforced)

1. At least one domain file or source file modified
2. New domain files listed in `CLAUDE.md`
3. `gitlog.md` listed in `CLAUDE.md`
4. New procedures listed in `_index.md`
5. Changed domain files have `Epistemic:` and `Last verified:` headers
6. Changed domain files must not contain `## Plan` or `## Open Questions` sections
7. Commit message quality — at least 5 words; rejects vague single-word prefixes

## git-save.sh behaviour

`./scripts/git-save.sh "message"` does:
1. Prints context-aware **domain update checklist** (non-blocking) — flags which domain files likely need review based on what changed
2. `git add -A` + commit
3. Pull/rebase from remote
4. Regenerates `.claude/memory/gitlog.md` from last 15 commits
5. Amends the commit to include the updated gitlog
6. Pushes to GitHub
7. `git pull` on GCP server (auto-deploy to algotrader-us)

Always use `git-save.sh` — not raw `git commit`.

## Context-aware domain update checklist

| If changed | Reminder |
|------------|---------|
| `backend/strategies/stoch_rsi_mean_reversion.py` | Update relevant stochrsi-enhanced-*.md domain files |
| `backend/engine/live_broker.py` | Update CLAUDE.md Current Status and MEMORY.md if new bug fixed |
| `backend/engine/alpaca_trader.py` | Update alpaca-mcp.md and CLAUDE.md |
| `scripts/run_*.sh` | Update CLAUDE.md Run Commands bot table |
| `CLAUDE.md` | Commit message must explain why |
| `research-roadmap.md` | Have settled items been promoted to domain files? |
| `.claude/strategies/stochrsi-enhanced-*.md` | Is CLAUDE.md Validated Edges table current? |
| `backend/engine/backtester.py` | Update calibration-notes.md if calibration methodology affected |

## Hooks

These hooks are Claude Code automation. In Codex sessions, treat them as a required manual checklist unless the local app explicitly runs Claude hooks. `./scripts/git-save.sh` still works and regenerates `gitlog.md`, but the Claude `PreToolUse` / `PostToolUse` guards may not fire automatically.

| Hook | Trigger | Script | Purpose |
|------|---------|--------|---------|
| `SessionStart` | Every session open | `load-context.sh` | Prints branch/commit + UTC/IST time anchor, reminds to read gitlog + roadmap |
| `PreToolUse: Bash` | Every Bash call | `git-save-guard.sh` | Blocks git-save if checks 1–7 fail |
| `PreToolUse: Write` | Every Write to `.claude/` | `domain-naming-guard.sh` | Enforces lowercase-hyphenated naming convention |

## Naming conventions

- Harness spec: `.claude/harness-v4.md` (root of `.claude/`)
- Domain files: `lowercase-hyphenated.md` (enforced by domain-naming-guard)
- Memory files: `feedback_topic.md`, `project_topic.md` (underscores permitted in `memory/`)
- Strategy files: live in `.claude/strategies/`
- Procedures: live in `.claude/procedures/`, indexed in `_index.md`

## Domain files in this project

| File | Read when |
|------|----------|
| `.claude/strategies/research-roadmap.md` | Every session — after gitlog |
| `.claude/strategies/stochrsi-enhanced-gld.md` | Working on GLD, reviewing long-only vs full strategy, checking audit baseline |
| `.claude/strategies/stochrsi-enhanced-iau.md` | Working on IAU or reviewing 15m strategy params |
| `.claude/strategies/stochrsi-enhanced-slv.md` | Working on SLV or reviewing 15m strategy params |
| `.claude/strategies/stochrsi-enhanced-gdx.md` | Working on GDX or reviewing 15m strategy params |
| `.claude/strategies/stochrsi-enhanced-xle.md` | Working on XLE or planning Rolling Validation Test #1 |
| `.claude/strategies/research-log.md` | Deciding what to experiment on next, reviewing cross-strategy learnings |
| `.claude/strategies/composable-results.md` | Combining strategies or planning composable bot deployment |
| `.claude/strategies/event-surprise.md` | Researching economic event strategies or revisiting CPI/NFP trading |
| `.claude/strategies/regime-analysis.md` | Working on regime classification, regime-aware sizing, or interpreting live performance by regime |
| `.claude/strategies/regime-stochrsi-diagnostic.md` | Interpreting Apr 23 per-regime StochRSI results or deciding whether regime-aware sizing is justified |
| `.claude/strategies/regime-sizing-portfolio-diagnostic.md` | Evaluating whether regime multipliers improve portfolio-level return/drawdown before live sizing |
| `.claude/strategies/arbitrage-automation-concepts.md` | Exploring new strategy families, evaluating adjacent business ideas |
| `.claude/calibration/calibration-notes.md` | Running calibration, checking Apr 20 methodology, comparing backtest vs live |
| `.claude/calibration/live-trade-log.md` | Auditing trades, filling in daily trade data, reviewing calibration data |
| `.claude/calibration/gap-distribution.md` | Sizing overnight-capable positions, evaluating gap-risk policy, interpreting overnight gap losses |
| `.claude/integrations/alpaca-mcp.md` | Using Alpaca MCP tools, running trade audits, checking what data is available |

## Maintaining this file

Update harness-v4.md whenever conventions change — it is the in-project source of truth. If a hook is added, changed, or removed, reflect it here. Bump the minor version (e.g. v4.2 → v4.3) when the layer model or enforcement rules change.
