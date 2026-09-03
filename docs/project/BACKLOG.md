# Project backlog

This file is the lightweight intake queue for the fork. A task moves to a
GitHub issue when it needs discussion, cross-session ownership, or a pull
request. Keep completed spike evidence in `docs/spikes/`; do not turn this file
into a diary.

## Active

<!-- markdownlint-disable MD013 -->

| ID | Task | State | Branch / issue | Done when |
| --- | --- | --- | --- | --- |
| SIDB-001 | Enumerate every layout for app 3669040 and reconcile the website/API discrepancy | ready | `spike/app-3669040-layouts` | Reproducible inventory and evidence-backed completeness statement exist |

<!-- markdownlint-enable MD013 -->

## Next

<!-- markdownlint-disable MD013 -->

| ID | Task | Depends on | Done when |
| --- | --- | --- | --- |
| SIDB-002 | Build and validate a generalized Ren'Py Steam Controller profile | SIDB-001 | Mapping, importable artifact or documented creation steps, and on-device test notes exist |
| SIDB-003 | Decide whether layout enumeration belongs in a standalone tool or the fork | SIDB-001 | ADR records scope, API boundary, and maintenance trade-off |
| SIDB-004 | Prototype a safe Cursor MCP adapter for the Windows Buddy API | SIDB-001 | Read-only ping/status/controllers work from WSL; mutating calls remain approval-gated |

<!-- markdownlint-enable MD013 -->

## Workflow

1. Create or select one backlog item.
2. Start one workmux branch per independently mergeable task.
3. Record spike evidence or an ADR before broad implementation.
4. Use a second model/agent for review after the author has produced a diff.
5. Merge only after the branch-specific checks pass and remaining risks are
   explicit.
