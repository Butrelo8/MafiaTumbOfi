# Project State

## Current Position
- Phase: Ship prep / backlog grooming + infra. Security review findings live in `BUGS.md` (2026-03-22); follow-up work is **TODOS — Security — Post-review hardening** (P2).
- Branch: **`main`** (`main...origin/main`). **Uncommitted:** `TODOS.md` only — review diff before commit; use a feature branch per policy (not direct to `main`).
- Last completed (code): **Ops — Health version** — `getAppVersion()`, tests, `.env.example`; TODOS item closed.
- Next up: Commit or discard `TODOS.md` changes on a **`chore/*`** branch → then **Security — Post-review hardening** or next P2 (rate limiting / deploy / Content-SEO).

## Accumulated Decisions
- 2026-03-17: Hold Scope — VPS deploy as primary milestone; Stripe webhook only when there is a product; no first-paying-customer / merch push yet.
- 2026-03-16: Deploy shape — Render (API + Bun + SQLite on `/data`), Vercel (`web/`), migrations at API startup.
- 2026-03-21: First admin — single INSERT with scalar subquery `EXISTS` for `is_admin` to avoid double-admin on concurrent first signups.
- 2026-03-21: CORS — allowlist-only; return `undefined` from `cors` `origin` callback when `Origin` is not in `allowedOrigins` so reviewers see explicit deny (no misleading first-origin reflection).
- 2026-03-22: Admin GET success bodies — align with global `{ data: T }` via `successResponse` so clients are not split between top-level `total` and wrapped payloads; export download includes the same envelope.

## Blockers & Open Questions
- Horizontal scaling: in-memory rate limits are per-process — resolve when deciding multi-instance API (Redis on Coolify vs documented single-instance).
- Security follow-ups (non-blocking): see `BUGS.md` (2026-03-22) + TODOS **Security — Post-review hardening**.

## Session Notes
Last session: `code-review-graph` full build + visualize (local `.code-review-graph/graph.db` + `graph.html`); **save state** pause.
Stopped at: Working tree dirty — **`TODOS.md`** only (`git status`).
Resume with: **`git diff TODOS.md`** → **`git checkout -b chore/todos-…`** (or similar) → `git add` / `git commit` if keeping edits → implement **Security — Post-review hardening** or next **P2**.
