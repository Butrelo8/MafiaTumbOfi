# Handoff: A Carretera, tweak bar then build (2026-11-12)

Picked by the owner at 21:56 (mothership-10). This session stopped at the context limit set by its stance. The next
session starts here, on branch `cc/stonkdrone` in worktree `/mnt/e/Cursor Projects/MTO-stonkdrone`.

## What exists

- `docs/design/brief.md` holds the content brief, the asks and the pick. `docs/design/references.md` passes refs-check
  (sections `hero,musica,video,integrantes,contacto,botones`). Rows tagged **A:** are the build's trace.
- `docs/design/directions.md` › A has the palette, type, motion, cost and the honest limits.
  `docs/design/benchmark.md` has the bar (eptosuno: `revisar.sh` 5 FAIL, 2.53 MB at 390).
- Prototype: `docs/design/directions/a-carretera.html` + `data.js`. It is static and loads `/public/...`, so serve it from
  the repo root: `cd "/mnt/e/Cursor Projects/MTO-stonkdrone" && python3 -m http.server 3117 --bind 0.0.0.0`, then
  open `http://thiccpc-wsl:3117/docs/design/directions/index.html`. Port 3100 is taken by another process.
- The truck prototype's three.js scene, its stops and its DESIGN.md: `docs/design/DESIGN.md`, `docs/prototipo-camion.md`.
  Its `src/` lives on the `cc/goblindrone` history in this repo. Loops and posters: `public/escena/`.

## Next steps, in order

1. **Tweak bar** (seed step 4, "later: a tweak bar for the picked direction"). It is a small panel on the A prototype
   with knobs for: gold hue and lightness, the veil alpha, the display face (Saira Condensed italic vs 1–2 traced
   alternatives), name size, night/dusk preset, and loop vs poster. Stop for the owner's settings (AskUserQuestion,
   or the mothership) before the build. Check whether the seed says to stop there; the mothership's 21:57 message
   says "stop for the owner at the tweak bar if your brief says so".
2. **Build** in `src/pages/index.astro` (Astro + Tailwind, already the stack). Port the prototype's sections and
   content from `research/contenido/`. Keep the gold fill wipe as the working button. Put the button and icon
   code in one component each (`src/components/Boton.astro`, `src/components/Icono.astro`) so the pair chain
   (`/home/black/projects/mothership/docs/queue/2026-11-12-mto-buttons-icons-pair.md`) can swap them. No pill unless the
   owner picks it over 2–3 alternatives.
3. **Gate:** `revisar.sh` web at 390 and 1440 with 0 FAIL, `slop-check.py src` with no FAIL, then a Mac WebKit pass brief
   (skill `mac-webkit-pass`). Before any Cloudflare change, use the `cloudflare:*` skills. No deploy, no push.

## Open (the owner's, don't block; use placeholders)

- WhatsApp number (SPEC 228 835 1464 vs socials.ts 228 353 8827)
- ONErpm date and announcement post
- who is in the 5-person `cover.jpg`
- covers at ≥ 1000 px (the current ones are 160 px)
- the logo as a vector
- lead with "POR EL BLOC"?
- Tripo plan and attribution vs ToS §5.2.1
- Known A flaws: low-poly CC0 pickup at close stops; dusk turns the paint silver; dark-lens bug in the 16:9 loop
  (`docs/prototipo-camion.md`)
