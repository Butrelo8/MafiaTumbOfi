# N8N — Local testing (Option A: Schedule → App Health)

Proves N8N runs on a schedule and can call the app. The app stays the source of truth; N8N only pings `/health`.

## Prerequisites

- N8N running locally (e.g. `npx n8n` or Docker).
- App API running (e.g. `bun run start` → `http://localhost:3001`), **or** use the production frontend health URL: `https://mafia-tumbada-oficial.vercel.app/health`.

## Option 1: Import the workflow

1. Open N8N (e.g. http://localhost:5678).
2. **Workflows** → **Import from File** (or menu → Import).
3. Select `docs/n8n/schedule-to-health.json`.
4. Default URL in the workflow is `https://mafia-tumbada-oficial.vercel.app/health` (frontend health on Vercel). To ping the API instead, set **URL** to your API base + `/health` (e.g. `http://localhost:3001/health` or `http://host.docker.internal:3001/health` if N8N runs in Docker).
5. **Save** and **Activate** the workflow (toggle in the top right). The schedule runs every 5 minutes.

If import fails (version mismatch), use Option 2.

## Option 2: Create the workflow manually

1. **New workflow** → add node → search **Schedule Trigger**.
2. In the Schedule Trigger: **Trigger Interval** = **Minutes**, **Minutes Between Triggers** = `5`.
3. Add node → **HTTP Request**.
4. In HTTP Request: **Method** = GET, **URL** = `https://mafia-tumbada-oficial.vercel.app/health` (or `http://localhost:3001/health` for local API).
5. Connect **Schedule Trigger** → **HTTP Request**.
6. **Save** and **Activate**.

## Verify

- Wait up to 5 minutes (or trigger once with **Execute workflow**).
- In N8N, open the last run of **GET App Health** and confirm the response is `{ "status": "ok", "source": "frontend", "version": "0.4.0" }` (Vercel) or `{ "status": "ok", "version": "0.4.0" }` (API).
- Optionally check app logs: each request will show in the Hono logger.

## URL when N8N runs in Docker

If N8N is in a container and the API runs on the host:

- **Windows/Mac:** use `http://host.docker.internal:3001/health`.
- **Linux:** use the host’s IP (e.g. `http://172.17.0.1:3001/health`) or run N8N on the host (e.g. `npx n8n`).

## Next

After this works: same pattern for other scheduled or webhook-driven flows; keep booking and Stripe in the app.
