# Map: mto-buttons-icons (builder: auradrone, auditor: menacedrone)

Run `mto-buttons-icons`, ticket `docs/queue/2026-11-12-mto-buttons-icons-pair.md` (mothership). Branch `cc/auradrone`.
Design doc: `docs/design/DESIGN.md`. Tokens: the `:root` block in `src/pages/index.astro` (no tokens.css yet).
References (gate passed, sections botones, iconos, estados): `docs/design/references.md` › "Buttons and icons pair run".
Dev server: not started yet (the site has no database, so there is no scratch DB to protect; it runs from this worktree).

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
   Sources: boleto-perforado (Box Office, Design Lounge ticket). The band sells tickets-to-a-show feelings; the form says "contratación".
3. **Marco**: a square 2 px gold outline, uppercase, no fill at rest; the fill wipes up from the bottom (the working
   button, refined: chevron, focus ring inside the box, loading and done). Sources: teenage.engineering outline, rafadesign wipe.

Each is shown to the owner as stills of all six states at 390 and 1440 before the build (`docs/design/botones/`).

## One motion language (all three directions)
```css
--dur-press: 80ms;   --dur-state: 250ms;   --dur-fill: 500ms;   /* inside 40-80, 150-250, 350-500 */
--ease-fill: cubic-bezier(0.65, 0, 0.35, 1);   --ease-out: cubic-bezier(0.16, 1, 0.3, 1);
```
Only `transform` and `opacity` animate. A close is not slower than its open. Under `prefers-reduced-motion` nothing loops,
icons swap without a morph and the first frame after a click equals the settled one.

## Icons and tools
| icon | where | morph | tool |
|---|---|---|---|
| play to pause | loop toggle `#pausa` | A to B, 250 ms, with the label | GSAP MorphSVG |
| play to equalizer bars | Escuchar while the link is pending | A to B | GSAP MorphSVG |
| arrow to check | none on links (no fake done); kept for the toggle's done | A to B | GSAP MorphSVG |
| loading ring, pause, play (4 states, interruptible) | loop toggle | detailed | Rive state machine, lazy, weight-gated |
Rule: if the Rive runtime plus file adds more than 150 KB at 390 over the 1.55 MB baseline, or the WebKit pass fails, every icon
goes to GSAP and the report says so. GSAP and MorphSVG come from npm, self-hosted, loaded only on pages that need them.

## Plan
Files: `src/components/Boton.astro` (the picked form), `src/components/Icono.astro` (glyph set plus morph pairs),
`src/scripts/iconos.ts` (MorphSVG and the Rive hook), `src/lib/estadoBoton.ts` plus its test (the pure part: which state a
button is in from events), the toggle script moved out of the inline block, `docs/design/botones/index.html` (stills for the
owner, not shipped), DESIGN.md Components and States matrix rows, `package.json` (gsap, `@rive-app/canvas-lite` if the gate
holds).
Entry points reused: Boton, Icono and the `#pausa` toggle; no second entry point.

States per component (domain = real event that drives it):
| component | idle | hover | press | focus-visible | loading | done |
|---|---|---|---|---|---|---|
| Boton (link, in page) | yes | yes | yes | yes | n/a: an anchor jump is instant | n/a: no result to confirm |
| Boton (link, off-site: Escuchar, platforms, WhatsApp) | yes | yes | yes | yes | after press, until the page hides; icon morphs, `aria-busy`; reset on `pageshow` | n/a: leaving the page is not a success to print |
| Loop toggle | yes | yes | yes | yes | while the video is buffering (`waiting`), real | playing (`playing`), icon and label change |
| Empty / error / disabled | n/a: static links with fixed labels; the toggle is hidden until JS runs and `play()` rejection leaves it on "Reproducir video" |

## Copy deck (Spanish, nothing new on the page except the toggle's loading label)
Escuchar, Contratar, Escribir por WhatsApp, Spotify, Apple Music, YouTube, "Pausar video", "Reproducir video", and new:
"Cargando video" (toggle while buffering; `aria-busy`, no visible spinner text beyond the icon). Off-site pending state keeps
the label (no width change, so no layout shift); the icon and `aria-busy` carry it.

## Checks planned (before each round, 390 and 1440, light/dark n/a: the site is dark only)
`revisar.sh` web with `--motion 40-80,150-250,350-500` and `--reduce`; `slop-check.py src`; `refs-check.py`; `check-matrix.py`;
`tokens.mjs` and `conform.mjs`; bun test; Mac WebKit pass at iPhone size before the owner looks.

## Rounds
(gate answer, R1, R2, R3 table go below)
