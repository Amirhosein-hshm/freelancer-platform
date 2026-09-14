# Business Rules

These rules affect behavior and must not be inferred from UI state alone. Verify request/response fields in `openapi.json` or the relevant generated model.

## Identity and authorization

- Roles: `admin`, `customer`, `freelancer`, `supervisor`.
- Public registration accepts only customer or freelancer. Supervisor is admin-provisioned; admin is bootstrap/admin-created.
- `/api/v1/auth/me` is authoritative for roles, permissions, freelancer profile, onboarding need, approval status, and level.
- Navigation/action hiding is not authorization. The backend decides every operation.

## Session/security

- Access and refresh tokens are HTTP-only cookies managed by the Next.js boundary. Never expose them to client code or localStorage.
- Refresh tokens rotate. Refresh once, update both cookies atomically, retry once, then clear the session on failure.
- Logout sends the raw refresh token from the secure cookie and clears the local session regardless of backend outcome. `refresh_token_jti` is never a credential.

## Projects

- Customer/admin create projects. `category_id` is derived by the backend from `form_template_id`; do not submit it.
- Project updates are draft-only, replace the full editable state, and must not omit existing values unintentionally.
- Update/delete/publish are draft-only. Start is offered after freelancer assignment. Cancel is offered only while non-terminal. Backend responses remain authoritative if state changes concurrently.
- Applications are reviewed while a project accepts applications. Freelancer eligibility, approval, required-level matching, and duplicate/application-state rules belong to the backend.
- Only the selected freelancer may deliver. A delivery with an assigned supervisor goes to supervisor review; otherwise it goes to customer review. Backend state is authoritative.
- The revision cap is three rounds. Hide unavailable actions when known, but still handle backend conflict/business-rule responses.
- Review approval completes the project; review rejection opens a revision. Rating score is 1-5 and is available only after an approved final review/completed project. Backend transitions are authoritative.

## Forms and files

- Only draft form templates are mutable. Published templates are read-only/versioned.
- Render active fields/options from the selected template. `validation_rules` is an open backend-owned record; do not reproduce it without confirmed semantics.
- `FormValueInputRequest.value` is only specified as a string. Current UI encodings in `src/features/projects/template-fields.tsx` are assumptions pending backend confirmation.
- Upload through `POST /api/v1/files` using multipart `file` plus `context`; retain returned asset IDs. Download through authenticated `GET /api/v1/files/{file_asset_id}`.
- The contract declares no local MIME/size limits. Do not invent them; surface backend validation.

## Tickets and notifications

- Ticket recipients come only from `/api/v1/users/related`.
- Creator and target ownership governs ordinary ticket visibility/actions; backend authorization is final.
- `/ws/notifications` is outside OpenAPI. Do not invent payload types or lifecycle behavior.

## Role workflow boundaries

- Customer: create/manage projects, review applications/deliveries, submit final review/rating, tickets.
- Freelancer: onboarding/profile approval, resume/portfolio, eligible marketplace, applications, delivery/revision, ratings, tickets.
- Supervisor: category-scoped review work and tickets. Do not infer project assignment mechanics from role alone.
- Admin: users/RBAC, categories/templates, freelancer approval/levels, admin on-behalf project/application actions, reporting, operational oversight.
