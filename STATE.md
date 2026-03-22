# Project State

## Current Position
- Phase: Ship prep / security & API hygiene (`feat/ship-0.5.0` or current feature branch — align with `git branch` when resuming).
- Last completed: **CORS allowlist-only** — disallowed `Origin` no longer falls back to `allowedOrigins[0]`; `Access-Control-Allow-Origin` omitted; tests in `security.test.ts` (see TODOS Completed + CHANGELOG [Unreleased]).
- Next up: **P2** — distributed rate limiting (Redis/Upstash or document single-instance in DEPLOY.md), or next P3 if staying on small API hygiene.

## Accumulated Decisions
- 2026-03-17: Hold Scope — VPS deploy as primary milestone; Stripe webhook only when there is a product; no first-paying-customer / merch push yet.
- 2026-03-16: Deploy shape — Render (API + Bun + SQLite on `/data`), Vercel (`web/`), migrations at API startup.
- 2026-03-21: First admin — single INSERT with scalar subquery `EXISTS` for `is_admin` to avoid double-admin on concurrent first signups.
- 2026-03-21: CORS — allowlist-only; return `undefined` from `cors` `origin` callback when `Origin` is not in `allowedOrigins` so reviewers see explicit deny (no misleading first-origin reflection).

## Blockers & Open Questions
- Horizontal scaling: in-memory rate limits are per-process — resolve when deciding multi-instance API (Redis/Upstash vs documented single-instance).

## Session Notes
Last session: 2026-03-21 / 22 (CORS shipped; tests green).
Stopped at: CORS todo closed; codebase ready for next backlog item.
Resume with: **Distributed rate limiting** open todo in `TODOS.md`, or `.gitignore` branch work if that was still in flight — run `git status` first.
