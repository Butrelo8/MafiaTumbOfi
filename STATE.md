# Project State

## Current Position
- Phase: `feat/ship-0.5.0` — ship prep / security & API hygiene backlog
- Last completed: Admin booking export hardened (`ALLOW_ADMIN_BOOKING_EXPORT` in production, audit log, tests — see DECISIONS 2026-03-21)
- Next up: Pick next P2 from TODOS (e.g. **CORS allowlist-only**)

## Accumulated Decisions
- 2026-03-17: Hold Scope — VPS deploy as primary milestone; Stripe webhook only when there is a product; no first-paying-customer / merch push yet.
- 2026-03-16: Deploy shape — Render (API + Bun + SQLite on `/data`), Vercel (`web/`), migrations at API startup.
- 2026-03-21: First admin — single INSERT with scalar subquery `EXISTS` for `is_admin` to avoid double-admin on concurrent first signups.

## Blockers & Open Questions
- Horizontal scaling: in-memory rate limits are per-process — resolve when deciding multi-instance API (Redis/Upstash vs documented single-instance).

## Session Notes
Last session: 2026-03-21 (inferred from DECISIONS / TODOS)
Stopped at: No prior STATE.md; workstream is feature branch with open P2 security/API items.
Resume with: **CORS origin fallback** in `src/index.ts` or other open P2s in TODOS.
