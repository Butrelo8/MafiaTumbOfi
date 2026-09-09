# 01 — Keep/toss inventory
Labels: `wayfinder:grilling` · Blocks: 02, 06, 07 · Blocked by: — · Assignee: —

## Question
Exactly which files/dirs/deps/env vars survive the rebuild and which get deleted?
Candidate toss: `src/` (Hono API), `drizzle/`, `web/src/pages/admin*`, `web/src/pages/api/`,
`web/src/pages/booking*`, `contratacion.astro`, `BookingForm.astro`, `middleware.ts` (Clerk),
Clerk/Drizzle/libsql/Resend/Zod deps, all API+DB+cron env vars, API tests, `TourTable` API fetch path.
Candidate keep: `web/` shell, `DESIGN.md`, `Seo.astro`, `sitemap.xml.ts`, public assets, marketing components.
Output: a definitive two-column list in the spec.
