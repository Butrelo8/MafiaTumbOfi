# Project State

## Current Position
- Phase: Branch **`fix/redo-admin`** (verify vs `main` before merge); **P1 lead-funnel roadmap (slices 1–4)** closed in **`TODOS.md`** (**## Completed** → umbrella card).
- Last completed: **Content / SEO — Homepage & booking copy** (`index.astro` hero blurb, trust strip, `booking.astro` intro + form `h2` + FAQ); trust strip refactored to **4-col grid** + **SVG** icons (second cell uses **Discogs** path for “Repertorio propio + covers” — review trademark if implying official Discogs); **`TODOS.md`** roadmap card removed from Open + **Completed** entries refreshed.
- Next up: **P2+ Open** backlog — e.g. **Infra — Redis rate limiting**, **Monitoring / Sentry**, **Payments / Stripe** when needed; or **merge `fix/redo-admin`** if diff is only the shipped marketing/admin/copy work.

## Accumulated Decisions
<!-- Key decisions made during development. Keep each decision as:
     - YYYY-MM-DD: decision — rationale
-->
- 2026-04-11 (session start): `STATE.md` created — repo had no session handoff file; TODOS references STATE.md for booking schema context.
- 2026-04-11: **P1 funnel umbrella** moved to **## Completed** — Open list is P2+ only; avoids duplicate “shipped” roadmap card in **## Open**.
- 2026-04-11: **Trust strip** — CSS grid mirrors stats-bar rhythm; **Discogs** SVG used as decorative icon next to repertoire copy (not a product integration); **`aria-hidden`** on icon wrapper, visible text carries meaning.
- 2026-04-11: **Admin** — **`ADMIN_CLERK_ID`** env replaces first-user heuristic; **`getOrCreateUser`** reconciles **`is_admin`** when env set; migration **`0010_admin_explicit_clerk_ids.sql`**.

## Blockers & Open Questions
- **`fix/redo-admin`**: confirm scope (admin redo vs homepage/booking) and whether branch is **merge-ready** vs needs more commits.
- **Discogs logo**: if the site implies official Discogs presence, check **Discogs brand** guidelines; otherwise purely decorative next to “repertorio” is lower risk.

## Session Notes
Last session: 2026-04-11
Stopped at: **`STATE.md` save** after homepage trust strip (grid + SVG + Discogs) and **TODOS** roadmap hygiene.
Resume with: **`git status` / diff vs `main`** on `fix/redo-admin` → merge or continue Open tickets; run **`bun test`** before any merge. Optional: **`/dream`** to consolidate session notes into topic files.
