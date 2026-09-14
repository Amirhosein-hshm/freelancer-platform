# Decisions, Issues, and Unknowns

## Active decisions

Decision: Use backend lifecycle actions instead of local lifecycle inference.
Why: Authorization, eligibility, and state transitions are backend-owned.
Evidence: OpenAPI action endpoints/error contracts; `src/features/projects/project-domain.ts` treats helpers as UX capabilities only.
Status: Active.

Decision: Keep credentials behind the same-origin Next.js API boundary.
Why: Browser code must not receive access/refresh tokens.
Evidence: `src/app/api/v1/[...path]/route.ts`, `src/lib/api/session.ts`, `src/proxy.ts`.
Status: Implemented.

Decision: Treat generated API artifacts as disposable contract output.
Why: Prevent handwritten contract drift.
Evidence: `orval.config.ts`, `openapi.json`, `generated/api`.
Status: Active.

Decision: Use backend list capabilities exactly as declared.
Why: `/projects/my` exposes pagination but no status/search filter.
Evidence: OpenAPI parameters and `src/features/projects/project-list.tsx`.
Status: Active; current status groups filter only the fetched page and disclose that limitation.

Decision: Use the implemented design tokens, not the removed generated design master.
Why: The master prescribed DM Sans, marketing motion, and component details that conflict with the current Persian operational UI.
Evidence: `src/app/layout.tsx`, `src/app/globals.css`, `src/components/ui`.
Status: Active.

## Known issues

- Navigation includes future routes (`/reviews`, `/admin`, `/reports`) that currently resolve to not-found.

## UNKNOWN

- Exact backend encoding expected for dynamic `FormValueInputRequest.value` types (`multi_select`, `file`, `datetime`, boolean). Current encodings are documented in source but not confirmed by OpenAPI.
- Whether supervisor assignment is exclusively category-derived or may be explicitly stored per project. The contract exposes category supervisors and `assigned_supervisor_user_id` but no normal project-assignment action.
- Live backend behavior has not been verified in this documentation pass; the checked-in OpenAPI snapshot is the available contract authority.
- Freelancer approval has no documented pre-submission status; show submission for non-approved/non-suspended profiles and treat backend `409`/`422` as authoritative.
- Freelancer application state is per-project: derive it from `GET /api/v1/projects/{project_id}` `applications[]` by matching the current freelancer profile. Never persist application IDs or assume global application/assignment endpoints.

## ASSUMPTION

- `src/features/projects/template-fields.tsx` encodes booleans as `true`/`false`, lists/file IDs as comma-separated strings, and datetimes as UTC ISO strings from Tehran wall time. Treat backend `422` as authoritative until confirmed.

## CONFIRMED

- OpenAPI snapshot: 90 paths, 123 HTTP operations, 265 schemas, API version `0.1.0`.
- Project update is draft-only, full replacement; category derives from template.
- Project details expose `form_template_id` and existing `form_values`; lossless draft editing uses those backend-provided values.
- Customer project list filtering is page-local because the endpoint has no server status filter.
