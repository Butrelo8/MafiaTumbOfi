# Project State

## Current Position
- Phase: **Marketing homepage polish + press kit toggle** (2026-04-18 session). **`web/src/lib/showPressAssets.ts`** exports **`showPressAssetsSection`** — drives homepage **`#press`** block, hero “Material de prensa” CTA, **`MarketingLayout`** mobile “Press kit”, **`Layout.astro`** nav. Set **`false`** to hide without deleting markup. **`web/bun test`** green (**82** in `web/` at last run).
- **Earlier (2026-04-11):** Admin CRM wired end-to-end — `internal_notes` + `deleted_at`; admin API/UI, drip filter, etc. (see git history / prior STATE bullets if needed).
- Last completed: Press visibility wired to one shared flag + nav/hero aligned.
- Next up: **Commit** press-toggle files on a branch (`showPressAssets.ts`, `index.astro`, `MarketingLayout.astro`, `Layout.astro`) if you want that slice isolated; **or** resume prior **ship gate** (migrate + deploy API/web, smoke `/admin`) from 2026-04-11 notes. Repo still has **large unrelated dirty tree** — review **`git status`** before assuming any single feature is the only diff.

## Accumulated Decisions
- **2026-04-18:** Press kit visibility — **single source** **`showPressAssetsSection`** in **`web/src/lib/showPressAssets.ts`** so homepage section and layout nav stay in sync (frontmatter-only on `index.astro` alone cannot drive **`MarketingLayout`**).
- **2026-04-11 (session):** Drizzle **`bookings`** must declare **`internalNotes`** + **`deletedAt`** so ORM matches **`drizzle/0011_`** / **`0012_`** — rationale in **`DECISIONS.md`** (2026-04-12 entry).
- **2026-04-12 (prior):** **`deleted_at`** soft-delete — **`DELETE /api/admin/bookings/:id`**; operators see only non-deleted; recovery via SQL.
- **2026-04-12 (prior):** Admin search — client **~200ms** debounce; **AND** with pipeline pills; no server-side search yet.
- **2026-04-12 (prior):** **`internal_notes`** — **PATCH** + **`/admin/save-internal-notes`** relay; max 10k.
- **2026-04-11:** **Turso (libsql)** prod DB; **`ADMIN_CLERK_ID`**; Clerk **`authorizedParties`** + CORS expansion; mobile menu / Clerk modal ordering.

## Blockers & Open Questions
- **Ship gate:** many modified files on **`main`** (unstaged) — not only press-toggle; run **`git status`**, decide branch/PR scope, do **not** assume production matches local until merged and deployed.
- **DB:** prod/staging must have **`0011`** / **`0012`** before API that reads/writes them — **`bun run migrate`** (or Render migrate step) per **`DEPLOY.md`**.
- **Horizontal API scaling:** in-memory rate limits — **P2** Redis (or doc single-instance) in **`TODOS.md`**.
- **Stripe / monitoring:** **P3** / **P4** per **`TODOS.md`**.

## Session Notes
Last session: **2026-04-18** — **save state** after **press kit toggle** (`showPressAssets.ts`, conditional **`index.astro`** hero + press section, **`MarketingLayout`** / **`Layout.astro`** nav).
Stopped at: **Pause** — wide working tree; isolate commits or continue admin ship work per priority.
Resume with: **`cd web && bun test`** then **commit** press-toggle slice **or** **migrate + deploy** + smoke **`/admin`** per earlier plan; then **`TODOS.md`** next open card.

Optional: **`/dream`** to consolidate session signal into topic files.
