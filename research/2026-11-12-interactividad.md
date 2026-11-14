# Interactividad: what the band figures and scene props can do (2026-11-12)

family: mto-interactive · ledger: `research/2026-11-12-interactividad.claims.tsv` (C1–C34)

Question: which animations (band skeletons), transition props (day↔night, headlights, wipes) and interactive bits
(eyes or heads following the cursor, clicking a member, scroll moments) fit the new Blender truck scene, and for each
one: how it is made, effort, phone risk, whether it needs real-time 3D, and a working example.

## Verdict

For the first scene, the bits that work are the ones that live inside or on top of the pre-rendered Cycles video:
- idle loops baked into the render;
- day↔night as two renders joined at a cut hidden behind an occluder (an overpass or a sign gantry);
- a Blender-rendered grid of head turns that follows the cursor;
- a stacked-alpha clip when a member is clicked.

Live three.js figures and eye bones come later, if ever [C1, C28, C15, C34, C25]. Two blockers come before any of it.
First, the four Tripo GLBs have no skeleton at all [C1]. Second, Tripo's own terms say free-plan outputs belong to
Tripo, with no commercial use [C12, C13]. That second point is an owner decision about money and rights, not a
technical one.

Confidence: medium. The licence and rig facts are high: they rest on owner sources and on files I measured. The
ranking is a judgment built on other people's models and devices. Nothing here was built or measured on a phone with
these figures.

## Headline findings

1. **Licence first: on Tripo's free plan the figures belong to Tripo.** The Terms (§5.2.1, last updated 2025-07-11)
   say that "for Free Users, Tripo retains all rights", including distribution and licensing [C12]. Tripo's help page
   says commercial use is "Not granted" on free and granted on paid plans [C13]. The pricing page lists the free plan
   as "Public Models · Non-Commercial Use", with Pro at 20 USD/month billed annually [C9]. The handoff's "CC-BY, not
   verified" assumption is contradicted by the owner's own documents. A Tripo blog post that says "CC BY 4.0" was
   only seen as a snippet (see Disagreeing sources).
   Caveat: these are the vendor's documents about its own terms (dated 2025-07-11, read 2026-11-12). Not verified:
   which plan the owner used, and whether upgrading later moves rights in models generated while on the free plan. The
   terms do not say. A band page that sells bookings plausibly counts as commercial use; that is my reading, not
   legal advice.
2. **The figures cannot animate yet: no bones, and far too heavy for live use.** Each GLB is one mesh with no skin, no
   joints, no morph targets and no clips: 288k–477k triangles and 12.9–18.8 MB, each with three textures of about
   1.5–2 MB [C1]. Every figure idea below needs a rig first. Options:
   - Tripo's rig API (biped, v3.0, Mixamo-named bones; 25 credits in the doc's example) [C7, C8];
   - Mixamo's free auto-rigger [C2];
   - hand rigging in Blender.

   Any live use also needs heavy decimation. For scale, a 55k-triangle Mixamo figure ships at 233 KB gzipped
   [C3].
   Caveat: C1 is my own parse of the glTF JSON chunk; the Tripo rig facts are the vendor's API docs.
3. **"Eyes follow the mouse" cannot use eye bones: none exist and Tripo's rig adds none.** Tripo's rig is biped-only,
   "no facial joints, no IK chain pre-setup", with noisy jaw weights [C28]. Its docs name no face bones [C8]. The eyes
   are painted into the texture. That leaves two routes:
   - **Head-turn grid (recommended).** Render each member's head at 9 (3×3) or 15 directions in Blender and swap
     frames by pointer angle, the way face_looker, creepyface and page-mascot do [C25, C26, C27].
   - **New pupil meshes.** Model pupils in Blender and drive them live in three.js, which needs a live figure. Effort
     is L.

   Caveat: C28 is one studio's May 2026 test of uploaded meshes, not of these toys.
4. **Transitions: hide the cut behind something that crosses the frame.** In the old build, transitions between shots
   were the costliest problem. "Splitting at the black" became the recipe [C29], and a cut hidden behind a pillar and a
   door jamb worked over 5 frames of black [C34]. On a highway the same occluder can be an overpass, a tunnel mouth, a
   sign gantry or a passing trailer. It also hides a day→night switch: the clip after the occluder is the night render,
   with headlights and street lamps on.
   Caveat: C34 was tested on AI-generated plates in the old santuario, not on a Blender highway. The occluder trick is
   unchanged, but the highway version is untested.
5. **Overlays on the video: use stacked-alpha AV1, not native alpha video.** The same clip measured:
   - VP9 alpha: 1.1 MB (Chrome, Firefox);
   - HEVC alpha: 3.4 MB (Safari);
   - stacked-alpha AV1 (colour on top, alpha below, a WebGL shader): 460 kB in Chrome, Firefox and iPhone Safari
     [C15].

   Native alpha also misbehaves on Android: Chrome gets the alpha wrong and Firefox stalls [C16]. That matters for a
   member's reaction clip or a smoke puff laid over the loop.
   Caveat: one author's test on one clip in 2024, at Shopify scale. Our own lab measured VP9 alpha at 124 KB for a
   small 540×720 figure [C4].
6. **Gyroscope on phones costs a permission tap on iOS, so make it opt-in or skip it.** `requestPermission()` needs a
   secure context and a click or tap, and it rejects without one [C10]. Not every browser requires it, so
   feature-detect first [C33]. page-mascot simply switches cursor tracking off on touch devices [C27]. creepyface
   follows the finger instead [C26].
   Caveat: MDN documents the API, not how many visitors accept the prompt. No acceptance-rate data was found.
7. **Free motion with safe licences exists, and Mixamo is fine for rendered video only.**
   - Mixamo is free for commercial use. Its one ban is "distribute the raw character and animation files" [C2].
     Rendered frames are fine; a GLB with Mixamo curves on a public page is a grey area [C2].
   - CMU mocap may be "copied, modified, or redistributed without permission" [C24].
   - Quaternius's Universal Animation Library has 120+ clips under CC0 [C11].

   None of these has instrument playing confirmed (see Not found). Strumming, steering and the head nod should be
   hand-keyed, as the earlier figure script already did [C32].
   Caveat: the Mixamo terms are an Adobe staff FAQ and call the service a "limited duration technology preview".
8. **Live skinned figures on phones are plausible at low triangle counts but unmeasured here.** One forum dev ran 25
   low-poly characters (about 20 bones each) at 120 fps once physics was off [C19]. Another saw 60 fps on a phone
   drop to 10–20 fps after a Blender re-export [C20]. The phone budget is a 3 MB entry and 1 MB per gesture [C31].
   three.js itself is about 2.1 MB unminified in our lab page, less minified and gzipped [C3].
   Caveat: these are other models on unknown devices. Nobody measured these figures or the G63.

## Ranked table

Ranked by fit for the **first scene**: a pre-rendered Cycles loop with the inside→outside camera move, phone budget
3 MB entry / 1 MB per gesture [C31]. Effort S = hours, M = 1–3 days, L = a week or more. "Live 3D" means three.js
running in the page.

| # | Idea | How | Effort | Phone weight / perf risk | Live 3D? | Example |
|---|---|---|---|---|---|---|
| 0 | **Prerequisite: rig + licence** | Settle the Tripo rights [C12]. Rig the four GLBs (Tripo rig API v3.0 biped with Mixamo names [C7], or Mixamo auto-rig, or Blender). Decimate only if anything goes live | M | none for video; for live use the 13–19 MB GLBs must drop by about 50× | no | [Tripo rig API](https://developers.tripo3d.com/en/docs/animations-rig.md) |
| 1 | **Idle loops baked into the render** (head nod on the beat, blinks, strum, steering, ember flare, toy smoke puffs) | Hand-keyed in Blender on the rig; periods divide 240 frames; rendered into the scene loop | M (after #0) | none: it is inside the loop you already ship | no | own: handoff idea list [C32]; [lab 3](file:///home/black/projects/visual-lab/blender/lab/mixamo-walk-to-threejs-glb/NOTES.md) [C3] |
| 2 | **Hidden cut behind an occluder** (overpass, tunnel mouth, sign gantry, passing trailer) | Two renders that each end/start on a frame covered by the occluder; the cut lands there | S–M | none beyond the clips | no | own: `research/wayfinder/santuario/tickets/01-prueba-nave-sacristia.md` [C34] |
| 3 | **Day↔night swap at that cut** (sun low in the day clip, moon up after it; **headlights and street lamps on** in the night clip) | Two loops of the same shot (day HDRI / night HDRI already on disk); the transition clip passes the occluder and swaps. Headlights are emissive lenses + spotlights in the night render | M | doubles that stop's weight (two loops); keep each ≤ 1 MB | no | live equivalent: [three.js sky system](https://discourse.threejs.org/t/complete-sky-system-for-three-js-skybox-sun-moon-day-night-cycle-clouds-stars-lensflares/88311) [C21]; no pre-rendered web example found |
| 4 | **Head follows the cursor** (per member, desktop) | Blender: render the rigged head (or the whole bust) at 3×3 or 5×3 turns, alpha, one sprite sheet; JS picks the cell by pointer angle, dead zone near the figure | M (after #0) | small: 9–15 cells per member as WebP/AVIF (likely tens of KB each, not measured); off on touch or follows the finger | no | [page-mascot](https://themenonlab.blog/blog/page-mascot-cursor-following-website-characters) [C27], [creepyface](https://github.com/4lejandrito/creepyface) [C26], [face_looker](https://github.com/kylan02/face_looker) [C25] |
| 5 | **Click / tap a member → reaction** (waves, raises the glass, guitar flourish) plus name card | Short Blender render per member as stacked-alpha AV1 over the loop; or simply a name card + highlight ring at first | M per clip | each clip must stay well under 1 MB; stacked alpha 460 kB for a full clip in Jake's test | no | [stacked-alpha video](https://jakearchibald.com/2024/video-with-transparency/) [C15] |
| 6 | **Street lamps sweeping light over the truck at night** | In the night render: lamp posts on a period that divides the loop; their light passes over the paint | S | none (inside the loop) | no | none found (searched: "three.js day night toggle headlights") |
| 7 | **Smoke puffs** (cigarette, exhaust) | Baked in the render (toy puffs already in the idea list [C32]); or a CSS/canvas overlay | S | none baked; tiny as overlay | no | own idea list [C32]; no overlay example opened |
| 8 | **Section wipes in CSS** (pixel or curtain wipe between text sections, over the video) | GSAP ScrollTrigger scrub, squares in the next section's colour | S | small (GSAP) | no | catalog: `visual-lab/web/visuales-fichas/transicion-pixelada.md` [C30] |
| 9 | **Scroll-scrubbed moment** (scrub the inside→outside camera move) | Video with dense keyframes (1 per 5 frames); `currentTime` follows scroll; mp4 for iOS, webm for Firefox | M | high: about 5× the bytes of a normal encode [C22]; choppy on weak Android | no | [muffinman scrubbing demo](https://muffinman.io/blog/scrubbing-videos-using-javascript/) [C22] |
| 10 | **Gyroscope tilt** (phone parallax of the overlay layers) | `deviceorientation` → small offset of overlays; iOS needs a tap on an "activar" button | S | low CPU; UX cost of the permission prompt on iOS | no | [MDN](https://developer.mozilla.org/en-US/docs/Web/API/DeviceOrientationEvent/requestPermission_static) [C10, C33] |
| 11 | **Live head/neck following the cursor in three.js** | Rigged, decimated GLB; neck and spine bones rotate toward the pointer; remove those tracks from the idle clip | L | three.js + figure GLB on the 3 MB entry; skinned perf varies [C19, C20] | yes | [Codrops tutorial](https://tympanus.net/codrops/2019/10/14/how-to-create-an-interactive-3d-character-with-three-js/) [C17] |
| 12 | **Live eyes (new pupil meshes) following the cursor** | Add pupil/iris meshes in Blender, parent to the head bone, rotate live | L | same as #11 | yes | none opened for a GLB toy; Codrops [C17] is the head version |
| 13 | **Live day↔night sky** (Sky addon, sun position uniform) | three.js `Sky` (WebGLRenderer) or `SkyMesh` (WebGPU) driven by scroll or a toggle | L for this site (it would replace the pre-rendered scene) | high: whole scene live | yes | [three.js Sky](https://threejs.org/docs/pages/Sky.html) [C18], cycle as a lerp table [C5] |
| 14 | **Rive 2D versions of the members** (pointer-tracked eyes) | Draw flat versions, rig in Rive, Pointer Move listener moves the eyes | L (new art) | rive.wasm about 199 KB + .riv | no (2D canvas) | [Rive listeners](https://rive.app/docs/editor/state-machine/listeners.md) [C23]; landonorris.com ships Rive [C6] |
| 15 | **Live Mixamo clips in a GLB** | Mixamo clips on the rig, exported as named glTF clips | M | as #11 | yes | licence grey area [C2]: prefer CMU [C24] or Quaternius CC0 [C11] |

## Top 5 for the first scene

1. **#1 Baked idle loops.** This is the cheapest life in the shot and costs zero extra bytes. It needs the rig (#0).
2. **#2 Hidden cut behind an overpass or gantry.** The inside→outside move needs somewhere to change shots, and the old
   build proved the trick [C34].
3. **#3 Day↔night at that cut, with headlights and street lamps (#6) coming on.** This is the owner's sun/moon ask,
   rendered rather than live. The night HDRI is already on disk.
4. **#4 Head-turn grid that follows the cursor.** This is the owner's "eyes follow the mouse", built from a Blender
   render. It costs a few small sprite sheets, and on phones the head follows the finger or tracking switches off
   [C26, C27].
5. **#5 Tap a member → name card first, reaction clip later.** The card needs no new render. The reaction clips can
   follow as stacked-alpha AV1 [C15].

Leave out of the first scene: everything with "Live 3D = yes" (#11–13, #15). None of it fits a 3 MB phone entry
alongside the scene video until a decimated figure is measured.

## For

- Pre-rendered is how this repo already works: "Render real geometry, not generated video", and the loop is a
  Cycles render [C31 source, `docs/brief-camion.md`].
- A head grid swap is simple: "The pointer's angle relative to the mascot picks a cell", with "A dead zone keeps the
  head settled when the cursor is close" [C27].
- Stacked alpha: "this is 460 kB. A huge reduction compared to 1.1 or 3.4 MB for the native version" [C15].
- Safe motion licences: Quaternius is "Free to use in personal, educational and commercial projects. (CC0 License)"
  [C11]; CMU "may be copied, modified, or redistributed without permission" [C24].

## Against

- Tripo free plan: "Tripo retains all rights" to outputs [C12]; commercial use "Not granted" [C13].
- Tripo rig: "no facial joints, no IK chain pre-setup"; "Jaw weights are noisy" [C28].
- Scrubbing costs bytes: dense keyframes made the file "about five times more" [C22].
- Live skinned figures can collapse on a phone: "(40-80 fps on my PC, 10-20 fps on my phone)" after a re-export [C20].
- Native alpha on Android: "Chrome Android gets the alpha channel wrong." [C16].

## Disagreeing sources

- **S1 (Tripo licence):** a Tripo blog post says the free tier is CC BY 4.0 and usable commercially with attribution
  [C14, snippet]. The Terms (§5.2.1) and the help page say the opposite [C12, C13]. The Terms are primary: Tripo's
  help page says the Terms are "the authoritative document". The blog stays a snippet and is not used.
- **S1 (rig quality):** Tripo's own doc presents v3.0 as "higher-quality humanoid rigging" [C7]. An independent test
  found over-smoothed shoulder weights and no facial joints [C28]. They do not contradict on facial bones, which
  neither source lists.
- **S2 (Mixamo):** the Adobe FAQ allows "unlimited commercial" use but bans redistributing raw files [C2]. Whether a
  GLB served to browsers counts as redistribution is not addressed. The visual-lab note reads it as a grey area; I keep
  that reading.
- **S3 (live skinned figures):** 25 low-poly characters at 120 fps [C19] versus one character at 10–20 fps on a phone
  after a re-export [C20]. Neither measured our figures. C19 is the cleaner test (physics removed). C20's cause was
  never found.
- **S4 (transition props):** no dissent found after: "website day night toggle three.js scene sun moon transition
  headlights awwwards", "three.js character head follow mouse bone lookAt example". No source argued against
  occluder cuts or paired renders. The only counterweight is cost (two loops per stop).
- **S5 (cursor following on phones):** page-mascot turns tracking off on touch [C27]; creepyface follows the finger
  instead [C26]; MDN offers the gyroscope behind a permission tap [C10, C33]. Three valid choices, no consensus. The
  claim that iOS forgets the gyroscope permission after a browser restart is snippet-only (the Slider Revolution FAQ
  returned 404).
- **S6 (alpha delivery):** our lab played a 56-frame alpha AVIF sequence fine in Chromium [C4]. Jake Archibald found
  animated AVIF broken in Safari and "struggles to hit even a few frames per second" on Android [C15/C16 source]. The
  lab tested an AVIF frame sequence on a canvas, not an animated AVIF `<img>`, so both can hold. For phones, prefer
  stacked-alpha AV1.

## Sub-questions

| id | type | question | owner source | answer |
|---|---|---|---|---|
| S1 | fact | What do the Tripo GLBs carry, and what does Tripo's auto-rig give? | the GLB files; Tripo docs | No skin, bones or clips; 288k–477k tris, 13–19 MB [C1]. The rig API adds a biped with Mixamo-style names, no face bones [C7, C8, C28]. Free-plan outputs belong to Tripo [C12, C13] |
| S2 | fact | Which free motion libraries exist, and what do their licences allow on a website? | Adobe FAQ; CMU; Quaternius | Mixamo: free, no raw-file redistribution [C2]; CMU: redistribute freely [C24]; Quaternius UAL: CC0 [C11]; Rokoko's free library: Not found |
| S3 | number | What runs real-time on a phone, and what must be pre-rendered? | three.js forum; lab 3 | Low-poly skinned figures can run [C19] but vary [C20]; 55k tris → 233 KB gz [C3]; budget 3 MB / 1 MB [C31]. The Cycles look (G63, gold/chrome) stays pre-rendered |
| S4 | fact | How are day↔night, sun/moon, headlights, lamps, wipes and smoke done, at what cost? | three.js docs; repo research | Pre-rendered pairs joined at an occluder cut [C34, C29]; live: Sky addon [C18], sky system [C21], lerp table [C5]; CSS wipes [C30] |
| S5 | fact | How do eyes/heads follow the cursor, and what replaces the cursor on a phone? | MDN; Codrops; repos | Live bones [C17]; image grid [C25–C27]; Rive Pointer Move [C23]; phone: finger, off, or gyroscope behind a tap [C10, C33] |
| S6 | fact | Live 3D vs layered video: alpha video, scrubbing, Rive: support and cost | Jake Archibald; muffinman; lab 3 | Stacked-alpha AV1 460 kB [C15]; native alpha bugs [C16]; scrubbing 5× bytes [C22]; Rive wasm 199 KB [C6]; lab AVIF/WebM alpha [C4] |

## Blocked

| URL / call | failure | used instead | ledger ids leaning on it |
|---|---|---|---|
| `resa search "three.js eyes follow cursor" --source reddit` | HTTP 403 | WebSearch + forum threads | C19, C20 |
| `resa search "gyroscope permission iOS website parallax" --source reddit` | 429, not retried | MDN | C10, C33 |
| https://www.rive.app/blog/introduction-to-listeners | 404 | Rive docs listeners page | C23 |
| https://www.rokoko.com/products/studio/motion-library | 404 | none (Rokoko licence not opened) | none |
| https://mintlify.wiki/JustADev1024/threejs-car/features/day-night-cycle | 404 | three.js sky system thread | C21 |
| https://www.sliderrevolution.com/faq/enabling-gyroscope-permission-in-ios-for-3d-parallax/ | 404 | MDN | C10, C33 |
| https://mocap.cs.cmu.edu/faqs.php | TLS certificate error (exit 7) | the same page over http | C24 |

## Not found

- **Instrument-playing clips in free libraries** (guitar strum, accordion/bajo sexto). Tried: the Quaternius page (no
  instruments listed). Mixamo's catalogue needs a login, so it was not searched. Default: hand-key them [C32].
- **Rokoko free motion library licence.** The product page returned 404. A CG Channel snippet says commercial use is
  allowed, but it was not opened.
- **A working web example of pre-rendered day↔night or headlights switching on.** Searched "website day night toggle
  three.js scene sun moon transition headlights awwwards". Only live three.js demos and CSS toggles came back.
- **Phone acceptance rate of the iOS gyroscope prompt.** No data found.
- **Android gyroscope specifics** beyond MDN's "not all user agents implement these methods" [C33].

## Sources

- Tripo: https://developers.tripo3d.com/en/docs/animations-rig.md · https://www.tripo3d.ai/pricing ·
  https://www.tripo3d.ai/terms · https://www.tripo3d.ai/help/privacy-policy/how-to-use-tripo-models-commercially
- Auto-rig comparison: https://www.strayspark.studio/blog/ai-auto-rigging-showdown-2026-tripo-meshy-cascadeur-mixamo
- Motion: https://community.adobe.com/questions-696/mixamo-faq-licensing-royalties-ownership-eula-and-tos-589400 ·
  http://mocap.cs.cmu.edu/faqs.php · https://quaternius.com/packs/universalanimationlibrary.html
- three.js: https://threejs.org/docs/pages/Sky.html ·
  https://discourse.threejs.org/t/complete-sky-system-for-three-js-skybox-sun-moon-day-night-cycle-clouds-stars-lensflares/88311 ·
  https://discourse.threejs.org/t/tips-for-optimizing-skinned-boned-characters/47326 ·
  https://discourse.threejs.org/t/performance-issues-regarding-blender-exports-and-mixamo-animations/48179 ·
  https://tympanus.net/codrops/2019/10/14/how-to-create-an-interactive-3d-character-with-three-js/
- Cursor-following images: https://github.com/kylan02/face_looker · https://github.com/4lejandrito/creepyface ·
  https://themenonlab.blog/blog/page-mascot-cursor-following-website-characters
- Rive: https://rive.app/docs/editor/state-machine/listeners.md
- Video: https://jakearchibald.com/2024/video-with-transparency/ · https://muffinman.io/blog/scrubbing-videos-using-javascript/
- Device orientation: https://developer.mozilla.org/en-US/docs/Web/API/DeviceOrientationEvent/requestPermission_static ·
  https://developer.mozilla.org/en-US/docs/Web/API/Device_orientation_events/Detecting_device_orientation
- Own: `blender/assets/reparto/*.glb` (measured) · `docs/brief-camion.md` · `docs/handoffs/2026-11-12-g63-y-figuras.md` ·
  `research/README.md` · `research/wayfinder/santuario/tickets/01-prueba-nave-sacristia.md` ·
  `~/projects/visual-lab/blender/lab/mixamo-walk-to-threejs-glb/NOTES.md` · `~/projects/visual-lab/web/visuales.md` ·
  `~/projects/visual-lab/web/site-reading-fichas/landonorris-com.md`

## Self-check

- **Is each headline's source the owner of the claim?** Licence: yes (Terms, help page, pricing). Rig contents: yes
  (the files). Rig quality: no, a third-party test [C28], labelled as such. Alpha video: Jake Archibald's own
  measurement, not the browser vendors'. Gyroscope: MDN, the documentation owner.
- **Is the first headline the one the decision turns on?** Yes. Without commercial rights, no figure idea ships
  publicly. Swapping headlines 1 and 2 would not change the verdict, since both block every figure idea.
- **Does each caveat say what was measured?** Yes. Each caveat names the sample (one clip, one forum dev, one studio
  test) or says the source is vendor documentation.
- **Anything old or superseded?** Codrops is from 2019 (its approach still holds, but the code predates current
  three.js). The Mixamo FAQ is from 2022 and still says "technology preview". The forum perf threads are from 2023.
- **Single-source numbers:** 460 kB / 1.1 MB / 3.4 MB [C15] (one author); 5× for scrubbing [C22] (one demo);
  120 fps × 25 [C19] and 10–20 fps [C20] (one forum post each); 25 credits per rig [C8] (the doc's example only).
  Each is labelled single-source above.
