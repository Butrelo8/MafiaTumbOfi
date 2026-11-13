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
