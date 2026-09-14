# Slice 4: Freelancer Workflow

Status: In progress.

## Completed

- Freelancer onboarding creates the backend profile through React Hook Form and Zod.
- `/freelancer` loads the authoritative profile and supports profile editing and approval submission.
- Resume management supports upload, version listing, current selection, current-summary update, and deletion.
- Portfolio management supports create, edit, ordering, featured state, optional URL/file, and confirmed deletion.
- `/projects/available` provides the backend-filtered paginated marketplace and freelancer project detail.
- Project detail supports application submission and withdrawal using the current freelancer application returned by backend details.
- Accepted applications link to a direct project workbench gated by the backend-selected application.
- The workbench presents delivery/revision history and submits initial or revised delivery versions with authenticated file assets.

## Decisions

- `/auth/me` owns profile ID, onboarding need, approval status, and level.
- Approval prerequisites and transitions are backend-owned; the frontend submits and displays backend errors.
- Admin approval/rejection/level assignment is outside the freelancer UI.
- Resume and portfolio file validation remains backend-owned.
- Application state is derived per project from `GET /api/v1/projects/{project_id}` `applications[]`; withdrawal uses the returned `application_id` through the generated withdrawal operation. Never persist application IDs or add global application/assignment endpoints.
- A revision response is a new delivery version; no separate freelancer revision-response or close endpoint exists.
- Profile edits keep the server-rendered `/freelancer` page authoritative: the form resets when refreshed profile props change, and edits refresh the current route without navigating away first.
- `/freelancer/ratings` reads the backend freelancer-ratings response and displays the average plus rating comments; no client-side rating inference is used.

## Remaining Work

1. Slice 4 workflow verification.
