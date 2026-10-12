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
Blender: for realistic human movement (Mixamo → Blender → ffmpeg), load the skill `blender`.
Do not call the `*_for_cli` tools of the `blender` MCP: from Claude Code they hang until killed at 120 s
(/home/black/projects/visual-lab/blender/lab/headless-for-cli-tools/). For a saved .blend, without the UI:
`/mnt/e/Blender/blender.exe -b "$(wslpath -w file.blend)" --python script.py`.
<!-- mpaf:animacion-blender:end -->

<!-- mpaf:deploy-cloudflare:start -->
Cloudflare: before touching `wrangler.*` or Workers code, use the `cloudflare:*` skills (wrangler,
workers-best-practices) and the `cloudflare-docs` MCP instead of writing the config from memory.
<!-- mpaf:deploy-cloudflare:end -->

## Research and methods

This repo is where the scene work happens; reusable methods live elsewhere. When a technique fails, or before
trial and error: `~/.claude/scripts/buscar-research <term>` (visual-lab, ComfyUI, this repo, Resolve).
Keep here only what is specific to this site (tickets, scene scripts). Distill general lessons into
`/home/black/projects/visual-lab` (routing table in its `CLAUDE.md`; Blender notes: `blender/blender-notas.md`;
ComfyUI generation/upscaling: `comfyui/`).

Other repos' `CLAUDE.md` (Davincy Resolve, visual-lab, ComfyUI) do **not** load in a session started
here, nor do their settings, skills or MCP servers. Quick visit (a few edits there): read that repo's `CLAUDE.md`
first and follow it. Real work in that repo: start a new session in its folder.

<!-- mpaf:edicion-resolve:start -->
DaVinci Resolve: before using the `resolve` MCP, the user starts CursorBridge in Resolve (Workspace → Scripts).
Technique, API limits and helpers (`prep_clip.sh`, `luts.sh`, `parallax.py`): /home/black/projects/visual-lab/resolve/CLAUDE.md.
Starting a render or deleting media/timelines/projects = ask permission for each action.
Generated clips (ComfyUI, Blender): before importing, read the `Deliver:` line of the technique in
/home/black/projects/visual-lab/STATUS.md (size, fps, loop, how it enters at 24p). Prep:
`prep_clip.sh in out [W H FPS]` (default 1920 1080 24); it refuses if the clip has more fps than FPS: a 48 fps loop
enters at 24p as a half-speed variant (`RETIME=1`), never with `fps=24`, which drops every other frame.
i2v clips: trim 2 frames from the start of each one when joining them (avoids a 2–3 frame freeze).
<!-- mpaf:edicion-resolve:end -->

<!-- mpaf:animacion-rive:start -->
Rive: to animate characters or interactive UI, load the skill `rive`. `rive-mcp` is the default MCP;
`rive` (official) only connects when the desktop editor is open.
<!-- mpaf:animacion-rive:end -->

<!-- mpaf:produccion-visual:start -->
Visual production: `director` for shots, script and notes on a cut; `frameref` (user skill) for the look
of each shot; `comfy-local` (user skill) to generate, never the generate/run tools of the comfy MCP.
ComfyUI methods (transitions, loops with a fixed plate): /home/black/projects/visual-lab/comfyui/playbooks.md.
Blender: `blender` skill (+ `kiln-prop` for props). Do not call the `*_for_cli` tools of the `blender` MCP: they hang.
<!-- mpaf:produccion-visual:end -->
