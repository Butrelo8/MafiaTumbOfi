---
title: Page first on the live site, the intro never blocks reading
type: build
status: open
assignee:
gate:
blocked_by: []
closed_as:
gist:
---

## Question

Make the live home (`/`, `src/pages/index.astro`) follow the owner's page-first rule (map Notes, owner 2026-11-23 06:16).

**What happens today.** The apertura covers the page for about 13 s, and the field LCP p75 on phones is 22 s. The cause
is in `src/scripts/apertura.ts`:
- `MIN 2400` and `MAX 7000` hold the writing on screen.
- The overlay waits for the video's `duration * 1000 + 3000` before it hands over (`empalmar`).
- `ESCENA_MAX 3000` waits for the canvas.
- The nav and the page are `inert` while it plays (lines 19 and 35).
- `apertura.mp4` shares the pipe with `escena.glb` (`docs/handoffs/2026-11-20-g63-sucesor.md`).

**What changes.**
- The h1, the nav and the section text paint first and are readable and scrollable at once.
- The "MTO" writing and the clip play as a header or background behind the content: no overlay and no `inert`.
- three.js, the GLBs and `apertura.mp4` start loading after first paint.

**Keep the look:** the same writing, clip, fade and scene. Only the order things load in and the layering change. The
existing skips stay: reduced motion, `#anchor`, `?f`, `?parada`, `?toma`, and a return visit.

## Done-check

Evidence goes in `docs/wayfinder/escenas/assets/01-lcp.md`, with the command, the before and after numbers, and the
URLs:

1. **LCP before and after.** Measure on the same build pair and with the same script.
   - **Browser:** the snap Chromium (`/snap/bin/chromium`, which plays H.264). Headless Playwright's bundled Chromium
     does not decode H.264, so it cannot measure this intro.
   - **Settings:** 390×844 viewport, mobile UA, 4× CPU throttle, Fast 4G.
   - **Runs:** five or more, reported as the median.
   - **How:** LCP comes from a `PerformanceObserver('largest-contentful-paint')`. `scripts/medir-inicio.mjs` measures
     TTFF, not LCP, so add LCP to it or write a sibling script.
   - **Report:** LCP, the LCP element, time to readable h1, and TTFF, to show the scene did not get slower.
2. **Scroll test.** At first paint plus 500 ms, the page scrolls by wheel and by touch, and the nav links take focus.
3. **The look.** A side-by-side still of the intro, before and after, at 1440 and 390.
4. **Field LCP.** Note the field LCP p75 seven days after deploy, if the data source exists. Otherwise say so.

```sh
bun test && bun run build
! grep -n 'inert = true' src/scripts/apertura.ts
test -s docs/wayfinder/escenas/assets/01-lcp.md && grep -qi 'LCP' docs/wayfinder/escenas/assets/01-lcp.md
```
