# Handoff: truck-bed load redo (caja4), 2026-11-14 16:12, cookingdrone on `cc/nerddrone`

Spec (read first): `/home/black/projects/mothership/docs/queue/2026-11-14-mto-truck-bed-props-redo.md`. The report goes to
`/home/black/.cache/cc-deck/reports/all/cookingdrone-1794691006.md`, then SendMessage `mothership-10` one line (rules at the
end of the spec brief: verdict line, "model: opus effort: high" before it, `paths:` line, never send to a suggested name).
Nothing is committed yet. Commit on this branch only, after the renders are in.

## Decisions (made, with reasons)
- **Everything is modelled procedurally in Blender.** That is the route props pass 2 used, so 0 Tripo credits and no TRELLIS.
  The props are simple shapes.
- **Two arrangements, the same 110 kg of gear in each.** The gear: an amp in an ATA road case, the bass, 12-string (docerola),
  requinto and 61-key hard cases, a snare case, a milk crate of cables, a full cooler, moving blankets, and the donut (kept).
  - **A:** the four cases stand on edge in a file along the left wall. The amp sits in the right front corner and the cooler
    behind it. Four ratchet straps hold the load, two of them over the amp.
  - **B:** the amp and cooler sit against the cab. The cases lie flat, three high on the left, with the keyboard case on edge.
    The crate, snare case and blankets go behind the cooler. One cargo net covers everything.
- **The tie-downs are assumed: 6 wall rings** (4 corners and a mid pair, `ANCLAS_Y`). The truck model has none. A and B use the
  same rings.
- **Removed: piñata, balloons, papel picado, flag.** They hang loose and would not survive the drive. This is stated on the page
  as an owner question.
- **Spare tire and gas can are left out.** A 37" tire would take half of the 1.05 × 1.76 m bed. The can is heavy, so it would
  have to sit against the cab, where the amp is.
- **Recommendation: B.**
  - Both pass the checker and both put the cg at y −1.82, between the rear axles at −1.08 and −2.11.
  - The net holds everything, while A leaves its folded blankets loose below the rail.
  - B has 6 items over the rails against A's 8, and its top is 0.64 m against A's 0.66 m.
  - The tradeoff: A reads more as band gear from the scene-2 camera.
  - The scene stills are dressed with B (`CAMA4` default "b").
- **Owner scene picks applied.** 3B is `esc3-hombro`. 4B is `ESC4_LUZ = "cabina"`, now the default in
  `blender/utileria.py:1343`. Both are recorded in DESIGN.md › Components and in the camera table of `escenas-plan.md`.

## Done (uncommitted; `git status`)
- `blender/caja4.py` (new) does four things:
  - it measures the bed (CAJA4 lines) and probes the axles (`CAJA4 eje`);
  - it builds the props, straps and net (laid by ray casts) and runs the checks (`revisar_carga` → `CAJA4 CHECK … PASS`);
  - it defines the options `caja4-{a,b}`, `caja4-{a,b}-esc2`, `caja4-{a,b}-esc4`, and the scene re-dress
    `esc2-abre4, esc2-fin4, esc3-hombro4, esc3-fin4, esc4-cabina4, esc4-fin4, esc5-fin4`.
  - The 16 spp previews passed: A 11 props, 110 kg, 8 over the rails, top 0.66 m; B 10 props, 110 kg, 6 over, top 0.64 m.
- `docs/design/references.md` has the new section "Bed load, real-life pass" (id `caja4`). `refs-check` PASS.
- `docs/design/escenas/utileria/index.html`:
  - a new first section `s-caja4` (A/B close-up, scene 2 and scene 4, with notes on why each item sits where it does);
  - scenes 3 and 4 now show only B;
  - the caja3 section is retitled as history.
  - **The jpgs it points to do not exist yet** (`caja4-*.jpg`). The re-dressed scene stills will overwrite the old `esc*` jpgs.
- `docs/design/DESIGN.md`, `docs/design/escenas-plan.md`, and the caja4 section in `docs/design/escenas/handoff-ronda2-resto.md`.
- The first frames and the props list went to the user: `tmp/caja4/preview-16spp.jpg`, `tmp/caja4/lista-props.md`.

## Exact next step
Steps 1-5 were done at 17:10 by the ldrone session, and committed.
- The 18 finals are published to `docs/design/escenas/utileria/` by `tmp/caja4/publicar.py`, at q88 full and q70 `-mini`
  (the convention of `tmp/jpg.py` / `tmp/mini.py`). At q85 the page weighed 3.18 MB at 390 and failed the 3 MB budget.
- The page numbers match `h.log`: A has 8 items over the rails and tops out at 0.66 m; B has 6 and tops out at 0.64 m.
  The cg is at y -1.82 for A and -1.81 for B.
- Checks:
  - `revisar.sh`, image mode: 20 stills, 0 FAIL, banding <= 0.8 %.
  - `slop-check`: exit 0.
  - `revisar.sh` web: exit 0, 2.89 MB at 390.
- `esc5-abre` and `esc6-*` were not re-rendered: the bed is not in frame.
- `esc3-espejo*` and `esc4-relleno*` are no longer linked from the page. They are left in place.

Next: wait for the owner's A/B pick. If it is A, re-render with `WSLENV=CAMA4 CAMA4=a`, then re-run `publicar.py` and the
checks.

## Open questions (the owner's, on the page)
- Bed A or B.
- Should the piñata, balloons or flag come back, for example as a scene-only touch?
- If the owner picks A, re-render the scene options with `WSLENV=CAMA4 CAMA4=a`.

## Gotchas (route to visual-lab as `gotchas:` lines in the report)
- Placing props from their nominal sizes collided by 2-4 cm, because ball corners, handles and latches stand proud. What worked:
  snap each prop by its measured world bounding box and chain each one's front face to the back face of the one ahead
  (`poner`/`atras`/`der` in `caja4.py`).
- A rotated object's AABB (from its rotated `bound_box`) overstates its footprint. A z-rotated donut failed the "inside the
  tailgate" check. What worked: keep round props unrotated about z.
- A taut strap over a load is the upper convex hull of the load's top profile from one anchor to the other (ray-cast down per
  2 cm). A cargo net is a max filter plus a blur of the height field, clamped to the rails at the edge.
- `caja3.py` uses `F = False` as "no parent". Reusing `F` for the floor height broke every builder (`Object.parent expected an
  Object, not float`). Use another name (`PZ`).
- Forum photos (TalkBass, DrumForum, Maverick, MusicPlayer) return 403 or a paywall to fetches, and Flickr's static URLs
  return 429. What worked: Openverse's API (`api.openverse.org/v1/images/?q=…`) with `/v1/images/<id>/thumb/`.
- `blender.exe` is Windows: a WSL env var reaches it only through `WSLENV`.
- `wslpath -w tmp/x` on a relative path that does not exist yet gives `\tmp\x`, so Windows Blender saved the renders to
  `C:\tmp\x`. What worked: pass an absolute WSL path (`$PWD/tmp/x`), or create the folder first.
- The GPU is shared with rizzdrone (colddrone). The 16 spp previews ran while it showed 40-60 % use; the finals wait for a
  quiet GPU.

## Suggested skills
`blender` (only if motion is added), `eagle-eye` (not needed: stills only).
