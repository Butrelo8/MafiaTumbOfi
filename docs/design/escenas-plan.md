# MTO scene site: scenes, props, phone version, assets (plan v2, 2026-11-12)

Plan only: no site code. It turns the owner's picks (mothership `docs/queue/2026-11-12-mto-scene-site-vision.md`, picks at
23:02) and the owner's answers to v1's questions (23:52, 23:54, relayed by the mothership) into a list the build can follow.
A Carretera (35565d7) stays the placeholder until this is built.

**Controlling idea:** the band picks you up and never stops driving. Scrolling is the ride, everything comes to the truck
or rides beside it, and the ride ends with their number on the plate. Tone: playful, nothing too serious.

**Storyboard:** `docs/design/escenas/storyboard/hoja-16x9.jpg` and `hoja-9x16.jpg` (one frame per scene, rendered with the
G63 stand-in, the four figures in the cab, and simple shapes for the props and the screen truck still to be modelled).
Script: `blender/storyboard.py`. v1's sheets (blockout stops, parked truck) are kept in `storyboard/v1-blockout/` as history. Frames are stored as JPEG; the script writes PNG.

## 0. Owner rules (23:52–23:54) and what is still open

Settled:
- **The truck never parks.** Every scene works with the truck driving; a stop happens as the truck passes it or with the
  camera moving round the moving truck. A scene that cannot pass that test is cut. No separate blockout stage in the build:
  scenes are built with the real truck from the start.
- **All four ride inside the cab** (manager driving, Héctor beside him, Alexandro and Diego in the rear seats). The bed carries
  the instruments and playful props. Window-down names work for everyone.
- **The manager gets a name plate and a card.**
- **Tour dates are in**, read from the band's Instagram by a separate watcher job (§5).
- **Figures:** a friend (a games 3D artist) pays for Tripo; the figures are regenerated on his paid plan as a pre-build step.
- **Truck:** the owner's Sketchfab G-wagon 6×6 by srush651, on the owner's Mac (§4).
- **No press kit:** the glovebox scene is cut (§1).
- **Radio:** the least intrusive option (§2, scene 1).
- **Stickers:** our own designs, placed free-hand on the tailgate and bed (§2, scene 2).

Still open (owner):
1. **The manager's name**, the role line for his card, and his Instagram if he wants it linked.
2. **Rights in the regenerated figures.** On Tripo's paid plans the outputs belong to the paying account, which is the friend,
   not the band. A short written licence from him to the band (commercial use on the website, any medium) closes it. Not
   legal advice; ToS §5.2.1 as read in `research/2026-11-12-interactividad.md` (C12/C13).
3. **The v3 transition must be re-rendered.** The owner liked it with Alexandro and Diego in the bed; with them in the cab,
   the bed reveal at its end now shows instruments and props. About 1.4 h for both formats at the v3 settings
   (`docs/temblor-texturas.md`: 41 + 43 min) once the new truck and figures are in.

## 1. Scene distribution

The test on every scene: does it work with the truck driving?

| # | Scene (title on its sign) | Test | Why |
|---|---|---|---|
| 1 | Cabina (MÚSICA) | **keep** | inside the moving cab; the road passes through the windshield |
| 2 | Caja (REDES) | **keep** | a tail-chase of the moving truck; the stickers ride on it |
| 3 | Pantalla (VIDEOS) | **keep, reworked** | a roadside billboard passes in seconds and cannot stay in frame while you pick a video; an LED-screen ad truck (pantalla móvil) drives beside the band instead |
| 4 | Costado (LA BANDA) | **keep** | a drive-alongside, then the camera goes over the roof to the driver's side; four windows, all moving |
| 5 | Gira (GIRA) | **keep, reworked** | the gas-station stop fails (the truck would have to pull in). The dates go on the back screen of the same pantalla móvil, driving ahead in the band's lane |
| — | Guantera (PRENSA) | **cut** | there is no press kit. The glovebox survives as a playful easter egg inside scene 1 (it drops open and spills junk), which passes the test |
| 6 | Placa (CONTRATACIÓN) | **keep** | the camera leads the truck, travelling backwards ahead of it; the truck keeps coming. The roadside CONTRATACIONES sign is dropped, because it would pass by |

Order: fans first (listen, follow, watch, meet), then the dates, then booking, so the ride ends on the action the page sells.
**Contratar** stays in the fixed DOM header the whole time, so a booker never has to ride to the end.

| # | Holds | Camera sits | Move to the next scene (scroll drives it) |
|---|---|---|---|
| 1 Cabina | latest single + the radio | between the rear passengers' heads (Alexandro left, Diego right, just out of frame), 20 mm: the manager driving, Héctor, the road through the windshield (v3 f0) | **The v3 move:** forward between the front heads, out through the windshield under the mirror, up, and the truck drives on beneath until the camera settles high behind the bed (192 f, 8 s). The green REDES sign passes overhead at the end |
| 2 Caja | socials as our own stickers; instruments and playful props in the bed (stand-ins: guitars on their cases, an inflatable donut, a cooler, a piñata) | high behind the bed, 28 mm (v3 f191) | A horn from behind: the pantalla móvil overtakes on the left. The camera drops and slides left into the gap between the two vehicles; a VIDEOS sign gantry passes overhead |
| 3 Pantalla | the 14 videos on the pantalla móvil's side screen | outside the band's truck, by the driver's mirror, looking back-left at the screen, 24 mm; the manager's window in the right of frame | The pantalla móvil eases ahead; the camera swings round the band truck's rear corner to the passenger side and dollies forward alongside; a LA BANDA sign passes |
| 4 Costado | the four in their windows: Héctor and Diego on this side, then the manager and Alexandro | drive-alongside, passenger side, 6 m out, 24 mm, whole truck in frame (phone: one window per stop) | Mid-scene the camera goes up over the roof to the driver's side for the other two windows. Then it climbs onto the hood: the pantalla móvil is back, ahead in the lane, its rear screen facing the band |
| 5 Gira | the dates from the watcher's file on the pantalla móvil's rear screen | just over the band truck's hood, 30 mm, looking ahead at the screen truck's back | The pantalla móvil turns off at an exit; the camera keeps flying forward, overtakes the truck, and turns to face it, travelling backwards ahead of it |
| 6 Placa | booking: the licence plate opens WhatsApp | ahead of the truck, low, travelling backwards at its speed, 32 mm, headlights toward camera | End. One headlight flash lands the scene (the button) |

How the moves are made:
- **Desktop: real-time three.js** (the owner's answer 2 clears the licence path). One camera rail through the live scene,
  driven by native scroll: section anchors → progress → damp → position and look-at curves with a field of view per segment,
  stepping back on tall windows. Ficha: `visual-lab/web/visuales-fichas/kage-scroll-world.md` (status: unproven). The v3 control
  points (`blender/transicion.py` `CAMINO`) become the first segment of the rail, so desktop and phone share framing.
  **The truck never parks:** the scroll moves the camera and the pantalla móvil relative to the truck, and the world (road,
  lamp posts, gantries) streams past at a constant speed whether or not the visitor scrolls. Everything that has to stay in
  frame for reading rides with the truck: that is why the billboard and the gas station became the pantalla móvil.
- **Phone:** the moves are pre-rendered clips, scrubbed by scroll, and every scene holds on an idle loop of the moving
  truck (road, lamps and wheels are periodic, `escena.py` already loops at 192 m per 10 s). Ficha:
  `visual-lab/web/visuales-fichas/video-que-avanza.md` (replicated, score 0.919; not measured on a real phone).
- **Section titles on green highway signs** (owner pick 2): each title is on a sign gantry the move passes under. On the phone the
  gantry is also where one clip ends and the next begins, so the cut hides behind it (`research/2026-11-12-interactividad.md` #2,
  C34; proven on AI plates in the old santuario, **unproven on a highway**). Every sign's text also exists as the section's DOM `h2`.
- **Light:** night in every scene. Dusk-to-night (idea 9) was not picked.

## 2. Prop plan

"Needs" uses: **M** model (or a separate mesh cut from the truck), **R** rig, **A** animation (keyed in Blender or driven in code),
**T** texture only. Every in-scene control has a DOM twin: a real `<a>` or `<button>` in the section's markup, in reading order,
44 px, with the button and icon from the buttons-icons chain (the **Tecla** button and its "scene twin, a key on the cab dash",
`cc/auradrone` 9f9e101, `docs/design/DESIGN.md` › Components and `docs/design/botones/`). Nothing here redesigns them.

Pattern sources: "ficha" = a visual-lab ficha with its status; a row in `visuales.md` or in the MTO research is **not** a ficha,
so those are marked unproven with their source.

| Scene | Prop | Hover (desktop) | Click / tap | DOM fallback | Needs | Pattern source |
|---|---|---|---|---|---|---|
| **1** | **Radio** | dial lamp warms; the dash display shows the hovered single's title | turn the dial (drag, or ‹ ›): it steps through the 9 releases in `catalog.json`, the display shows title + cover; **no sound** by default | ‹ › `<button>`s + `aria-live` title, list of the 9 releases with links | M (faceplate, knob, display as its own mesh), A (knob turn in code), T (cover from `public/music/`) | unproven (no ficha) |
| 1 | Cassette in the deck | the cover in its window catches light | **Escuchar**: opens the shown release's `href` (Spotify, Apple Music or YouTube, per `catalog.json`) | the Tecla "Escuchar" | M, T | unproven |
| 1 | Dash key (Tecla scene twin) | lip shows | same as the cassette | same | M (extrusion), A (press = translation) | unproven: authored in the buttons-icons spec, not from a ficha |
| 1 | Glovebox (easter egg) | latch glints | it drops open and spills playful junk (a rubber duck, a deck of cards, a toy sombrero; owner may swap) that rattles back in | none (decorative, `aria-hidden`; no content behind it) | M (door cut from the truck mesh, hinge pivot; 3 small props), A | `objeto-que-se-abre.md` (unproven) |
| 1 | Manager's eyes in the rear-view mirror | they follow the pointer (the heads face away from this camera; the mirror shows his eyes) | none | none | R, head-turn grid rendered into the mirror | unproven: research #4, head-turn grid (face_looker, creepyface, page-mascot, C25–C27) |
| 1 | Héctor's head | turns a little toward the pointer (profile) | none | none | R, grid 3×3 | unproven (as above) |
| **2** | Our own stickers ×4 (Instagram, TikTok, Spotify, YouTube), stuck free-hand on the tailgate, the bed sides and the rear window | the corner peels | opens the profile in a new tab; on a phone the first tap peels and shows a 44 px "Abrir Instagram ↗" chip, the chip opens it | footer socials row (all six links from `socials.ts`) | T (our sticker art, see the rules below), A (curl of a plane in a shader, or a 6-frame sprite) | unproven: `visuales.md` lists `StickerPeel` (a DOM component), no ficha |
| 2 | Bed props (instruments, inflatable donut, cooler, piñata: stand-ins, owner to swap) | one wobbles on hover | none | none (decorative) | M ×4–6 (`kiln-prop`), A (wobble in code) | unproven |
| **3** | Pantalla móvil side screen | the screen's pixels brighten, the play glyph morphs (icon chain) | ‹ › change the video (a quick LED wipe); click the screen opens the video on YouTube (DESIGN rule: link out, no embedded player) | list of the 14 videos (thumbnail + link) | M (box truck with an LED panel), T (YouTube `hqdefault` thumbnail on the panel, LED dot mask in the shader) | unproven (no ficha) |
| **4** | Each of the four windows (Héctor, Diego; then the manager, Alexandro) | the glass lowers and a name plate rises: name · role, gold Instagram link | a short pre-baked pose (a wave, a hat tip, a guitar air-strum) | member cards ×4 (the manager added) | M (each window glass as its own mesh), R, A (one pose per member) | unproven; reaction clip format on the phone: stacked-alpha AV1 (research #5, C15) |
| 4 | The four heads | follow the pointer | none | none | R, grids | unproven (research #4) |
| **5** | Pantalla móvil rear screen | rows brighten | a date row opens its Instagram post (`post` in the dates file) | `<ul>` of dates, each linking to its post; the empty state below | M (same truck), T (rows drawn from the dates file: a canvas texture on desktop, a DOM overlay on the phone video, so dates change without a re-render) | unproven |
| **6** | Licence plate | headlights flash twice (120 ms pulses: emissive + spotlight) | horn sounds (only on this tap, and only if sound is on), then WhatsApp opens through the existing `/wa` counter route (main's hotfixes) | Tecla "Escribir por WhatsApp" | M (plate), T (plate text), A (light pulse in code), sound (horn ≤ 40 kB or synthesized) | horn and sound toggle: `interacciones-que-responden.md` (proven: Web Audio, a mute toggle stored per visitor); light flash: unproven |

**Prop count per scene:** 1 Cabina 6 · 2 Caja 2 · 3 Pantalla 1 · 4 Costado 2 · 5 Gira 1 · 6 Placa 1. That is 13 prop rows; 8 of
them are clickable (the 3 head-grid rows and the 2 decorative rows are not). Scenes 2, 3, 5 and 6 have no head grid: the
heads are behind glass and under about 40 px tall there, too small for a head turn to read.

**Radio, the lightest way (owner answer 7).** No audio file, no autoplay, no embed on load. The dial changes what the dash
display and the cassette show (cover + title of each of the 9 releases); **Escuchar** opens the release on its platform. UI
sounds (dial click, tuning static) are synthesized and **off** until the visitor turns sound on in the header. If the owner
later wants listening inside the page: a Spotify embed `iframe` created only when the visitor taps "Escuchar aquí", never
before (third-party weight and cookies land only on that tap; not measured).

**Stickers, our own art (owner answer 8).** The platforms do not allow their marks to be redrawn: Meta says not to alter or
reshape the Instagram glyph and not to rotate it, to take it only from Meta's files, and to keep clear space of half its size
([Meta, Instagram icons](https://about.meta.com/brand/resources/instagram/icons)); YouTube says the icon "should never be altered",
with no custom colour, stretching, skewing or rotating ([brand.youtube](https://brand.youtube)); Spotify asks for its logo or icon as
supplied when its content is shown ([Spotify design guidelines](https://developer.spotify.com/documentation/design)); TikTok's
brand guidelines cover colour, scale, clear space and rotation (excerpts only seen; not opened in full). So:
- Each sticker is our own illustration and lettering (band jokes: a strawberry for PUTIFRESA, a sombrero, the MT monogram) with a
  call to action in words: "SÍGUENOS EN INSTAGRAM", "ESCÚCHANOS EN SPOTIFY", "MÍRANOS EN YOUTUBE", "ANDAMOS EN TIKTOK". Naming the
  platform in a plain call to action is the use the guides expect; the name is never styled as our logo.
- The platform's official glyph sits on the sticker **unaltered**: official file, its own colours (or the monochrome version the
  platform supplies), with its clear space, **kept upright** even when the sticker is stuck at an angle (a separate decal that
  does not rotate), and outside the part that peels.
- Nothing suggests partnership or endorsement (Meta bars that explicitly).
- Not verified: TikTok's and Spotify's exact wording on profile-link icons; read each kit in full before the art is final.

## 3. Desktop and phone

**Desktop: real-time three.js**, with the figures regenerated on the friend's paid Tripo plan (open item 2 for the rights). The
Cycles look (headlight pools, glass, bounce on the figures) has to be baked into lightmaps or rebuilt (`docs/temblor-texturas.md`:
even EEVEE changed faces and hair). **Fallback if the bake fails the look:** desktop plays the pre-rendered 16:9 clips with the
head grids, stickers and lights as sprite overlays on top (the phone's method at desktop size).

**Phone: the same six scenes as Blender renders, behaving differently.** No hover, no cursor:

| Scene | Phone (9:16) change |
|---|---|
| 1 Cabina | taps on ‹ › under the radio or a swipe on the dial; the mirror eyes follow the finger while it is down; the glovebox opens on tap (a short clip) |
| 2 Caja | tap peels a sticker and shows its chip |
| 3 Pantalla | the side screen fills most of the frame; swipe left/right changes the video; tap opens it |
| 4 Costado | a 5.9 m truck side-on does not fit 9:16 (`docs/escena-transicion.md`), so the scene is four stops, one window each, with the over-the-roof move between the second and third; tap plays the pose clip and shows the name card |
| 5 Gira | the dates are a DOM overlay on the rendered rear screen (dates update without a render) |
| 6 Placa | tap: the headlight flash plays as an overlay, the horn sounds if sound is on, WhatsApp opens |
| all | tilt (owner pick 3) turns the head grids, the same cells the pointer picks on desktop. Feature-detect it (C33): on where no permission prompt is needed; on iOS it sits behind an "Activar movimiento" key and is never asked on load (research #6, C10). Without tilt the heads follow the last tap |

Every pattern in this table is **unproven**: no visual-lab ficha covers dial swipes, DOM overlays on a scrubbed video, the
tap → clip flow, or tilt-driven head grids. Tilt rests on research #6 (C10, C33), which is not a ficha.

**Every scene, accessibility:** the DOM twins are in reading order and tabbable; focus on a twin also lights its prop; a "saltar
escena" link at each section start; under `prefers-reduced-motion` there is no camera rail and no scrubbing: each scene is its
storyboard still over the normal page sections, and head grids and peels are off; sound is off by default, its toggle sits in
the header, and the horn plays only on the plate tap; WCAG AA for every label over the scene (sits on `--veil`), Spanish-first
labels.

### Weight budget per scene

Phone, measured on the v3 move (`blender/render/transicion/v3-720x1280/`, 192 frames, 8 s, night), x264 crf 23:
```
720x1280  all-intra (-g 1)   2.68 MB     540x960  all-intra (-g 1)   1.79 MB
720x1280  key every 6 f      1.42 MB     540x960  key every 6 f      0.93 MB
720x1280  key every 12 f     1.27 MB     540x960  normal (-g 240)    0.74 MB
720x1280  normal (-g 240)    1.14 MB     540x960  WebP seq, 96 fr q70 0.76 MB
shipped v3 clip (crf 16, 720x1280): 2.95 MB
```
A scrubbed 8 s move fits the 1 MB-per-gesture budget (research C31) at 540×960 and 24 fps with a keyframe every 6 frames (0.93 MB).
The WebP sequence costs 0.76 MB, but only because it keeps every other frame (12 fps); at 24 fps it would land near 1.5 MB.
Recommendation: `-g 6` H.264 for the moves and normal H.264 for idle loops. A 12 fps WebP sequence on a canvas is the fallback if the
`-g 6` seek stutters. Both are unproven: nobody measured a `-g 6` seek on a real phone (the ficha only compared `-g 1` with `-g 250`),
and `video-que-avanza.md` lists the image-sequence comparison as an open item.

| Scene | Phone (540×960) | Desktop (live, **target, not measured**) |
|---|---|---|
| Entry (before scene 1 shows) | ≤ 3 MB: poster AVIF ≤ 0.12 MB, JS ≤ 0.08 MB, scene 1 idle loop ≤ 0.4 MB, move 1→2 ≤ 1 MB | ≤ 4.5 MB: three.js ≤ 0.25 MB gz, truck GLB ≤ 1.5 MB (667k tris decimated to ≤ 80k, Draco + KTX2), 4 figures ≤ 0.4 MB each (≤ 30k tris, 1k textures), road + HDRI ≤ 0.6 MB; a poster still shows at once |
| Head grids (phone, **target**) | 3×3 alpha WebP per head at 256 px cells, ≤ 0.08 MB each: manager (mirror and window), Héctor, Alexandro, Diego ≈ 0.4 MB, fetched with the scene that first shows each head | in the figures' GLBs (live heads) |
| 1 Cabina | idle 0.4, radio covers 9 × 25 kB, glovebox clip ≤ 0.3 | radio + cassette + glovebox junk ≤ 0.2 MB |
| 2 Caja | move ≤ 1, idle 0.4, sticker overlays with a 6-frame peel sprite ≤ 0.1 (target) | stickers ≤ 0.1 MB, bed props ≤ 0.4 MB |
| 3 Pantalla | move ≤ 1, idle 0.3, thumbnails 14 × 30 kB | pantalla móvil ≤ 0.4 MB + thumbnails 14 × 30 kB |
| 4 Costado | 4 short moves ≤ 1.2 total, 4 pose clips ≤ 0.4 each (stacked-alpha AV1) | 4 pose clips in the figures' GLBs ≤ 0.4 MB |
| 5 Gira | move ≤ 1, idle 0.3, dates file ≤ 5 kB | dates file ≤ 5 kB |
| 6 Placa | move ≤ 1, flash overlay ≤ 0.1, horn ≤ 0.04 | horn ≤ 0.04 MB |
| **Whole ride** | **≤ 12 MB**, fetched one scene ahead | **≤ 7 MB** |

## 4. Asset list

| Asset | Source | Status / gap |
|---|---|---|
| **Truck** | "Mercedes Benz G-wagon 6x6" by srush651, Sketchfab, https://sketchfab.com/3d-models/mercedes-benz-g-wagon-6x6-10a1f80c971143548d99b3e9ccc118e6, **CC Attribution** (read from the page 2026-11-12; Sketchfab's CC-BY is 4.0), 667.1k triangles, downloadable | The owner has the file **on the Mac**: copy it over (`ssh mac`, skill `mac-mirror`) into `blender/assets/camion/` with the page's licence text. This is **not** the G63 on disk today, which is a different upload by another author. Credit line for the site (footer or credits page): *"Mercedes Benz G-wagon 6x6" (https://sketchfab.com/3d-models/mercedes-benz-g-wagon-6x6-10a1f80c971143548d99b3e9ccc118e6) by srush651 (https://sketchfab.com/srush651), licensed under CC-BY-4.0 (http://creativecommons.org/licenses/by/4.0/).* Pre-build work: the four door windows as their own meshes, the glovebox door, rear seats measured (`vidrios()`, `sin_cabeceras()` and the seat ray casts need redoing on the new mesh). |
| Truck in the v3 clips and this storyboard | Brabus G63 6×6 "Mercedes Benz G-Wagon 6X6" by DJS, Sketchfab, CC-BY-4.0 (`blender/assets/camion/g63-6x6/modelo/license.txt`) | Stand-in; replaced by srush651's model. If any frame of it ships, its credit line is in that licence file. |
| Band figures ×3 + manager | Tripo, **regenerated on the friend's paid plan** as a pre-build step (inputs in `comfy-out/para-subir/`, fixes in `docs/tripo-glb.md`) | Open item 2 (written licence from the friend). Then: rig (Tripo rig API or hand rig; Mixamo forbids shipping its raw files, so not for the live GLBs), decimation to ≤ 30k tris with 1k textures. All four are adult figures. Name the member file `alexandro` (the member is **Alexandro** Montal in `members.ts`; today's file is `alejandro.glb`). |
| Manager's card | photo, name, role, Instagram | **Open item 1** (name); `public/members/` holds an unlisted `dimora.webp`, not checked whether it is him |
| Head-turn grids, pose clips | rendered / keyed from the rigged figures | after the rig |
| Pantalla móvil (LED box truck) | model in Blender (`kiln-prop`) or a CC0/CC-BY box truck | new; one model serves scenes 3 and 5 |
| Radio, cassette, dash key, glovebox junk, bed props (donut, cooler, piñata, instrument cases) | model in Blender (`kiln-prop`) | new; playful, owner may swap any |
| Instruments | primitives today; `blender/assets/guitarra.blend`, `tololoche.blend` exist | licences of both not checked (not in `sketchfab-creditos.txt`) |
| Sign gantries, plate | model in Blender | new; highway sign lettering needs a free font (SCT style), licence not checked |
| Sticker art | our own illustration and lettering + each platform's official glyph, unaltered | new (§2 rules) |
| Sounds: horn, dial click, tuning static | synthesized in Web Audio (as `interacciones-que-responden.md`) or CC0 | new |
| Night sky, asphalt, road | `qwantani_night_puresky_2k.hdr`, `Asphalt031`, `Road007` (`blender/assets/camion/`) | in use; CC0 sources (Poly Haven, ambientCG) per their sites, not re-checked here |
| Covers, member photos, video thumbnails | `public/music/`, `public/members/`, YouTube `hqdefault` | in repo |

**Build dependency:** `blender/transicion.py`, `reparto.py`, `personaje.py`, `temblor.py`, `blender/tripo/`, `docs/escena-transicion.md`,
`docs/temblor-texturas.md`, `docs/tripo-glb.md` and the changes to `blender/escena.py` and `src/lib/escena.json` exist only as
untracked or modified files in the main checkout (`/mnt/e/Cursor Projects/MTO`, branch `cc/goblindrone`). They are not on any
branch yet; `blender/storyboard.py` runs them from there. They need committing before a build session can use them.

## 5. Tour dates: the file the sign reads

The watcher is a **separate job** (resa/cronjobs; not part of this plan). It reads the band's Instagram posts, finds the date
announcements, and writes one file. How it reads Instagram (the Graph API with the band's own account, or reading public posts)
and how it is triggered are the watcher job's decisions; Instagram's terms on automated reading apply there.

File: `public/data/fechas.json`, served as a static asset and fetched at load, so a new file goes live with a redeploy and the
page never needs a rebuild of its code.
```json
{
  "version": 1,
  "actualizado": "2026-11-12T23:00:00-06:00",
  "fuente": "https://www.instagram.com/mafia_tumbada_oficial/",
  "fechas": [
    {
      "fecha": "2026-12-05",
      "hora": "21:00",
      "ciudad": "Xalapa",
      "estado": "Veracruz",
      "lugar": "Nombre del lugar",
      "post": "https://www.instagram.com/p/XXXXXXXX/",
      "boletos": null
    }
  ]
}
```
(The values above show the shape only; they are not dates.) Rules for the reader:
- `fecha` is ISO `YYYY-MM-DD`, read in Mexico City time. Rows whose `fecha` is before today are dropped in the browser, so a
  stale file never shows past shows. Sorted ascending; the sign shows the next 5, the DOM list shows all.
- `hora`, `lugar` and `boletos` may be `null`; `ciudad` and `post` are required (a row without them is dropped).
- A missing file, invalid JSON, a `version` other than 1, or no future rows all mean **empty state**.

**Empty state:** the rear screen shows "PRÓXIMAS FECHAS · MUY PRONTO" over a slow LED crawl of "SÍGUENOS EN INSTAGRAM", and the
DOM section shows one line, "Las próximas fechas salen primero en nuestro Instagram", with a link to the profile, plus the
Contratar Tecla. The scene stays in the ride either way.

## Storyboard notes

`hoja-16x9.jpg` and `hoja-9x16.jpg`, frames in `docs/design/escenas/storyboard/`. Rendered with the G63 stand-in and the
figures seated per §0 (Alexandro and Diego moved into the rear seats by `blender/storyboard.py`; their arms keep the old
strumming pose, so the hands float). The pantalla móvil, bed props and stickers are simple shapes that stand in for models
still to be made; they show framing and the truck's size in frame, not looks. The move between each pair is in §1. Not
proven by render: the moves after 1→2, and the hidden cut behind a gantry.

Weak in these frames, to fix when the real truck is in:
- 1 Cabina: with the rear pair seated, their heads fill both edges of the 20 mm frame. Either start the v3 camera 0.25 m further
  forward, or lean the rear pair toward their windows.
- 3 Pantalla, 9:16: both vehicles sit small in the lower third. The phone shot needs the camera closer, between the two.
- 4 Costado: the side of the truck is nearly black and only Héctor's window reads. It needs a rim light from the camera side
  and lit cab interiors so all four windows read.
- The rear seat was measured by ray cast on the G63 (seat back y −0.73, cushion z 1.19). Redo the measurement on srush651's model.
