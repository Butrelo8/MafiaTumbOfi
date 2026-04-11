# Deploy: API (Render) + Frontend (Vercel) + SQLite

- **API:** Hono + Bun on Render (Web Service with persistent disk for SQLite).
- **Frontend:** Astro (SSR) on Vercel via `@astrojs/vercel` (serverless adapter; see `web/astro.config.mjs`).
- **Database:** SQLite file on Render disk at `/data/sqlite.db`; migrations run at API startup.

Deploy order: **API first**, then frontend (so you can set `PUBLIC_API_URL` to the live API).

**Optional — booking UI smoke (no live API):** From repo root, `bun run test:e2e` runs Playwright against `astro dev` and **mocks** `POST …/api/booking` in the browser (no Resend/DB). First time on a machine: `cd web && bunx playwright install chromium`. See **README** (E2E section). CI can run the same command when you add a workflow step.

---

## 1. Deploy API on Render

1. Push the repo to GitHub (if you haven’t). Render deploys from Git.

2. In [Render Dashboard](https://dashboard.render.com/) → **New** → **Blueprint**. Connect the repo and select the one that contains `render.yaml`.

3. Render will create the **mto-api** web service from `render.yaml`. Set these **secret** env vars in the service’s **Environment** (they are `sync: false` in the Blueprint):

   | Variable | Description |
   |----------|-------------|
   | `FRONTEND_URL` | Dev frontend URL (e.g. `http://localhost:4321`). Optional in prod if you only use `PRODUCTION_URL`. |
   | `PRODUCTION_URL` | **Required.** Your Vercel frontend URL, e.g. `https://your-app.vercel.app` (no trailing slash). Used for CORS. |
   | `RESEND_API_KEY` | From [Resend](https://resend.com). |
   | `BOOKING_NOTIFICATION_EMAIL` | Email that receives booking form submissions. |
   | `CLERK_PUBLISHABLE_KEY` | From [Clerk](https://dashboard.clerk.com) (same app as frontend). |
   | `CLERK_SECRET_KEY` | From Clerk. |
   | `ADMIN_CLERK_ID` | **Required for `/api/admin/*`.** Clerk **User ID** for the band account (Dashboard → Users → copy id; matches JWT `sub`). New signups never auto-gain admin. |
   | `DRIP_CRON_SECRET` | **Optional but recommended** for nurture emails: long random string; must match the **cron** service (see below). |
   | `PUBLIC_SITE_URL` | **Optional** for drip email links; falls back to `PRODUCTION_URL` / `FRONTEND_URL`. |
   | `PUBLIC_WHATSAPP_URL` | **Optional** — adds WhatsApp CTA in Email 3 (same pattern as the Astro site). |

4. **DB:** The Blueprint attaches a 1 GB persistent disk at `/data`. `DB_PATH` is set to `/data/sqlite.db`. Migrations and a fast schema check run on every start (`bun run migrate && bun run check-db && bun run start` — see `render.yaml`).

### Bun on Render (Node runtime)

The API service uses **`runtime: node`** with **`buildCommand`** / **`startCommand`** that call the **Bun** CLI (`bun install`, `bun run …`). That assumes Render’s **Node** native environment continues to ship **Bun** alongside Node — true today, but **not a permanent platform guarantee**.

**Checklist (major upgrades):** After you change the service **Node version**, switch **environment type**, or Render ships a **large platform update**, verify before trusting prod traffic:

- [ ] In the Render **Shell** (or a one-off deploy), run **`bun --version`** and confirm **`bun run migrate`** / **`bun run start`** still work.

**If `bun` is missing** from a future image: fall back to something you control — e.g. **`npx bun@latest run migrate`** (and equivalent for `start`), or move the service to a **Docker** deploy with an explicit Bun/Node base image.

5. **Booking nurture drip (optional):** The Blueprint adds **`mto-drip-cron`**, which **cannot** read the API’s SQLite file (different instance / no disk mount). It only **`curl`s** `POST /api/internal/process-drip` on **mto-api**. Set **`DRIP_PROCESS_URL`** on the cron service to your public API URL plus path, e.g. `https://mto-api.onrender.com/api/internal/process-drip`, and set **`DRIP_CRON_SECRET`** to the **same** value on **both** **mto-api** and **mto-drip-cron**. Optional tuning: **`DRIP_EMAIL_2_DELAY_HOURS`**, **`DRIP_EMAIL_3_DELAY_HOURS`**, **`DRIP_BATCH_SIZE`** (see root **`.env.example`**).

6. Deploy. After deploy, copy the **service URL** (e.g. `https://mto-api.onrender.com`) for the frontend.

7. In **Clerk Dashboard** → your application → **Paths** / **Allowed redirect URLs**: add your production frontend URL and, if needed, the API URL. Add the frontend origin to **CORS** if Clerk uses it.

### Reverse proxy headers (TLS and rate limits)

The API expects a **trusted** edge that terminates TLS and sets forwarding metadata:

| Header | Role |
|--------|------|
| **`X-Forwarded-Proto`** | Scheme seen by the client (`https` when the browser used HTTPS). **Render sets this** for Web Services. |
| **`Forwarded`** (RFC 7239) | Optional fallback: if `X-Forwarded-Proto` is missing, HTTPS enforcement reads `proto=` from the first segment (e.g. `Forwarded: for=…;proto=https`). |
| **`X-Forwarded-For` / `X-Real-IP`** | Used for **rate limiting** (booking, auth, **`GET /health`**). Configure the proxy to **append** the real client IP and avoid trusting raw client-supplied values from the open internet. |

If **neither** `X-Forwarded-Proto` nor `Forwarded: proto=` is present, the app **does not** redirect to HTTPS (avoids redirect loops when the edge is misconfigured). Fix the proxy instead.

**`GET /health`** is limited to **120 requests per minute** per client id (derived from the same forwarded-IP logic). N8N or uptime checks should poll at a sane interval.

**Local dev (direct Bun, no proxy):** `X-Forwarded-For` / `X-Real-IP` are often missing, so rate limiting uses the shared key `unknown` for all traffic. Expect one bucket for the whole process; heavy parallel tests can hit limits faster than in production behind Render.

---

## 2. Deploy Frontend on Vercel

1. In [Vercel](https://vercel.com/) → **Add New** → **Project**. Import the same Git repo.

2. **Root Directory:** set to `web` (the Astro app lives in `web/`).

3. **Build:** You **must** set the build command so the runtime patch runs:
   - **Vercel** → your project → **Settings** → **Build & Development** → **Build Command** → set to **`bun run build`** (then Save).
   - The repo’s `web/package.json` script `build` runs `astro build` then `node scripts/patch-vercel-runtime.mjs` to set the serverless runtime to Node 20. If you leave the default (e.g. `astro build`), the patch never runs and the deploy fails with "invalid runtime: render (nodejs18.x)".

4. **Environment variables** (Vercel project → Settings → Environment Variables):

   | Variable | Value | Notes |
   |----------|--------|--------|
   | `PUBLIC_API_URL` | `https://your-render-api.onrender.com` | Your Render API URL (no trailing slash). |
   | `PUBLIC_CLERK_PUBLISHABLE_KEY` | From Clerk | Same as API. |
   | `CLERK_SECRET_KEY` | From Clerk | Required for SSR/auth(). |

5. Deploy. Note the Vercel URL (e.g. `https://your-app.vercel.app`).

6. **Back on Render:** set `PRODUCTION_URL` to that Vercel URL so the API allows CORS from the production frontend.

---

## 3. Post-deploy checklist

- [ ] API: `https://your-api.onrender.com/health` returns `{"status":"ok",...}`.
- [ ] Frontend loads; booking form submits to the API (check Network tab and Resend inbox).
- [ ] API env **`ADMIN_CLERK_ID`** set to the band Clerk user id; `/admin` works for that user only (new signups never auto-admin).
- [ ] In Clerk dashboard, production frontend URL is in allowed redirect/origin list.

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
- **Migrations:** They run at API startup. If you add new migrations, push and redeploy; the new instance will run `bun run migrate` then start.
- **SQLite on Render:** The disk is only available at **runtime**. Do not run migrations in a pre-deploy or build step; the start command handles them.
- **"no such table: users" / admin 500:** The DB was not migrated. In Render → your API service → **Settings**: set **Start Command** to exactly `bun run migrate && bun run check-db && bun run start`, set **Environment** → **DB_PATH** to `/data/sqlite.db`. Then **Manual Deploy** → redeploy. Check **Logs** for `[migrate] DB_PATH:` to confirm the path.
- **check-db:** Startup fails fast if either `users` or `bookings` is missing from the DB (after migrate).
- **Vercel "invalid runtime: render (nodejs18.x)":** The Astro preset runs `astro build` only, so the patch never runs. **Fix:** In Vercel → Project → **Settings** → **Build & Development** → **Build Command**, set to **`bun run build`** (not the default). Then redeploy. The `build` script in `web/package.json` runs the patch after `astro build`.
- **Health check:** Use the **Render** API URL for `/health`, e.g. `https://mto-api-xxxx.onrender.com/health`. The **Vercel** app (Astro) has no `/health` route and will return 404 for that path.

---

## 7. Accessing the production database

The production DB is a **SQLite file** on Render’s persistent disk at `/data/sqlite.db`. There is no network connection string; you access it by reaching the Render instance or by exporting data through your app.

### Option A: Render Shell (paid plans only)

**SSH/Shell** is available only on **paid** Web Services (not free tier).

1. In [Render Dashboard](https://dashboard.render.com/) → your **mto-api** service → **Shell** (or use [Render SSH](https://render.com/docs/ssh) from your terminal).
2. In the shell you can:
   - Inspect the file: `ls -la /data/sqlite.db`
   - Query with Bun:  
     `bun -e "const db = require('bun:sqlite').Database; const d = new db('/data/sqlite.db'); console.log(d.query('SELECT * FROM users').all());"`
   - If `sqlite3` is available in the image: `sqlite3 /data/sqlite.db "SELECT * FROM users;"`

### Option B: Download the DB file with SCP (paid plans only)

With SSH enabled you can copy the file to your machine, then open it locally (e.g. Drizzle Studio or any SQLite client):

- See [Render SSH docs](https://render.com/docs/ssh) for `render scp` or `scp` usage to copy from the service to your machine (e.g. `scp` from the instance to your laptop).

### Option C: Export data via your API (any plan)

The app exposes **Clerk-protected**, read-only admin endpoints:

- **`GET /api/admin/bookings`** — paginated list: query params **`limit`** (default 50, max 200) and **`offset`** (default 0). Response **`data`** includes **`bookings`**, **`total`** (full table row count), **`limit`**, **`offset`**, **`hasMore`**. Negative **`offset`** returns **`400`** (`VALIDATION_ERROR`).
- **`GET /api/admin/export/bookings`** — JSON export inside **`{ "data": { "exportedAt", "total", "last24hCount", "bookings", "returnedCount", "truncated", … } }`**. **`total`** is the full booking count in the database; the **`bookings`** array is capped per response (default **10000** rows, override with **`ADMIN_EXPORT_MAX_ROWS`**, hard max **50000**). When truncated, **`data`** also includes **`totalInDb`** and **`warning`**. **`last24hCount`** is computed in SQL (not by loading all rows). Used from **`/admin/export-bookings`** on the frontend.

Both routes are **default-deny** for export in production: **`GET /api/admin/export/bookings`** returns **403** unless **`ALLOW_ADMIN_BOOKING_EXPORT=true`** on the API **or** the API runs with **`NODE_ENV=development`** (local). On real hosts set **`NODE_ENV=production`** and enable export only via **`ALLOW_ADMIN_BOOKING_EXPORT=true`** for short debugging windows. Successful exports emit a structured **audit** line to the API logs (`action: admin_booking_export`, `userId`, `sessionId`, `timestamp`). No SSH required; works on free tier.

### Summary

| Goal | Free tier | Paid (Shell/SSH) |
|------|-----------|------------------|
| Run one-off queries | Use Option C (API export) | Shell + `bun` or `sqlite3` |
| Open DB in Drizzle Studio | Not possible (no direct access) | SCP the file, then `DB_PATH=./prod.db bun db:studio` |
| Backup the DB | Option C or add backup job that uploads to S3/GCS | SCP or backup job |

---

## 8. N8N (local testing / VPS)

N8N is used for scheduled tasks, optional notifications, and external API workflows; the app keeps booking and Stripe (critical path).

- **Local testing:** Run N8N (e.g. `npx n8n` or Docker). See **`docs/n8n/README.md`** for the Option A test: Schedule (every 5 min) → GET app `/health`. Import `docs/n8n/schedule-to-health.json` or create the workflow manually.
- **VPS:** Run the same N8N instance on the VPS (Docker or systemd); expose only behind auth or internal URL; document the URL and start command in this section or in a VPS-specific deploy doc.
