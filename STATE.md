# Project State

## Current Position
- Phase: Ship prep / backlog grooming + infra; **security review (2026-03-22)** logged in `BUGS.md`, follow-up captured in **TODOS — Security — Post-review hardening**.
- Branch: **`main`** — confirm dirty files with `git status` before committing doc updates.
- Last completed (this workstream): **Ops — Health version** — `getAppVersion()` from `package.json` + `APP_VERSION` / `RELEASE_VERSION`; tests in `appVersion.test.ts` + `health.test.ts`; `.env.example` updated; TODOS item closed.
- Next up: **P2** — **Security — Post-review hardening** (logs, proxy docs, optional `/health` limit, export gate); or distributed rate limiting / deploy / Content-SEO; use a feature branch for any commit per policy.

## Accumulated Decisions
- 2026-03-17: Hold Scope — VPS deploy as primary milestone; Stripe webhook only when there is a product; no first-paying-customer / merch push yet.
- 2026-03-16: Deploy shape — Render (API + Bun + SQLite on `/data`), Vercel (`web/`), migrations at API startup.
- 2026-03-21: First admin — single INSERT with scalar subquery `EXISTS` for `is_admin` to avoid double-admin on concurrent first signups.
- 2026-03-21: CORS — allowlist-only; return `undefined` from `cors` `origin` callback when `Origin` is not in `allowedOrigins` so reviewers see explicit deny (no misleading first-origin reflection).
- 2026-03-22: Admin GET success bodies — align with global `{ data: T }` via `successResponse` so clients are not split between top-level `total` and wrapped payloads; export download includes the same envelope.
- 2026-03-22: Post-review hardening — `safeLog` (no stacks in prod), `Forwarded` proto fallback for HTTPS, `/health` rate limit, admin export only via `ALLOW_*` or `NODE_ENV=development`.

## Blockers & Open Questions
- Horizontal scaling: in-memory rate limits are per-process — resolve when deciding multi-instance API (Redis on Coolify vs documented single-instance).
- Security follow-ups (non-blocking): production log redaction; proxy `x-forwarded-proto` contract; optional `/health` rate limit; stricter admin-export env matrix — see `BUGS.md` + TODOS **Security — Post-review hardening**.

## Session Notes
Last session: Full codebase security review; findings recorded in `BUGS.md`, actionable slice in `TODOS.md`, state synced here.
Stopped at: Documentation-only updates; commit on a feature branch when ready.
Resume with: **`git checkout -b chore/security-review-followups`** (or similar) → commit `BUGS.md`, `TODOS.md`, `STATE.md` → implement **Security — Post-review hardening** or next **P2**.