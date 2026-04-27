## MTO — mafia-tumbada-ofi

**Purpose:** Official website + admin CRM for regional Mexican band. Public booking form, Clerk-gated admin dashboard, email drip campaigns.

**Stack:**
- Backend: Hono + Bun API on Render (src/)
- Frontend: Astro SSR on Vercel (web/)
- DB: Drizzle + libsql (Turso prod, local SQLite dev)
- Auth: Clerk (env var for first admin)
- Email: Resend
- Styling: OKLCH tokens, Inter + Cormorant + JetBrains Mono
- Design system: DESIGN.md (source of truth)

**Key Patterns:**
- DB auto-detects Turso vs local file via env vars
- Admin auth: ADMIN_CLERK_ID env var matched against JWT sub
- Soft-delete: deletedAt flag, hard-delete requires ALLOW_ADMIN_DELETE_ALL_BOOKINGS=true
- Booking pipeline: form → Zod validate → leadScore (0–1000) → insert → Resend emails → schedule drips
- Drip cron: external hourly POST to /api/internal/process-drip with DRIP_CRON_SECRET bearer token

See CLAUDE.md for full architecture.
