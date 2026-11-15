# Diego: hand and prop fixes on the three Mixamo clips

Spec: `/home/black/projects/mothership/docs/queue/2026-11-14-diego-clip-fixes.md`. It follows `docs/diego-mixamo-skin.md`.
Scripts: `blender/partes/mixskin/`. Numbers: `blender/partes/mixskin/out/fix/*.json`. Corrected blends: `blender/assets/reparto/`
(git-ignored).

**State, 2026-11-14 23:45:**
- Driving is done and passes.
- Sitting_drinking is done and passes, with the owner's hand pose (see "Sitting_drinking: done").
- Guitar_playing waits on the owner's placement. The mothership changed the process at 22:36: the owner places props by
  hand.

## Sitting_drinking: done

**The owner's pose.**
- He posed the hand in `diego_place_drinking.blend`, saved at 23:01; a copy is kept as `diego_place_drinking_owner2301.blend`.
- The pose: an IK control `MANO_ctrl` (on RightForeArm, chain 2, plus Copy Rotation on RightHand), an elbow pole
  `CODO_ctrl`, and the bottle on an empty that rides the hand (`place_ik.py`). No finger keys.
- His control sat 24 mm past the arm's reach, which locks the elbow straight.

**The small fix on top** (`place_nudge.py`, 4 / 14 mm), applied under the mothership's rule:
- MANO_ctrl is pulled back 24 mm toward the shoulder; the hand moves 4 mm and the elbow unlocks from 0.2° to 23.6°.
- The bottle slides 14 mm along its axis, out of the face. At f305 that leaves 0 inside, with the fist at 0.34 mm.

**The sip bake** (`sip_bake.py`):
- His evaluated f305 pose goes into the fix layer: arm 37.8°, forearm 79.4°, hand 99.3°.
- It is eased in over f218–240 and out over f332–350, and matches his pose exactly at f305 (0.0 mm).
- In the eased window the elbow bend ranges 23–86°. The hand moves at most 12.7 mm per frame, against 9.1 in the clip.

**The bottle outside the sip.** His fixed angle in the hand drove the bottle into the thigh (16.7 mm) and the left hand
(23.8 mm) at rest.
- `prop_rest.py` keys the earlier fitted rest angle outside f218–350 and eases to his angle inside.
- The empty rides the hand bone at a constant offset of about 12 cm, not at its head frame; `prop_rest.py` measures that
  offset and applies the rest angle through it.
- `prop_settle.py` (two runs, max-filtered and smoothed slides) clears the remaining face touches at f243–277 and
  f177–179, and pulls the grip into the 0.5–2.5 mm band.

**After** (`out/fix/after_sitting_drinking.json`, every frame f1–457):
- **0 inside on every contact:** hands, forearms, seat and bottle, both ways.
- **Grip:** 0.50–2.44 mm.
- **Floor:** the bottle stays at least 66 mm above it.
- **Mouth:** the bottle's lip touches at the corner of the mouth or the philtrum. It is 56–96 mm from the lip-centre vertex
  over f241–331 (`out/fix/mouth_sitting_drinking.json`).
- **eagle.sh:** crawl 0.09, flicker 0.00, strobe 0, exit 0. Its one event, a jump at f83, is the clip's own sit-down
  (ickdrone's original run had it at f89; the hips move at 6–8 mm per frame).

Paths:
- blend: `blender/assets/reparto/diego_clip_sitting_drinking_sip.blend`;
- render directory: `blender/render/reparto/partes/diego/clips/fix/sitting_drinking_final/`, holding:
  - sheet: `sitting_drinking-contact.jpg`;
  - close-ups: `sitting_drinking-closeups.jpg`;
  - clip: `sitting_drinking_wb.mp4`.

## How it is measured

The tool is `pen_fix.py`, run on every frame.
- **Inside or outside:** a vertex counts as inside when it is behind the nearest face and at least 4 of 6 axis rays agree
  it is enclosed. This is ickdrone's test.
- **Two depths:**
  - pen.py's distance to the nearest face. It saturates near 6 mm, because TRELLIS's inner shells sit about 6 mm under the
    skin.
  - The outer-skin depth: the shortest of 26 rays to its last crossing. The fixes solve on this one.
- **What is tested:**
  - hands and forearms against the body;
  - hands, arms and trunk against every prop;
  - every prop's vertices against the whole body;
  - grips, given as hand:prop pairs: the smallest surface gap, negative when a vertex is inside.

## Before

The original clips with ickdrone's stand-ins: `out/fix/before2_*.json`.

| clip | contact | nearest-face max | outer-skin max | frames > 1 mm |
|---|---|---|---|---|
| sitting_drinking | L hand → body | 7.51 mm (f36) | 12.05 mm (f21) | 181 |
| | R hand → body (into the chin while drinking) | 7.41 mm (f56) | 32.99 mm (f327) | 225 |
| | forearms → body | 5.9 mm | 10.7 mm | 41 / 59 |
| | trunk → old seat | 42.9 mm | 42.9 mm | 398 |
| driving | hands → wheel rim | 11.6 mm | 11.6 mm | 151 (every frame) |
| | wheel → body | 2.8 mm | 28.8 mm | 151 |
| | trunk → old seat | 50.2 mm | 50.2 mm | 151 |
| guitar_playing | R hand → body (the strumming fist into the belly) | 5.93 mm (f168) | 30.78 mm (f35) | 188 |
| | R hand → guitar body | 14.3 mm (f179) | 14.3 mm | 56 |
| | L hand → guitar neck | 11.0 mm (f2) | 11.0 mm | 188 |
| | guitar neck → body | 2.0 mm | 8.2 mm | 35 |

## Body correction layer (`body_fix.py`)

- The clip's action moves to an NLA track. The "fix" action is active with COMBINE.
- It is keyed every frame on `mixamorig:{L,R}Arm`: one push per hand per frame, as a shoulder rotation without twist.
- The push runs along the mean outer normal, by the largest exit distance plus 1.5 mm.
- It is max-filtered over ±4 frames, then Gaussian-smoothed (σ 2), and iterated.

| clip | max correction | inside after |
|---|---|---|
| guitar_playing | R 25.4° | 0 |
| sitting_drinking | L 10.5°, R 18.9° | 0 |
| driving | 0° (nothing was inside) | 0 |

## Driving: done

**Wheel = option C.** This was the mothership's override, for this prop only.
- No rigid wheel follows these fists: the best circle leaves ±7 mm of radial residual.
- So the wheel is static at the least-nudge fit (`props_fit.py`, with a body-clearance term).
- `wheel_fix.py` nudges the fists onto the rim through the same layer: the shoulder takes the push across the arm, and a
  `ForeArm` channel takes the push along it.

After (`out/fix/after_driving.json`, every frame f1–151):
- **0 inside on every contact.** That includes the trunk against the seat and the wheel, and the wheel and seat against
  the body.
- **Grip gaps:** L 1.17–2.03 mm, R 0.92–2.03 mm (none over 3 mm).
- **How far each fist moved:** L 3.5 mm max, R 8.1 mm max. The budget was 7 mm; the mothership accepted 8.1.
- **The wheel:** 2.46 mm off the belly, tilted 27.3°. The stand-in is grey so it reads against the black shirt.
- **eagle.sh** on the Workbench side clip: crawl 0.03, flicker 0.01, strobe 0, exit 0.

Paths:
- blend: `blender/assets/reparto/diego_clip_driving_props.blend`;
- sheet: `blender/render/reparto/partes/diego/clips/fix/driving_props-contact.jpg`;
- close-ups: `.../fix/driving_props-closeups.jpg`;
- clip: `.../fix/driving/driving_wb.mp4`.

## Sitting_drinking: the bottle cannot reach the lips by fitting alone

- **The seat** (`props_fit.py` kind sit, `back=0.25`) is 24.5 × 27.8 cm, top 84.5 mm, with 0 inside in the fit.
  - Its front edge stops 8 mm short of the calves and feet of every frame.
  - It extends 25 cm behind the hips. With the default 2 cm it was only 4.8 cm deep, a rail rather than a seat.
- **The bottle**, Child Of on the right hand:
  - Rigid fits at 0.19, 0.22, 0.25 and 0.28 m all leave the tip about 60 mm from the mouth (vertex 123156). The bottle hits
    the head at f177–179 and f297–305.
  - During the sip hold (f241–331), the fist stays 20 cm from the mouth and 72° below it. The head is tilted back (the mouth
    normal's z is 0.94).
  - No straight fist-to-lips segment clears the head by more than 6.5 mm. The bottle neck's radius is 11 mm.
  - So a pinned bottle cannot reach the lips. The human clip puts the hand at a human's mouth height, which lands under
    Diego's big chin.
- **The mothership picked option A** (an additive arm raise in the fix layer, eased over f216–238 and f332–350).
  - Then, at 22:36, it switched to owner placement first.
  - A stays unapplied until the owner has placed the bottle and still needs it.
  - The search for the smallest raise is `sip_target.py`. It is slow (more than 10 minutes) and was stopped before it
    finished.
- **Placement blend:** `blender/assets/reparto/diego_place_drinking.blend`, with a note beside it.
  - The bottle is parented to the empty `prop_bottle_hand` on `mixamorig:RightHand`, so its `matrix_basis` is the
    hand-space placement.
  - The frame is 305 (the sip apex). Everything else has hide_select, and the 3D view opens through `shot_cam`.
  - Still: `blender/render/reparto/partes/diego/clips/fix/place/drinking_f305.png`.

## Guitar_playing: owner placement

- **The rigid fit** (`props_fit.py` kind guitar, 60 mm body, on `Spine`) cannot hold the fretting fist on the neck. The gap
  runs from −0.7 to 18.9 mm. The fit also held the guitar flat, about 9 cm off the belly.
- **Aiming the neck** at an empty on `LeftHand` (Damped Track, `guitar_track.py`) gave these numbers
  (`out/fix/after_guitar_playing.json`):
  - fists: 0 frames over 1 mm, max 0.68 mm (strum fist on the body) and 0.39 mm (fretting fist on the neck);
  - the guitar against the body: 2.64 mm at f110 and 3.43 mm at f179, with the strumming fist into the neck at 2.21 mm;
  - the fretting gap was over 3 mm on 171 of 188 frames.
  So that version is superseded.
- **Placement blend:** `blender/assets/reparto/diego_place_guitar.blend`, with a note beside it.
  - The guitar body is parented to the empty `prop_guitar_body_hand` on `mixamorig:Spine`, with the neck and soundhole as its
    children. The aim constraint is removed.
  - The frame is 63.
  - Still: `.../fix/place/guitar_f63.png`.

## After the owner saves

For each placement blend:
1. Read the prop's `matrix_basis`.
2. Run `pen_fix.py <blend> -- <out> 1 <grips>`:
   - drinking: `RightHand:prop_bottle`;
   - guitar: `LeftHand:prop_guitar_neck,RightHand:prop_guitar_body`.
3. Make the sheets: `clip_stills.py` with `contact.py`, and `closeup_at.py` with `cusheet.py`.
4. Render the Workbench side clip with `clip_wb.py`, then run `eagle.sh`.
5. For drinking, check the bottle tip against the mouth at the sip. Add the arm raise only if he still needs it.
