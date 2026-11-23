# Ticket 01 evidence: page first, the intro never blocks reading

Measured 2026-11-23 on the same machine, one build pair: `main` 0ea007d (before) and this branch (after). Both were built with
`bun run build`, with the gitignored `public/vivo/*.glb` and `draco/` copied in from `MTO-gamblingdrone` (the worktree had none), and
served by `scripts/servir-dist.mjs` (brotli, Range) on 127.0.0.1:4601 (before) and :4602 (after). No deploy: the URLs are local.

## 1. LCP before and after

Command (same script and settings for both):

```sh
PW=/mnt/e/tmp/pw-vivo/node_modules/playwright-core node scripts/medir-lcp.mjs http://127.0.0.1:4601/ 5 docs/wayfinder/escenas/assets/01-lcp-antes.json
PW=/mnt/e/tmp/pw-vivo/node_modules/playwright-core node scripts/medir-lcp.mjs http://127.0.0.1:4602/ 5 docs/wayfinder/escenas/assets/01-lcp-despues.json
```

Conditions: snap Chromium (157.0.8103.50, H.264), 390×844 @2x, mobile UA, 4× CPU throttle, Fast 4G (9 Mbps down, 1.5 Mbps
up, 60 ms), a cold cache per run, five runs, median. LCP is a `PerformanceObserver('largest-contentful-paint')`; the page gets no input,
so nothing freezes it early. "h1 readable" is the first frame where the topmost element at the h1's centre is the h1 itself, nothing is
`inert`, and it is opaque. TTFF is `html[data-listo]`, the live canvas' first frame (software GL here, so the absolute number is slow).

| | LCP (median) | LCP element | FCP | **h1 readable** | TTFF |
|---|---|---|---|---|---|
| before (main 0ea007d) | 228 ms | `h1` (text) | 228 ms | **17501 ms** | 7893 ms |
| after | 232 ms | `h1` (text) | 232 ms | **217 ms** | 7705 ms |

Before, per run:

| run | LCP ms | FCP ms | h1 readable ms | TTFF ms | escena.glb starts | apertura.mp4 starts |
|---|---|---|---|---|---|---|
| 1 | 312 | 312 | 15434 | 6497 | 558 | 205 |
| 2 | 228 | 228 | 20598 | 7638 | 555 | 231 |
| 3 | 224 | 224 | 15588 | 7893 | 547 | 232 |
| 4 | 236 | 236 | 17732 | 8027 | 564 | 237 |
| 5 | 228 | 228 | 17501 | 8091 | 549 | 227 |

After, per run:

| run | LCP ms | FCP ms | h1 readable ms | TTFF ms | escena.glb starts | apertura.mp4 starts |
|---|---|---|---|---|---|---|
| 1 | 388 | 388 | 232 | 7443 | 1523 | 434 |
| 2 | 236 | 236 | 217 | 7734 | 722 | 335 |
| 3 | 232 | 232 | 217 | 7929 | 728 | 337 |
| 4 | 224 | 224 | 211 | 7705 | 715 | 327 |
| 5 | 224 | 224 | 210 | 7623 | 712 | 346 |

**What the numbers say.**
- The page is readable at once: the h1 went from 15.4–20.6 s (the overlay and `inert` ended it) to about 0.2 s, the same frame as FCP.
- The browser's own LCP did not move (228 → 232 ms) because it was never the problem in this lab: Chrome counts the h1 text even
  while an opaque overlay covers it, and it is the largest candidate on both builds (no image or video frame registered as one). So LCP
  alone cannot show this fix; "h1 readable" is the number that does. I could not reproduce the 22 s field LCP p75 in the lab.
- The scene is not slower: TTFF 7893 → 7705 ms. The scene's files start later (escena.glb at 0.55 s → 0.72 s) and the clip at
  0.34 s instead of 0.21 s, both after FCP and after `load`; the extra delay is the cost of "after first paint", about 0.2 s.
- The three.js bundle (638 KB) is now a dynamic chunk, `import()`-ed after first paint; `pantalla.mp4` still starts at 13–17 s.

## 2. Scroll and focus test

```sh
PW=/mnt/e/tmp/pw-vivo/node_modules/playwright-core node scripts/probar-pagina-primero.mjs http://127.0.0.1:4601/ docs/wayfinder/escenas/assets/01-prueba-antes.json
PW=/mnt/e/tmp/pw-vivo/node_modules/playwright-core node scripts/probar-pagina-primero.mjs http://127.0.0.1:4602/ docs/wayfinder/escenas/assets/01-prueba-despues.json
```

At FCP + 500 ms, same phone conditions, intro still playing:

| | before | after |
|---|---|---|
| nav / h1 `inert` | yes | no |
| topmost element over the h1 and two nav buttons is the control itself | no (the overlay) | yes |
| Tab order from the top | Saltar, body, Saltar, body (nav unreachable) | Saltar, Cabina, Caja, Pantalla |
| wheel and touch drag reach the document, none cancelled | 1 wheel, 4 touchmove, 0 cancelled | same |
| a tap on `#p-caja` | waited for the intro to end (Playwright retried until the overlay left) | taken at once; the intro steps aside; `aria-current` moves to Caja |

The home has nothing to scroll: `html, body { overflow: hidden }`, the scene is fixed and the nav moves the camera (owner's design,
`index.astro`). `scrollHeight - innerHeight` is 0 on both builds, so "scrolls" here means the events are not blocked or cancelled, which
they are not. There is no section text on this page; the readable content is the h1, the nav and the credits line.

## 3. The look

Side by side, before | after, at 390 and 1440: `01-aspecto-390.png`, `01-aspecto-1440.png` (rows: the writing at 1.6 s, the clip 1 s
after it starts). Taken with `?respaldo` (no WebGL) so the timing is exact:

```sh
PW=... node scripts/fotos-apertura.mjs "http://127.0.0.1:4601/?respaldo" <out>/foto-antes   # and :4602 → foto-despues
```

The writing, the clip and the black ground are identical. What differs is only what the ticket asked for: the h1, the nav and (at 1440) the
credits line sit on top of the intro, and Saltar moved up by 60 px so it does not sit on the nav row. The fade into the scene is unchanged.
The full-GL runs of `medir-inicio.mjs` were not usable for stills here: under software GL a screenshot takes 12 s, so the moments drift.

## 4. Field LCP

Not available. The repo has no RUM source: `/e` (Analytics Engine `mto_events`) records page views and clicks only, no timings. The 22 s
figure in the map note came from outside the repo. To close this item, someone has to read the field LCP p75 seven days after the deploy
(CrUX or Cloudflare Web Analytics, if either is on for mafiatumbada.com), or add an LCP field to `/e`.

## Checks

```sh
bun test            # 150 pass, 0 fail
bun run build       # ok
! grep -n 'inert = true' src/scripts/apertura.ts   # no match
python3 -I ~/projects/visual-lab/web/scripts/slop-check.py src   # exit 1: 4 FAIL, all in /anterior and MemberCard (old pages, untouched); pill-button REVIEW at Apertura.astro:34 is the existing Saltar
revisar.sh "http://127.0.0.1:4602/?respaldo"   # 390 + 1440: overflow 0, tap 0 under 44 px, fixed-over-text 0 covered, contrast 0, CLS 0.000/0.001, weight 2.43 MB; one FAIL, motion-spec (the existing stroke-dashoffset writing, DESIGN.md › Opening)
refs-check.py docs/design/references.md --sections apertura-carga   # section-has-row, path-exists, row-complete, ficha-measured PASS; row-cites-library FAIL on 16 older prop rows (same on main, not from this change)
```
