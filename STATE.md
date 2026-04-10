# Project State

## Current Position
- Phase: Post–code-review hardening (API + deploy hygiene); primary milestone still **VPS deploy** (see TODOS roadmap).
- Last completed: Admin bookings **pagination + export cap** shipped: `src/lib/adminBookingsQuery.ts`, `src/routes/admin.ts` (`limit`/`offset`, `hasMore`; export SQL counts + `ADMIN_EXPORT_MAX_ROWS`), `web/src/pages/admin.astro` (`?page=`), tests (`admin-bookings-pagination.test.ts`, mock updates in `00-auth-protected.test.ts`); **TODOS** item closed; **CHANGELOG** / **DECISIONS** / **DEPLOY** / **.env.example** / **README** updated.
- Next up: **Open** `TODOS.md` → e.g. **CI: tests on push/PR** (P2) or next P3 code-review item; fix or triage **3 failing root `bun test` cases** (see Blockers) before treating suite as green.

## Accumulated Decisions
- 2026-04-10: Admin list uses **offset pagination** (default limit 50, max 200); export **caps rows** per request (`ADMIN_EXPORT_MAX_ROWS`, default 10k, hard max 50k) with **`truncated` / `warning`**; **`last24hCount`** via SQL, not in-memory filter — see `DECISIONS.md`.
- 2026-04-10: Rate limit refactor keeps **fixed-window** `count` + `resetAt` behavior (not sliding window) so limits match pre-refactor semantics; `createRateLimiter` + shared cleanup interval.
- 2026-04-10: Booking persist failures expose **`BOOKING_PERSIST_FAILED`** to clients; throws log **`BOOKING_INSERT_FAILED`**, empty `returning` logs **`INSERT_RETURN_EMPTY`** — same public code, distinct log codes for ops.
- 2026-04-10: `getClientId` documents **`unknown` single-bucket** for local dev without proxy; `DEPLOY.md` notes parallel.

## Blockers & Open Questions
- **`bun test` at repo root:** 3 failures **not** from admin pagination — `src/health.test.ts` (`APP_VERSION` override vs cached version), `web/src/lib/homepageHero.test.ts` (2 cases: hero video markup / marketing CSS expectations).
- None blocking merge of admin slice specifically; fix or quarantine above before release gate.

## Session Notes
Last session: 2026-04-10  
Stopped at: **`STATE.md` saved** after admin bookings pagination/export-cap implementation + docs.  
Resume with: Pick next **Open** task in `TODOS.md` (CI P2 or other); run `bun test` and address **health + homepageHero** failures if you need full green.

Consider running `/dream` to fold session notes into topic files if you use that workflow.
