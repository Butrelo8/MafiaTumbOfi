# Site `/` on a preview (2026-11-18, branch `cc/sitio-completo`, run `maincharacterdrone`)

Spec: mothership `docs/queue/2026-11-18-mto-full-site-preview.md`. The prototype is `/`; the A Carretera home is `/anterior`
(`noindex`, not linked); main's prod features are merged in (click events, `/wa/` counter, Spotify + Instagram on the first
screen, Plausible gated on `PUBLIC_PLAUSIBLE_DOMAIN`, fan list still parked).

## What the preview shows
- Lists: `research/contenido/catalog.json` is byte-identical to main's `src/data/catalog.json`. CI does pass Spotify secrets,
  but Spotify answers 403 and YouTube's feed 404 (`deploy.yml` header), so its build also falls back to that snapshot: the
  preview shows the same 9 releases and 14 videos. The new `/` imports the snapshot directly and never calls `loadCatalog()`,
  so a future prod merge will not pick up fresh lists unless that changes.
- Build env: none of `PUBLIC_ALLOW_INDEXING`, `PUBLIC_PLAUSIBLE_DOMAIN`, `PUBLIC_SITE_URL` was set: `noindex`, no Plausible.
- Scene: the run and the loop are the picture at every stop; `public/prototipo/parada-1..6.webp` (montaje-esc1..6) show
  only while the run cannot show a frame. The vertical 9:16 framing is still pending: at 390 the 16:9 render is cropped to its
  centre (the Videos stop shows only a strip of the screen).

## Build and deploy
```bash
# build on ext4 (a build on /mnt/e takes minutes), then upload a version, never a deploy:
rsync -a --delete --exclude node_modules --exclude blender --exclude dist --exclude .git --exclude research/tmp --exclude research/lighthouse --exclude .astro --exclude revisar --exclude docs/prototipo-camion --exclude effectcraft --exclude lab ./ ~/.cache/mto-sitio-completo/
cd ~/.cache/mto-sitio-completo && bun install && bunx astro build && bun test
bunx wrangler versions upload --preview-alias sitio-completo --message "full site preview"
```
A test click on a preview writes to prod's `mto_events` and `WA_CLICKS` (the preview shares the Worker's bindings).
`versions upload` does not make the version live; the alias URL is printed by the command. `run_worker_first` now includes
`/prototipo/*`: Workers Static Assets ignores Range and iOS Safari refuses a `<video>` without a 206 (`src/lib/rangoVideo.test.ts`
fails for any `.mp4` outside a worker-first route; `wrangler dev`: `Range: bytes=0-1` on `/prototipo/ruta.mp4` was 200, is now 206).

## Numbers (local `wrangler dev`, snap Chromium with H.264, 2026-11-18)
```
bun test                        44 pass, 0 fail
run -> loop handover, 1440      hold 700 ms in the station: loop t 33.1 -> 47.9 (+14.8 f in 600 ms), bucle.paused false
                                scroll +40: loop pauses (t null), hold: plays again; scroll out: run on, bucle off (f 569)
run -> loop handover, 390       same sequence: t 36.3 -> 50.7; out: run on
click event                     tap "Escribir por WhatsApp": POST /e {"event":"wa_click","page":"/","placement":"contratacion"}
                                204; GET /wa/5212283538827?text=... 302 -> wa.me
revisar web (dist, videos emptied) overflow 0 at 320/390/768/1440, tap<44 0, contrast 0, cls 0.000 / 0.032, reduced-motion 0,
                                weight 0.63 MB at 390 (videos excluded), FAIL img-upscaled (below)
slop-check src                  0 FAIL, 2 REVIEW (index.astro:123, tell 17 muted subtitle; I take it to be the Gira line at 191 that
                                DESIGN.md accepts, not verified; loop.ts:76 is /anterior)
```
`revisar.sh` never reaches network idle with the real videos (`ruta.mp4` stays pending in its Chromium), so its numbers come
from a copy of `dist/` with the two `.mp4` emptied: layout, tap, contrast and overflow do not depend on the video.
`img-upscaled` FAIL: the 9 cover files in `public/music/` are 160 px and show at 210-280 px; the YouTube thumbs are
`hqdefault` (480 px) at 644-716; `parada-1.webp` is 960 px at 1440. Covers need larger sources (not verified: where from).
Shots: `capturas/{390,1440}-<stop>.png` (live video) and `capturas/sin-video-{390,1440}-<stop>.png` (the still path), `resultados.json`.
