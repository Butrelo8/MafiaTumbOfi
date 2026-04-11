# Project State

## Current Position
- Phase: **`main`** (last check: clean vs `origin/main`); **P1 lead-funnel roadmap (slices 1–4)** closed — see **`TODOS.md`** **## Completed**.
- Last completed: **Marketing shell** — `.marketing-main` **`padding-top`** matches fixed header so **“Ver solicitudes”** is clickable (**`marketing-press.css`**). **Clerk** — **`MarketingLayout.astro`** closes fullscreen **`.mobile-menu`** after **`.menu-auth`** click (`setTimeout` + `closeMenu`) so Sign in / Sign up modals are not trapped under **z-index 200**; **`.hero-video`** **`pointer-events: none`**. **Auth** — **`ADMIN_CLERK_ID`** on API (**`adminClerkConfig.ts`**, **`getOrCreateUser`** reconcile + migration **`0010_admin_explicit_clerk_ids.sql`**); first-user-admin heuristic removed.
- Next up: **P2+** in **`TODOS.md`** (Redis rate limit, Sentry, Stripe, VPS, etc.). **Ops:** **Render** API needs **`TURSO_DATABASE_URL`** + **`TURSO_AUTH_TOKEN`** (no **`DB_PATH`** for remote Turso); ensure **`ADMIN_CLERK_ID`** set; **`PUBLIC_SIGN_UP_COMING_SOON`** on Render is **unused** (safe to delete). Run **`bun test`** before next ship / PR.

## Accumulated Decisions
<!-- Key decisions made during development. Keep each decision as:
     - YYYY-MM-DD: decision — rationale
-->
- 2026-04-11 (session start): `STATE.md` created — repo had no session handoff file; TODOS references STATE.md for booking schema context.
- 2026-04-11: **P1 funnel umbrella** moved to **## Completed** — Open list is P2+ only; avoids duplicate “shipped” roadmap card in **## Open**.
- 2026-04-11: **Trust strip** — CSS grid mirrors stats-bar rhythm; **Discogs** SVG used as decorative icon next to repertoire copy (not a product integration); **`aria-hidden`** on icon wrapper, visible text carries meaning.
- 2026-04-11: **Admin** — **`ADMIN_CLERK_ID`** env replaces first-user heuristic; **`getOrCreateUser`** reconciles **`is_admin`** when env set; migration **`0010_admin_explicit_clerk_ids.sql`**.
- 2026-04-11: **Fixed header vs main content** — **`padding-top`** on **`.marketing-main`** aligns slot content below **`.site-header`** so overlays do not eat clicks (admin strip link).
- 2026-04-11: **Clerk modal vs mobile menu** — defer **`closeMenu()`** after **`.menu-auth`** click so Clerk modal is not under fullscreen overlay; **`.hero-video`** does not capture pointer events.
- 2026-04-11: **Turso (libsql)** — prod API uses **`@libsql/client`** + **`drizzle-orm/libsql`** when Turso env set without **`DB_PATH`**; embedded replica when Turso + **`DB_PATH`**; else **`bun:sqlite`**. **`render.yaml`** drops persistent disk.

## Blockers & Open Questions
- **Discogs logo**: if the site implies official Discogs presence, check **Discogs brand** guidelines; otherwise purely decorative next to “repertorio” is lower risk.
- **Release hygiene:** confirm **Vercel** / **Render** envs match **`.env.example`** / **`web/.env.example`** (e.g. **`ADMIN_CLERK_ID`** only needed on **API**, not Vercel).

## Session Notes
Last session: 2026-04-11  
Stopped at: **`STATE.md` save** — branch **`main`**; marketing padding + Clerk menu stacking + **`ADMIN_CLERK_ID`** auth path + Render env note (**`PUBLIC_SIGN_UP_COMING_SOON`** unused in repo).  
Resume with: **`git pull`** if collaborating → pick next **P2** card from **`TODOS.md`** or ship checklist (**`bun test`**, env audit). Optional: **`/dream`** to consolidate session notes into topic files.
