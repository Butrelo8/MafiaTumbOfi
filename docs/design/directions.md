# Three directions: Mafia Tumbada (2026-11-12, for the owner's pick)

All three pages carry the same real content (`directions/data.js`, from `research/contenido/`), so only the look
changes. Each one: hero, music, video, members and contact, at 390 and 1440. Comparison page:
`directions/index.html`. Shots: `directions/shots/`. Row ids refer to `references.md`.

Measured on all three (localhost, lab):

| | A Carretera | B Cartel | C En vivo | eptosuno.com |
|---|---|---|---|---|
| `revisar.sh` web, 390 + 1440 | 0 FAIL | 0 FAIL | 0 FAIL | — |
| Text contrast fails (WCAG 4.5:1) | 0 | 0 | 0 | 11 (`tokens.mjs`) |
| Tier-A slop tells (eyebrow, numbered tabs, scroll cue, hollow type, marquee) | 0 | 0 | 0 | 5 by eye |
| Weight at 390, cache off | 1.51 MB (the loop is 980 KB) | 0.78 MB | 0.78 MB (still image; a loop adds ≤ 1.2 MB) | 363 KB after scroll (1440) |
| CLS 1440 | 0.016 | 0.078 | 0.063 | 0.001 |

All three are **heavier** than eptosuno. Its 363 KB is a real strength. A localhost LCP is not comparable with a live CDN,
so no speed claim is made. Where we beat it: contrast, no tier-A tells, one display family plus one text family instead
of five, and assets nobody else on the label has.

`slop-check.py` on `directions/`: no FAIL rows. Three REVIEW rows are kept on purpose:
- `js-intersection-reveal` (A): it plays and pauses the loop by visibility. It is not a reveal.
- `accent-edge-stripe` (B): the 3 px black rules are the poster's printed rules, across the full width, not an edge
  stripe on a card.
- `near-black-hex` (C ground): the ground is a patina green sampled from the logo's bolt, not a near-black.

## A: Carretera (the truck, 3D rendered)

**One line:** the band's black pickup on a night highway, rendered in Cycles. The page's sections are stops along the
road.

- **Trace:** hero = arraisballet poster/loop + landonorris render-while-visible + lusion stage; música = landonorris
  horizontal strip; video = dfm rendition sizing; integrantes = kage camera anchors (the cab shot, `docs/escena-transicion.md`
  on main); contacto = the veil technique over the rendered scene.
- **Palette and type:** `#000` + gold `oklch(80% .13 82)`, both from the logo's black faces and bronze-gold bevel. Saira
  Condensed 800 italic, whose lean echoes the logo's slant, over Saira. Tier B "chosen font": Saira picked for the slant,
  not as a default.
- **Buttons and icons:** square controls with a gold edge. On hover the fill wipes up from the bottom, like a dash light
  coming on (500 ms, cubic-bezier(.65,0,.35,1), row `botones` rafadesign). Press dips 2 px in 90 ms (boleto). Icons:
  play↔pause and arrow→WhatsApp as Rive state machines (row `botones` Rive, **unproven**: the library has no measured
  icon morph yet).
- **Cost:** Cycles at about 12 s/frame on the RTX 4070 Ti. The 9:16 loop is 13 min and the 16:9 loop 6–7 min, already
  rendered (`docs/prototipo-camion.md`). 1.51 MB at 390 against the 3 MB budget. Phone: video decode only; three.js live
  is optional, desktop only. Known flaws: the CC0 pickup is low-poly at close stops, dusk paint goes silver, and the 16:9
  loop has the dark-lens bug.
- **Tripo figures** (members in the cab): the owner cleared them on 2026-11-12, because they come from a friend's account
  and are public there. Tripo's Terms §5.2.1 say that for free users "Tripo retains all rights". Both facts are recorded
  here; the owner decides. `[ask: which plan made them, and any attribution it requires]`
- **How it beats eptosuno:** eptosuno shows a still B&W portrait with a giant blackletter name. A shows a rendered world
  the band owns, and no other label site has 3D. It differs on all three axes: palette (gold vs red), display face (slanted
  sans vs blackletter + Anton) and hero mechanism (scene vs photo).

## B: Cartel (print poster, no 3D)

**One line:** the page is a two-ink concert poster (black + the logo's gold on paper stock), and booking is a ticket stub.

- **Trace:** hero = anna-dawson tour posters → colour overlays + pina-bausch condensed display at 390; música =
  mattjumper grid + badomens cover-to-back swap (300 ms); video = a line-up set like the acts on a cartel; integrantes =
  synchronized credits; contacto = boleto-perforado ticket stub.
- **Palette and type:** paper `oklch(96% .008 90)`, ink `#000`, gold `oklch(78% .14 82)` from the logo. The photos are
  printed as a duotone (grayscale multiplied over gold). Anybody uses its width axis (62 %→150 %) the way wood type
  mixes widths on a poster, over Archivo. Tier B "light paper": it is the poster stock, not cream-terracotta.
- **Buttons and icons:** a black slab. On hover gold ink rolls up from the bottom (500 ms, the same rafadesign wipe);
  press dips 3 px and acts on release (boleto). Icons: rubber-stamp glyphs, with arrow→WhatsApp morphing in Rive
  (**unproven**, as in A).
- **Cost:** none to render. 0.78 MB at 390, all CSS, trivial on a phone. The weak spot is that the covers are 160 px
  webp and upscale soft in the grid. `[ask: covers at ≥ 1000 px]`
- **How it beats eptosuno:** it is the opposite on all three axes: light vs black, one wood-type family vs five faces,
  a poster lockup vs a portrait with a giant name. It reads as a Mexican cartel de baile, not as any rap site.

## C: En vivo (the band's live footage, no 3D)

**One line:** the crowd and the stage carry the page: a full-bleed live image (a loop once we have the footage), the 3D
logo mark over it, and the stage again behind the contact.

- **Trace:** hero = arraisballet loop recipe + sadlerswells overZoom 1.1→1 over 2 s; coastveracruz is the weight trap to
  avoid. música = paulkalkbrenner photo-to-squares (planned) + a lead release; video = load by proximity, with one
  teamusa scroll-run clip kept short; integrantes = badomens swap to a stage photo; contacto = the hero loop reused.
- **Palette and type:** ground `oklch(17% .018 165)`, the bolt's green-bronze patina; bronze `oklch(79% .12 78)` from the
  bevel. Big Shoulders Display 900 over Schibsted Grotesk.
- **Buttons and icons:** square controls with a bronze edge. They lean toward the pointer (6 px / 3.6 px, spring 260/26,
  rafadesign magnetic), dip to .96 on tap, and stay still on touch and under reduced motion. Icons: the play icon on the
  lead video morphs to pause in Rive (**unproven**).
- **Cost:** the prototype uses the still `public/band/band-2.jpg`. The real hero needs the band's raw footage of the Plaza
  Lerdo show `[ask]`, cut into a ≤ 1.2 MB AV1/H.264 loop. The scroll-run clip is M (all-intra encode, 2–4 MB, loaded by
  proximity). Phone: video decode only.
- **How it beats eptosuno:** both use real photos, but C's hero is the crowd, not a portrait, and the palette is patina
  and bronze, not black and red. It differs on 2 of 3 axes (palette and hero mechanism; both use a condensed display).
  It is the closest of the three to eptosuno.

## Recommendation

**A, Carretera.** It is the only direction that shows something no other artist on the label has, and the expensive part
(the scene and both loops) is already rendered and measured inside the mobile budget. Its risks are known and fixable:
re-render the 16:9 loop, model a better truck, settle the Tripo terms.
**B is the fallback** if the owner wants it live within days. It is the most distinct from eptosuno and needs no rendering.
C waits on footage we don't have.
