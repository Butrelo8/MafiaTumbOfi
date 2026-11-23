---
title: MTO scene site, the truck that never parks
kind: site
status: open
project: mto
---

# MTO scene site, the truck that never parks

## Destination

The six-scene site (1 Cabina, 2 Caja, 3 Pantalla, 4 Costado, 5 Gira, 6 Placa) is live on `main`, which is production.
Production auto-deploys on push. The site has to meet plan v2 (`docs/design/escenas-plan.md`):
- The truck drives the whole time, and scroll is the ride.
- Every in-scene control has a DOM twin.
- Desktop and phone each get the delivery the owner picked.
- The site keeps the **page-first rule** below.

The map is reached when every scene's props work on desktop and on a phone, the licences are clear, and LCP on a
phone-like run passes ticket 01's measurement.

## Notes

**Sources.** Read these first:
- Vision and owner picks: `~/projects/mothership/docs/queue/2026-11-12-mto-scene-site-vision.md`.
- Plan v2, with the scene table, props, phone and weight budgets: `docs/design/escenas-plan.md`.
- The older brief: `docs/brief-camion.md`.
- The lane rules for Blender work: `docs/lanes.md`.
- Handoffs: `docs/handoffs/`.

**Owner rule, page first (owner, 2026-11-23 06:16).** This rule applies to every ticket in this map.

The problem today: the live apertura intro covers the page for about 13 s, a 10 s video plus the 2.4 s minimum. The
field LCP p75 on phones is 22 s.

From now on:
- **Content shows first.** The h1, the nav and the section text are readable and scrollable at first paint.
- **The intro is a header or background.** It plays there and never blocks reading or scrolling. No overlay, and no
  `inert` nav while it plays.
- **Heavy assets load after first paint.** three.js, the GLBs and every video load only after it.
- **Keep the look.** The rule changes the order things load in, not how they look.
- **Measure LCP before and after** with the same run, as ticket 01 describes.

**Done so far.** Each item below is on `main`; each hash was checked with `git merge-base --is-ancestor <hash> main`.
- Plan v2 and the storyboard: `docs/design/escenas-plan.md`, `docs/design/escenas/storyboard/`.
- The Tripo v5 cast in the scenes, with the prototype route and loop re-rendered (`public/prototipo/ruta.mp4`,
  `bucle.mp4`): da918f3. Results are in `docs/tripo-v5-escenas.md`.
- The home `/` is now the live three.js scene, with six stop cameras that the section buttons move between, the screen
  truck playing a video, and the cast idling. The opening is the "MTO" writing plus the apertura clip (12 s, d92fb8a),
  which is still the grey Workbench previz. The old video home is at `/anterior-home/`. Handoff:
  `docs/handoffs/2026-11-19-home-live.md`.
- Cab cleanup and lights as objects (d913030); the Tripo console and roof console (2f0c202).
- The new G63 replaces the 6×6, with its roof rack, load and net: b4331ab, a43f397, ca217c9.
- Wheels and rack load after the first frame, and Draco is applied (e9b4dd0).
- Hand IK controls (232e8c1).
- The new roof load is rebuilt (baa51ac, 9715ea7).
- Site events `/e`: visits, clicks and source go to Analytics Engine `mto_events` (77a9248, c8a0062, 5ddebf6).
- The MTO gotchas were copied from visual-lab (9a8ce11). `cc/goblindrone` 4a7b5e9 is the same patch (`git cherry`
  marks it `-`), so it is not separate work.

**Not merged.** Three drone tips sit on `cc/` branches, all based on 9715ea7. Each one is a ticket below:

| Branch | Tip | Includes | Ticket | Handoff |
|---|---|---|---|---|
| `cc/deaddrone` (seated cast, seats lowered) | 27afeee | `cc/atedrone` 4457d2d, `cc/laggingdrone` 58dc35d | 04 | `docs/handoffs/2026-11-20-sentados-3.md` |
| `cc/youdrone` (roof net settled by physics) | ce1510d | `cc/copingdrone` 7b0db15 | 05 | `docs/handoffs/2026-11-20-red-fisica-youdrone.md` |
| `cc/clowndrone` (Héctor's D cap decals) | 18db209 | — | 06 | `docs/handoffs/2026-11-20-gorra-d.md` |

Read a branch's handoff with `git show <branch>:<path>`. Merge is the close (wayfinder standard §3.3).

**Stale doc, not fixed here.** The repo `CLAUDE.md` still says `src/` is a placeholder on `fresh-start`. The live home on
`main` is the scene.

## Decisions so far

- [Page first on the live site, the intro never blocks reading](tickets/01-pagina-primero.md): The h1 and the nav are readable and usable from the first paint (h1 readable 17.5 s → 0.2 s on a throttled phone); the intro is a background layer and the heavy files load after first paint.
- [The manager's head and the steering wheel after the seats were lowered](tickets/02-volante-manager.md): owner #69: raise the front seats less (0.15 m instead of 0.20)
- [The owner saves the seated placement file](tickets/03-colocacion-sentados.md): owner #70: the owner places the cast and saves the file
- [Licences for the manager's figure and the Tripo terms](tickets/07-licencias.md): owner #71: keep the risk until go-live; owner accepts it for production

## Not yet specified

- The sticker art itself (our own illustration plus each platform's unaltered glyph, plan v2 §2). It is graduated when
  ticket 12 starts.
- The bed props' final list. Plan v2 keeps them as stand-ins the owner may swap.
- The v3 transition re-render with all four in the cab (plan v2 §0 item 4, "later, not now").

## Out of scope

- The tour-dates watcher that reads Instagram and writes `public/data/fechas.json`. It is a separate job (plan v2 §5).
  This map only reads the file.
- The fan list (`docs/lista-de-fans.md`), parked by the owner.
- The press kit and the glovebox PRENSA scene, cut in plan v2 §1. The glovebox survives as an easter egg in ticket 11.
