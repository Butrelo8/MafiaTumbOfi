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
- `blender/` — scene and look scripts for the scroll-driven 3D santuario
- `docs/HANDOFF.md` — **start here**: current state, what is blocked, and
  pointers to every other document
- `docs/blender-notas.md` — **read before touching `blender/`**: Blender 5.2
  quirks, measurement method and decisions already taken

## Design rules

Read [`DESIGN.md`](./DESIGN.md) before changing the page. Preserve the
Gótico Tumbado direction: black-on-black surfaces, Grenze Gotisch for display
type only, Archivo for body/UI, JetBrains Mono for tabular data, red neon for
links, rules and glow, and gold for display type, the MTO monogram and CTAs.

Cormorant Garamond, Inter and the coastal turquoise belong to the retired
Veracruz Noir direction — do not reintroduce them.

Keep the asymmetric editorial layout, responsive spacing, WCAG AA contrast,
visible focus states, Spanish-first labels, 44px touch targets, and
reduced-motion support. Do not add centered stock-hero layouts, gold body text,
or motion that ignores `prefers-reduced-motion`.

## Environment

Use `.env.example` for the current site and build-only catalog variables. Keep
credentials private; variables intended for the browser must be explicitly
prefixed `PUBLIC_`.

<!-- mpaf:animacion-blender:start -->
Blender: para movimiento humano realista (Mixamo → Blender → ffmpeg), carga la skill `blender`.
<!-- mpaf:animacion-blender:end -->

<!-- mpaf:deploy-cloudflare:start -->
Cloudflare: antes de tocar `wrangler.*` o código de Workers, usa las skills `cloudflare:*` (wrangler,
workers-best-practices) y el MCP `cloudflare-docs` en vez de escribir la config de memoria.
<!-- mpaf:deploy-cloudflare:end -->

## Research and methods

This repo is where the scene work happens; reusable methods live elsewhere. When a technique fails, or before
trial and error: `~/.claude/scripts/buscar-research <term>` (visual-lab, ComfyUI, this repo, Resolve).
Keep here only what is specific to this site (tickets, scene scripts). Distill general lessons into
`/mnt/e/Cursor Projects/visual-lab` (routing table in its `CLAUDE.md`; Blender notes: `blender/blender-notas.md`)
or ComfyUI `research/` (generation, upscaling).

Other repos' `CLAUDE.md` (Davincy Resolve, visual-lab, ComfyUI) do **not** load in a session started
here, nor do their settings, skills or MCP servers. Quick visit (a few edits there): read that repo's `CLAUDE.md`
first and follow it. Real work in that repo: start a new session in its folder.
