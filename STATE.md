# Project State

## Current Position
- Phase: MTO web + API — marketing polish + admin UX
- Last completed: **`/booking/gracias`** — YouTube embed (**`HTA31yUX41A`**) + **`bookingThanksPresentation.ts`** + tests + e2e assert; **`/admin`** — **`MarketingLayout`**, dark table/legend/banners, **`btn-secondary`** export, **`adminPageTheme.test.ts`**; **`TODOS.md`** — both items moved to **## Completed**; **`CHANGELOG`** / **`DECISIONS`** updated (admin shell decision).
- Next up: **`git status`** on **`fix/minor-bugs`** — review diff, run **`bun test`** + **`bun run test:e2e`**, conventional commit(s), then push (you run **`git push`** per agent policy). Open backlog starts with **Infra — Redis rate limiting** in **`TODOS.md`**.

## Accumulated Decisions
- 2026-04-11: API Clerk `authorizedParties` must use **`clerkAuthorizedParties`** (`expandCorsAllowedOrigins(allowedOrigins)`) — raw env list caused **401** on `GET /api/admin/bookings` when the browser origin was **www** but Render had only apex **`PRODUCTION_URL`** (CORS already expanded; Clerk did not). See `DECISIONS.md` for full rationale.
- 2026-04-11: **`PUBLIC_SITE_URL`** included in API **`allowedOrigins`** raw list when set — keeps Clerk parties aligned if only that URL is configured on the API.
- 2026-04-11: **`/admin`** uses **`MarketingLayout`** (not light **`Layout`**) for brand parity + **`robots="noindex,nofollow"`**; see **`DECISIONS.md`**.

## Blockers & Open Questions
- None — uncommitted work is local only until you commit/push.

## Session Notes
Last session: 2026-04-11  
Stopped at: Feature work done; working tree dirty on **`fix/minor-bugs`** (see **`git status`**).  
Resume with: Review **`git diff`**, **`bun test`**, **`bun run test:e2e`**, commit with conventional messages (e.g. separate **`feat(web):`** commits for gracias vs admin if you want clean history), then push.
