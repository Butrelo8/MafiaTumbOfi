# Project State

## Current Position
- Phase: Ship prep / backlog grooming + infra.
- Branch: **`main`** — **uncommitted:** `TODOS.md` only (Content/SEO split into four items; Ops — Health version `Solution` / `Done When` filled). Confirm with `git status` / `git log` whether admin JSON work is already committed.
- Last completed (this workstream): **Ops — Health version** — `getAppVersion()` from `package.json` + `APP_VERSION` / `RELEASE_VERSION`; tests in `appVersion.test.ts` + `health.test.ts`; `.env.example` updated; TODOS item closed.
- Next up: **P2** rate limiting / deploy slice / Content/SEO; or commit doc + code changes on a feature branch per policy.

## Accumulated Decisions
- 2026-03-17: Hold Scope — VPS deploy as primary milestone; Stripe webhook only when there is a product; no first-paying-customer / merch push yet.
- 2026-03-16: Deploy shape — Render (API + Bun + SQLite on `/data`), Vercel (`web/`), migrations at API startup.
- 2026-03-21: First admin — single INSERT with scalar subquery `EXISTS` for `is_admin` to avoid double-admin on concurrent first signups.
- 2026-03-21: CORS — allowlist-only; return `undefined` from `cors` `origin` callback when `Origin` is not in `allowedOrigins` so reviewers see explicit deny (no misleading first-origin reflection).
- 2026-03-22: Admin GET success bodies — align with global `{ data: T }` via `successResponse` so clients are not split between top-level `total` and wrapped payloads; export download includes the same envelope.

## Blockers & Open Questions
- Horizontal scaling: in-memory rate limits are per-process — resolve when deciding multi-instance API (Redis on Coolify vs documented single-instance).

## Session Notes
Last session: Implemented `/health` version from `package.json` + env overrides; tests; CHANGELOG + TODOS completed entry.
Stopped at: Ready to branch/commit (policy: not on `main`).
Resume with: **`git checkout -b chore/health-version`** → `git add` / `git commit` → next open **P2** or **Content/SEO** task.
