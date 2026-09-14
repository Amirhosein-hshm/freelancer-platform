# Codex Context Index

Read only the files needed for the current task.

## Required context

1. `AGENTS.md` (repository/Next.js instructions).
2. `docs/context/project-rules.md` (global rules and source-of-truth order).
3. The active phase file.
4. Relevant source files and the matching generated API module/models.

Do not load `openapi.json` or all of `generated/api` into context. Inspect only the relevant paths/schemas. Generated API code is disposable and must not be edited.

## Phase files

| Work | Read |
| --- | --- |
| Slices 1-2 regression/foundation work | `docs/phases/foundation.md` |
| Slice 3 customer workflow | `docs/phases/slice-03-customer.md` |
| Slices 4-7 planning | `docs/phases/backlog.md` |

Read `docs/context/business-rules.md` when a task touches authorization, ownership, lifecycle, files, forms, feedback, or tickets. Read `docs/context/decisions.md` when changing architecture or resolving an unknown/conflict.

