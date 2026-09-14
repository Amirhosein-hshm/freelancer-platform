# Slices 1-2: Foundation Record

Status: Completed. This is a regression guide, not an implementation narrative.

## Implemented

- Authentication pages/forms: login, register, forgot password, change password, logout.
- Protected routing, refresh/logout handling, HTTP-only session cookies, server session reads.
- Responsive role-aware application shell, dashboard, dark mode, RTL/Persian typography.
- Orval-generated client/models and same-origin API proxy.
- Shared API error/envelope, pagination, URL-query, formatting, motion, and auth helpers with focused tests.
- Shared accessible UI/form states: loading, empty/error states, dialogs, tables, pagination, live region, error summary.
- Shared authenticated file upload/download primitives.

## Durable constraints

- Preserve the server-managed token boundary and single refresh/retry behavior.
- `/auth/me` remains the session/role authority; frontend role checks are UX only.
- Generated clients remain unmodified; handwritten helpers normalize rather than redefine contracts.
- Existing UI tokens in `src/app/globals.css` and primitives in `src/components/ui` are the design-system authority.

## Deviations/risks

- The shell intentionally advertises later workflow routes before those pages exist; see `docs/context/decisions.md`.
- The onboarding route is only a placeholder and does not make Slice 4 complete.

## Main locations

`src/app/(auth)`, `src/app/(dashboard)/dashboard`, `src/app/api/v1/[...path]`, `src/proxy.ts`, `src/features/auth`, `src/components/shell`, `src/components/ui`, `src/lib/api`, `src/lib/auth`, `src/lib/url`.

