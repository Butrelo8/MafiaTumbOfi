# Project State

## Current Position
- Phase: Ship prep / API contract hygiene + infra backlog.
- Branch: **`main`** (uncommitted: admin JSON + CHANGELOG/TODOS/DEPLOY — commit on a feature branch per policy before merge).
- Last completed: **Admin list/export success JSON** — `GET /api/admin/bookings` and `GET /api/admin/export/bookings` use `successResponse`; payload under `data` (`bookings` + `total`, etc.); `web/src/pages/admin.astro` reads `data.bookings`; tests in `00-auth-protected.test.ts`; see TODOS Completed + CHANGELOG [Unreleased].
- Next up: **P2** — distributed rate limiting (Redis on Coolify when multi-instance, or document single-instance in DEPLOY.md). **P3** — `/health` version from package.json; other open TODOS as prioritized.

## Accumulated Decisions
- 2026-03-17: Hold Scope — VPS deploy as primary milestone; Stripe webhook only when there is a product; no first-paying-customer / merch push yet.
- 2026-03-16: Deploy shape — Render (API + Bun + SQLite on `/data`), Vercel (`web/`), migrations at API startup.
- 2026-03-21: First admin — single INSERT with scalar subquery `EXISTS` for `is_admin` to avoid double-admin on concurrent first signups.
- 2026-03-21: CORS — allowlist-only; return `undefined` from `cors` `origin` callback when `Origin` is not in `allowedOrigins` so reviewers see explicit deny (no misleading first-origin reflection).
- 2026-03-22: Admin GET success bodies — align with global `{ data: T }` via `successResponse` so clients are not split between top-level `total` and wrapped payloads; export download includes the same envelope.

## Blockers & Open Questions
- Horizontal scaling: in-memory rate limits are per-process — resolve when deciding multi-instance API (Redis on Coolify vs documented single-instance).

## Session Notes
Last session: 2026-03-22 — admin bookings/export `successResponse` alignment; `bun test` green (43 tests).
Stopped at: Local changes not yet committed; ready to branch + commit or continue with next TODOS item.
Resume with: **`git status`** → commit admin JSON work on a feature branch if desired → then **P2 rate limiting** (see `TODOS.md`) or **P3 health version**.
