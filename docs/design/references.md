# References: Mafia Tumbada, three directions (2026-11-12)

Paths are relative to `~/projects/visual-lab`. Each `borrow` cell opens with the direction it feeds:
**A** Carretera (the truck / Blender night road), **B** Cartel (a print poster and ticket, no 3D),
**C** En vivo (built on the band's live footage, no 3D). The client material (the logo, the photos, the covers) supplies
content and brand facts only.

The truck prototype's rows from 2026-11-09 are kept below as direction A. `docs/design/DESIGN.md` still describes that
prototype.

Gate: `python3 -I ~/projects/visual-lab/web/scripts/refs-check.py docs/design/references.md --sections hero,musica,video,integrantes,contacto,botones`

| section | library entry | borrow | cost |
|---|---|---|---|
| hero | arraisballet · smooth video hero · `web/visuales.md#recipe-smooth-video-hero` | A: poster is the exact first frame of the Cycles loop, 24 fps, keyframe every 2 s, faststart, no audio. C: same recipe for a muted live-footage loop cut from the band's own files | B |
| hero | landonorris.com · 3D scene that renders only while visible · `web/visuales.md#dissection-landonorris-com` | A: the live three.js road pauses when off-screen or when the tab is hidden; without WebGL2, a class on `<html>` swaps in the loop | B |
| hero | lusion.co · dark WebGL stage inside the page · `web/site-reading-fichas/lusion-co.md#look` | A: the scene sits in one framed stage, not full-bleed chrome; one accent only (the logo's gold) | A |
| hero | urielurbina.com · one condensed black face (Reddit Sans Condensed 900, caps, tight) plus one accent · `web/site-reading-fichas/urielurbina-com.md#look` | A (tweak bar): the alternative display face to Saira Condensed italic; upright only, so it loses the logo's lean | B |
| hero | anna-dawson · tour posters → colour overlays · `web/designer-fichas/anna-dawson.md` | B: the hero is a poster lockup on paper; band photo as a two-ink overprint (black + the logo's gold) | B |
| hero | pina-bausch.de · condensed display 80–100 px on a phone · `web/site-reading-fichas/pina-bausch-de.md#look` | B: the name set big at 390 too, stacked; the type is the poster, not a caption over a portrait (that is eptosuno's hero) | B |
| hero | sadlerswells.com · media entrance overZoom 1.1→1 + fade, 2 s · `web/site-reading-fichas/sadlerswells-com.md#look` | C: the live loop eases in once on load; the 3D logo mark sits over it | B |
| hero | coastveracruz.com · full-bleed video hero, Veracruz · `web/site-reading-fichas/coastveracruz-com.md#look` | C: the trap to avoid: a 10 MB hero gave 8.1 s mobile LCP; our budget is ≤1.2 MB at 390 with an AV1/H.264 ladder | M |
| musica | landonorris.com · horizontal gallery driven by scroll · `web/visuales-fichas/galeria-horizontal.md#visual-reading` | A: releases as one strip that passes like road signs | M |
| musica | mattjumper.com · 3-up thumbnail grid, one accent on the buy control · `web/site-reading-fichas/mattjumper-com.md#look` | B: covers in a tight grid printed on the poster; one gold control per release | B |
| musica | badomensofficial.com · merch card, second photo on hover · `web/visuales-fichas/tarjeta-merch.md#visual-reading` | B: a cover turns to its back (title, type, platform) on hover or focus, no lift or scale | B |
| musica | paulkalkbrenner.net · photo breaks into squares then the "Recordings" block · `web/visuales-fichas/transicion-pixelada.md#visual-reading` | C: the hero still breaks into cover-sized squares that become the release grid | B |
| video | dfm.mt · video rendition sized to its box · `web/site-reading-fichas/dfm-mt.md#look` | A, B, C: thumbnails served at the size the 390 box needs; no embedded YouTube player (SPEC §3) | B |
| video | Index · load video by proximity · `web/visuales.md#index-by-technique` | C: the live clip in this section only loads when it is near the viewport | B |
| video | teamusa · all-intra video that advances with scroll · `web/visuales-fichas/video-que-avanza.md#visual-reading` | C: one short live clip (crowd → stage) scrubbed by scroll, kept short with a visible way past (scrolljacking guardrail) | M |
| video | user: DESIGN.md › Do's and Don'ts (links out, no embedded players; owner) | The catalog's other 9 titles as a two-column text list with hairline rows under "Más en YouTube", so all 14 videos are reachable; titles verbatim from `catalog.json` (content only) | B |
| integrantes | kage · fixed camera anchors per section, damped move · `web/visuales-fichas/kage-scroll-world.md` | A: one camera stop per member inside the cab (the inside→outside shot, `docs/escena-transicion.md` on main) | M |
| integrantes | synchronized.studio · type-led, staggered fades ~0.6 s · `web/site-reading-fichas/synchronized-studio.md#look` | B: the names set as type on the poster's credits block, one stagger | B |
| integrantes | badomensofficial.com · second photo on hover · `web/visuales-fichas/tarjeta-merch.md#visual-reading` | C: member portrait swaps to a stage photo on hover or focus | B |
| contacto | MTO's own note · veil under text over a rendered scene · `web/visuales.md#technique-text-over-a-rendered-scene` | A: the contact panel over the road, veil sized to the brightest frame (lowest alpha that keeps 4.5:1) | B |
| contacto | boleto-perforado · ticket-punch transition · `web/visuales-fichas/boleto-perforado.md#visual-reading` | B: contratación is a ticket stub; the WhatsApp control punches through it | B |
| contacto | arraisballet · poster = first frame · `web/visuales.md#recipe-smooth-video-hero` | C: the closing section reuses the hero's live loop, already cached, under the contact line | B |
| contacto | teamusa · reduced-motion start, visible motion toggle · `web/visuales.md#dissection-sports-withgoogle-com-teamusa` | A, B, C: honour `prefers-reduced-motion`; one motion toggle in the footer | B |
| contacto | user: `research/contenido/socials.ts` + SPEC §4 | A, B, C: WhatsApp only, prefilled message with date and city | B |
| botones | rafadesign · strength tile hover wipe · `web/visuales-fichas/interacciones-que-responden.md#interaction-inventory-the-actual-state-of-each-control` | A: the button fill wipes up from the bottom like a dash light coming on (scale-y 0→1, 500 ms, cubic-bezier(.65,0,.35,1)) and wipes back down on leave. B: the same wipe in gold ink, like a roller pass | B |
| botones | boleto-perforado · press dips, acts on release · `web/visuales-fichas/boleto-perforado.md#recipe` | B: press dips the control about 90 ms, and the punch happens on release. A: the same press dip, read as a switch | B |
| botones | rafadesign · magnetic buttons · `web/visuales-fichas/interacciones-que-responden.md#recipe` | C: the main controls lean toward the pointer (up to 6 px x / 3.6 px y, spring 260/26), with a tap dip to 0.96; off on touch and under reduced motion | B |
| botones | Rive CLI · hover/press state machine without the editor · `rive/rive-notas.md#rive-cli-rml-from-text-no-editor--2026-10-08` | A, B, C: morphing icons (play↔pause, arrow→WhatsApp glyph, menu→close) as small Rive state machines. Library gap: no measured icon morph exists yet, so this is an unproven row | M |

## Buttons and icons pair run (2026-11-12, run `mto-buttons-icons`)

Direction A Carretera is picked; this run replaces `Boton.astro` and `Icono.astro`. The three rows tagged **Tecla**, **Boleto**
and **Marco** are the three button forms offered to the owner (no pill: tell 20, `web/ai-slop-tells.md`). The pill is not a
candidate unless the owner asks for it. Gate: `python3 -I ~/projects/visual-lab/web/scripts/refs-check.py docs/design/references.md --sections botones,iconos,estados`

| section | library entry | borrow | cost |
|---|---|---|---|
| botones | todoist.com · one button built as two layers, a lighter lower lip as the pressed-key look · `web/site-reading-fichas/todoist-com.md#look` | Tecla: a square gold cap over a 4 px dark-gold lip; the press sinks the cap onto the lip (translateY 3 px in 80 ms), release springs it back. The ficha's pill shape and bounce spring are not borrowed (square corners; no `linear()` spring) | B |
| botones | nothing.tech · white rectangular CTA with a trailing chevron, and underlined mono text links with the same chevron · `web/site-reading-fichas/nothing-tech.md#look` | Tecla and Marco: a trailing chevron that nudges 4 px on hover and focus; secondary actions (the platform list) may drop to an underlined text link with the same chevron | B |
| botones | boleto-perforado · a stub acts on release, a stamp lands after · `web/visuales-fichas/boleto-perforado.md#recipe` | Boleto: the button is a stub with half-circle notches cut from both side edges (perforation); press dips 2 px for 80 ms and the act fires on release; the done state lands a stamp (scale 1.6 to 1, 320 ms, expo out) | B |
| botones | teenage.engineering · outline-only button, 1 px border, a squared uppercase face · `web/site-reading-fichas/teenage-engineering.md#look` | Marco: a square 2 px gold outline, uppercase label, no fill at rest; the fill wipe is the rafadesign row above (this is the refined version of the working button) | B |
| iconos | rafadesign · each icon reacts when its tile is hovered (arrow moves up-right, loop turns 180°, 700 ms) · `web/visuales-fichas/interacciones-que-responden.md#interaction-inventory-the-actual-state-of-each-control` | Every icon answers its button's hover and focus with one small move on the shared 250 ms token (the play glyph leans 2 px forward; the chevron, which belongs to the button form, nudges 4 px; no external-link arrow); transform only | B |
| iconos | rafadesign · sound toggle: `aria-pressed`, the label changes, the icon gets an x · `web/visuales-fichas/interacciones-que-responden.md#interaction-inventory-the-actual-state-of-each-control` | The loop toggle's play and pause glyphs morph (GSAP MorphSVG, 250 ms) while the label changes with them, so the motion is never the only cue | B |
| iconos | landonorris.com and griflan.com · buttons and icons are Rive files, each with its own state machine · `web/visuales.md#index-by-technique` (row "Interactive micro-animations (buttons, icons)") | Not built in this run: Rive's runtime is a 199 KB transfer on landonorris (`web/site-reading-fichas/landonorris-com/speed-390-throttled.json`), over the 150 KB cap; kept as an open lab question for the scene phase. Library gap: no measured icon morph exists in the library, so the GSAP row is unproven | M |
| iconos | GSAP licence note · MorphSVG is free since the Webflow licence · `web/visuales.md#libraries-vetted-2026-10-16` | GSAP core plus MorphSVG for simple A to B pairs (play to pause, the loading ring to pause); self-hosted from npm, not a CDN | B |
| estados | boleto-perforado · press dips, acts on release, a stamp marks the end · `web/visuales-fichas/boleto-perforado.md#recipe` | The six states of every button (idle, hover, press, focus, loading, done) share one motion language: 80 ms press, 250 ms state change, 500 ms fill; loading and done appear only where a real event drives them (the video buffering and playing); links have no loading or done | B |
| estados | teamusa · a visible control for motion, reduced motion respected · `web/visuales.md#dissection-sports-withgoogle-com-teamusa` | Under `prefers-reduced-motion` nothing loops, icons swap with no morph, and the first frame after a click equals the settled one | B |

## Scene props, phase 1 options (2026-11-13, run `nerddrone`)

The props of the scene plan (`docs/design/escenas-plan.md` §2) that had no picked look: three options each, stills rendered in the
night scene with the G63 by `blender/utileria.py`, shown on `docs/design/escenas/utileria/index.html` for the owner's pick. The visual-lab library
covers only the dash key, the glovebox motion, the sticker build and the bed-prop wobble. The mothership agreed (2026-11-13 00:41)
that the rest is traced to real-world photo and spec sources, with the URL in the row. Those rows have no library path and fail
`row-cites-library` on purpose. O = page opened, S = seen only in search results. Stills use Windows fonts (Bahnschrift, Impact,
Consolas) as stand-ins; the shipped lettering needs free fonts, and SCT signs use "tipografía México" (NOM-034, below).
Gate: `python3 -I ~/projects/visual-lab/web/scripts/refs-check.py docs/design/references.md --sections radio,guantera,calcas,pantalla,portico,placa,caja`

| section | library entry | borrow | cost |
|---|---|---|---|
| radio | todoist.com · a two-layer key, a lighter lip as the pressed look · `web/site-reading-fichas/todoist-com.md#look` (with MTO `docs/design/botones/`, the Tecla) | Dash key in all three radio options: a square gold cap over a dark lip next to the head unit, labelled ESCUCHAR; press = translation, as the Tecla | B |
| radio | real world · Pioneer KEH cassette head units, 1980s: radiomuseum.org/r/pioneer_cassette_car_stereo_with_fmmwlw_electronic_tuner.html (S); the 2026 KEH reissue, slashgear.com/2297116/pioneer-retro-car-stereo-box-speakers-cost-details/ (O) | **Rejected by the owner 2026-11-13 (all three radios).** Option A: single-DIN black face, amber segment display, two chrome knobs, cassette door with the cover in its window | M |
| radio | real world · 1947–53 GMC truck AM/FM reproduction radio, classicparts.com/mobile/1947-53-Original-Style-Reproduction-AM_FM-Radio-GMC/productinfo/69%2D802/ (S); commons.wikimedia.org/wiki/Category:Automobile_radio_receivers (O) | **Rejected by the owner 2026-11-13 (all three radios).** Option B: chrome face, warm horizontal tuning scale with a red needle, push buttons, a separate cassette deck under it | M |
| radio | real world · Pioneer DEH-12E single-DIN with a big volume knob, sonicelectronix.com/item-21459-Pioneer-DEH-12E.html (O); clear-shell cassette, duplication.com/shop/Empty-Audio-Cassette-C-ZERO-clear-liners-with-screws.html (O) | **Rejected by the owner 2026-11-13 (all three radios).** Option C: one big dial with a lit ring (the dial the visitor turns), green one-line display, a gold cassette pull-out | M |
| guantera | objeto-que-se-abre · a lid that drops on a hinge with an overshoot, the shade timed with it, a settle tail · `web/visuales-fichas/objeto-que-se-abre.md` (status: unproven) | The door drops about 70° and the junk spills onto it; the motion (cubic-bezier(.3,1.15,.4,1), 0.55 s, settle ~1.2 s) is for the build, the stills show the open state | M |
| guantera | real world · rubber duck, en.wikipedia.org/wiki/Rubber_duck (S); lotería Don Clemente, mexicodesconocido.com.mx/historia-del-juego-de-la-loteria-y-los-54-versos-para-cantarla.html (S); black-and-gold child charro hat, caballobronco.com/en/products/sombrero-charro-infantil-negro-con-oro-imp-71272 (S) | Option A duck + cards + straw sombrero (the plan's set); B lotería-style cards + black-and-gold sombrero + pine freshener; C band junk (loose cassette, picks, set list, sunglasses) | M |
| calcas | kiln-utility-box · stickers as decal quads ~0.6 mm off the painted surface, cropped from a photo atlas · `blender/lab/kiln-utility-box/NOTES.md` (status: proven) | Every sticker is a quad just off the tailgate; the build bakes our art into one atlas | B |
| calcas | ayzz · stickers placed at random angles for a playful tone · `web/designer-fichas/ayzz.md` | Free-hand placement at slight angles (owner answer 8); the platform glyph area stays upright (escenas-plan §2 rules) | B |
| calcas | real world · die-cut truck decals with a white border, squaresigns.com/product/truck-decals (S); customink.com/products/stickers-magnets/stickers/full-color-4-in-die-cut-sticker-with-border/1196600 (S) | Option A fat white border die-cut; B text-led bumper strips in black and gold (DESIGN.md palette); C round badges | M |
| pantalla | real world · box truck with LED screens on three sides, peru-retail.com/innovadores-camiones-led-busqueda-consumidor/ (O); LED screen trailers, es.accio.com/plp/led-advertising-trailer (S) | Option A rigid box truck, panels on both sides and the back; B a pickup towing a screen trailer on a mast; C the box truck with a marquee of warm bulbs. The LED look is a pixelated image under a round-dot mask, emissive | M |
| portico | real world · NOM-034-SCT2/SEDATU-2022, platiica.economia.gob.mx/wp-content/uploads/sites/2/PDF_Normas_Publicas/034-sct2-sedatu-2022.pdf (O): reflective green field, white legend and 4 cm border, 8 cm corner radius, ≥ 5.50 m clearance, types bandera / puente | Green field, white retroreflective legend and border, clearance over 5.5 m in all three options | M |
| portico | real world · gantry sign in Cotaxtla, Veracruz, commons.wikimedia.org/wiki/File:Desviación_a_la_Autopista_México-Veracruz_150D_(6261085939).jpg (O); cantilever sign, commons.wikimedia.org/wiki/File:Mexican_overhead_guide_sign_to_El_Puertecito.jpg (O) | Option A truss gantry across the road; B bandera cantilever from the right shoulder; C a sign on a puente peatonal (no photo found: unverified form) | M |
| placa | real world · state plates of Mexico, unotv.com/nacional/placas-vehiculares-en-mexico-asi-son-los-disenos-de-cada-estado/ (O); Veracruz plate history, ejecentral.com.mx/nuestro-eje/reemplacamiento-2026-en-veracruz-que-autos-cambiaran-primero-como-identificarlas-y-cuando-inicia (O) | Option A a state-format plate (state name on top, dark characters) whose characters spell the band, with no seals or QR (it must not pass as a real plate); B a black-and-gold fantasy plate; C a plain plate with the call to action on a chrome frame | M |
| caja | interacciones-que-responden · the pat-to-reveal mascot: a small reaction on hover or tap · `web/visuales-fichas/interacciones-que-responden.md` (status: proven) | One wobble per prop on hover (plan §2), not on every prop at once (tell 13) | B |
| caja | real world · Intex sprinkle donut float, homedepot.com/p/Intex-Sprinkle-Donut-Tube-Pool-Float-56263EP/305479596 (S); Coleman steel-belted cooler, outdoorgearlab.com/reviews/camping-and-hiking/cooler/coleman-steel-belted (O); 7-point piñata, mexicodesconocido.com.mx/significado-las-pinatas.html (O); tololoche fundas, listado.mercadolibre.com.mx/fundas-para-tololoche (S) | Option A fiesta (donut, red cooler, star piñata); B on tour (tall tololoche case, road case stencilled MT, amp, blue cooler); C rancho (beer crates, straw sombreros, a string of warm bulbs) | M |

## Scene props, round 2 (2026-11-13, owner's picks 02:51; run `circudrone`)

Picks: radio → an infotainment touchscreen, glovebox C with the door cut from the truck mesh, stickers mixed, pantalla C, signs B,
plate A matched to the current official Veracruz plate, bed A fuller. The handoff is `docs/design/escenas/handoff-fase1-ronda2.md`.
Plate ruling (mothership, 02:53): a stylised version with the official layout, no state or national seals and no QR.
O = page opened; S = seen only in search results. Gate: `refs-check.py docs/design/references.md --sections radio,guantera,placa,caja`.

| section | library entry | borrow | cost |
|---|---|---|---|
| radio | real world · 2025 G-Class cabin, MBUX on 12.3" screens in place of COMAND: hagerty.com/media/?p=384794 (S); slashgear.com/1547804/2025-mercedes-g-class-updates-iconic-suv-g63-g550 (S); gallery autos.yahoo.com/see-interior-exterior-photos-2025-120000032.html (S) | Variant (a): one wide screen floating on top of the dash on a short stem, glass face on a black bezel, top leaning back; the cassette and the Tecla go | M |
| radio | real world · 2025 Ram 1500 Uconnect 5, 14.5" screen set into the stack: moparinsiders.com/rams-14-5-inch-uconnect-5-screen-bigger-isnt-always-better (S); gallery aol.com/view-interior-photos-2025-ram-050100368.html (S) | Variant (b): the screen built into the centre stack at the COMAND slot, following the stack's ~22° lean; the Tecla stays as a hard key beside it | M |
| radio | todoist.com · a two-layer key, a lighter lip as the pressed look · `web/site-reading-fichas/todoist-com.md#look` (with MTO `docs/design/botones/`, the Tecla) | The screen face's Escuchar is the Tecla drawn flat: filled gold square cap on a dark-gold lip, Saira 600, a play triangle. The ‹ › keys are square ghost keys on `--line`. Face made by `blender/pantalla_tablero.py` from `catalog.json` (9 releases) in DESIGN.md type | B |
| guantera | objeto-que-se-abre · a lid that drops on a hinge with an overshoot, the shade timed with it, a settle tail · `web/visuales-fichas/objeto-que-se-abre.md` (status: unproven) | Glovebox C: the door is the G63's own dash faces in the box x 1.95–2.35, y 1.15–1.30, z 1.15–1.38, hinged on the lower edge (axis X) and turned 70°, a dark open box behind the cut; the junk (cassette, picks, set list, sunglasses) lies on the door's inside | M |
| placa | real world · NOM-001-SCT-2-2016, platiica.economia.gob.mx/wp-content/uploads/sites/2/PDF_Normas_Publicas/001sct22016.pdf (O, §5.1.1–5.1.3, 5.3.4, 5.3.11): 300 × 150 mm, 14 mm corner radius, 3 mm rim, four 20 × 6 mm slots 50 mm from the sides and 10 mm from top and bottom, characters embossed 2 mm, legends ≤ 18 mm, an exclusive character area | Both plate variants: the size, corners, rim, slots, embossed characters and a clear character area. Not borrowed: the national seal (bottom left, §5.3.4) and the 20 mm QR (§5.3.11), per the 02:53 ruling | M |
| placa | real world · Veracruz layout, unotv.com/nacional/placas-vehiculares-en-mexico-asi-son-los-disenos-de-cada-estado/ (O, 2025-05-05): state name on top beside a QR, characters in the centre, the state name again at the bottom beside a yellow figure, national arms left, state arms right; 2026 reemplacamiento, ejecentral.com.mx/nuestro-eje/reemplacamiento-2026-en-veracruz-que-autos-cambiaran-primero-como-identificarlas-y-cuando-inicia (O) and veracruz.quadratin.com.mx/programa-de-reemplacamiento-2026-ano-nuevo-placas-nuevas/ (O): neither describes the 2026 design | VERACRUZ on top, our characters in the centre, a bottom line beside a plain yellow bar standing in for the figure; no arms, no QR. **Colours not verified against a photo:** no source found shows the 2026 issue; white field and black characters are kept from round 1 | M |
| caja | interacciones-que-responden · the pat-to-reveal mascot: a small reaction on hover or tap · `web/visuales-fichas/interacciones-que-responden.md` (status: proven) | Still one wobble per prop on hover, now over more props; the build picks which few respond (tell 13) | B |
| caja | real world · as round 1 (Intex donut, Coleman cooler, 7-point piñata) plus party props: beach ball, balloons tied to the roll bar, a second ring float, maracas, a small LED speaker, a straw sombrero (generic objects, no single source) | Bed A fuller, composed as a pyramid peaking at the piñata: A1 stacked (the piñata sits on the cooler and donut), A2 hanging (the piñata hangs from the roll bar). Judged from the scene-2 camera (`T.CAMINO[-1]`, v3 f191) | M |
| placa | user: owner's reference image of the current Veracruz private-car plate (mothership, 03:30; `/tmp/claude-1001/-home-black-projects-mothership/106e6a19-3b07-4875-ac71-16a1b3d770b6/images/10.png`, not kept in the repo) | Plate redone after it (supersedes the stylised A1/A2): white field, VERACRUZ heading, olive stepped fret in the top corners, faint crest watermark, QR top right, the slogan logo, TRANSPORTE PRIVADO AUTOMOVIL, 30, round seals, red T. Ours: MT-420-VER, a QR to the band's wa.me (`research/contenido/socials.ts`), the MT monogram in the national-seal spot (Ley sobre el Escudo, la Bandera y el Himno Nacionales), a simplified crest lookalike. Face: `blender/placa_veracruz.py` | M |

## Stickers, design pass (2026-11-13, run `nerddrone`; brief: mothership 03:40, owner "so they stand out as real stickies")

Two directions, art in `blender/calcas_arte.py` (A "puesto de merch": four separate pieces in four finishes, bold-pop colour;
B "troca": black and gold, sun-faded, stacked in one corner). Glyph ruling (mothership 04:25): IG, YouTube and TikTok get a neutral
grey upright slot; Spotify uses its official file. O = page opened; S = seen only in search results.
Gate: `refs-check.py <this section> --sections calcas3` (the older sections fail `row-cites-library`, see the report).

| section | library entry | borrow | cost |
|---|---|---|---|
| calcas3 | kiln-utility-box · stickers as decal quads ~0.6 mm off the paint, one atlas · `blender/lab/kiln-utility-box/NOTES.md`; export without the Smart UV re-unwrap (decals bake black) · `blender/blender-notas.md` | Each sticker is its own quad 0.6 mm off the tailgate at its ray-cast spot; the build packs the eight arts in one atlas and exports `as_is` | B |
| calcas3 | ayzz · stickers at playful free-hand angles · `web/designer-fichas/ayzz.md` | Angles within ±0.15 rad; the glyph stays upright on its own quad (escenas-plan §2) | B |
| calcas3 | bold-pop illustration · thick ink outline, a solid extrusion stepping down-right, saturated flat fills · `web/refs/mengto-skills/agent-skills/illustration/illustration-bold-pop/SKILL.md` | A1 strawberry (PUTIFRESA, sunglasses) and the A-side heroes: ink outline + down-right extrusion; pink, lime, turquoise, lemon from the bed props (`utileria.py` ROSA/LIMA/TURQ) | M |
| calcas3 | vintage-emblem illustration · one hero object on a sun disc, a heavy condensed wordmark · `web/refs/mengto-skills/agent-skills/illustration/illustration-vintage-emblem/SKILL.md` | A2 and B2 holo badges: the cassette on a sun disc, ESCÚCHANOS in Saira Condensed Black (DESIGN.md display face, slanted) | M |
| calcas3 | `StickerPeel` (the library's only peel reference) · `web/visuales.md`; real world · laminates, stickerapp.com/blog/sticker-academy/how-to-choose-the-right-laminate-for-your-stickers (O): matte "soft, muted finish with no glare", gloss "reflective", cracked ice "catches the light and shifts as you move it"; 4over4.com/guide/sticker-printing-guide-materials-and-finishes (S): holo is printed on white or clear film, then laminated | One finish per sticker: gloss vinyl = clearcoat, matte paper = rough with no coat, holo = thin-film iridescence over a silver field, gold chrome letter-cut = metallic; the peel corner is a real curl of the mesh with the white backing on its underside | M |
| calcas3 | Y2K floating stickers (decathlonyestalgia) · `web/visuales.md`; real world · skateboardstickers.com/blogs/skateboard-stickers-about-history-culture/slaps-and-the-aesthetics-of-decay (O): "faded ink", torn edges, "cracked vinyl", "half-peeled", overlap as "conversation"; troca calcas on Mercado Libre, listado.mercadolibre.com.mx/calcomanias-para-camionetas-pick-up (S), listado.mercadolibre.com.mx/calcomanias-de-san-judas (S); "Puro Veracruz" stickers: searched, none found | B: sun fade, chips out of the rim, scuffs that show the white vinyl, the stack in one corner with overlap never over a glyph slot; A4 gold letter-cut lettering after tailgate lettering. **Not verified:** no photo of a real Veracruz tailgate was opened | M |
| calcas3 | user: owner 03:40 via mothership ("we might need to dig more design on the stickers so they stand out as real stickies"); glyph ruling, mothership 04:25; Spotify's icon zip from developer.spotify.com/documentation/design (O). The Meta, YouTube (brand.youtube) and TikTok (developers.tiktok.com design guidelines) packs need a manual download | Grey upright slots sized as clear space (2× the glyph); Spotify's official PNG on its slot | M |
| calcas3 | user: owner 04:38 on `calcas3-arte.jpg` ("those are good, use more variations like that") | Eight more, band stickers with no platform glyph (no slot, no brand files), same rows as above: A5 PUTIFRESA lettering die-cut (bold-pop, gloss), A6 MT holo starburst (owner 05:30: MÍRANOS / EN YOUTUBE under the MT instead of TUMBADO), A7 lotería-style card EL CASETE (matte paper), A8 MAFIA TUMBADA ribbon (gloss); B5 PURA MT gold chrome letter-cut (troca lettering; owner 05:15: the band is from Xalapa, "pura mt o pura mafiatumbada" instead of PURO VERACRUZ; 05:30 PURA MT), B6 MT shield with a gold rope border (gloss, faded), B7 card EL SOMBRERO (matte, faded, chipped), B8 VER country-code oval (gloss, the oldest after B1). **Not verified:** the lotería card and the country-code oval come from general knowledge; no page of either was opened | M |

## Scenes 2-6, key stills (2026-11-13, run `npcdrone`; mothership queue 2026-11-13-mto-scenes-2-6-stills)

Each scene's opening frame (its hold, `escenas-plan.md` §1 camera table) and the end frame of its move, Cycles, night, the G63 with
the owner's picked props (bed B, the sticker mix, pantalla C, sign B, the Veracruz plate). Film frames come from frameref
(`E:\ComfyUI\references\<film>\NNN.jpg`, film-grab): analysis only, never copied into the repo or onto the contact page.
Gate: `refs-check.py <this section> --sections escenas` (PASS; the older sections fail `row-cites-library`).

| section | library entry | borrow | cost |
|---|---|---|---|
| escenas | kage-scroll-world · one camera rail through a live scene, a field of view per segment · `web/visuales-fichas/kage-scroll-world.md` (status: unproven) | Every still is a key on that rail: lens and position per the plan's table, the end frame of each move is where the next segment starts; 2: frame collateral/004 (tail-chase, rear three-quarter, night), kept higher so the bed and stickers read; 3 end: nightcrawler/029 (low rear three-quarter, lane lines converging), mirrored to the passenger side; 5 end: collateral/022 (the car small in its lane between the lamp rows, from high ahead); 6: collateral/028 (head-on three-quarter at bumper height, headlights to camera); 5 hold: drive/014 (the night road ahead over the dash), moved outside over the hood | M |
| escenas | video-que-avanza · scrubbed pre-rendered clips on the phone, a cut hidden at a gantry · `web/visuales-fichas/video-que-avanza.md` | 9:16 keeps 75 % of the 16:9 horizontal angle (storyboard.py `v()`); scene 4's phone frame is one window per stop; the end frames of 2 and 3 sit under the next sign, where the clip cut hides | M |

## Bed props, design pass (2026-11-13, run `saltydrone`; owner 05:36 "might need to work on those bed truck props as well, like the stickers one")

Bed B stays the frame: the piñata hangs from the roll bar over a low pile, balloons at the bar's ends. Twelve props a corridos tumbados
trio (requinto, bajo sexto, tololoche) would carry, each with its own material, on a model sheet; two arrangements, A tidy and B
lived-in, at the close-up (`VISTA_CAJA`) and scene-2 (`VISTA_ESC2`) cameras. Built by `blender/caja3.py`. What we change on purpose:
the round-1/2 boxes become shaped fundas and a real ATA case, and the decals are our own sticker art, only the band pieces with no
platform glyph (the §2 brand rules stay on the tailgate). At ESC2 (about 2 px/cm) only silhouettes and colour blocks read; materials
and decals are judged from the close-up. O = page opened; S = seen only in search results.
Gate: `refs-check.py <this section> --sections caja3`. **Not verified:** no photo was opened; every real-world row is S (search results only), and the search for corridos tumbados bands with gear in a pickup bed found no photo.

| section | library entry | borrow | cost |
|---|---|---|---|
| caja3 | kiln-prop · background prop: inventory, real size logged, one material per physical material, worn edges from a Bevel-node mask on boxes (`edges="bevel"`) · `blender/skills/kiln-prop/SKILL.md` | Every prop built by script at its real size (sizes in each builder's docstring); worn edges by a Bevel-vs-true-normal mask broken by noise: laminate to grey, tolex to grey, red cooler plastic stress-whitened, hat-box card scuffed to kraft | M |
| caja3 | kiln-utility-box · decals as quads ~0.6 mm off the surface, packed in one atlas, exported `as_is` · `blender/lab/kiln-utility-box/NOTES.md` | Our sticker art (`blender/calcas_arte.py`: a-mafia, b-ver, a-loteria, a-putifresa, b-escudo, a-estrella, b-pura) on flat faces only: road-case lid and front, cooler side, requinto lid, hat-box lid; the build packs them with the tailgate set | B |
| caja3 | interacciones-que-responden · one small reaction on hover · `web/visuales-fichas/interacciones-que-responden.md` (status: proven) | Each prop is one joined object with its origin at its foot, so the build can wobble it about its base; still one wobble per hover (tell 13) | B |
| caja3 | real world · tololoche and bajo sexto fundas, listado.mercadolibre.com.mx/fundas-para-tololoche (S): "Funda para tololoche 3/4 acolchada tipo mochila reforzada", "Funda reforzada acolchada docerola / bajo quinto / sexto, color negro", "tipo maletín, no rígido"; no hard case found for either · with `blender/skills/kiln-prop/SKILL.md` (sizes logged as assumptions) | The tololoche (1.80 m, lower bout 0.66 m) and the bajo sexto (1.05 m) in soft padded fundas, quilted nylon, a front pocket; the hard case goes to the requinto (0.98 m, rectangular tolex with an aluminium valance) | M |
| caja3 | real world · ATA road cases, idjnow.com/prox-xs-utl10w-case.html (S): grooved aluminium extrusions, laminated ply, recessed butterfly twist latches, spring handles; ca.tchweb.com/blogs/case-hardware/case-hardware-breakdown (S): ball corners absorb impact; a used rolling case listed as "road-worn exterior with stickers, marker labels" (craigslist, S) · with `blender/lab/kiln-utility-box/NOTES.md` | Road case 0.76 × 0.46 × 0.50 m: extrusions on all 12 edges, 8 ball corners, two latch dishes, side handles, stencil MAFIA TUMBADA / XALAPA, VER. · BACKLINE 03, stickers on the lid and front | M |
| caja3 | real world · plastic papel picado for outdoor fiestas, walmart.com/ip/Mexican-Party-Banners-5-Pack-with-10-Tissue-Paper-Flags-per-Banner-Papel-Picado-Mexicano-by-Fiesta-Wraps/2045499676 (S): plastic panels sewn on a string, ~16 × 12.5 in, "some of the colors would flip in a breeze" · with `web/visuales.md` (Y2K floating stickers row: playful colour shapes) | A string of 9 punched panels along the roll bar (A taut, B sagging off one end), the bed props' pink, turquoise, lemon, lime and orange; panel 0.24 × 0.30 m, punch pattern as alpha | M |
| caja3 | real world · generic objects, no single source, sizes assumed and logged: Coleman-style 48 qt cooler (0.64 × 0.37 × 0.42 m, as round 1's outdoorgearlab row), party tower speaker 0.72 m, tejana hat box 0.50 m across, straw tejana, 12-bottle crate (no brand), band flag 0.90 × 0.60 m on a pole, duffel, XLR coil, ratchet straps · with `blender/skills/kiln-prop/SKILL.md` | The rest of the twelve; the flag carries the MT shield (b-escudo) on black, never a national flag | M |
| caja3 | user: the sticker pass as the model (owner 05:36 "like the stickers one"); bed B picked 03:22 (`docs/design/escenas/utileria/index.html`) | Model sheet first, then A tidy / B lived-in at both cameras, and stop for the owner's mix | M |

## World, Night B (2026-11-14, run `yeehawdrone`; owner's pick 19:13 of the world audit, built in `blender/mundo.py`)

The world around the truck for scenes 1–6: road, verges, plants, far field, sky and mist. The audit's photos and film frames
(`~/cc-out/mto-world/referencias.md`, R1–R4 and F1–F4) carry over; film frames are analysis only, never copied into the repo.
What we match: R1's plants up to the asphalt and the pole line on the verge, R2's far trees as one band of crowns, R3's worn
asphalt, F2's lamp halos in haze over a warm-grey sky floor, F3's detail only inside the light pools. What we change on
purpose: night instead of day (R1–R3), no city glow (F2), our road is one carriageway of a divided autopista, so the left edge
is yellow and the lane line white dashed (R1 has a double yellow centre line).
Gate: `python3 -I ~/projects/visual-lab/web/scripts/refs-check.py docs/design/references.md --sections mundo`.

| section | library entry | borrow | cost |
|---|---|---|---|
| mundo | user: owner 19:13 via mothership, direction B of `~/cc-out/mto-world/hoja-direcciones.jpg` ("Húmeda, neblina"); 23:56 "before digging further into more animations, let's work on the scene and models" | Night B in every scene's Cycles render: overcast sky (kloppenheim_07, 0.25), mist 0.0028, dense green verge, tropical shrubs, a crown band, a CFE pole line | M |
| mundo | blender-notas · fog behaves the opposite between engines, don't transfer volume values · `blender/blender-notas.md` | The Cycles fog is its own key (`escena.json` noche.cycles.niebla, a fog box 82 m high so the sky stays clean); the page's FogExp2 0.012 is left alone | B |
| mundo | real world · R1 Commons `File:MEX 180 Estado Veracruz.JPG` (PD, O), R2 `File:Afueras de la ciudad de Jamapa.jpg` (CC BY-SA 4.0, O) · with `blender/blender-notas.md` | Mowed strip 3 m, guinea grass 1–1.6 m to 14 m, shrubs and pachira to 40 m, crowns 22–260 m, nothing 260–700 m, the hill ring under fog; poles every 48 m at x −9, 11 m, three wires sagging 1.2 m | M |
| mundo | real world · R3 Commons `File:EnteringAlvarado Highway180.JPG` (CC BY-SA 3.0, O); NOM-034-SCT2-SEDATU-2022 (DOF 2023-09-19, O) · with `blender/blender-notas.md` | asphalt_02 at 3 m with wheel paths, oil bands, patches, cracks and a 40 m macro mask, read on y wrapped to the 192 m loop; M-3.1 white right edge, M-3.3 yellow left edge, M-2.3 dashes 4.92/9.85 m (13 per loop), studs every 32 m | M |
| mundo | real world · F2 Collateral (2004) `collateral/022.jpg`, F3 Sicario (2015) `sicario/032.jpg` (frameref, O) · with `web/visuales-fichas/kage-scroll-world.md` | The LoD rule: hero plants only within ~14 m and inside the lamp and headlight pools; silhouettes beyond against a sky one step lighter | B |

## Bed load, real-life pass (2026-11-14, run `cookingdrone`; owner 11-14 "positioning in real life and it must have sense")

The owner rejected caja3's A and B. This pass loads the bed the way a touring band loads an open pickup: instruments in hard cases
(owner), the donut kept (owner), heavy items against the cab, straps or a net to the bed's tie-downs, the tailgate shut. Built by
`blender/caja4.py`, which measures the bed first (floor z 0.933, 1.05 × 1.76 m inside, rails only 0.25-0.30 m above the floor)
and checks every arrangement in code (`revisar_carga`: inside the walls and ahead of the tailgate, no two props interpenetrate,
anything above the rails under a strap or the net, nothing can slide forward more than 3 cm, heavy items against the cab).
What we match: the load-out order of the guides and forum posts below. What we change on purpose: the piñata, balloons, papel
picado and flag are gone (they hang loose and would not survive the drive); the cases keep the sticker art.
Marks: O = photo or page opened and looked at; S = search excerpt only; T = text of the page read, no photo.
**The gap, plainly:** no photo of band gear loaded in a pickup bed was opened. Forum threads that have them (TalkBass, DrumForum,
Maverick Truck Club, MusicPlayer) refused automated fetches (403, paywall redirect), Flickr rate-limited (429), and the earlier
pass's 22 photos (`cc/goblindrone:docs/design/props-placement/referencias.md`) hold no band gear in a bed. The positions rest on
the loading guides (text) and on two real photos of touring gear outside a truck.
Gate: `refs-check.py <this section> --sections caja4`.

| section | library entry | borrow | cost |
|---|---|---|---|
| caja4 | kiln-prop · background prop: inventory, real size logged, one material per physical material, worn edges from a Bevel-node mask · `blender/skills/kiln-prop/SKILL.md` | Every prop built by script at its real size (docstrings in `caja4.py`): hard cases 0.98-1.22 m, a 61-key keyboard case 1.02 m, a 14-inch snare case, a milk crate of cables, navy quilted moving blankets; reuses caja3's laminate, tolex, aluminium and cooler materials | M |
| caja4 | kiln-utility-box · decals as quads ~0.6 mm off the surface · `blender/lab/kiln-utility-box/NOTES.md` | Band stickers on the amp case lid and the B case lids (a-mafia, b-ver, a-putifresa, b-pura, b-escudo, a-estrella), the stencil MAFIA TUMBADA · BACKLINE 01 on the amp case | B |
| caja4 | real world · "4am Load Out", flickr.com/photos/96913438@N00/21696703 via Openverse (O, CC BY-NC-ND): night, a crew rolling ATA road cases into a truck, the cases packed tight side by side · with `blender/skills/kiln-prop/SKILL.md` | Cases go in as a tight block, nose to tail, with no gaps to slide into | M |
| caja4 | real world · "Gear", flickr.com/photos/40609437@N04/7872450798 via Openverse (O, CC BY-NC): a stickered guitar hard case, gig bags and a plastic milk crate holding cables · with `blender/skills/kiln-prop/SKILL.md` | The cable kit rides in a milk crate; hard cases carry stickers | M |
| caja4 | real world · drum cases with a rolling trap case, vintagedrumforum.com/attach/73597 and attach/73614 (O): round drum cases stacked, ATA trunks on casters · with `blender/skills/kiln-prop/SKILL.md` | The snare case is a round can with a lid band and strap; road cases have butterfly latches and ball corners | B |
| caja4 | real world · Art of Manliness, "How to load a pick-up truck", artofmanliness.com/skills/cars/how-to-load-a-pick-up-truck/ (O, an illustration, not a photo): heavy items as close to the cab as possible, even left to right, long items along the sides, boxes between them heavy at the bottom, ratchet straps, a tarp or webbing over the top · with `blender/skills/kiln-prop/SKILL.md` | Both arrangements: amp and full cooler against the cab wall; long cases lengthwise; B's net is the "webbing over the top" | M |
| caja4 | real world · cargo guides (S): place the heaviest cargo against the cab, over the axle, so it can't slide forward in hard braking; at least two straps per major item; hooks seated in the tie-down loops, not on the rails; pickups have tie-downs near the cab and near the tailgate (uhaul.com, slashgear.com "truck bed tie-down tips", jacosuperiorproducts.com cargo management) · with `blender/skills/kiln-prop/SKILL.md` | The amp is under two straps in A; straps and net hook only to six rings on the walls (four corners, one mid pair; the model has none, so they are assumed and drawn the same in A and B); the checker's frenado rule | M |
| caja4 | real world · TalkBass threads (S): "strap everything down", a bass on its side under a bungee net, a padded bed, cabs not laid on their back; Fender, "5 dos and don'ts for transporting your amp" (S): a cover or case, face down at most · with `blender/skills/kiln-prop/SKILL.md` | The amp travels upright in its case; cases lie flat or on edge, never loose; blankets as padding and void fill | M |
| caja4 | user: owner 11-14 on Board #34: "keep the donut, the instruments can go in cases for much easier modeling, what props can we get that are easier to do"; scene picks the same day: 3B (rear door), 4B (lit cab) | Two arrangements (A strapped, B under a net), the donut on top of each, the scene stills re-dressed with B and the picks applied | M |

## More props on bed B (2026-11-14, run `ldrone`; owner 11-14 "they can be irrelevant to the genre but must look good")

The owner picked bed B and asked whether to keep adding props. Twelve candidates sit on top of B. Each one is built by script in
`blender/caja5.py`, at real size and in the DESIGN.md palette (black, warm white and gold, plus the donut's pink as the one
accent). Each rides the way it would on the road: under B's net, bolted or zip-tied to the sport bar, in the stake pocket, or
over the cab. Three amounts are shown (ligera, media, llena). Each is measured against props-placement rules 1 and 3 and for
silhouette overlap (CAJA5 MEDIDA lines).

What we match: how each item is carried in the reference photos below. What we change on purpose:
- the piñata and the balloons ride bagged and netted instead of hanging;
- the flag stands in the stake pocket instead of the roll bar;
- the props' colours move to the palette (the reference piñata is blue and yellow; the crate's red becomes the stock yellow).

Marks: O = photo opened and looked at (a thumbnail); S = search excerpt only.
**The gap, plainly:** the balloons have no photo. The searches ("balloons in bag car", "balloons tied car") returned airships
and parades. The transport bag is a common balloon-shop practice, not checked against a photo.
Gate: `refs-check.py <this section> --sections caja5`.

| section | library entry | borrow | cost |
|---|---|---|---|
| caja5 | kiln-prop · background prop: inventory, real size logged, one material per physical material · `blender/skills/kiln-prop/SKILL.md` | Every candidate built by script at its real size (docstrings in `caja5.py`): 0.66 m star piñata, 11-inch balloons, 0.15 × 0.17 m papel picado, 7'0" board, 20 L can, 0.62 m neon panel; caja3's flag, hat box, beer crate and speaker reused | M |
| caja5 | real world · Wikimedia Commons "Star stjärna pinata SWEDEN" (O, CC BY-SA 3.0): a star piñata, five cones and tissue fringe at the tips · with `blender/skills/kiln-prop/SKILL.md` | Piñata shape: a ball with five cones and a fringe at each tip; colours moved to gold and black with pink fringe | B |
| caja5 | real world · Commons "Adorno de papel picado en la calle Carranza de Aguascalientes 07" and "Papel picado, Feria Nacional del Libro de la BUAP" (O, CC BY-SA 4.0): strings of punched tissue panels over a street · with `blender/skills/kiln-prop/SKILL.md` | Panels on a taut string, punched pattern as alpha; tied at both ends | B |
| caja5 | real world · Commons "American Flag on Pickup Truck" (O, CC BY-SA 4.0) and "Flags on a truck in Greenwood, October 2023" (O, CC BY 4.0): flags on poles in a pickup bed's corners · with `blender/skills/kiln-prop/SKILL.md` | The MT flag on a 1.5 m pole in the rear left stake pocket, flying back | B |
| caja5 | real world · Commons "Chevrolet Colorado Lifeguard at La Jolla" and "KNRM Lifeguard Schiermonnikoog Volkswagen Amarok" (O, CC BY 2.0): surfboards on a rack over a pickup bed; "Osaka Motor Show 2017 (286)" (O): a board standing in a bed · with `blender/skills/kiln-prop/SKILL.md` | The board rides over the cab on a rack bar clamped to the sport bar and a roof pad, strapped, deck down and fins up | M |
| caja5 | real world · Commons "Lyspærer i rekke" (O, CC BY-SA 3.0): a festoon string of round bulbs on black cable · with `blender/skills/kiln-prop/SKILL.md` | Warm bulbs on short pigtails off a black cable, zip-tied along the sport bar and the bed ledges (outline lights, props-placement rule 7) | B |
| caja5 | real world · Commons "Lightboks.webp" (O, CC0) and "Roland CUBE Street with batteries" (O, CC BY 2.0): battery speakers with lit drivers · with `blender/skills/kiln-prop/SKILL.md` | caja3's tower speaker with its rings in gold and pink, lying rings-up under the net | B |
| caja5 | real world · Commons "Hat Tin" (O, CC BY 2.5), "2 Kisten Bier in einem Reisebus" (O, CC BY-SA 4.0), "Camping-Chair-Background" (O, public domain), "Helinox Ground Chair 1" (O, CC BY-SA 4.0) · with `blender/skills/kiln-prop/SKILL.md` | Round hat box; crates of bottles carried in a vehicle; folding chairs flat | B |
| caja5 | real world · Openverse "Willys MB", flickr.com/photos/10101160@N08/2852611529 (O, CC BY-NC): a jerry can in a holder on a jeep · with `blender/skills/kiln-prop/SKILL.md` | The can in a steel tray with a strap, bolted beside the right rail | B |
| caja5 | real world · Commons "Neon.JPG" (O, CC BY-SA 3.0) and "Boulevard Hotel (Neon sign), Miami Beach" (O, public domain): neon letters as glowing outline tubes · with `blender/skills/kiln-prop/SKILL.md` | MT as gold outline tubes (text bevel, no fill) on a black panel | B |
| caja5 | real world · props-placement rules, `cc/goblindrone` docs/design/props-placement/reglas.md (O): rule 1 sight lines (scene 2: the tailgate stickers, ≤ 2 % covered), rule 3 clutter budget (4 per exterior view), rule 5 one silhouette, rule 7 two light colours, rule 8 it rides · with `blender/skills/kiln-prop/SKILL.md` | caja5's `medir`: rule 1 and rule 3 measured by ray casts at 1/5 of the still, plus the share of silhouette where items over the rails stack | M |
| caja5 | user: owner 11-14 picked bed B: "Need to see if we keep adding more props, they can be irrelevant to the genre but must look good" (via mothership) | Twelve candidates alone in studio light for one-by-one picks, three amounts on B, the piñata, balloons, papel picado and flag back as candidates, packed to survive the drive | M |
| caja5 | ai-mesh-to-rig · image → mesh with local TRELLIS.2, then cleanup in Blender · `blender/ai-mesh-to-rig.md` | The alien: TRELLIS.2 through StableGen's graph (`MTO-colddrone/blender/partes/trellis2.sh`, seed 33, 203 s) from the owner's photo cropped to the alien by hue (`tmp/caja5/recorte.py`; the photo and the crop stay local), scaled to 1.5 m, its texture kept, roughness 0.12 plus a clear coat for blown vinyl. Mirroring the crop to remove the person's fingers merged the legs (the toy leans), so the first mesh stays, with a small bump on one shoulder | M |
| caja5 | user: owner 11-14 picks from the studio sheet (via mothership): "let's keep the 5 speaker and 7 the beer box, also if we can add the alien to our props", his photo of a 1.5 m green inflatable alien; then "also if you can add soda cans, water props to the middle in the van or give them to the characters" | One dressed B (speaker, beer crate, alien standing on the amp case strapped to the sport bar); drinks with made-up labels (`blender/etiquetas.py`) in the front console's cupholders and against Diego's hand on the rear armrest, parented to the hand bone, 0 hand vertices inside the can | M |

## Prototype `/prototipo` (2026-11-16, run `cryingdrone`; mothership queue 2026-11-16-mto-site-prototype)

The look is already picked (A, DESIGN.md), so no new direction: these rows say where each piece of the prototype comes from. The
client material supplies content and facts only.

| section | library entry | borrow | cost |
|---|---|---|---|
| escenario | teamusa · all-intra video that advances with scroll · `web/visuales-fichas/video-que-avanza.md#recipe` | One fixed stage; the scroll sets `currentTime`. The ficha's all-intra wants a 3-5 s clip; ours is 46 s, so a keyframe every 3 frames (run, 2.9 MB) and every 4 (loop, 1.8 MB) | M |
| escenario | kage · fixed camera anchors per section, damped move · `web/visuales-fichas/kage-scroll-world.md` | Each section holds its run-frame range over its own height; the travel between two sections interpolates linearly (`ruta.json` `secciones`) | M |
| hero | arraisballet · smooth video hero, poster = first frame · `web/visuales.md#recipe-smooth-video-hero` | The stage's first paint is run frame 0 as a still, swapped for the video once it can seek | B |
| musica | landonorris.com · horizontal gallery · `web/visuales-fichas/galeria-horizontal.md#visual-reading` | The 9 covers as one strip over a veil band; platforms as three Teclas | B |
| video | dfm.mt · rendition sized to its box · `web/site-reading-fichas/dfm-mt.md#look` | Five YouTube thumbs at hqdefault, links out, no embedded player | B |
| integrantes | kage · fixed camera anchors per section · `web/visuales-fichas/kage-scroll-world.md` | The band loop is this section's picture, so the members go in one 520 px column and the cab stays visible beside it | M |
| contacto | MTO's own note · veil under text over a rendered scene · `web/visuales.md#technique-text-over-a-rendered-scene` | The contact panel on `--veil` over the last frames of the run | B |
| contacto | teamusa · reduced-motion start, visible motion toggle · `web/visuales.md#dissection-sports-withgoogle-com-teamusa` | Under reduced motion the stage changes pose in steps and the loop never plays; a visible Pausar video toggle in La banda | B |
| gira | user: `docs/design/escenas-plan.md` §5 empty state (owner's plan); the library has no dates-section ficha (paulkalkbrenner has only an index row, not read) | No dates in the repo, so the section shows the plan's line "Las próximas fechas salen primero en nuestro Instagram" and two links (Instagram, the Plaza Lerdo video); no invented dates | B |
| contacto | user: `docs/design/brief.md` › open (WhatsApp number, `socials.ts`) | The number as plain text under the button, taken from the same `socials.ts` link the button uses; unconfirmed (SPEC §4 says another) | B |
| pendiente | ai-slop-tells · tell 6, a labelled clay placeholder · `web/ai-slop-tells.md#1-the-tells-ranked` | What the repo cannot fill stays a dashed grey frame with a bold "Texto pendiente" label and what it waits on (2026-11-16: none left on the page; the 4th member, the manager, arrived from the owner); unrendered scenes are listed in the footer note; never styled to pass as finished | B |

## Site `/` (2026-11-18, run `maincharacterdrone`; mothership queue 2026-11-18-mto-full-site-preview)

No new direction: the prototype becomes `/`. These rows say where each piece the merge and the build added comes from.

| section | library entry | borrow | cost |
|---|---|---|---|
| escenario | arraisballet · smooth video hero, poster = first frame · `web/visuales.md#recipe-smooth-video-hero` | One still per stop (the Tripo v5 montaje-esc1..6, 960×540 webp) behind the video: shown for the stop in view only while the run cannot show a frame (loading, no H.264); the videos hide (`.sin-video`) so a poster never covers it | B |
| hero | user: `research/DESIGN.md` › Conversion additions (main, 2026-11-18) | Spotify (gold Tecla, the one primary) and Instagram (plain Tecla) on the first screen, plus Contratar | B |
| contacto | user: `docs/analytics.md` (main) | `data-placement` on header, hero, musica, video, grupo, gira, contratacion, footer; one delegated listener sends `wa_click` / `follow_click` to `POST /e`; the WhatsApp link is the `/wa/` counter | B |
| musica | user: `src/lib/plausibleClient.ts` (main) | Plausible page views only when `PUBLIC_PLAUSIBLE_DOMAIN` is set (CI sets it; a preview does not); `whatsapp_contratacion` kept on the contact button | B |
| video | user: `worker.js` header (iOS Safari refuses a <video> without a 206; main) | The run and the loop are `<video>`s under `/prototipo/`: that path goes through `worker.js` (`run_worker_first`) so a Range request answers 206, which iOS Safari needs | B |
| integrantes | kage · fixed camera anchors per section · `web/visuales-fichas/kage-scroll-world.md` | Unchanged from the prototype: the loop plays when the visitor holds still in the station | M |
| gira | user: `docs/design/escenas-plan.md` §5 empty state | Unchanged: no dates in the repo, so the plan's line and two links | B |

## P1 "more alive", phase 1 stills (2026-11-18, run `brainrotdrone`; mothership queue 2026-11-18-mto-vivo-p1-phase1)

The P1 package from Fable's audit, mocked in Cycles stills for the owner's pick (`blender/vivo_p1_stills.py`), plus the night
bake now live. The library is thin for these looks: no ficha covers glare, LED walls, dash screens, drizzle or a headlight
sweep. So each row names the nearest library entry, and the film frame it matches (frameref, `E:\ComfyUI\references\<film>\NNN.jpg`;
analysis only, never copied into the repo). Where the library has nothing, the row says so.
Gate: `refs-check.py <this section> --sections bake,glare,cabina,llovizna,led,rotulos,placa,destello`.

| section | library entry | borrow | cost |
|---|---|---|---|
| bake | kage-scroll-world · one live scene, the camera on a rail; the world streams past · `web/visuales-fichas/kage-scroll-world.md` (status: unproven) | The world's look comes from one Cycles render of a 192 m road period, top-down, shown unlit and repeated (`blender/vivo_bake.py`); sodium pools from the instanced pole lamps, treeline as two cards; matches collateral/022 (the freeway between rows of sodium lamps) | M |
| glare | pmndrs/postprocessing · bloom merged into few passes · `web/visuales.md` (libraries table, Zlib) | Not a full-screen bloom: one sprite per lamp (soft glow + a thin horizontal streak), so its cost is per lamp, not per pixel; the stills fake it in a post pass (`scripts/p1-destellos.py`); matches collateral/010 (oncoming headlights blooming in the haze) and 004 (tail lamps) | M |
| cabina | todoist.com · a two-layer key, a lighter lip as the pressed look · `web/site-reading-fichas/todoist-com.md#look` (the Tecla, as the radio rows above) | Dash screen on the dash top (radio2-a's place): the latest single's cover, title, Escuchar as the Tecla drawn flat, ‹ › for the 9 releases; the cab stays dark around it, lit by the screen and the oncoming sweep; matches collateral/023 and 029 (the driver lit by the dash, bokeh through the windshield) | M |
| cabina | user: no library entry for a headlight sweep through a cab (Fable's P1 audit, 2026-11-18) | An oncoming car on the other carriageway (Quaternius, CC0, already in the page) whose two spots rake the cab; two stills at 46 m and 17 m; matches collateral/029 | B |
| llovizna | user: no library entry for drizzle or insects in headlights (Fable's P1 audit, 2026-11-18) | 2,600 short streaks falling and streaming back past the truck, plus 40 moths near the lamps, lit only where the beams reach (stops 1, 5, 6); live it is one Points draw, off on the phone tier | B |
| led | nothing.tech · a dot-matrix face used as one brand voice · `web/site-reading-fichas/nothing-tech.md#look` | The rear screen drawn as an LED panel (round-dot cells, 180 x 185 per screen) with the stop-5 copy; the side screen already uses the same mask (pantalla_3d.py) | M |
| led | badomens · a marquee that runs by itself · `web/visuales-fichas/tarjeta-merch.md` | The rear crawl ("MIRA DÓNDE ANDAMOS · INSTAGRAM ·"): one line on a dark red band, cut on the right; live it scrolls; the bulb chase is the same idea in light (every third bulb dim in the still) | B |
| rotulos | user: `docs/design/escenas-plan.md` §1 (section titles on green highway signs) and the NOM-034 row above (`portico`) | Each stop's own title on both title panels (ickdrone's portico_b and arco_c), from one atlas (`scripts/letreros-atlas.py`, Saira 600), swapped live only while no label is in view | B |
| placa | button-states-and-icon-morphs · hover/press states, one reveal per control · `web/visuales-fichas/button-states-and-icon-morphs.md` | The member's name plate (name, role, Instagram in gold) next to the window that lowers; from the hood cameras it faces the camera, not the door | M |
| destello | interacciones-que-responden · Web Audio horn, a mute toggle stored per visitor · `web/visuales-fichas/interacciones-que-responden.md#recipe` (proven) | Stop 6's plate click: two headlight flashes (lights at 3x, the lens glare 'fuerte'), the horn only with sound on, then `/wa`; matches collateral/028 (head-on headlights at bumper height) | B |
