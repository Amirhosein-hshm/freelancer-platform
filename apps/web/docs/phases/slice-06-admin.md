# Slice 6: Admin Workflow

Status: In progress.

## Completed

- Admin dashboard loads backend system analytics.
- Dedicated admin reports load dashboard, user, project, freelancer, and customer statistics.
- User list/create/detail, activation, blocking, deletion, role assignment, and profile update are available.
- Freelancer approval-status list, approval/rejection, level assignment/history, profile creation, and soft deletion are available; profile creation is wired into the list route.
- Category creation, edit, deletion, and category-level supervisor assignment/removal are available.
- Form-template list/detail, creation, draft name editing, publish/delete, and field/option CRUD controls are available for drafts; published templates remain read-only.
- Admin-on-behalf project, application, and ticket operations are available through generated endpoints.
- Dedicated `/admin/reports` view loads dashboard, user, project, freelancer, and customer statistics.

## Decisions

- Permission grant/revoke is out of scope; admin role assignment is the required RBAC capability.
- Supervisor assignment is category-level; no project-level assignment endpoint is assumed.
- Backend authorization, lifecycle, template versioning, and validation remain authoritative.
- Admin forms use React Hook Form and Zod; generated API models are not duplicated.

## Remaining Work

- Replace remaining native prompt-based note entry with shared accessible dialogs.
- Improve API error presentation and field-level messages across the remaining admin forms.
- Complete live-backend workflow verification.
- Verify the admin category assignment path enables Slice 5 supervisor review end to end.

## Known Issues

- Some existing admin modules use compact markup and generic error toasts; they require further hardening before production sign-off.
- Live backend verification is blocked while `http://127.0.0.1:8000` is unavailable.
