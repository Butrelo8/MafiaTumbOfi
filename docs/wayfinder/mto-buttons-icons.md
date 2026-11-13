# Map: mto-buttons-icons (builder: auradrone, auditor: menacedrone)

Run `mto-buttons-icons`, ticket `docs/queue/2026-11-12-mto-buttons-icons-pair.md` (mothership). Branch `cc/auradrone`.
Design doc: `docs/design/DESIGN.md`. Tokens: the `:root` block in `src/pages/index.astro` (no tokens.css yet).
References (gate passed, sections botones, iconos, estados): `docs/design/references.md` › "Buttons and icons pair run".
Dev server: not started yet (ports 3100 and 3119 belong to other trees; this worktree gets its own port, URL goes here) (the site has no database, so there is no scratch DB to protect; it runs from this worktree).

## Ticket
Buttons and icons that read as crafted, not stock. Every button has idle, hover, press, focus, loading and done where a real
event drives them. Icons morph in detail. Direction A Carretera is picked; the working `Boton.astro` and `Icono.astro` are
replaced, keeping their props (`href`, `lleno`, `icono`, `id`; `nombre`, `clase`) so `index.astro` barely changes.
Constraints: no pill unless the owner picks it; one motion language; the owner picks the form from stills before the build;
alexander-oliva.com and eptosuno.com are anti-references.

## What exists today (grepped in the code)
- `Boton.astro` is used 6 times in `index.astro`: header Contratar (l.75), hero Escuchar with the play icon (l.92) and Contratar
  (l.93), three platform buttons (l.113), the WhatsApp button (l.150). All are `<a>`; none is a `<button>`.
- `Icono.astro` knows one glyph, `play`, used in Boton and in the video cards (l.124).
- The one real `<button>` is the loop toggle `#pausa` (l.96), a plain text button; its script is inline (l.159-190). It sets
  `aria-pressed` and also swaps its label, which double-signals; the rebuild uses one or the other, not both.
- The press today is `transform 90ms`, outside the default 40-80 ms band of `motion-spec`. The new press is 80 ms.
- The wipe is 500 ms `cubic-bezier(.65,0,.35,1)`, inside 350-500.

## Three directions (button forms, none a pill)
1. **Tecla**: a square gold cap on a 4 px dark-gold lip, like a dash key; press sinks the cap onto the lip; trailing chevron
   nudges on hover. Sources: todoist two-layer button, nothing.tech chevron.
2. **Boleto**: a stub with half-circle notches on both side edges; press dips and acts on release; done lands a stamp.
   Sources: boleto-perforado (Box Office, Design Lounge ticket).
3. **Marco**: a square 2 px gold outline, uppercase, no fill at rest; the fill wipes up from the bottom (the working
   button, refined: chevron, focus ring inside the box, loading and done). Sources: teenage.engineering outline, rafadesign wipe.

Each is shown to the owner as stills of all six states at 390 and 1440 before the build (`docs/design/botones/`).

## One motion language (all three directions)
```css
--dur-press: 80ms;   --dur-state: 250ms;   --dur-fill: 500ms;   /* inside 40-80, 150-250, 350-500 */
--dur-fill-out: 350ms;
--ease-fill: cubic-bezier(0.65, 0, 0.35, 1);   --ease-out: cubic-bezier(0.16, 1, 0.3, 1);
```
Only `transform` and `opacity` animate. A close is not slower than its open. Under `prefers-reduced-motion` nothing loops,
icons swap without a morph and the first frame after a click equals the settled one.

## Icons and tools
GSAP MorphSVG only (mothership 23:05: keep the 150 KB cap; Rive stays an open lab question for the scene phase, unproven).
| icon | where | morph | tool |
|---|---|---|---|
| play to pause | loop toggle `#pausa` | crafted, inside one 250 ms band: 60 ms anticipation (shrink to .88), the morph through a squeezed intermediate shape, overshoot (`back.out`), settle | GSAP MorphSVG |
| loading ring to pause | loop toggle, when buffering ends | same band | GSAP MorphSVG; the ring's spin is a CSS rotate |
Exception to "transform and opacity only": MorphSVG sets the path's `d` from JS on a 24 px SVG (cheap to paint). `revisar` cannot
see it (checklist: motion done with rAF/JS is judged): R1 carries a frame strip of each morph. Under reduced motion the icon
swaps in one frame with no intermediate shape, and the ring is a static glyph.
Glyph rule: the play glyph means "this plays media" (Escuchar, video cards, the toggle). Off-site arrows are dropped; the trailing
chevron belongs to the button form, not to the icon set. Brand marks (Spotify, Apple Music, YouTube) are never morphed or restyled.

## Plan
Files: `src/components/Boton.astro` (the picked form), `src/components/Icono.astro` (glyph set plus morph pairs),
`src/scripts/iconos.ts` (MorphSVG), `src/lib/estadoBoton.ts` plus its test (the pure part: which state a
button is in from events), the toggle script moved out of the inline block, `docs/design/botones/index.html` (stills for the
owner, not shipped), DESIGN.md Components and States matrix rows, `package.json` (gsap).
Entry points reused: Boton, Icono and the `#pausa` toggle; no second entry point.

States per component (domain = real event that drives it):
| component | idle | hover | press | focus-visible | loading | done |
|---|---|---|---|---|---|---|
| Boton (link, in page) | yes | yes | yes | yes | n/a: an anchor jump is instant | n/a: no result to confirm |
| Boton (link, off-site: Escuchar, platforms, WhatsApp) | yes | yes | yes | yes | n/a: nothing loads on this page, and on iPhone the native app opens with this page still alive, so a busy state would stick | n/a: leaving the page is not a success to print |
| Loop toggle | yes | yes | yes | yes | while the video is buffering (`waiting`), real; the label becomes "Cargando video" (no `aria-busy`: the label carries it) | playing (`playing`), icon and label change |
| Error (toggle) | `play()` rejected (iOS Low Power Mode): `pausado = true`, repaint to "Reproducir video". The video's `error` event (source fails): the toggle hides and the poster stays. Both in `estadoBoton.ts` tests |
| Empty / disabled | n/a: static links with fixed labels; the toggle is hidden until JS runs |

## Copy deck (Spanish, nothing new on the page except the toggle's loading label)
Escuchar, Contratar, Escribir por WhatsApp, Spotify, Apple Music, YouTube, "Pausar video", "Reproducir video", and new:
"Cargando video" (toggle while buffering; `aria-busy`, no visible spinner text beyond the icon). Off-site links show no pending state.

## Checks planned (before each round, 390 and 1440, `--theme light` and `--theme dark` both run and both contrast rows recorded, each state via `--state`)
`revisar.sh` web with `--motion 40-80,150-250,350-500` and `--reduce`; `slop-check.py src`; `refs-check.py`; `check-matrix.py`;
`tokens.mjs` and `conform.mjs`; bun test; Mac WebKit pass at iPhone size before the owner looks.

## Gate answer (menacedrone, 2026-11-12 23:05) and how each fix is resolved
1. Scene twin: every form is shown both ways in the stills (DOM states and a mock of its in-scene object: Tecla a dash key,
   Boleto a decal on the windshield, Marco a plate frame with an emissive fill). DESIGN.md gets "Scene version needs": the DOM
   twin stays a focusable `a` or `button` with the same accessible name, kept in sync with the prop; DOM focus mirrored onto
   the prop as a ring or glow; projected hit area at least 44 px at 390; each state maps to a clip or a material parameter;
   reduced-motion parity. Scope stays buttons and icons.
2. Rive dropped from the build (table above).
3. Boleto: the stamp is 250 ms (inside 150-250). It has no done on links, so it lands only on the loop toggle, when the video
   starts playing after the user pressed "Reproducir video" (a user-driven play, not every buffer). The notches are cut from
   the inner stub with `mask`; the focus ring is an outline on the unmasked wrapper, so it is not clipped and no notch is
   filled with `--bg` over the hero video.
4. Reduced motion: the loading ring is a static glyph; "Cargando video" is a visible label change; `aria-busy` dropped.
5. Hover, the chevron nudge and the icon lean sit under `@media (hover: hover)`.
6. Error state fixed as in the states table; staging for the `--state` shots: the loop route aborted (real source failure),
   `HTMLMediaElement.prototype.play` overridden to reject (init script), and the loop route held open (waiting).
7. Copy: Escuchar becomes "Escuchar en Spotify" (play glyph kept, destination named; `catalog.json` release 0 is a Spotify
   link). The platform buttons get no brand marks. Stills decide whether they drop to chevron text links.
8. Stills show lleno and plain per form, the platform buttons as boxes and as text links, and the toggle in each form. Tecla
   gets a plain variant that is not a gold cap (accent share: two gold caps in the hero otherwise).
Also: `slop-check` REVIEW `js-intersection-reveal` at `index.astro:168` is the loop's play/pause observer, not a reveal.
Light and dark: the page has one dark theme, so the light/dark item is recorded n/a (single theme), not PASS. The wipe back
down is 350 ms (token `--dur-fill-out`), faster than the 500 ms in. The rafadesign `aria-pressed` half is not borrowed.
Authored, not from a ficha: the 4 px chevron nudge, the 250 ms icon reaction, Boleto's half-circle notches, the translateY press.

## Rounds
(gate answer, R1, R2, R3 table go below)
