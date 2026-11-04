# Cloudflare target findings — static Astro for mafiatumbada.com

Researched via Cloudflare Docs MCP + Astro docs (context7). Docs last-updated stamps Aug 2026.

## 1. Workers Static Assets, not Pages

Cloudflare explicitly recommends **Workers Static Assets for new projects**:

> "Workers Static Assets is the recommended way to deploy static sites, single-page applications, and full-stack apps on Cloudflare. If you are starting a new project, use Workers instead of Pages. Pages continues to work, but new features and optimizations are focused on Workers."
> — https://developers.cloudflare.com/workers/best-practices/workers-best-practices/

Also: https://developers.cloudflare.com/workers/static-assets/ and https://developers.cloudflare.com/workers/static-assets/migration-guides/migrate-from-pages/
(Static asset requests are free; Workers has broader feature set — Workers Logs, Logpush, serve-assets-on-a-path — which Pages lacks.)

Decision: **Worker with assets only, no `main`, no Worker script.**

## 2. Minimal wrangler.jsonc

Site lives in `web/`, Astro static build outputs `web/dist/`. Put `wrangler.jsonc` in `web/` and set Workers Builds root directory to `web`.

```jsonc
{
  "name": "mafiatumbada",           // MUST match the Worker name in the dashboard
  "compatibility_date": "2026-09-08",
  "assets": {
    "directory": "./dist/",
    "not_found_handling": "404-page",      // serves nearest 404.html
    "html_handling": "auto-trailing-slash"
  }
}
```

- No `"binding": "ASSETS"` — that is only valid when a `main` Worker script exists.
- No `main`, no `_worker.js`, no `.assetsignore` needed for a pure static build (add `.assetsignore` only to skip `node_modules`/`.DS_Store` if they end up in `dist/`).
- Requires **wrangler v4+** (`bun add -d wrangler@^4`); v4.34.0+ for the 100k-file limit.
- Docs: https://developers.cloudflare.com/workers/static-assets/routing/static-site-generation/ · https://developers.cloudflare.com/workers/wrangler/configuration/#assets

Local/manual:
```bash
cd web && bun run build      # astro build -> web/dist
npx wrangler deploy --dry-run   # validate
npx wrangler deploy
```

### Git integration (Workers Builds) settings
Dashboard → Worker → **Settings → Builds → Connect** (GitHub repo).
- **Root directory**: `web`
- **Build command**: `bun run build` (or `npm run build`)
- **Deploy command**: `npx wrangler deploy` (default)
- **Non-production branch deploy command**: `npx wrangler versions upload` (default; gives preview URLs if non-prod branch builds enabled)
- **Branch control**: production branch = `main`
- Caveat: the Worker name in the dashboard **must equal** `name` in the wrangler config at that root directory, or the build fails.
- Docs: https://developers.cloudflare.com/workers/ci-cd/builds/ · https://developers.cloudflare.com/workers/ci-cd/builds/configuration/ · https://developers.cloudflare.com/workers/ci-cd/builds/build-branches/

## 3. Redirects and sitemap.xml

**Use a `_redirects` file** — supported on Workers Static Assets (not just Pages).
- Plain text, no extension, placed in the **static asset output dir**. With Astro, author it at `web/public/_redirects` so the build copies it to `dist/_redirects`.
- It is parsed by Workers, not served as an asset.
- Format: `[source] [destination] [code?]`, default code is **302** — so 301s must be explicit:
  ```
  # old path -> new
  /booking /contratacion 301
  /blog/* /noticias/:splat 301
  ```
- Supported: 301/302/303/307/308, splats (`*` / `:splat`, one per URL), placeholders (`:name`), proxying (code 200). **Not** supported: query-param matching, domain-level redirects, country/cookie conditions, rewrites with non-redirect codes.
- Order matters (top-most wins); static rules before dynamic. Redirects always run, even if an asset matches the path, and run **before** `_headers`.
- Limits: 2,000 static + 100 dynamic (2,100 total), 1,000 chars per rule.
- Caveat (irrelevant here, no Worker script): `_redirects` rules do not apply to responses produced by Worker code.
- Docs: https://developers.cloudflare.com/workers/static-assets/redirects/ · limits: https://developers.cloudflare.com/workers/platform/limits/#static-assets

Alternative for domain-level or query-based redirects (e.g. `www` → apex): **Redirect Rules / Bulk Redirects** at the zone level, not `_redirects`.

**sitemap.xml**: nothing special. `@astrojs/sitemap` emits `dist/sitemap-index.xml` + `sitemap-0.xml` at build; Workers serves them as ordinary static assets from `assets.directory` with correct content type. Same for `robots.txt` (put it in `web/public/`). Ensure `site: 'https://mafiatumbada.com'` is set in astro.config so URLs are absolute.

## 4. DNS / domain cutover from Vercel

Constraint that drives the ordering: **Workers Custom Domains require an active Cloudflare zone** — the domain's nameservers must already be managed by Cloudflare. "Unlike Pages, Workers does not support any domain whose nameservers are not managed by Cloudflare." So the nameserver move must come *first*; you cannot pre-attach the custom domain the way Vercel lets you pre-verify.

Recommended ordering:
1. **Before anything**: lower TTLs at the current DNS provider (~300s) and let old TTLs expire. If DNSSEC is enabled, remove the DS record at the registrar and wait a full DS TTL (24–48h for most TLDs) — changing nameservers before the old DS TTL expires makes validating resolvers return **SERVFAIL**.
2. Deploy the Worker and verify it fully on `*.workers.dev` (and a preview URL). Site must be correct before it owns the domain.
3. Add `mafiatumbada.com` to Cloudflare (**Full setup**). Let the quick scan import records, then **manually audit every record** — MX/SPF/DKIM/DMARC for email, any Resend/verification TXT, subdomains. Missing records here is the #1 way the cutover breaks things unrelated to the website.
4. Point the apex `A`/`AAAA` (or existing CNAME) at Vercel still, proxied or DNS-only, so that when nameservers flip the site keeps serving from Vercel — zero-downtime holding state.
5. Change nameservers at the registrar to the two assigned Cloudflare nameservers. Wait for zone status **Active**.
6. **Now** add the Custom Domain to the Worker (dashboard → Worker → Domains/Settings → Domains & Routes → Add → Custom Domain, or `routes: [{ pattern: "mafiatumbada.com", custom_domain: true }]` + `wrangler deploy`). Cloudflare creates the DNS record and issues the cert automatically.
   - **Caveat: you cannot create a Custom Domain on a hostname that already has a CNAME DNS record.** So delete the leftover Vercel apex record first, or step 6 errors out. This is the main out-of-order failure mode.
7. `www`: a Custom Domain matches the hostname exactly — a Worker on `mafiatumbada.com` will **not** receive `www.mafiatumbada.com`. Either add `www` as a second Custom Domain, or (preferred for SEO) add a proxied placeholder record for `www` (`A → 192.0.2.0` or `AAAA → 100::`) plus a Redirect Rule www → apex.
8. Verify, then remove the domain from the Vercel project. Re-enable DNSSEC only after DNS is confirmed stable, and add the new DS record at the registrar.

What breaks if done out of order:
- Attaching the custom domain before the zone is active → not possible; Workers rejects non-Cloudflare-nameserver domains.
- Flipping nameservers before auditing records → email and third-party verifications drop silently.
- Flipping nameservers with DNSSEC still active at the registrar → SERVFAIL, hard outage.
- Leaving the Vercel CNAME on the apex → Custom Domain creation fails.

Docs: https://developers.cloudflare.com/workers/configuration/routing/custom-domains/ · https://developers.cloudflare.com/dns/zone-setups/full-setup/setup/ · https://developers.cloudflare.com/fundamentals/performance/minimize-downtime/ · https://developers.cloudflare.com/dns/dnssec/ · https://developers.cloudflare.com/learning-paths/dns-best-practices/concepts/phase-4/

## 5. Astro config changes

Per Astro docs, `@astrojs/vercel` is only needed for on-demand rendered routes or Vercel platform services (Web Analytics, Vercel Image Optimization). For a purely static site it is unnecessary — and on managed static hosting Astro states you generally do not need an adapter at all.

Remove from `web/astro.config.mjs`:
- `import vercel from '@astrojs/vercel'` and the `adapter: vercel({...})` entry
- any `output: 'server'` / `output: 'hybrid'` (`hybrid` was merged into `static` in Astro v5) → set `output: 'static'` (this is the default, so it can simply be omitted)
- any Vercel-only options: `imageService`, `webAnalytics`, `isr`, `maxDuration`, `edgeMiddleware`

Then remove `@astrojs/vercel` from `web/package.json`, and delete `web/vercel.json` if present. Also drop `export const prerender = false` from any page, and delete the SSR-only relay/API routes (`web/src/pages/admin/*.ts`) — endpoints cannot run in a static build. Keep/confirm `site: 'https://mafiatumbada.com'` for sitemap + canonical URLs.

Docs: https://docs.astro.build/en/guides/integrations-guide/vercel/ · https://docs.astro.build/en/reference/configuration-reference/#output · https://docs.astro.build/en/guides/integrations-guide/sitemap/ · https://docs.astro.build/en/guides/upgrade-to/v5/
