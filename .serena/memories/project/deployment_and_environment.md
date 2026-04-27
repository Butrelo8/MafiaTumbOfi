## Deployment & Environment

**Deployment:**
- Backend (API): Render (free tier, keep-alive via cron-job.org)
- Frontend: Vercel

**Critical Environment Variables:**

API (root `.env`):
- `TURSO_DATABASE_URL` + `TURSO_AUTH_TOKEN` — prod DB (omit to use local SQLite)
- `RESEND_API_KEY` — email delivery
- `BOOKING_NOTIFICATION_EMAIL` — recipient for booking alerts
- `ADMIN_CLERK_ID` — first admin (matches JWT sub from Clerk)
- `CLERK_SECRET_KEY` — Clerk verification
- `DRIP_CRON_SECRET` — shared secret for cron endpoint

Frontend (web/.env):
- `PUBLIC_CLERK_PUBLISHABLE_KEY` — Clerk public key
- `PUBLIC_PLAUSIBLE_DOMAIN` — analytics domain (opt-in)

**DB Detection:**
Uses Turso when both `TURSO_DATABASE_URL` + `TURSO_AUTH_TOKEN` are set; falls back to file SQLite (`DB_PATH`, default `./data/sqlite.db`).

**Soft-Delete:**
Admin delete sets `deletedAt`; rows filtered from all queries. Hard-delete requires `ALLOW_ADMIN_DELETE_ALL_BOOKINGS=true`.

**Drip Cron:**
External Render cron POSTs `/api/internal/process-drip` with `DRIP_CRON_SECRET` bearer token hourly. Processes batches of `DRIP_BATCH_SIZE` (default 20).

See DEPLOY.md for full details.
