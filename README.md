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

[`DESIGN.md`](./DESIGN.md) is the source of truth for the visual system.

Keep the Veracruz Noir direction: black-on-black surfaces, Cormorant Garamond
for headlines only, Inter for body/UI, JetBrains Mono for tabular data,
turquoise for links and focus, and gold for signature labels and CTAs. Preserve
the asymmetric editorial layout, responsive spacing, WCAG AA contrast, visible
focus states, Spanish-first labels, 44px touch targets, and reduced-motion
support.
