# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project

**mafia-tumbada-ofi** — Official website + admin CRM for a regional Mexican band. Handles booking form submissions, Clerk-gated admin dashboard, and email drip campaigns.

## Commands

### API (root)

```bash
bun dev              # API dev server on :3001 (hot reload)
bun test             # Unit + integration tests
bun run lint         # Biome check
bun run format       # Biome format --write
bun run lint:fix     # Biome check --write --unsafe
```

### Database

```bash
bun run db:generate  # Generate Drizzle migrations after schema changes
bun run db:migrate   # Apply pending migrations
bun run db:studio    # Drizzle Studio GUI
```

### Frontend (web/)

```bash
cd web && bun dev            # Astro dev server on :4321
cd web && bun build          # Production build (Vercel adapter)
cd web && bun run test:e2e   # Playwright booking smoke test (mocked API, port 4329)
```

### Single test file

```bash
bun test src/routes/booking.test.ts
```

## Architecture

Two separate runtimes, deployed independently:

`**src/` — Hono + Bun API** (Render)

- Entry: `src/index.ts` — middleware setup + route mount
- Routes: `src/routes/` — `booking.ts` (public), `admin.ts` (Clerk-gated), `internal.ts` (drip cron)
- DB: `src/db/schema.ts` (Drizzle/libsql), auto-detects Turso vs local file via env vars
- Libs: `src/lib/` — lead scoring, drip scheduling, Resend email helpers, Zod Spanish error messages

`**web/` — Astro SSR** (Vercel)

- Pages: `web/src/pages/` — marketing, booking form, admin dashboard, API relay routes
- Admin relay routes in `web/src/pages/admin/*.ts` proxy to the Hono API (avoids CORS in admin UI)
- Auth via Clerk middleware: `web/src/middleware.ts`

`**drizzle/` — Migrations** — edit `src/db/schema.ts` → `db:generate` → `db:migrate`

## Key Patterns

**DB environment detection** (`src/db/detect.ts`): uses Turso when both `TURSO_DATABASE_URL` + `TURSO_AUTH_TOKEN` are set; falls back to file SQLite (`DB_PATH`, default `./data/sqlite.db`).

**Admin auth**: `ADMIN_CLERK_ID` env var must match the JWT `sub` from Clerk.

**Soft-delete**: admin delete sets `deletedAt`; rows are filtered out of all queries. Hard-delete requires `ALLOW_ADMIN_DELETE_ALL_BOOKINGS=true`.

**Booking pipeline**: form submit → Zod validate → compute `leadScore` (0–1000) + `leadPriority` → insert → send Resend emails → schedule drip dates.

**Drip cron**: external Render cron POSTs `/api/internal/process-drip` with `DRIP_CRON_SECRET` bearer token hourly. Processes batches of `DRIP_BATCH_SIZE` (default 20) rows.

## Linting

Biome applies only to `src/**/*.ts`, `scripts/**/*.ts`, `web/src/**/*.ts`. Astro `.astro` files are excluded. Style: single quotes, no semicolons, 100-char line width, `noExplicitAny: error`.

## Environment Variables

See `.env.example` (root) and `web/.env.example`. Critical:

- `TURSO_DATABASE_URL` + `TURSO_AUTH_TOKEN` — prod DB (omit to use local SQLite)
- `RESEND_API_KEY`, `BOOKING_NOTIFICATION_EMAIL` — email delivery
- `ADMIN_CLERK_ID`, `CLERK_SECRET_KEY` — admin access
- `DRIP_CRON_SECRET` — shared secret for cron endpoint

## Architecture Decisions

- Backend on Render (free tier, keep-alive via cron-job.org)
- Frontend on Vercel
- Auth with Clerk (env var for first admin)

## Code style

- See .cursor/rules/ for detailed conventions
- TypeScript strict mode always
- Hono routes follow REST naming
- Drizzle schema is source of truth for types

## Workflow

- Claude executes code; user plans and architects
- Plans in ticket format: What / Why / Context / Solution / Done When / Effort / Priority / Depends On
- No code generated unless explicitly asked

## Conventions

- Conventional Commits
- Drizzle for all queries, no raw SQL

## Design system

Source of truth: `DESIGN.md` (project root).

When running `/design-review`, `/review`, `/qa`, or any frontend skill:

- Read `DESIGN.md` before evaluating or generating UI
- Flag violations: wrong font stack, gold-dominant palette, centered hero template, uniform section padding, AOS zoom/flip, Cormorant on body text
- Token reference: color (`--accent` = veracruz turquoise, `--gold` = signature-only), type (`--ff-display` = Cormorant headline-only, `--ff-body` = Inter, `--ff-mono` = JetBrains Mono for tabular data), spacing (`--space-section` for major, `--space-lg` for editorial blocks)
- Direction: Veracruz Noir — editorial press kit × regional mexicano × gulf-coast noir
- Audience: fans lead homepage, promoters deep-link `/contratacion`

