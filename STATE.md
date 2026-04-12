# Project State

## Current Position
- Phase: Post–P1 lead funnel; **admin CRM** on **2026-04-12** — sort, filters, drawer, **`internal_notes`**, stale **Nuevo** badge, pipeline summary, quick actions, CSV (vista actual), **debounced search** (name/email/phone **AND** pills), **soft-delete** (`deleted_at` + **`DELETE /api/admin/bookings/:id`** + drawer **Ocultar** + **`/admin/delete-booking`** relay). Prod: **Vercel + Render + Turso** (`DECISIONS.md`).
- Last completed: **Admin — Soft delete** — migration **`0012_booking_soft_delete.sql`**, **`bookingNotSoftDeleted`** on list / export / **PATCH** / resend / **`processDripEmails`**, Astro relay + **`?deleted=ok`** banner; tests include **`admin-soft-delete.test.ts`**. Same stretch: **Admin — Search** (`adminBookingSearch.ts`, **`applyRowFilters`**). **`bun test`** green (**282**).
- Next up: **`TODOS.md`** first **## Open** — **Infra — Distributed rate limiting** (P2) unless reprioritized.

## Accumulated Decisions
- **2026-04-12:** **`deleted_at`** soft-delete — **`DELETE /api/admin/bookings/:id`**; operators see only non-deleted; recovery via SQL — **`DECISIONS.md`**.
- **2026-04-12:** **Admin search** — client-only **~200ms** debounce; **AND** with pipeline pills; no server-side search yet.
- **2026-04-12:** **`internal_notes`** — operator **`PATCH`** + **`/admin/save-internal-notes`** relay; max 10k — **`DECISIONS.md`**.
- **2026-04-11:** **Turso (libsql)** prod DB — **`@libsql/client`** + Drizzle; **`render.yaml`** without persistent disk.
- **2026-04-11:** **`ADMIN_CLERK_ID`** — only configured Clerk id is admin; migration **`0010`**.
- **2026-04-11:** Clerk **`authorizedParties`** aligned with CORS / **`expandCorsAllowedOrigins`**.
- **2026-04-11:** **Clerk vs mobile menu** — defer **`closeMenu()`** after **`.menu-auth`** so modals are not under overlay; **`.hero-video`** **`pointer-events: none`** (`CHANGELOG` / marketing).

## Blockers & Open Questions
- **Horizontal API scaling:** in-memory rate limits per process — **P2** Redis (or doc single-instance) in **`TODOS.md`** until multi-replica.
- **Stripe:** webhook not shipped — **P3**.
- **Monitoring:** Sentry optional — **P4**.
- **Deploy / migrate:** run **`bun run migrate`** where prod/staging lives so **`0011_booking_internal_notes`** and **`0012_booking_soft_delete`** exist before notes PATCH / soft-delete (Render startup migrate if you rely on it).
- **Release hygiene:** API **Render** envs — **`TURSO_*`**, **`ADMIN_CLERK_ID`**, **`DRIP_*`** as per **`DEPLOY.md`** / **`.env.example`**; Vercel **`web`** vars separate.

## Session Notes
Last session: **2026-04-12** — **save state** after **Admin — Search** + **Admin — Soft delete** shipped (API, Astro, tests, **CHANGELOG** / **TODOS** / **DECISIONS**).
Stopped at: **Pause** — local **git** not re-verified in this step; run **`git status`** before assuming clean.
Resume with: **`TODOS.md` → Infra — Distributed rate limiting**; confirm migration **`0012`** applied in any target environment.

Optional: **`/dream`** if you consolidate session notes into topic files.
