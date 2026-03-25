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
- Booking form: http://localhost:4321/booking  
- Admin: http://localhost:4321/admin (Clerk sign-in required; the **first user to sign in** becomes admin and can view bookings).

## Project Structure

```
MafiaTumbadaOfi/
├── src/                 # Hono API
│   ├── index.ts
│   ├── routes/          # auth, booking, users
│   ├── middleware/
│   ├── db/               # SQLite + Drizzle schema
│   └── lib/
├── web/                 # Astro frontend
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
| `bun test` | Run tests |
| `bun db:generate` | Generate Drizzle migrations |
| `bun db:migrate` | Run pending migrations (applies `drizzle/*.sql` via `scripts/run-migration.ts`; same as `bun run migrate`) |
| `bun db:upgrade-kit-snapshots` | Drizzle-kit only: upgrade internal migration journal/snapshot metadata (`drizzle-kit up:sqlite`); does **not** apply SQL to the DB |
| `bun db:studio` | Open Drizzle Studio |

## Scripts (web/)

| Command | Description |
|---|---|
| `bun dev` | Start Astro dev server (port 4321) |
| `bun build` | Build for Vercel (output in `.vercel/output/`) |
| `bun preview` | Same as `dev` (Vercel adapter does not support `astro preview`; use `vercel dev` for production-like local) |

## Environment Variables

- **API:** See root `.env.example` (PORT, FRONTEND_URL, DB_PATH, RESEND_API_KEY, BOOKING_NOTIFICATION_EMAIL).
- **Frontend:** See `web/.env.example` (PUBLIC_API_URL for the booking form).

## Deploy

- **API:** Render (Bun + SQLite on a persistent disk). See `render.yaml` and [DEPLOY.md](./DEPLOY.md).
- **Frontend:** Vercel (Astro SSR with `@astrojs/vercel`). Set root directory to `web/` and env vars as in DEPLOY.md.
