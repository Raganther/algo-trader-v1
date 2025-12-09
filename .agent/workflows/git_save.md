---
description: How to save progress and update project memory
---

This workflow ensures that the project memory is synchronized with the codebase before every commit.

1.  **Update System Manual**:
    - Check `.agent/memory/system_manual.md`:
        - Update **Infrastructure** or **CLI Commands** if you changed how the system works.
        - **Note**: Do NOT add research insights or strategy results here.

2.  **Stage Changes**:
    - Run: `git add .`

3.  **Commit Changes**:
    - **CRITICAL:** If you have research findings, results, or detailed explanations, you **MUST** include them in the commit body.
    - Use multiple `-m` flags:
        ```bash
        git commit -m "[Type]: [Short Description]" -m "Detailed Findings:
        - Result A: +10% Return
        - Analysis: Strategy works because...
        - Next Steps: Optimize X..."
        ```
    - *Types*: `feat`, `fix`, `docs`, `refactor`, `test`.

4.  **Update History**:
    # 2. Update Memory
    ./scripts/update_memory.sh
    python3 scripts/curate_memory.py
    `
    - Run: `git add .agent/memory/recent_history.md`
    - Run: `git commit --amend --no-edit` (Include history in the same commit)
