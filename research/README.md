# research/ — what the old build found

Kept on the `fresh-start` branch (2026-11-03) when the old scroll-driven 3D santuario was removed.
The old build, whole, is on `dev` at `f7e1cc6` (and `main` is untouched, still the live site).
Recover any deleted tracked file with `git checkout f7e1cc6 -- <path>`.

Paths written inside these files point to the old layout (`docs/`, `blender/*.py`, `tmp/`, `entrega/`, `.wayfinder/`).
`tmp/` and the media are gone; `docs/` and `.wayfinder/` are now under `research/`. Language: Spanish unless noted.

## Top level

| File | What it is / what it found |
|---|---|
| `blender-notas.md` | Blender 5.2 field notes for this project. Decisions: Cycles/OptiX not EEVEE (gold and chrome render black in EEVEE), glow in ffmpeg post, mobile budget 2 MB target / 3 MB cap, "measure before opining". General Blender traps live in `~/projects/visual-lab/blender/blender-notas.md`. |
| `resolucion-1440.md` | Why 1920 video looked soft at 2560×1440: the cause is the source (plates are 1696 px wide, browser upscales bilinearly, codec is not the cause). Lanczos to 2560 gives ×1.2 fine detail for ×1.35 bytes; RTX VSR fails the sharpness check; unsharp doubles the weight. Includes the desktop weight numbers. |
| `loops-v5.md` | Atrio loop fixes: baked rain texture was 98 % frozen in the loop (rms 1.29 vs 0.17 live); truck droplets were 0 % live pixels; how each was measured and fixed. |
| `pase-visual-2026-09-23.md` | Visual-flatness diagnosis of the 3D scene: only 7 of 285 meshes used image textures; wood, wax, felt, glass had no relief or dirt. Shows what makes a Blender scene read "plastic". |
| `scope-terminado-2026-10-12.md` | Plan for "done": steps, costs, what to defer, the 2026-10-25 deadline logic (MTO technique reused for the portfolio redesign). |
| `skills-audit-2026-10-12.md` | Audit of 27 Claude Code transcripts: where time was lost (foreground `sleep` 2.17 h, system python without numpy, etc.) and which fixes became hooks/scripts. |
| `santuario-web.md` | How the old site mounted the santuario (data file, player, preload via fetch→blob, UI layers) and what was provisional. |
| `CONTEXT-glosario-santuario.md` | Glossary of the old build's terms (espacio, estación, transición, oclusor, loop, reliquia). |
| `DECISIONS.md` | ADR log from the April 2026 site (Hono/Drizzle/Clerk/Turso backend, booking, admin). The backend is long gone; kept for the reasons behind decisions. |
| `DESIGN.md` | Design system of the "Gótico Tumbado" direction (tokens, type, motion rules). History, not current rules. |

## specs/ (design rationale)

| File | What it is |
|---|---|
| `specs/2026-09-16-santuario-3d-scroll-design.md` | Approved design of the scroll-driven 3D scene (pre-rendered frames on canvas, loops on stop). The architecture was later replaced by per-section video. |
| `specs/2026-09-17-santuario-profundidad-design.md` | Depth, pop-in and the "altar" station. |
| `specs/2026-10-10-micro-colgado-design.md` | Hanging gold microphone as the bokeh subject; Fable's corrections. |
| `specs/2026-10-14-asset-map-design.md` | Design of the asset-dependency map (plate → loop → transition → mask) and the stale-check. |

## wayfinder/ (decisions with reasons)

| File | What it found |
|---|---|
| `wayfinder/MAP.md`, `wayfinder/SPEC.md` | April 2026 static-rebuild spec: one Astro page, no backend, WhatsApp-only contact, no dates section. |
| `wayfinder/tickets/01..09` | Keep/toss inventory, section order, WhatsApp CTA, copy, asset trim and perf budget (09). 04 is void (no tour dates). |
| `wayfinder/tickets/05-cloudflare-target-findings.md` | Cloudflare recommends Workers Static Assets, not Pages, for new projects; the config that followed. |
| `wayfinder/santuario/MAP.md` | Index of every santuario decision, one line each. Read this first for the 3D work. |
| `…/tickets/01-prueba-nave-sacristia.md` | Hidden cut behind a pillar works; MiniMax beat DepthFlow; 864×480 too small. |
| `…/tickets/02-instrumentos-nave.md` | Klein and MiniMax hold instruments without deforming; 1 of 3 seeds succeeds. |
| `…/tickets/03-layout-ui.md` | UI over the scene: titular que se abre, one piece at a time, dark hole bottom-left. |
| `…/tickets/04-resolucion.md` | Measured RTX VSR vs FlashVSR vs native H3: FlashVSR invents detail and flickers; H3 1280×704 + RTX ×1.5 chosen; H3 needs sides multiple of 32; 12 GB VRAM ceiling. |
| `…/tickets/05-peso-carga.md` | Weight budget (mobile entry ≤ 3 MB, gesture ≤ 1 MB), codec order AV1→HEVC→H.264 (few iPhones decode AV1), `preload="auto"` does not fully download on slow nets so use fetch→blob. |
| `…/tickets/06-movil.md` | 9:16 mobile version (720×1280; crops of the 16:9 are too small, vertical needs its own generation). Long log. |
| `…/tickets/07-guion-espacios.md` | Script of camarín, cripta and atrio, including the black truck in the atrio, and the transition recipes. Long log. |
| `…/tickets/10-acabado-ui.md` | UI finish and motion review. |
| `…/tickets/11-navegacion-por-gesto.md` | One gesture = one section; scroll hijack needs keyboard, swipe, focus, screen reader and history handling; reduced motion cuts. |
| `…/tickets/12-contrabajo.md` | Making the upright bass read as a bass: real silhouette, seat height or higher. |
| `…/tickets/13-placa-y-capas.md` | Fixed locked-off plate + generated layers only where things move; canny alone is not enough. |
| `…/tickets/14-look-de-cine.md` | 180° shutter on transitions (−20 % bytes), halation, real-lens depth of field T2.8; grain in HTML not baked. |
| `…/tickets/15-micro-colgado.md` | Hanging mic as bokeh subject; 10 s native H3 loop fits in 12 GB at 928×512. |
| `…/tickets/16-loops-de-10s.md` | 10 s loops everywhere; candles/dust at period 240 so they do not repeat at 5 s; vertical 512×928 with grey-veil matching. |
| `…/tickets/17-transiciones-micro-v5.md` | Compositing a 2D subject over a moving shot with Blender camera tracking. |
| `…/tickets/08-hero-a-nave.md`, `09-integracion-web.md` | Short stubs. |

## contenido/ (band data, not research; moved out of `src/data/`)

`catalog.json` (release catalog snapshot), `members.ts` (band members), `socials.ts` (official social URLs).

## entrega/ (record of the frozen deliverables; the masters themselves are left untracked in `entrega/maestros/`)

| File | What it is |
|---|---|
| `entrega/LEEME.md` | What each frozen file was (names, codecs, ladder, seams, provisional Flow transitions) as of 2026-10-14. |
| `entrega/MANIFEST.tsv` | Frames, KB and short sha256 per delivered file, plus origin. Checksums for the lossless masters. |

## lighthouse/

`www.mafiatumbada.com_2026-04-28_10-35-21.report.{html,json}` — Lighthouse on the live site, 2026-04-28: performance 36, accessibility 96, best practices 96, SEO 100. Force-added (the `.gitignore` ignores `*.report.*`).

## tmp/ (the markdown that survived; the rest of `tmp/` is archived outside the repo)

Hand-written verdicts and notes from `tmp/`, paths preserved. Ticket 07 transitions (English).

| File | What it found |
|---|---|
| `tmp/07/fasth3/veredicto.md` | Local FastH3 (first+last frame) vs Google Flow job2 for camarín → cripta; latest verdict: splitting the transition at the black is the recipe; the phone still waves when it moves. |
| `tmp/07/fasth3/partido.md` | The split-at-the-black round, RIFE comparators; the full-frame warp median disagreed with the eye (do not use it as a pick criterion). |
| `tmp/07/fasth3/partido/gemini/*.md` (6) | Gemini continuity reviews of the split candidates. Unverified: Gemini invents video descriptions, check against frames. |
| `tmp/07/fasth3/revisar/**/eagle/report.md` (4) | Eagle review reports of one-take clips (boiling stones, phone dial wobble, speed judder). |
| `tmp/07/flow/job{1..4}/{STEPS,notes,veredicto}.md` | Google Flow (Veo 3.1 Fast) runs per transition: steps for a browser drone, end-frame match (frames 0/184 match, last 7 creep), darkness, verdicts. |
| `tmp/07/flow/upscale_job2.md` | Flow 720p→1080p upscale keeps geometry (0.0–0.1 px offset). |
| `tmp/07/look/veredicto.md` | LOOK + halation applied over loops and provisional transitions; seams. |
| `tmp/07/look/determinismo/LEEME.md` | ffmpeg `vignette` dithers with state carried across frames, so the LOOK is not per-frame deterministic; use `dither=0`. |
| `tmp/07/masks/RECETA.md` | Precise-mask recipe with SAM 3.1 in core ComfyUI nodes (no custom nodes). |
| `tmp/07/seedance/medicion.md` | Seedance 1.5 pro vs the local take: real camera move but lands off the plate (2.1 % stretch); worse for MTO. |
| `tmp/07/seedance_api/runs.md`, `runs_15pro.md` | Seedance 2.0 mini API tests ($1.14): ignored the last frame; 1.5 pro not available to the account. |
| `tmp/cine-look/NOTAS.md` | Cine-look prototype notes (shutter, halation, DOF). |
| `tmp/micro/NOTAS.md`, `tmp/micro/fable/REVISION.md` | Hanging-mic build chain and Fable's review. |
| `tmp/hero-src/*.info.json` | yt-dlp metadata of the two reference videos used for the old hero (not markdown; copied because they are the only record of the sources). |
