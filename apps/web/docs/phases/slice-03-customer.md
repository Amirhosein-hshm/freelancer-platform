# Slice 3: Customer Workflow

Status: Complete. Remaining cross-cutting hardening belongs to Slice 7; known contract uncertainty is recorded below.

## Completed

- `/projects` server page loads `/api/v1/projects/my` with URL pagination and session-aware shell.
- Customer project cards show backend status, priority, visibility, budget, code, and creation date.
- Status groups filter/count only the fetched page and explicitly disclose that limitation when more pages exist.
- Project domain labels and UX capability helpers cover project/application/delivery/review statuses.
- Project create/edit Zod schema and request-value helpers exist.
- Dynamic active-template field renderer exists for text, numeric, date/time, boolean, select, multi-select, file, and related field types.
- Shared file upload/asset UI needed by project forms exists.
- Focused tests cover project domain formatting/capabilities and file asset behavior.
- `/projects/new` implements customer/admin project creation with active categories, published templates, dynamic fields, draft submission, and API error handling.
- `/projects/[project_id]` renders project metadata plus embedded applications/deliveries and paginated status/revision history as a read-only server page.
- `/projects/[project_id]/edit` loads draft details, category/template data, and prefills the shared React Hook Form; successful updates use the generated draft-only full-replacement mutation.
- Project detail actions support draft delete, publish, assigned-project start, and non-terminal cancel with confirmation dialogs, pending states, backend errors, and refresh/redirect behavior.
- Customer application review supports backend accept/reject operations with confirmation, optional rejection notes, pending/error feedback, and detail refresh.
- Customer delivery review supports backend approval or revision requests with required revision reasons, confirmation, pending/error feedback, and detail refresh.
- Customer final review supports backend approval or revision decisions with optional comments, confirmation, pending/error feedback, and detail refresh.
- Completed projects support customer rating create, update, and confirmed delete with score validation, optional comments, visibility control, and existing-rating prefilling.
- Project editing preserves the exact stored template ID/version; active published templates remain available for deliberate replacement.
- Project detail presents delivery-specific supervisor/customer reviews and links each revision to a dedicated read-only detail route.
- `/tickets`, `/tickets/new`, and `/tickets/[ticket_id]` implement paginated customer tickets, related-user targeting, two-step creation, replies, attachments, message edit/delete, close, and closed-ticket read-only behavior.
- Ticket creation preserves the initial message for retry when ticket creation succeeds but message submission fails.

## In Progress


## Not Started

- None for the customer-owned Slice 3 workflow.

## Known Issues

- The page description/action are customer-oriented, while admins can also see the nav item; role-specific copy/actions have not been resolved.
- Dynamic form value encodings are unconfirmed; see `docs/context/decisions.md`.

## Decisions

- Fetch `/projects/my`; do not substitute `/projects` or invent ownership filtering.
- Keep server pagination authoritative. Any page-local grouping must remain labeled as page-local.
- Use generated request/response types and backend action endpoints for lifecycle mutations.
- Update requests send the full desired draft state and never send `category_id`.
- Capability helpers decide what to offer, never what is authorized.
- Preserve a draft project's exact `form_template_id`; never migrate it to a newer template version implicitly.
- Tickets use related users returned by `/users/related`; creator/target ownership and backend authorization remain authoritative.
- Ticket creation is two-step because the create request has no message body; partial success must route to the created ticket without creating a duplicate.

## Remaining Work

Recommended order:

1. Start Slice 4 with freelancer onboarding/profile. Add broader route/component, accessibility, and live-backend coverage in Slice 7.

## Required evidence for continuation

- Global: `docs/context/project-rules.md` and `docs/context/business-rules.md`.
- Unknowns/decisions: `docs/context/decisions.md`.
- Current code: `src/app/(dashboard)/projects/page.tsx`, `src/features/projects`, `src/features/files`, shared API/form/UI helpers.
- Contract: relevant project/category/form-template/file/feedback generated modules and models; inspect matching `openapi.json` paths only when generated types omit semantics.
