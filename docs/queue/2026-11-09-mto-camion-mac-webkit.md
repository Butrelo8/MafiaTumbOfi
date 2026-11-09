# Mac WebKit pass: MTO truck prototype (branch cc/goblindrone)

## Goal
- The truck page (three.js live scene, 4 camera stops as tabs, night/dusk switch, poster + loop fallback) works in WebKit at iPhone size.

## Evidence
- URL: http://thiccpc-wsl:3109/ (astro preview of the branch build on WSL, tailnet; answers 200 from WSL). If the Mac can't reach it,
  the WSL side needs `tailscale serve` on 3109 (shared config: ask mothership-57, don't change it from the Mac).
- Chromium numbers (WSL / Windows Chrome, 2026-11-09): weight at 390 = 1.00 MB (`scripts/medir-peso.mjs`, live path);
  frame time p95 at 390 CPU×4 = 36.4 ms, at 1440 = 6.2 ms (Windows Chrome, RTX 4070 Ti D3D11); slop-check, refs-check in `docs/prototipo-camion.md`.
- Baseline: the newest earlier pass dir on the Mac (`~/cc-out/*-webkit/`), reuse its Playwright with `PW_DIR=<dir>/node_modules`. Node: `/opt/homebrew/bin/node`.

## Task (each answer is a number)
1. Load `/?sinrespaldo` in WebKit at 390×844 (deviceScaleFactor 3, isMobile, hasTouch). Report `document.documentElement.dataset.modo` after 15 s
   (`vivo` = live scene, `video`/`poster` = fallback) and the WebGL renderer string.
2. Click each tab (`#tab-inicio`, `#tab-musica`, `#tab-grupo`, `#tab-contratacion`), wait 2.2 s, screenshot; same with `.hora button[data-preset="atardecer"]`.
   Count shots where the canvas is blank (mean luma of the canvas area < 3).
3. Frame times: `window.__escena.frameTimes` over 5 s → p50, p95 (ms).
4. Keyboard: focus `#tab-inicio`, press ArrowRight 3 times → report the id of the selected tab (expect `tab-contratacion`).
5. Reduced motion (`reducedMotion: 'reduce'`): after a tab click, report the camera move time (expect 0: cut) via two screenshots 100 ms apart differing < 1 % of pixels.
6. Load `/` with WebGL disabled if the harness allows it, and report `dataset.modo` and whether `#loop` has a `src` ending in `.mp4`.

## Constraints
- Read only. Write only under `~/cc-out/mto-camion-webkit/`.
- On a 502/403, wait with an `until` loop up to 10 min, then report.
- Touch: synthetic events on document.body, never `new Touch()` (crashes WebKit).
- No footage of minors is on this page (no band photos); if any `banda-*`/`.corte` element appears, `visibility:hidden` before screenshots.
- Every background step has a timeout; a step that can't finish is reported as a failure with the reason.
- Both presets (Noche, Atardecer).
- macOS WebKit is not iOS Safari: say where a phone could differ (WebGL2 memory, HDR texture float support, autoplay of the fallback video).

## Done-check
`test -s ~/cc-out/mto-camion-webkit/results.json`

## Report
Verdict first: OK to merge from WebKit's side, yes or no. Then the six numbers.
