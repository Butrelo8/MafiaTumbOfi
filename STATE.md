# Project State

## Current Position
- Phase: **Admin CRM wired end-to-end** (2026-04-11 session) — `internal_notes` + `deleted_at` in **`src/db/schema.ts`**; **`src/routes/admin.ts`** — soft-delete **DELETE**, list/export filtered, **PATCH** `{ pipelineStatus, internalNotes }`, resend/PATCH on non-deleted rows only; **`processDripEmails`** skips soft-deleted; **`web/src/pages/admin.astro`** — search (debounced), pipeline pills, stale **Nuevo** badge, **`tel:`**, CSV (visible rows), drawer + save notes, soft-delete relay, sortable event date. Docs: **CHANGELOG**, **DECISIONS** (schema vs migrations). **`bun test`** green (**269** at last run).
- Last completed: Integration that had been **split** earlier (libs/migrations on `main` without full UI/API) is now **connected**; **`00-auth-protected.test.ts`** mock **`db`** chain fixed for `.where().orderBy().limit()` / export without **`.offset()`**.
- Next up: **Commit on a feature branch** → PR → deploy **API** (Render) + **web** (Vercel); run **`bun run migrate`** (or your prod migrate path) so **`0011`** / **`0012`** exist **before** new API ships. Then pick **`TODOS.md`** first **## Open** (e.g. **Infra — Distributed rate limiting**, P2) unless reprioritized.

## Accumulated Decisions
- **2026-04-11 (session):** Drizzle **`bookings`** must declare **`internalNotes`** + **`deletedAt`** so ORM matches **`drizzle/0011_`** / **`0012_`** and filters type-check — rationale in **`DECISIONS.md`** (2026-04-12 entry).
- **2026-04-12 (prior):** **`deleted_at`** soft-delete — **`DELETE /api/admin/bookings/:id`**; operators see only non-deleted; recovery via SQL.
- **2026-04-12 (prior):** Admin search — client **~200ms** debounce; **AND** with pipeline pills; no server-side search yet.
- **2026-04-12 (prior):** **`internal_notes`** — **PATCH** + **`/admin/save-internal-notes`** relay; max 10k.
- **2026-04-11:** **Turso (libsql)** prod DB; **`ADMIN_CLERK_ID`**; Clerk **`authorizedParties`** + CORS expansion; mobile menu / Clerk modal ordering.

## Blockers & Open Questions
- **Ship gate:** uncommitted / unpushed work — run **`git status`**, branch, PR; do **not** assume production has the new **`admin.astro`** + **`admin.ts`** until merged and deployed.
- **DB:** prod/staging must have columns from **`0011`** / **`0012`** before API that reads/writes them — **`bun run migrate`** (or Render migrate step) per **`DEPLOY.md`**.
- **Horizontal API scaling:** in-memory rate limits — **P2** Redis (or doc single-instance) in **`TODOS.md`**.
- **Stripe / monitoring:** **P3** / **P4** per **`TODOS.md`**.

## Session Notes
Last session: **2026-04-11** — **save state** after **admin CRM wiring** (schema, API, **`admin.astro`**, drip filter, tests, **CHANGELOG** / **DECISIONS**).
Stopped at: **Pause** — verify **git** locally (`git status`, branch, tests) before push/PR.
Resume with: **Migrate + deploy** API then web, smoke **`/admin`** (drawer, notes, delete, CSV); then **`TODOS.md`** next open card.

Optional: **`/dream`** to consolidate session signal into topic files.
