# Deploy: API (Render) + Frontend (Vercel) + SQLite

- **API:** Hono + Bun on Render (Web Service with persistent disk for SQLite).
- **Frontend:** Astro (SSR) on Vercel via `@astrojs/vercel` (serverless adapter; see `web/astro.config.mjs`).
- **Database:** SQLite file on Render disk at `/data/sqlite.db`; migrations run at API startup.

Deploy order: **API first**, then frontend (so you can set `PUBLIC_API_URL` to the live API).

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

4. **DB:** The Blueprint attaches a 1 GB persistent disk at `/data`. `DB_PATH` is set to `/data/sqlite.db`. Migrations run automatically on every start (`bun run migrate && bun run start`).

5. Deploy. After deploy, copy the **service URL** (e.g. `https://mto-api.onrender.com`) for the frontend.

6. In **Clerk Dashboard** → your application → **Paths** / **Allowed redirect URLs**: add your production frontend URL and, if needed, the API URL. Add the frontend origin to **CORS** if Clerk uses it.

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
- [ ] Clerk: first user to sign in in production becomes admin; `/admin` works for that user.
- [ ] In Clerk dashboard, production frontend URL is in allowed redirect/origin list.

---

## 4. Optional: custom domains

- **Render:** Service → Settings → Custom Domain.
- **Vercel:** Project → Settings → Domains. After adding a domain, update Render’s `PRODUCTION_URL` and Clerk’s allowed URLs to that domain.

---

## 5. Troubleshooting

- **CORS errors:** Ensure `PRODUCTION_URL` on Render exactly matches the frontend origin (scheme + host, no trailing slash).
- **Migrations:** They run at API startup. If you add new migrations, push and redeploy; the new instance will run `bun run migrate` then start.
- **SQLite on Render:** The disk is only available at **runtime**. Do not run migrations in a pre-deploy or build step; the start command handles them.
- **"no such table: users" / admin 500:** The DB was not migrated. In Render → your API service → **Settings**: set **Start Command** to exactly `bun run migrate && bun run check-db && bun run start`, set **Environment** → **DB_PATH** to `/data/sqlite.db`. Then **Manual Deploy** → redeploy. Check **Logs** for `[migrate] DB_PATH:` to confirm the path.
- **Vercel "invalid runtime: render (nodejs18.x)":** The Astro preset runs `astro build` only, so the patch never runs. **Fix:** In Vercel → Project → **Settings** → **Build & Development** → **Build Command**, set to **`bun run build`** (not the default). Then redeploy. The `build` script in `web/package.json` runs the patch after `astro build`.
