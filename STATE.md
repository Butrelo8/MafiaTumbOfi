# Project State

## Current Position
- Phase: Ship prep / backlog grooming + infra; **security post-review hardening** done in tree (see `DECISIONS.md` 2026-03-22, `BUGS.md` fixed entries); **booking** uses structured `logServerInfo` + `markBandEmailFailed` + empty-insert guard (`CHANGELOG` [Unreleased]).
- **Eng lead codebase review (2026-03-22):** Findings and deferred hygiene are in `DECISIONS.md` (same date, “Engineering lead codebase review”) and new **Open** items in `TODOS.md`: shared `allowedOrigins`, `/users/me` → `successResponse`, optional Playwright booking smoke. Ship order unchanged: VPS, Resend domain, Content/SEO first.
- Branch: **`main`** — run `git status` before assuming a clean tree; use a feature branch for new work (not direct to `main`).
- Last completed (this workstream): **Security — Post-review hardening** (safeLog, `Forwarded` proto fallback, `/health` rate limit, admin export matrix) + **booking observability** (`logServerInfo`, DRY failed-band update, `INSERT_RETURN_EMPTY` path + tests).
- Next up: **P2** open in `TODOS.md` — **Deploy — VPS**, **Resend domain**, **Content/SEO**; **API** hygiene todos (shared origins, `/me` envelope) when convenient; **Infra — Distributed rate limiting** when multi-instance; pick one vertical slice per branch.

## Accumulated Decisions
- 2026-03-17: Hold Scope — VPS deploy as primary milestone; Stripe webhook only when there is a product; no first-paying-customer / merch push yet.
- 2026-03-16: Deploy shape — Render (API + Bun + SQLite on `/data`), Vercel (`web/`), migrations at API startup.
- 2026-03-21: First admin — single INSERT with scalar subquery `EXISTS` for `is_admin` to avoid double-admin on concurrent first signups.
- 2026-03-21: CORS — allowlist-only; return `undefined` from `cors` `origin` callback when `Origin` is not in `allowedOrigins` so reviewers see explicit deny (no misleading first-origin reflection).
- 2026-03-22: Admin GET success bodies — align with global `{ data: T }` via `successResponse` so clients are not split between top-level `total` and wrapped payloads; export download includes the same envelope.
- 2026-03-22: Post-review hardening — `safeLog` (no stacks in prod), `Forwarded` + `X-Forwarded-Proto` for HTTPS, `/health` rate limit, admin export only via `ALLOW_*` or `NODE_ENV=development` (see `DECISIONS.md`).
- 2026-03-22: Booking `REQUEST_RECEIVED` — JSON info line via `logServerInfo` (stdout); band-email failure uses `markBandEmailFailed`; empty `.returning()` → 500 `INTERNAL_ERROR`.
- 2026-03-22: Eng lead review — document follow-ups in `TODOS.md` (DRY origins, `/me` `successResponse`, Playwright smoke); do not reorder launch priorities.

## Blockers & Open Questions
- Horizontal scaling: in-memory rate limits are per-process — resolve when deciding multi-instance API (Redis on Coolify vs documented single-instance); see **TODOS — Infra — Distributed rate limiting**.

## Session Notes
Last session: **Docs — eng lead review** — added `DECISIONS.md` entry, three **Open** `TODOS.md` items (shared allowlist, `/me` `successResponse`, Playwright smoke), `STATE.md` + `CHANGELOG` [Unreleased] pointers.
Stopped at: Resume from **Next up** above.
Resume with: Pick next **P2** from `TODOS.md` Open → **`git checkout -b feat/…`** → implement → `bun test` → commit / PR.
