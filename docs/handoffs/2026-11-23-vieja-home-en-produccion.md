# Handoff: production serves the old video home again (2026-11-23, run chefskisdrone, stopped at the context limit)

Task from the owner via mothership-4e (07:16): production shows the OLD design; the 3D scene is a preview.
1. `/` serves the old video home (`src/pages/anterior-home.astro`, 314 lines, layout `src/layouts/MarketingLayout.astro`) with every
   current function: `/e` beacon (pv, clicks, nd/nm, sources), WhatsApp `/wa/`, `nolog`, page-first loading. Compare it with the current
   `src/pages/index.astro` for functions the old one lacks (contact/booking buttons, member cards, tour dates, meta/OG, sitemap, Sentry),
   port them and list what was ported.
2. The scene moves to a hidden `/escena` (noindex, not in sitemap or nav); `/anterior-home` redirects 301 to `/` (`public/_redirects`).
3. Production must not request `/vivo/*.glb` from `/` at all.
Done-check: `bun test` + build pass; Playwright on the built site: `/` at 390 and 1440 shows the old design (screenshots), zero 404s in
the network log for `/`, one pv beacon with source fields, a WA tap counted; `/escena` still loads its scene locally. Commit, no push.
Report ≤ 4 lines: what changed, what was ported, screenshots, hash.

## State
- Branch `cc/chefskisdrone` is at b507549, which is already in `main`; the rebase is a no-op. Nothing of this task is started.
- `src/pages/anterior-home.astro` calls `trackPageview(document)` at line 222 (and `trackClicks`, line 219). Not yet checked: where it
  gets Sentry, the Seo component, OG tags, and whether `Apertura`-style intros or heavy assets load before first paint.
- My page-first pieces: `src/lib/trasPintar.ts` (runs a function after load + a frame) is reusable for any heavy asset on the old home.

## Measuring tools already in the repo (reuse them)
- `scripts/servir-dist.mjs <dist> <port>`: serves a built dist with Range and brotli. Start it with `run_in_background`.
- `scripts/medir-lcp.mjs`, `scripts/probar-pagina-primero.mjs`, `scripts/fotos-apertura.mjs`: need `PW=/mnt/e/tmp/pw-vivo/node_modules/playwright-core`
  and the snap Chromium (`/snap/bin/chromium`, plays H.264). Phone settings: 390×844, 4× CPU, Fast 4G.
- Playwright network log: use `page.on('response')` and `page.on('requestfailed')` for the zero-404 check; the beacon is `POST /e`
  (contract: `~/projects/cronjobs/docs/site-events.md`; client in `src/lib/clickEvents.ts`; worker tests in `e.test.mjs`).

## Gotchas
- `public/vivo/*.glb` and `public/vivo/draco/` are gitignored and absent from a fresh worktree; copy them from `/mnt/e/Cursor Projects/MTO-gamblingdrone/public/vivo/`
  to test `/escena` locally. They are also absent from the CI build, which is why production returns 404 for `/vivo/escena.glb` today
  (checked by `curl` 2026-11-23 13:07 GMT). After this task `/` must not reference them at all; `/escena` may.
- Under software GL a screenshot of the scene takes ~12 s; for timed stills of an intro use `?respaldo`.
- `bun test` (not `node --test`) runs the worker tests.
- `docs/wayfinder/escenas/map.md` lists the home as the live scene; the owner's new decision (production = old design, scene = preview)
  should be written back by the mothership's session, not by this one.
