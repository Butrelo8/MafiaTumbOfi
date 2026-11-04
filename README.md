# Mafia Tumbada

Official one-page Astro site for Mafia Tumbada. Astro builds static files to
`dist/`, served by Cloudflare Workers Static Assets.

## Commands

```bash
bun dev
bun run build
bun test
npx wrangler deploy
```

`npx wrangler deploy` publishes the built `dist/` directory using
`wrangler.jsonc`.

## Environment

Copy `.env.example` to `.env` when local configuration is needed. Site URL,
indexing, analytics, and build-only Spotify catalog credentials are documented
there. Spotify credentials stay server-side and are never `PUBLIC_` vars.

## Design

The front end is being redone from scratch; `src/` holds a placeholder page.
What the old build found is indexed in [`research/README.md`](./research/README.md);
the next direction is in [`docs/brief-camion.md`](./docs/brief-camion.md).
