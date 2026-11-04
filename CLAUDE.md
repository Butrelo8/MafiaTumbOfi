# CLAUDE.md

## Project

Mafia Tumbada is one static Astro page. The build output in `dist/` is served
by Cloudflare Workers Static Assets.

**Fresh start (branch `fresh-start`, 2026-11-03):** the old scroll-driven 3D
santuario was removed; `src/` is a placeholder. The front end is being redone
from scratch with Blender (see `docs/brief-camion.md`). The old build lives on
`dev` (`f7e1cc6`) and `main`; findings are kept in `research/` (index:
`research/README.md`).

## Commands

```bash
bun dev
bun run build
bun test
npx wrangler deploy
```

## Structure

- `src/pages/index.astro` — placeholder page; `src/lib/publicSiteUrl.ts` (+ test) builds its canonical URL
- `public/` — band photos, music covers, favicon, `robots.txt`, `_redirects` (the old hero videos are gone)
- `wrangler.jsonc`, `worker.js` — Cloudflare Workers Static Assets configuration (the `/video/*` worker route is now dead)
- `research/` — everything kept from the old build; **start at `research/README.md`**. Read
  `research/blender-notas.md` before touching Blender
- `docs/brief-camion.md` — the two candidate directions for the new front end and the open questions
- `blender/assets/` — third-party models and textures (untracked, large); tracked there: only licenses
- `scripts/` — `esperar.sh`, `preflight.sh`, `medir-peso.mjs`

## Design rules

None are current. The prior direction (Gótico Tumbado: black-on-black, Pirata One, gold, red neon) is in
`research/DESIGN.md` as history, not as rules. Cormorant Garamond, Inter and the coastal turquoise belong to the
older Veracruz Noir direction. Until the owner picks the look, keep WCAG AA contrast, visible focus states,
Spanish-first labels, 44px touch targets and `prefers-reduced-motion` support.

## Environment

Use `.env.example` for the current site and build-only catalog variables. Keep
credentials private; variables intended for the browser must be explicitly
prefixed `PUBLIC_`.

## Scene work

- Python with numpy/PIL/cv2: `uv run -q --with numpy --with opencv-python-headless --with pillow python -I`
  (the system `python3` has none of them).
- Environment check before a batch: `scripts/preflight.sh`.
- Waiting on a job: `scripts/esperar.sh` with `run_in_background` or Monitor, never a foreground `sleep`.
  A hook in `.claude/settings.json` denies foreground `sleep` and system python with numpy/cv2/PIL.
- Findings go to: site-specific notes → this repo's `docs/`; general method → `~/projects/visual-lab`;
  client or sales findings → ProyectoInvestigación, only through its own session.

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
Methods come from the Routing table of /home/black/projects/visual-lab/CLAUDE.md. Call the scripts in
/home/black/projects/visual-lab/scripts, never copy them.
Findings go to: general method -> visual-lab (report `gotchas:` lines, they land in its gotchas-inbox.md);
site-specific notes -> this repo's `docs/`. Every discovery goes in the report as a `gotchas:` line
(`symptom -> what worked`, one per line).
<!-- mpaf:produccion-visual:end -->
