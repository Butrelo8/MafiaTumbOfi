# Deploy: API (Render) + Frontend (Vercel) + Turso (libsql)

- **API:** Hono + Bun on Render (Web Service; **no** persistent disk — DB is **Turso** / libsql).
- **Frontend:** Astro (SSR) on Vercel via `@astrojs/vercel` (serverless adapter; see `web/astro.config.mjs`).
- **Database:** **Turso** (hosted SQLite-compatible libsql). Migrations and schema check run at API startup (`bun run migrate && bun run check-db && bun run start`). Optional **file SQLite** (`bun:sqlite` + `DB_PATH` only) remains for local/offline dev when Turso env vars are unset — see `**.env.example`** and `src/db/detect.ts`.

Deploy order: **API first**, then frontend (so you can set `PUBLIC_API_URL` to the live API).

**Optional — booking UI smoke (no live API):** From repo root, `bun run test:e2e` runs Playwright against `astro dev` and **mocks** `POST …/api/booking` in the browser (no Resend/DB). First time on a machine: `cd web && bunx playwright install chromium`. See **README** (E2E section). CI can run the same command when you add a workflow step.

---

## 1. Deploy API on Render

1. Push the repo to GitHub (if you haven’t). Render deploys from Git.
2. In [Render Dashboard](https://dashboard.render.com/) → **New** → **Blueprint**. Connect the repo and select the one that contains `render.yaml`.
3. Render will create the **mto-api** web service from `render.yaml`. Set these **secret** env vars in the service’s **Environment** (they are `sync: false` in the Blueprint):

  | Variable                     | Description                                                                                                                                                                                                |
  | ---------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
  | `FRONTEND_URL`               | Dev frontend URL (e.g. `http://localhost:4321`). Optional in prod if you only use `PRODUCTION_URL`.                                                                                                        |
  | `PRODUCTION_URL`             | **Required.** Your Vercel frontend URL, e.g. `https://your-app.vercel.app` (no trailing slash). Used for CORS.                                                                                             |
  | `RESEND_API_KEY`             | From [Resend](https://resend.com).                                                                                                                                                                         |
  | `BOOKING_NOTIFICATION_EMAIL` | Email that receives booking form submissions.                                                                                                                                                              |
  | `CLERK_PUBLISHABLE_KEY`      | From [Clerk](https://dashboard.clerk.com) (same app as frontend).                                                                                                                                          |
  | `CLERK_SECRET_KEY`           | From Clerk.                                                                                                                                                                                                |
  | `ADMIN_CLERK_ID`             | **Required for `/api/admin/*`.** Clerk **User ID** for the band account (Dashboard → Users → copy id; matches JWT `sub`). New signups never auto-gain admin.                                               |
  | `DRIP_CRON_SECRET`           | **Optional but recommended** for nurture emails: long random string; must match the **cron** service (see below).                                                                                          |
  | `PUBLIC_SITE_URL`            | **Optional** for drip email links; falls back to `PRODUCTION_URL` / `FRONTEND_URL`.                                                                                                                        |
  | `DRIP_VIDEO_URL`             | **Optional** — URL for nurture **Email 2** video (plain text + button). If unset, the API uses the historical default so links are never empty; set in production to change the video without redeploying. |
  | `PUBLIC_WHATSAPP_URL`        | **Optional** — WhatsApp CTA in nurture **Email 3** (same env as the Astro site).                                                                                                                           |
  | `TURSO_DATABASE_URL`         | From [Turso](https://turso.tech): `turso db show <name> --url` (e.g. `libsql://…`). **Required** for production in `render.yaml`.                                                                          |
  | `TURSO_AUTH_TOKEN`           | `turso db tokens create <name>` — treat as a secret; rotate if leaked.                                                                                                                                     |

4. **DB (Turso):** The Blueprint sets `**TURSO_DATABASE_URL`** and `**TURSO_AUTH_TOKEN**` (`sync: false` — you paste values in the Dashboard). **Do not** set `**DB_PATH`** on the API service for production (unset = remote libsql only). Migrations run against Turso on every deploy start. **CLI (Windows):** `npm i -g @turso/cli` or [Turso CLI install](https://docs.turso.tech/cli/overview); create DB and token before first deploy.
  **Existing data on Render disk:** Before switching to Turso, export or dump the old SQLite file (if any), then import into Turso (`turso db shell <name>` with SQL dump) **or** run migrations on an empty Turso DB and accept empty tables — see §7.

### Bun on Render (Node runtime)

The API service uses `**runtime: node`** with `**buildCommand**` / `**startCommand**` that call the **Bun** CLI (`bun install`, `bun run …`). That assumes Render’s **Node** native environment continues to ship **Bun** alongside Node — true today, but **not a permanent platform guarantee**.

**Checklist (major upgrades):** After you change the service **Node version**, switch **environment type**, or Render ships a **large platform update**, verify before trusting prod traffic:

- In the Render **Shell** (or a one-off deploy), run `**bun --version`** and confirm `**bun run migrate**` / `**bun run start**` still work.

**If `bun` is missing** from a future image: fall back to something you control — e.g. `**npx bun@latest run migrate`** (and equivalent for `start`), or move the service to a **Docker** deploy with an explicit Bun/Node base image.

1. **Booking nurture drip (optional):** The Blueprint adds `**mto-drip-cron`**, which does not open the DB directly; it `**curl`s** `POST /api/internal/process-drip` on **mto-api** (same pattern as the old SQLite-on-disk setup). Set `**DRIP_PROCESS_URL`** on the cron service to your public API URL plus path, e.g. `https://mto-api.onrender.com/api/internal/process-drip`, and set `**DRIP_CRON_SECRET**` to the **same** value on **both** **mto-api** and **mto-drip-cron**. Optional tuning: `**DRIP_EMAIL_2_DELAY_HOURS`**, `**DRIP_EMAIL_3_DELAY_HOURS**`, `**DRIP_BATCH_SIZE**` (see root `**.env.example**`). On **mto-api**, set `**DRIP_VIDEO_URL`** and `**PUBLIC_WHATSAPP_URL**` when you want drip copy to track the live video and WhatsApp links without redeploying (see table above).
2. Deploy. After deploy, copy the **service URL** (e.g. `https://mto-api.onrender.com`) for the frontend.
3. In **Clerk Dashboard** → your application → **Paths** / **Allowed redirect URLs**: add your production frontend URL and, if needed, the API URL. Add the frontend origin to **CORS** if Clerk uses it.

### Reverse proxy headers (TLS and rate limits)

The API expects a **trusted** edge that terminates TLS and sets forwarding metadata:


| Header                              | Role                                                                                                                                                                                      |
| ----------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `**X-Forwarded-Proto`**             | Scheme seen by the client (`https` when the browser used HTTPS). **Render sets this** for Web Services.                                                                                   |
| `**Forwarded`** (RFC 7239)          | Optional fallback: if `X-Forwarded-Proto` is missing, HTTPS enforcement reads `proto=` from the first segment (e.g. `Forwarded: for=…;proto=https`).                                      |
| `**X-Forwarded-For` / `X-Real-IP**` | Used for **rate limiting** (booking, auth, `**GET /health`**). Configure the proxy to **append** the real client IP and avoid trusting raw client-supplied values from the open internet. |


If **neither** `X-Forwarded-Proto` nor `Forwarded: proto=` is present, the app **does not** redirect to HTTPS (avoids redirect loops when the edge is misconfigured). Fix the proxy instead.

`**GET /health`** is limited to **120 requests per minute** per client id (derived from the same forwarded-IP logic). N8N or uptime checks should poll at a sane interval.

**Local dev (direct Bun, no proxy):** `X-Forwarded-For` / `X-Real-IP` are often missing, so rate limiting uses the shared key `unknown` for all traffic. Expect one bucket for the whole process; heavy parallel tests can hit limits faster than in production behind Render.

---

## 2. Deploy Frontend on Vercel

1. In [Vercel](https://vercel.com/) → **Add New** → **Project**. Import the same Git repo.
2. **Root Directory:** set to `web` (the Astro app lives in `web/`).
3. **Build:** You **must** set the build command so the runtime patch runs:
  - **Vercel** → your project → **Settings** → **Build & Development** → **Build Command** → set to `**bun run build`** (then Save).
  - The repo’s `web/package.json` script `build` runs `astro build` then `node scripts/patch-vercel-runtime.mjs` to set the serverless runtime to Node 20. If you leave the default (e.g. `astro build`), the patch never runs and the deploy fails with "invalid runtime: render (nodejs18.x)".
4. **Environment variables** (Vercel project → Settings → Environment Variables):

  | Variable                       | Value                                  | Notes                                    |
  | ------------------------------ | -------------------------------------- | ---------------------------------------- |
  | `PUBLIC_API_URL`               | `https://your-render-api.onrender.com` | Your Render API URL (no trailing slash). |
  | `PUBLIC_CLERK_PUBLISHABLE_KEY` | From Clerk                             | Same as API.                             |
  | `CLERK_SECRET_KEY`             | From Clerk                             | Required for SSR/auth().                 |

5. Deploy. Note the Vercel URL (e.g. `https://your-app.vercel.app`).
6. **Back on Render:** set `PRODUCTION_URL` to that Vercel URL so the API allows CORS from the production frontend.

---

## 3. Post-deploy checklist

- API: `https://your-api.onrender.com/health` returns `{"status":"ok",...}`.
- Frontend loads; booking form submits to the API (check Network tab and Resend inbox).
- API env `**ADMIN_CLERK_ID`** set to the band Clerk user id; `/admin` works for that user only (new signups never auto-admin).
- In Clerk dashboard, production frontend URL is in allowed redirect/origin list.

---

## 4. Optional: custom domains

- **Render:** Service → Settings → Custom Domain.
- **Vercel:** Project → Settings → Domains. After adding a domain, update Render’s `PRODUCTION_URL` and Clerk’s allowed URLs to that domain.

---

## 5. Post-launch

- **Resend — Verify sending domain:** In [Resend → Domains](https://resend.com/domains) verify a domain you own, then set **RESEND_FROM_EMAIL** (e.g. `noreply@tudominio.com`) in Render and in `.env`. Until then, Resend only delivers to the account owner; after verification, **customers** receive the “Recibimos tu solicitud” confirmation at any email.
- **Custom domain:** Add your domain in Vercel (and optionally Render); set `PRODUCTION_URL` and Clerk allowed origins to that domain.
- **Monitoring:** Optional: add Sentry or similar; ensure Render/Vercel logs are checked after deploys.

---

## 6. Troubleshooting

- **CORS errors:** Ensure `PRODUCTION_URL` on Render exactly matches the frontend origin (scheme + host, no trailing slash).
- **Migrations:** They run at API startup against whatever `**detectDbMode()`** resolves (Turso or file SQLite). If you add new migrations, push and redeploy.
- **Turso / startup:** Do not run migrations only in a build step without DB access — the **start** command runs migrate + check-db + start.
- **"no such table: users" / admin 500:** Migrations did not apply or env is wrong. In Render → **mto-api** → **Settings**: **Start Command** = `bun run migrate && bun run check-db && bun run start`. **Environment:** `**TURSO_DATABASE_URL`** and `**TURSO_AUTH_TOKEN**` set; `**DB_PATH` unset** for remote Turso. **Manual Deploy** → redeploy. Logs: `**[migrate] libsql: remote`** (Turso) or `**[migrate] DB_PATH:**` (file SQLite fallback).
- **check-db:** Startup fails fast if either `users` or `bookings` is missing from the DB (after migrate).
- **Vercel "invalid runtime: render (nodejs18.x)":** The Astro preset runs `astro build` only, so the patch never runs. **Fix:** In Vercel → Project → **Settings** → **Build & Development** → **Build Command**, set to `**bun run build`** (not the default). Then redeploy. The `build` script in `web/package.json` runs the patch after `astro build`.
- **Health check:** Use the **Render** API URL for `/health`, e.g. `https://mto-api-xxxx.onrender.com/health`. The **Vercel** app (Astro) has no `/health` route and will return 404 for that path.

---

## 7. Accessing the production database

Production data lives in **Turso** (libsql), not on the Render instance disk. Use the **Turso CLI / dashboard**, **Drizzle Studio** against Turso env, or the app’s **admin export** routes.

### Option A: Turso CLI / dashboard

- Install CLI: [Turso CLI](https://docs.turso.tech/cli/overview) (macOS/Linux Homebrew, or `**npm i -g @turso/cli`** on Windows).
- `**turso db shell <database-name>**` — run SQL against the remote database.
- `**turso db inspect**` / Turso web dashboard — usage, branches, tokens.

### Option B: Drizzle Studio against Turso

From repo root, set `**TURSO_DATABASE_URL**` and `**TURSO_AUTH_TOKEN**` (see `**.env.example**`). `**drizzle.config.ts**` switches to the Turso driver when both are set. Then:

```bash
bun run db:studio
```

### Option C: Export data via your API (any plan)

The app exposes **Clerk-protected**, read-only admin endpoints:

- `**GET /api/admin/bookings`** — paginated list: query params `**limit**` (default 50, max 200) and `**offset**` (default 0). Response `**data**` includes `**bookings**`, `**total**` (full table row count), `**limit**`, `**offset**`, `**hasMore**`. Negative `**offset**` returns `**400**` (`VALIDATION_ERROR`).
- `**GET /api/admin/export/bookings**` — JSON export inside `**{ "data": { "exportedAt", "total", "last24hCount", "bookings", "returnedCount", "truncated", … } }**`. `**total**` is the full booking count in the database; the `**bookings**` array is capped per response (default **10000** rows, override with `**ADMIN_EXPORT_MAX_ROWS`**, hard max **50000**). When truncated, `**data`** also includes `**totalInDb**` and `**warning**`. `**last24hCount**` is computed in SQL (not by loading all rows). Used from `**/admin/export-bookings**` on the frontend.
- `**POST /api/admin/bookings/delete-all**` — hard-deletes **every** row in `**bookings`** (including soft-deleted). Body `**{ "dryRun": true }**` returns `**{ count }**` only; `**{ "confirm": "DELETE_ALL_BOOKINGS" }**` runs the delete inside a transaction and returns `**{ deletedCount }**`. Same default-deny as below: `**ALLOW_ADMIN_DELETE_ALL_BOOKINGS=true**` or `**NODE_ENV=development**`. UI relay `**POST /admin/delete-all-bookings**`. Audit log line: `**action: admin_bookings_delete_all**` with `**deletedCount**`.

**Export** is **default-deny** in production: `**GET /api/admin/export/bookings`** returns **403** unless `**ALLOW_ADMIN_BOOKING_EXPORT=true`** on the API **or** the API runs with `**NODE_ENV=development`** (local). On real hosts set `**NODE_ENV=production**` and enable export only via `**ALLOW_ADMIN_BOOKING_EXPORT=true**` for short debugging windows. Successful exports emit a structured **audit** line to the API logs (`action: admin_booking_export`, `userId`, `sessionId`, `timestamp`). `**POST /api/admin/bookings/delete-all`** uses the same pattern with `**ALLOW_ADMIN_DELETE_ALL_BOOKINGS**`; successful deletes emit `**admin_bookings_delete_all**` (includes `**deletedCount**`). No SSH required; works on free tier.

### Summary


| Goal                      | Approach                                                                    |
| ------------------------- | --------------------------------------------------------------------------- |
| Run one-off queries       | Turso shell (**§7 Option A**) or API export (**Option C**)                  |
| Open DB in Drizzle Studio | **§7 Option B** with Turso env vars                                         |
| Backup / DR               | Turso [backups](https://docs.turso.tech/concepts/backup) + Option C exports |


### Legacy: file SQLite on Render (optional)

If you intentionally keep `**DB_PATH`** on Render **without** Turso env (not in the default Blueprint), the API uses `**bun:sqlite`** on that path — you would attach a **persistent disk** again and set `**DB_PATH`** to the mounted file (e.g. `/data/sqlite.db`). The default `**render.yaml**` in this repo is **Turso-only** (no disk).

---

## 8. N8N (local testing / VPS)

N8N is used for scheduled tasks, optional notifications, and external API workflows; the app keeps booking and Stripe (critical path).

- **Local testing:** Run N8N (e.g. `npx n8n` or Docker). See `**docs/n8n/README.md`** for the Option A test: Schedule (every 5 min) → GET app `/health`. Import `docs/n8n/schedule-to-health.json` or create the workflow manually.
- **VPS:** Run the same N8N instance on the VPS (Docker or systemd); expose only behind auth or internal URL; document the URL and start command in this section or in a VPS-specific deploy doc.

