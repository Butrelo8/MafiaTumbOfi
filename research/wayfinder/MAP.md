# Map: Static single-page rebuild (no backend)

Label: `wayfinder:map`

## Destination

A written **spec** for rebuilding mafiatumbada.com as a single static Astro page,
no backend, WhatsApp as the only contact channel, hosted on Cloudflare.
Done when the spec is complete enough to hand to an implementer with nothing left to decide.

## Notes

- Domain: marketing site for a regional Mexican band. Audience: fans (promoters de-prioritized by user decision).
- Consult before UI decisions: `DESIGN.md` (Veracruz Noir tokens, type, palette).
- Locked already: (1) deliverable is a spec, build comes after; (2) WhatsApp-only contact, no form;
  (3) one page, `/contratacion` + `/booking` + `/admin` gone; (4) keep Astro, `output: 'static'`.
- Plan, don't do: tickets produce decisions, not code.

## Decisions so far

- **01 keep/toss** — inventory locked in `SPEC.md` §1. Root `src/`, `drizzle/`, Render/Vercel
  config, admin+booking+api pages, Clerk middleware, and all API/DB/auth/email deps and env
  vars are deleted. `web/` marketing shell, 8 components, 6 data files, 7 libs and `public/`
  survive. Astro goes `output: 'static'`, no adapter, no Clerk.

## Not yet specified

- ~~Copy/content rewrite~~ → **ticket 08** resolved in `SPEC.md` §8 (full string set, salvage-marked).
- ~~Asset trim + perf budget~~ → **ticket 09** resolved in `SPEC.md` §9.
- Whether any social-proof/press material gets a place on the page.
- ~~Repo history / API archival~~ → resolved in `SPEC.md` §7 (`api-final` tag, no branch).

## Out of scope

- Any replacement CRM, lead scoring, drip email, or admin UI. Manager doesn't use it — that's the premise of this effort.

- **02 page structure** — `SPEC.md` §2. 15 sections → 7 + footer. Cut: trust-strip, repertorio,
  testimonios, paquetes, fechas, standalone redes + press. `El grupo` trimmed to 3 fixed members.
  Tour dates dropped outright → **ticket 04 void**.
- **03 whatsapp cta** — `SPEC.md` §4. `wa.me/5212288351464` prefilled; number hardcoded in
  `socials.ts`, `PUBLIC_WHATSAPP_URL` deleted; hero + §7 + footer, no sticky bar; `tel:` fallback.
- **Música source** — `SPEC.md` §3. Build-time Spotify fetch + YouTube uploads RSS, daily
  Cloudflare cron → deploy hook. Snapshot fallback so a bad fetch can't fail the build.
- **05 cloudflare** — `SPEC.md` §5. Workers Static Assets, assets-only `wrangler.jsonc` in `web/`.
  Measured DNS: the zone is **already on Cloudflare nameservers**, DNSSEC off, MX/SPF are
  Cloudflare Email Routing — so the cutover is 4 steps, not a nameserver migration.
- **06 redirects** — `SPEC.md` §6. `web/public/_redirects`, explicit 301s, `/contratacion` +
  `/booking*` → `/#contratacion`. `/admin`, `/health` get no rule (404 on purpose).
  `sitemap.xml` deleted — one indexable URL doesn't need one; robots.txt trimmed to two lines.
- **07 repo shape** — `SPEC.md` §7. `web/` flattens to the repo root via `git mv` (one
  package.json, one biome config). Keep DESIGN/DECISIONS/CHANGELOG/STATE + `docs/superpowers`;
  rewrite README + CLAUDE.md; delete TODOS/BUGS/DEPLOY/docs/n8n. Old API kept as a
  `api-final` tag, not a branch.
- **08 copy** — `SPEC.md` §8. Salvage-first: most of the hero, bio and `#contratacion` Spanish
  survives verbatim. Real edits: hero blurb and bio ¶2 drop promoter framing and the hardcoded
  "Ocho singles" (goes stale under §3's auto-fetch), bio ¶3 moves into `#contratacion`, and the
  "respondemos en menos de 24 horas" SLA is deleted — WhatsApp makes no such promise.
- **09 assets/perf** — `SPEC.md` §9. Deleted `public/assets/orphan/` (7.4 MB, unreferenced) and
  the 1.2 MB logo PNG; `public/` 21 MB → 13 MB. Apr Lighthouse baseline invalidated (predates the
  perf merge). Found two live bugs: `/video/hero-poster.webp` 404s, and Clerk still ships ~103 KB
  to the public homepage — poster refs deleted, Clerk dies with §1. `hero.mp4` re-encode
  rejected on quality — stays 9.8 MB (animated WebP also rejected: ~7.3 MB, cannot stream).
  `public/` 21 MB → 13 MB. Budget: <1 MB initial load, LCP <2.5s, perf ≥90 throttled mobile.

