## Codebase Structure

### Root (API — Hono + Bun)
```
src/
├── index.ts              # Entry point, middleware setup, route mount
├── routes/
│   ├── booking.ts        # Public booking form endpoint
│   ├── admin.ts          # Clerk-gated admin dashboard relay
│   └── internal.ts       # Drip cron processor
├── db/
│   ├── schema.ts         # Drizzle schema (source of truth for types)
│   └── detect.ts         # DB detection: Turso vs local SQLite
├── lib/
│   ├── score.ts          # Lead scoring (0–1000)
│   ├── drip.ts           # Drip schedule dates
│   ├── email.ts          # Resend helpers
│   └── errors.ts         # Zod Spanish error messages
└── tests/                # Backend tests
```

### web/ (Frontend — Astro)
```
web/src/
├── pages/
│   ├── index.astro       # Homepage (Veracruz Noir hero + sections)
│   ├── contratacion.astro  # Canonical booking page
│   ├── booking.astro     # Legacy redirect
│   ├── booking/gracias.astro  # Thank you page
│   └── admin/            # Clerk-gated admin relay routes
├── components/
│   ├── Hero.astro        # Full-bleed hero with background video
│   ├── Marquee.astro     # Scrolling tour dates marquee
│   ├── TourTable.astro   # Tour dates table
│   ├── ArtworkShelf.astro  # CD covers gallery
│   ├── FilmStrip.astro   # Band photos strip
│   ├── SignatureCTA.astro  # Call-to-action section
│   ├── BookingForm.astro # Form (POST /api/booking)
│   ├── MarketingLayout.astro  # Layout + fullscreen mobile menu
│   └── ui/               # Form inputs, buttons, surfaces
├── layouts/              # Layout wrappers
├── lib/
│   ├── showPressAssets.ts  # Press kit visibility control
│   └── tourDates.ts      # Static tour dates (CMS/API later)
├── data/                 # Static data
├── styles/
│   ├── tokens.css        # Global OKLCH tokens
│   ├── marketing-press.css  # Marketing page styles + tokens
│   └── global.css        # Base styles
└── middleware.ts         # Clerk auth check
```

### drizzle/ (Migrations)
Edit `src/db/schema.ts` → `bun run db:generate` → `bun run db:migrate`

### Config
- `.env.example` (root) — API secrets, Turso, Resend, Clerk, Drip cron
- `web/.env.example` — Frontend Clerk public key, Plausible domain
- `CLAUDE.md` — Full architecture & commands
- `DESIGN.md` — Visual system, tokens, typography
- `.cursor/rules/` — Code style rules (Biome, TypeScript strict, etc.)

### Recent Work (STATE.md)
Branch: `feat/desegin-consultation-redo` (fullscreen menu, nav hover fixes, Veracruz Noir)
Large working tree. Next: git status review, commits, full testing.
