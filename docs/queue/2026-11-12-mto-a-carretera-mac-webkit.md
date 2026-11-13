# Mac WebKit pass: MTO A Carretera build (branch cc/spaghettidrone)

## Goal
- The one-page A Carretera site (hero poster + Cycles loop, release strip, videos, members, WhatsApp contact) works in
  WebKit at iPhone size and at 1440.

## Evidence
- URL: http://thiccpc-wsl:3119/ (astro preview of the branch build, tailnet). If it does not answer, ask the mothership
  to restart it on WSL: `cd "/mnt/e/Cursor Projects/MTO-spaghettidrone" && MIRROR=$HOME/.cache/mto-spaghettidrone-site PORT=3119 scripts/prototipo.sh`.
- Chromium numbers (WSL, 2026-11-12, `revisar.sh` web, table in `docs/design/build-revisar/table.tsv`): 0 FAIL;
  weight at 390 = 1.49 MB; CLS 0.000 (390) / 0.016 (1440); contrast, tap targets and overflow 0 at both widths.
- Baseline: the newest earlier pass dir on the Mac (`~/cc-out/*-webkit/`); reuse its Playwright with
  `PW_DIR=<dir>/node_modules`. Node: `/opt/homebrew/bin/node`.

## Task (each answer is a number or a short string)
1. Load `/` in WebKit at 390×844 (deviceScaleFactor 3, isMobile, hasTouch). After 5 s report `#loop.currentSrc`
   (expect it to end in `loop-720x1280.mp4`), `#loop.paused` (expect false), and whether `#loop` has the class `on`.
2. Same at 1440×900: `currentSrc` should end in `loop-1600x900.mp4`.
3. Click `#pausa`: report `#loop.paused` (expect true) and the button's `aria-pressed` (expect "true"); click again (expect false / "false").
4. Reduced motion (`reducedMotion: 'reduce'`) at 390: after 5 s, `#loop.paused` (expect true) and `#pausa` text (expect "Reproducir video").
5. Screenshot each section at 390 and 1440 (`#inicio`, `#musica`, `#video`, `#integrantes`, `#contacto`): count shots where
   the heading is missing or clipped, and report whether the headings render slanted (synthetic oblique of Saira
   Condensed 800; Chromium slants it).
6. Horizontal overflow: `document.documentElement.scrollWidth` at 390 (expect 390). Swipe the `.tira` strip left with
   synthetic touch events on the element and report `.tira.scrollLeft` after (expect > 0).
7. Keyboard: from the top, Tab until focus reaches the first `.lanz` link; report how many Tabs it took and whether a
   3 px gold ring is visible in the screenshot.

## Constraints
- Read only. Write only under `~/cc-out/mto-a-carretera-webkit/`.
- On a 502/403, wait with an `until` loop up to 10 min, then report.
- Touch: synthetic events on the element, never `new Touch()` (crashes WebKit).
- Band photos: adults only on this page; no minors' footage.
- Every background step has a timeout; a step that can't finish is reported as a failure with the reason.
- macOS WebKit is not iOS Safari: say where a phone could differ (autoplay of muted inline video under Low Power Mode,
  `<source media>` selection, `100svh`).

## Done-check
`test -s ~/cc-out/mto-a-carretera-webkit/results.json`

## Report
Verdict first: OK from WebKit's side, yes or no. Then the seven answers.
