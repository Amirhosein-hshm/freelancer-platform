# Slices 4-7 Backlog

Status: Not started except shared foundations noted below. Read the relevant API modules before planning each slice.

## Slice 4: Freelancer

- Profile/onboarding and approval submission; admin approval is not part of the freelancer-owned UI.
- Resume versions/current selection and portfolio CRUD.
- Eligible marketplace via `/projects/available`; applications/withdrawal; selected-project workbench; delivery/revision; ratings.
- Backend owns approval/level eligibility and application/delivery state. The current onboarding page is only a placeholder.

## Slice 5: Supervisor

Status: Implemented in the frontend.

- Category/supervised project views, pending-review queue, delivery decision, revision context, tickets.
- `/reviews` provides pending reviews and category-scoped projects with URL pagination.
- `/reviews/[project_id]` provides delivery review decisions and revision context.
- Supervisor scope is category-oriented; assignment mechanics remain unknown and must not be inferred.

## Slice 6: Admin

- Users/status/roles/permissions; categories and supervisors; form-template drafts, fields/options, publishing/versions.
- Freelancer approval/rejection/levels/history; admin on-behalf project/application actions; analytics/reporting.
- Admin UI does not bypass backend ownership, lifecycle, or permission checks.

## Slice 7: Quality and hardening

- Complete workflow tests, accessibility and responsive audits, production build, performance review, and live OpenAPI regeneration/diff check.
- Notifications remain blocked on an explicit `/ws/notifications` contract.

## Shared foundations already available

Shell/auth, API proxy/generated hooks, query provider, errors, pagination, URL state, forms/UI primitives, file upload, dynamic template fields, project labels/capabilities.
