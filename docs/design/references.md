# References: truck on an endless highway (hybrid prototype, 2026-11-09)

Paths are relative to `~/projects/visual-lab`. The seed (`mothership/docs/queue/2026-11-09-mto-truck-hybrid-prototype.md`)
already fixes the path (hybrid three.js + one Cycles loop), the scene and the mood (night + dusk presets, owner update
11-09), so this table is the library trace for the build, not a menu waiting for a pick.

| section | library entry | borrow | cost |
|---|---|---|---|
| hero | `web/visuales.md#recipe-smooth-video-hero` (arraisballet.com) | Poster = exact first frame of the Cycles loop (`ffmpeg -frames:v 1`), so the poster → live scene swap has no jump; loop at 24 fps, keyframe every 2 s, faststart, no audio | B |
| hero | `web/visuales.md#dissection-landonorris-com` (landonorris.com) | three.js scene in the hero that renders only while visible (`isRendering` flag); here: pause the render loop when the tab is hidden | B |
| camera-nav | `web/visuales-fichas/kage-scroll-world.md` (kage) | Fixed camera anchors per section, damped move between them with per-stop fov; dependency-free three.js. Here driven by buttons/keys, not scroll | M |
| camera-nav | `web/visuales-fichas/interacciones-que-responden.md` (rafadesign) | Camera tour between labelled points of one 3D model; the label names where the camera goes | M |
| labels | `web/visuales.md#technique-text-over-a-rendered-scene` (MTO's own note) | Veil under text sized by measuring the brightest frame under it; lowest alpha that keeps 4.5:1 | B |
| fallback | `web/visuales.md#dissection-sports-withgoogle-com-teamusa` (teamusa) | Start from `prefers-reduced-motion`; a visible motion toggle; state on `<html>` as a data attribute | B |
| fallback | `web/visuales.md#dissection-landonorris-com` (landonorris.com) | If WebGL2 is missing, add a class on `<html>` and show the poster/loop; the page works without 3D | B |
| lighting | user: owner decision 11-09, night and dusk as two presets of one scene; night palette traces to `research/DESIGN.md` (Gótico Tumbado: black, gold, red neon) | One values file (`src/lib/luces.json`) read by both Blender and three.js; preset switch in the UI | M |
| truck | user: no truck in `blender/assets/`; seed allows a free licensed model. Quaternius "Pickup Truck", CC0, https://poly.pizza/m/qn4grQgHm8 (old atrio used a black full-size pickup) | Full-size pickup, repainted black clearcoat + chrome; wheels are separate nodes so they can spin | B |
