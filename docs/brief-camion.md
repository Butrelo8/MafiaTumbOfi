# Brief: new front end with a truck (not started)

Status: preparation only. Nothing here is decided; the owner picks the open questions below before any build.
Index of what the old build learned: `research/README.md`.

## The two options

| | A. Orbital camera around a moving truck | B. Fixed scenes around a truck on a highway |
|---|---|---|
| Idea | One truck, always moving; the camera circles it. Sections are camera angles/distances. | Several fixed shots of a truck driving a highway; each section is one shot. |
| Loop | Natural: a full 360° orbit returns to frame 0, so one clip loops with no seam. | Each shot needs its own loop or a road that repeats (wheels, road lines, scenery scrolling). |
| Scroll link | Scroll scrubs orbit angle (or moves between a few orbit stops). | One gesture = one shot (as the old build did), or scroll scrubs time inside each shot. |
| Cost | One scene, one truck, one render pass; fewer files. | N scenes/cameras; more renders, more weight. |
| Risk | Moving truck + moving camera: wheel/ground motion must loop exactly. | Transitions between shots (the old build's costliest problem). |

Recommendation for the first test (not a decision): build A first. One scene is cheaper to light and loop, and a
failed A still produces the truck, lighting and render settings B needs.

## What carries over from the old research

- **Render real geometry, not generated video.** The old build's recurring defect ("the phone waves", stones that
  keep moving, boiling surfaces) came from AI video models (H3, Flow, Seedance) between plates. A Blender render of
  a modelled scene has stable surfaces by construction. (`research/tmp/07/fasth3/veredicto.md`,
  `research/tmp/07/seedance/medicion.md`.)
- **Blender lighting/render:** Cycles with OptiX, not EEVEE; gold and chrome rendered black in EEVEE
  (`research/blender-notas.md`; re-check on the Blender version in use). Glow/halation in ffmpeg post, not in the
  compositor. Plain colour and procedural noise read as plastic: give surfaces relief, dirt and image textures
  (`research/pase-visual-2026-09-23.md`). A truck needs reflections: a real HDRI, not only point lights. Measure
  before judging by eye (the old notes' main rule).
- **Look:** 180° shutter on moving shots cut bytes by about 20 % and looks filmic; loops with a still camera need none;
  halation + light diffusion over a 2383-style grade; grain as an HTML overlay, not baked
  (`research/wayfinder/santuario/tickets/14-look-de-cine.md`). A moving truck means shutter matters here.
- **Phone budget and resolution:** mobile entry ≤ 3 MB and each gesture ≤ 1 MB, measured in a real browser with
  `scripts/medir-peso.mjs`; vertical 9:16 at 720×1280 needs its own render, since a crop of the 16:9 has too few pixels;
  codecs AV1 → HEVC → H.264 (few iPhones decode AV1); `preload="auto"` does not fully download on slow networks, so
  fetch → blob before use (`tickets/05-peso-carga.md`, `tickets/04-resolucion.md`).
- **Desktop resolution:** a 1920 source looks soft on 2560×1440 (the browser upscales bilinearly). Render at 2560 for
  large screens; a Lanczos 2560 step costs about ×1.35 bytes (`research/resolucion-1440.md`). With Blender the source
  can simply be rendered larger.
- **Scroll and loop lessons:** "one gesture = one section" works, but hijacking scroll needs keyboard, swipe, focus,
  screen-reader and history handling, and `prefers-reduced-motion` must cut directly (`tickets/11-navegacion-por-gesto.md`).
  Loop seams: blend about 0.83 s and compare first/last frames numerically; ffmpeg `vignette` dithers across frames, so
  set `dither=0` (`research/tmp/07/look/determinismo/LEEME.md`). 10 s loops with periodic elements at 240 frames
  avoid visible repetition at 5 s (`tickets/16-loops-de-10s.md`).
- **Hosting:** Workers Static Assets, not Pages. `wrangler.jsonc` still routes `/video/*` through `worker.js` for HTTP Range;
  keep that only if the new site serves video the same way (`research/wayfinder/tickets/05-cloudflare-target-findings.md`).
- **Content that stays true:** WhatsApp is the only contact path, no tour dates (`research/wayfinder/SPEC.md`); band data in
  `research/contenido/`; photos and music covers in `public/`.

## Open questions for the owner

1. **Look references:** two or three films, ads or stills that show the truck and mood wanted. The old Gótico Tumbado
   look (black, gold, red neon; `research/DESIGN.md`) — keep, drop, or evolve? Day, dusk or night?
2. **Truck model source:** no truck exists in `blender/assets/`. Buy/download a licensed model (which make and era? The old atrio used a black pickup
   "estilo Lobo"), model one, or use a photo-based kitbash (`kiln-prop` skill)? Licence must allow web use.
3. **Loop or scroll-driven:** the page plays a looping clip, or scroll scrubs the orbit angle / time? Scrubbing needs
   many small frames or an all-intra video (heavier); a loop is lighter but not interactive.
4. **Phone budget:** keep the old 3 MB entry / 1 MB per gesture, or loosen it? Minimum phone to support (mid-range Android?
   old iPhones without AV1)?
5. **Sections:** which sections does the page keep (Quiénes somos, Música, El grupo, Contratación, close), and does each
   map to a camera angle (A) or a shot (B)?
6. **Scope and who pays:** the band is unpaid family work; how many hours go into this and by when? (Old plan had a
   deadline of 2026-10-25; it no longer applies.)
7. **Merge plan:** `fresh-start` replaces the live site with a placeholder when merged into `main`. Merge only when the new front end is ready, or
   keep the old site live until then (recommended).
