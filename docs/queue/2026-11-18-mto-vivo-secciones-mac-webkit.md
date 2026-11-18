# Mac WebKit pass: MTO /vivo-secciones (branch cc/sweatingdrone)

## Goal
- The live three.js scene (truck driving on an endless road, band idling, screen truck playing a video, cars both ways) loads in
  WebKit at iPhone size, and the six section buttons (click and keyboard) move the camera between the stops.

## Evidence
- URL: https://thiccpc-wsl.tail82d42e.ts.net:4412/vivo-secciones (astro preview on WSL 127.0.0.1:4411 behind tailscale serve;
  2026-11-18 13:2x: page 200, `Range: bytes=0-1` on /vivo/pantalla.mp4 206).
- Chromium numbers (Windows Chrome headless, ANGLE D3D11 RTX 4070 Ti, `scripts/medir-vivo.mjs`, results
  `~/cc-out/mto-vivo-secciones/run2/medir.json` on WSL):
  rAF p50/p95 at 1440 = 6.1 / 12.2 ms (display cadence 6.1), render p95 12.5 ms; at 390 CPU x4 = 36.3 / 72.8 ms with the video,
  30.3 / 78.9 ms paused; 780 draw calls, 3.75 M triangles. TTFF on Fast 4G (165 ms RTT, 9 Mbps) 13.1 s, 13.7 MB.
  Clicks 10/10 and keys 6/6 land on the right stop and move the camera. revisar web (fallback path) passes all but weight-390.
- Baseline: the newest earlier pass dir on the Mac (`~/cc-out/mto-camion-webkit/`); reuse its Playwright with
  `PW_DIR=<dir>/node_modules`. Node: `/opt/homebrew/bin/node`.

## Task (each answer is a number)
1. Load the URL in WebKit at 390x844 (deviceScaleFactor 3, isMobile, hasTouch). Wait up to 90 s for `window.__vivo.ttff > 0`.
   Report ttff (ms), `window.__vivo.calls`, `window.__vivo.tris` and the WebGL renderer string. If it never arrives, report
   whether `#respaldo` became a `<video>` (the no-WebGL fallback) and any page errors.
2. Frame times: clear `window.__vivo.frameMs` and `renderMs`, wait 5 s, report p50 and p95 of each (drop the first 10 samples).
   Then `window.__vivo.el.pause()` and repeat. Report `window.__vivo.video` (true = the screen video started).
3. Clicks: click `nav button[data-parada="N"]` for N = 1, 2, 3, 4, 5, 0. After each, wait 2.3 s and report
   `aria-current="true"` index and the camera distance moved (`window.__vivo.estado().cam` before and after, metres).
4. Keyboard: focus `nav button[data-parada="2"]`, press ArrowRight, ArrowRight, ArrowLeft, End, Home, ArrowLeft (2.2 s apart);
   report `document.activeElement.dataset.parada` after each (expect 3, 4, 3, 5, 0, 5).
5. Shots: load `?sinpantalla&f=0&parada=N` for N = 0..5 at 390x844, wait for ttff + 1.5 s, screenshot. Count shots whose mean
   canvas luma < 3 (blank).
6. Reduced motion (`reducedMotion: 'reduce'`): click stop 3; two `estado().cam` reads 100 ms apart after the click must be equal
   (a cut, not a move). Report the difference in metres.

## Constraints
- Read only. Write only under `~/cc-out/mto-vivo-secciones-webkit/`.
- On a 502/403, wait with an `until` loop up to 10 min, then report.
- Touch: synthetic events on document.body, never `new Touch()` (crashes WebKit).
- The side screen plays band footage as a WebGL texture; `visibility:hidden` can't reach it. Every screenshot uses
  `?sinpantalla` (the screen becomes a flat dark panel). Never view or describe the video itself. Video-on runs are numbers only.
- Every background step has a timeout; a step that can't finish is reported as a failure with the reason.
- No theme switch on this page (night only).
- macOS WebKit is not iOS Safari: say where a phone could differ (WebGL2 memory with a 9.7 MB GLB and 3.75 M triangles,
  VideoTexture from a muted inline video, Draco WASM decode time).
- Python with numpy/PIL: `uv run -q --with numpy --with pillow python -I script.py`; bare `python3` has none.

## Done-check
`test -s ~/cc-out/mto-vivo-secciones-webkit/results.json`

## Report
Verdict first: does the live scene run in WebKit at iPhone size, yes or no. Then the six numbers.
