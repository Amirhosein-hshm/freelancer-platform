# AUTHORIZATION.md — Authorization Convention (RBAC)

This file defines the single, consistent authorization model used across all nine
bounded contexts in the `domain`/`application` layers. Every use case that gates an
action by role or ownership MUST follow this convention.

## 1. Roles

Roles remain exactly four: `admin`, `customer`, `freelancer`, `supervisor`. No new
roles are introduced by this convention, and no per-resource permission table exists.

## 2. The RBAC Schema

The existing RBAC shape (`Role`, `Permission`, `UserRole`, `RolePermission`) is
unchanged. The only thing that changes over time is the set of `permission_key`
values referenced by use cases, and the fact that use cases actually call
`IAuthorizationService.require_permission(...)`. Seeding the permission keys into the
DB is an **infrastructure concern** (Phase 2) — `domain`/`application` only reference
the string keys as constants.

## 3. Permission Keys

Permission keys follow `"<resource>.<action>"`, e.g. `project.create`, `project.apply`,
`category.manage`, `form.manage`, `ticket.assign`, `reporting.read`.

### 3.1 Two-tier ownership permission

For any use case that mutates a **specific owned resource** (a project, a review, a
rating), TWO permission tiers are defined:

- `<resource>.<action>_own` — the actor must ALSO be the resource's owner. The
  ownership check is made against the entity's own owner field, e.g.
  `project.customer_user_id == actor_id`.
- `<resource>.<action>_any` — bypasses the ownership check entirely and is granted to
  `admin` only.

The shared helper in `application/shared/authorization.py` implements this pattern:

```python
def authorize_owned_action(
    authz: IAuthorizationService,
    actor_id: EntityId,
    owner_id: EntityId,
    own_permission: str,
    any_permission: str,
) -> None:
    if actor_id == owner_id:
        authz.require_permission(actor_id, own_permission)
    else:
        authz.require_permission(actor_id, any_permission)
```

Known pairs: `project.manage_own` / `project.manage_any`,
`review.decide_own` / `review.decide_any`, `feedback.manage_own` / `feedback.manage_any`,
`ticket.close_own` / `ticket.close_any`.

### 3.2 Acting on behalf of another user (delegation)

When an actor performs an action on behalf of a **specific** non-admin user (for
example an admin submitting an application for a freelancer):

- Use a **SEPARATE use case** — never overload the self-service use case with an
  optional `on_behalf_of` parameter.
- Use a SEPARATE permission key with the suffix `_on_behalf`, e.g.
  `project.apply_on_behalf`.
- NEVER substitute the acting admin's id into a field whose business meaning identifies
  a specific non-admin actor (e.g. `ProjectApplication.freelancer_profile_id`,
  `SupervisorReview.supervisor_user_id`). Instead, record the actual performer in a new
  nullable audit field on the entity — e.g. `ProjectApplication.submitted_by_user_id`
  — which defaults to the actor in the self-service case and is set to the admin's id
  in the delegated case.
- Repository `add`/`update` signatures stay compatible: the audit field is just a new
  optional attribute, and it is surfaced on the corresponding Result DTOs.

### 3.3 Admin acting with their own elevated authority

When an admin acts with their OWN authority (not impersonating anyone), use the `_any`
permission tier from §3.1 and keep the admin's real id in whatever
`decided_by` / `changed_by` field already exists — never fabricate another user's id.
The one intentional exception is documented per use case (e.g. `ReviewDeliveryUseCase`
records `SupervisorReview.supervisor_user_id = actor_id` on the `_any` path because the
review record identifies who decided it).

## 4. Where the checks live

- `IAuthorizationService` (in `application/shared/authorization.py`) is the only port
  used for permission checks. `require_permission` raises `PermissionDeniedError` when
  the actor lacks the permission.
- The check is the FIRST step of `execute(...)`, before any other validation or
  repository access.
- Permission key strings are declared as module-level constants near the top of each use
  case module (e.g. `PERMISSION_PROJECT_MANAGE_OWN = "project.manage_own"`), following
  the existing `DEFAULT_LEVEL_KEY` style.
- The four system roles are immutable for removal/revocation: `RemoveRoleUseCase` and
  `RevokePermissionUseCase` raise `SystemRoleImmutableError` when the target role has
  `is_system=True`.
