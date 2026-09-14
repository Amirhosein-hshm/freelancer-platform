# Project Rules

## Source of truth

Use this order when sources conflict:

1. Explicit business requirements.
2. Explicit project decisions/constraints.
3. Backend behavior and authorization.
4. `openapi.json` and `generated/api`.
5. Existing frontend behavior.
6. Tests.
7. Documentation.
8. Inference.

Do not silently resolve conflicts. Record the conflict and authoritative decision in `docs/context/decisions.md`. Never turn an inference into a rule.

## Repository boundaries

- Frontend only. Do not change backend behavior, contracts, migrations, or tests.
- Before changing Next.js code, read the relevant Next 16 guide under `node_modules/next/dist/docs/` as required by `AGENTS.md`.
- API authority: `openapi.json`; generated models/hooks: `generated/api`; generation config: `orval.config.ts` and `src/lib/api/mutator.ts`.
- Never hand-edit `generated/api` or duplicate DTOs/enums in Markdown or handwritten types.
- Backend lifecycle, eligibility, ownership, and authorization are authoritative. Frontend guards only improve UX and must still handle `401`, `403`, `409`, and `422`.

## Architecture

- Next.js App Router with `(public)`, `(auth)`, `(dashboard)`, and `(dev)` route groups.
- Dependency direction: `app/features/components -> lib -> generated`.
- Prefer Server Components for initial composition/reads. Use Client Components for interaction, browser APIs, and mutation state.
- URL search params own shareable list state (filters, pagination, sorting, tabs). Local state owns transient UI state.
- Use TanStack Query for interactive server synchronization; invalidate only affected keys.
- Session traffic goes through same-origin `/api/v1/[...path]`; tokens remain HTTP-only cookies and are stripped from browser-visible responses.
- Use existing error, envelope, pagination, URL-query, form, file, and UI helpers before adding abstractions.

## UI and quality

- Persian-first RTL UI; keep Latin identifiers/emails/codes LTR where needed.
- Implemented tokens and typography in `src/app/globals.css` and `src/app/layout.tsx` are authoritative. Current font is Vazirmatn.
- Reuse `src/components/ui` primitives and Lucide icons. Preserve keyboard access, visible focus, error summaries/live regions, responsive layout, dark mode, and reduced motion.
- Every interactive form must use React Hook Form for registration/state and Zod through `@hookform/resolvers` for validation; reuse the shared field components and `FormProvider` pattern instead of ad-hoc controlled state or manual submit parsing.
- Do not invent API-backed counts, filters, validation rules, file limits, WebSocket payloads, or permissions absent from the contract/backend evidence.
- Validate proportionally with `pnpm test`, `pnpm typecheck`, `pnpm lint`, and `pnpm build`; inspect the final diff and preserve unrelated user changes.
