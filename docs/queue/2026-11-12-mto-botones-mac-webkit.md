# Mac WebKit pass: MTO Tecla buttons and the morphing loop toggle (branch cc/auradrone)

## Goal
- The Tecla buttons and the play/pause morph on the loop toggle work in WebKit at iPhone size and at 1440, before the owner looks.

## Evidence
- URL: http://thiccpc-wsl:3123/ (a static server on the built `dist/` of branch cc/auradrone, tailnet). If it does not answer,
  ask the mothership to restart it: `cd "/mnt/e/Cursor Projects/MTO-auradrone/dist" && python3 -m http.server 3123 --bind 0.0.0.0`.
- Chromium numbers (WSL, 2026-11-12, `scripts/revisar-botones.sh`, tables in `docs/design/revisar/botones-iconos/r1/*/table.tsv`):
  0 FAIL; weight at 390 = 1.62 MB; CLS 0.000 (390) / 0.017 (1440). Morph samples: `docs/design/revisar/botones-iconos/r1/morph/`.
- Baseline: the newest earlier pass dir on the Mac (`~/cc-out/*-webkit/`); reuse its Playwright with `PW_DIR=<dir>/node_modules`.
  Node: `/opt/homebrew/bin/node`.

## Task (each answer is a number or a short string)
1. At 390×844 (deviceScaleFactor 3, isMobile, hasTouch) load `/`, wait 5 s. Report `#pausa` text and the `d` attribute of
   `#pausa .icono path` (expect "Pausar video" and a path starting `M6 4L10 4`).
2. Click `#pausa` and sample `d` plus the path's `transform` with requestAnimationFrame for 400 ms (the code is in
   `scripts/morph-tira.mjs` in the repo; copy the sampling idea). Report the number of distinct `d` values (Chromium: 13),
   the time of the last change (Chromium: about 250 ms), and whether the final `d` starts `M6 4L12 7.43`. Report the
   `#pausa` text (expect "Reproducir video") and that it has no `aria-pressed` attribute.
3. Same with `reducedMotion: 'reduce'`: the distinct `d` count should be 1 (one-frame swap).
4. Touch: tap `.boton.lleno` (Escuchar en Spotify) with a synthetic tap but block navigation (`route` the Spotify URL to
   abort). Report the cap's computed `background-color` right after, and again after 1 s: both must equal the idle gold
   (`(hover: hover)` is false under touch, so no stuck hover fill).
5. Screenshot the hero, `#musica` (platform buttons) and `#contacto` at 390 and 1440 and report whether the lip (4 px dark-gold
   band under each cap) renders under every button and whether the 3 px focus ring after Tab (first Tab target: "Saltar al
   contenido", then keep tabbing) wraps the cap and the lip.
6. Route `**/escena/loop-*.mp4` to abort, reload, and report whether `#pausa` is hidden. Reload with the route held open
   (never fulfilled) and report `#pausa` text after 5 s (expect "Cargando video") and whether the ring is visible.

## Constraints
- Read only. Write only under `~/cc-out/mto-botones-webkit/`.
- On a 502/403, wait with an `until` loop up to 10 min, then report.
- Touch: synthetic events on the element, never `new Touch()` (crashes WebKit).
- Every background step has a timeout; a step that can't finish is reported as a failure with the reason.
- macOS WebKit is not iOS Safari: say where a phone could differ (a tap on a link that opens the Spotify app leaves this page alive;
  muted inline video under Low Power Mode refuses `play()`, which the toggle handles by showing "Reproducir video").

## Done-check
`test -s ~/cc-out/mto-botones-webkit/results.json`

## Report
Verdict first: OK from WebKit's side, yes or no. Then the six answers.
