# CLAUDE.md

## Project

Mafia Tumbada is one static Astro page. The build output in `dist/` is served
by Cloudflare Workers Static Assets.

## Commands

```bash
bun dev
bun run build
bun test
npx wrangler deploy
```

## Structure

- `src/pages/index.astro` — page entry point
- `src/components/` — page components
- `src/data/` — catalog, member, and social data
- `src/styles/` — global and marketing styles
- `public/` — static media, favicon, robots, and redirects
- `wrangler.jsonc` — Cloudflare Workers Static Assets configuration
- `DESIGN.md` — visual-system source of truth

## Design rules

Read [`DESIGN.md`](./DESIGN.md) before changing the page. Preserve the
Veracruz Noir direction: black-on-black surfaces, Cormorant Garamond for
headlines only, Inter for body/UI, JetBrains Mono for tabular data, turquoise
for links and focus, and gold for signature labels and CTAs.

Keep the asymmetric editorial layout, responsive spacing, WCAG AA contrast,
visible focus states, Spanish-first labels, 44px touch targets, and
reduced-motion support. Do not add centered stock-hero layouts, gold body text,
or motion that ignores `prefers-reduced-motion`.

## Environment

Use `.env.example` for the current site and build-only catalog variables. Keep
credentials private; variables intended for the browser must be explicitly
prefixed `PUBLIC_`.
