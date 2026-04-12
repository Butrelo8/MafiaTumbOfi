# mafia-tumbada-ofi

> Professional web presence for Mafia Tumbada — official page, press kit, and booking form in one place.

Built for regional Mexican bands who want to look serious to promoters without needing any tech knowledge.

## Stack

- **Frontend:** Astro (static site, SEO, fast load)
- **API:** Hono + Bun
- **Database:** SQLite + Drizzle ORM (MVP)
- **Email:** Resend (booking form → email to band)

Clerk (auth) and Stripe (payments) are available in the codebase if you add an admin panel or ticket sales later.

## Booking flow

Form on site → `POST /api/booking` → validate → insert into SQLite (status `pending`) → Resend to band → confirmation email to requester → update status to `sent` or `failed`. Bookings are stored in the `bookings` table; band can reply from inbox or use a future admin to view them.

## Getting Started

```bash
# API
bun install
cp .env.example .env
# Fill RESEND_API_KEY, BOOKING_NOTIFICATION_EMAIL

bun db:generate
bun db:migrate
bun dev
```

In another terminal:

```bash
# Frontend (Astro)
cd web
bun install
cp .env.example .env
# PUBLIC_API_URL=http://localhost:3001 is the default (see root .env PORT)
bun dev
```

- API: http://localhost:3001  
- Site: http://localhost:4321  

## Lint and format

[Biome](https://biomejs.dev/) runs at the **repo root** on `src/**/*.ts`, `scripts/**/*.ts`, and `web/src/**/*.ts` only (`.astro` files are not linted/formatted by Biome yet). It respects **`.gitignore`** (including **`.code-review-graph/`**, which is ignored so local graph tooling does not break Biome’s UTF-8 reader).

```bash
bun run lint        # check
bun run format      # format write
bun run lint:fix    # check + safe/unsafe fixes (e.g. import cleanup)
```

Run `bun run lint` before opening a PR or shipping.

- Booking form: http://localhost:4321/booking  
- Admin: http://localhost:4321/admin (Clerk sign-in required; API **`ADMIN_CLERK_ID`** must match your Clerk user id — see root **`.env.example`**; bookings load in pages of 50 via `GET /api/admin/bookings?limit=&offset=`). **Danger zone — vaciar todas las solicitudes:** `POST /api/admin/bookings/delete-all` hard-deletes every row in **`bookings`** (including soft-deleted). Gated like export: **`ALLOW_ADMIN_DELETE_ALL_BOOKINGS=true`** or **`NODE_ENV=development`** on the API; UI uses **`/admin/delete-all-bookings`** relay with phrase **`DELETE_ALL_BOOKINGS`** and optional **`dryRun`** for row count.

**Versioning:** Root `package.json` and `web/package.json` use the **same semver** for releases. Frontend `GET /health` and `GET /api/health` return `version` from `web/package.json`, overridable with `APP_VERSION` / `RELEASE_VERSION` (see `web/.env.example`; same semantics as the API `GET /health`). The Vercel adapter does not support `astro preview` locally; use **`bun run test:e2e`** (Playwright + `astro dev` on port **4329**) for a deterministic booking UI smoke, or `vercel dev` for production-like SSR.

### E2E (Playwright — booking smoke)

From repo root (after `bun install` in `web/` once):

```bash
cd web && bunx playwright install chromium   # first machine only
bun run test:e2e                             # from repo root, or: cd web && bun run test:e2e
```

Tests mock `POST …/api/booking` in the browser (no real API, DB, or Resend). Playwright starts **`astro dev`** on **127.0.0.1:4329** so it does not collide with a dev server on 4321. Specs live under **`web/e2e/*.e2e.ts`** (that suffix keeps **Bun** from treating them as `bun test` files).

## Project Structure

```
MafiaTumbadaOfi/
├── src/                 # Hono API
│   ├── index.ts
│   ├── routes/          # booking, users, admin
│   ├── middleware/
│   ├── db/               # SQLite + Drizzle schema
│   └── lib/
├── web/                 # Astro frontend
│   ├── e2e/             # Playwright specs (*.e2e.ts — not run by bun test)
│   ├── src/data/        # members.ts, socials.ts (official band links)
│   ├── src/pages/       # index, booking
│   └── public/
├── drizzle/             # Generated migrations
└── data/                # SQLite file (created on first run)
```

## Scripts (root)

| Command | Description |
|---|---|
| `bun dev` | Start API with hot reload |
| `bun start` | Start API (production) |
| `bun test` | Run API + unit tests (`bun test`) |
| `bun run test:e2e` | Playwright: booking form smoke (`web/`, mocked API) |
| `bun run lint` | Biome check (`src/`, `scripts/`, `web/src/**/*.ts`) |
| `bun run format` | Biome format (write) |
| `bun run lint:fix` | Biome check with `--write --unsafe` |
| `bun db:generate` | Generate Drizzle migrations |
| `bun db:migrate` | Run pending migrations (applies `drizzle/*.sql` via `scripts/run-migration.ts`; same as `bun run migrate`) |
| `bun db:upgrade-kit-snapshots` | Drizzle-kit only: upgrade internal migration journal/snapshot metadata (`drizzle-kit up:sqlite`); does **not** apply SQL to the DB |
| `bun db:studio` | Open Drizzle Studio |

## Scripts (web/)

| Command | Description |
|---|---|
| `bun dev` | Start Astro dev server (port 4321) |
| `bun build` | Build for Vercel (output in `.vercel/output/`) |
| `bun preview` | Not supported with `@astrojs/vercel/serverless` — use `vercel dev` or **`bun run test:e2e`** for local checks |
| `bun run test:e2e` | Playwright booking smoke (starts dev server on port 4329) |
| `bun run test:e2e:install` | `playwright install chromium` (first-time browsers) |

## Environment Variables

- **API:** See root `.env.example` (PORT, FRONTEND_URL, `DB_PATH`, `TURSO_DATABASE_URL` / `TURSO_AUTH_TOKEN`, **ADMIN_CLERK_ID**, RESEND_API_KEY, BOOKING_NOTIFICATION_EMAIL).
- **Frontend:** See `web/.env.example` (`PUBLIC_API_URL`, `PUBLIC_SITE_URL` for canonicals / absolute **OG image**, optional **`PUBLIC_ALLOW_INDEXING=false`** for **`noindex`** on previews).

## Email (Resend)

Booking uses **two** sends from the API (`src/routes/booking.ts`):

| Role | Env var (API / Render) | Notes |
|------|------------------------|--------|
| **Band inbox** — “new booking” alert | `BOOKING_NOTIFICATION_EMAIL` | Required. Any address you can **receive** at (Gmail, `bookinginfo@yourdomain` with Cloudflare Email Routing → Outlook, etc.). |
| **From** — visible sender for both emails | `RESEND_FROM_EMAIL` | Optional. If unset, uses `onboarding@resend.dev`. For a real `@mafiatumbada.com` **From**, verify the domain in [Resend → Domains](https://resend.com/domains) (DNS in Cloudflare), then set e.g. `noreply@mafiatumbada.com`. |
| **Customer “Recibimos tu solicitud”** | *(none)* | Always sent **to** the email the visitor typed in the form. Until a domain is verified in Resend, delivery to arbitrary addresses may be limited — see `DEPLOY.md` and `BUGS.md`. |

**Production:** change values on **Render** (API service → Environment), not in the Resend dashboard alone. `RESEND_API_KEY` stays from Resend; rotate there if needed.

More deploy detail: [DEPLOY.md](./DEPLOY.md) (Resend domain, `PRODUCTION_URL` / CORS).

## Deploy

- **API:** Render (Bun + **Turso** / libsql). See `render.yaml` and [DEPLOY.md](./DEPLOY.md).
- **Frontend:** Vercel (Astro SSR with `@astrojs/vercel`). Set root directory to `web/` and env vars as in DEPLOY.md.
