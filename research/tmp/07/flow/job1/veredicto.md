# Flow job1 (Veo 3.1 Fast, 20 credits): verdict

Board: `tmp/07/tablero/flow_job1_ab.jpg`. Numbers: `analisis.txt` (per-frame difference against start/end on a
160×90 gray copy, jump from the previous frame, mean luma) and `analisis.py`.

**Ends.** Frame 0 = start.png (mean difference 3.7 at 1280×720, offset 0 px, scale 1.000: only edges and
compression). Frame 184 = end.png (difference 1.1 on the small gray copy). The last 7 frames (185–191) creep: scale
1.025, −22 px horizontal. To join the cripta loop, cut at frame 184. The guitar at frame 0 and the telephone at 184
are intact.

**Middle.**
- 0–48: instead of pushing into the wardrobe, the camera trucks right past it and invents wall beyond it.
- 56–96: a free-standing rack enters from the right in the foreground, holding a black velvet jacket with gold
  piping and a red one. These are new objects, not the wardrobe's clothes.
- 104–112: a hard white light with a cyan lens flare behind the rack; it exists in neither plate.
- 113–144: the background **behind** the jackets turns into the cripta's arches while the jackets are still in
  frame, so the clothes end up hanging inside the cripta.
- 144–184: the jackets slide out to the left and the cripta settles.

**Does the occluder bridge the cut?** No. Minimum luma is 17.6 (frame 103) and the right edge always shows the
background, so the cloth never fills the frame. The swap is a morph behind a partial occluder: the opposite of family
C, which needs ~5–6 frames of full cover.

**As E6 at 720p + upscale?** No. It works as a reference for camera speed and cloth motion, which look natural, and
as a placeholder. As the final E6 it breaks the brief: new objects, a cold flash in a candlelit space, the
morph in view, and the plan 1 geography lost (no wardrobe door, no stairs). Upscaling does not fix any of that.
Usable only if trimmed to frames 0–184 and as a temporary stand-in.

**H3 route, better:** the occluder comes from a mask (cloth or wardrobe door animated in the maquette, present in the
depth control and in the mask) with ~5–6 frames of full cover and a `maskedmerge` join, so no morph is visible. The
path follows the Blender camera (a real push into the wardrobe and down the stairs). Both ends are pixel-exact with
the plates and the E5 loops, there are no new objects, it runs on the local GPU at no cost, and resolution is ours.
**Worse:** much more setup (animated occluder, depth, H3 seeds, composite), it needs the GPU to itself, and H3 paints
dark occluders as lit stone or uneven smoke (so the cloth must be composited from the mask, not generated). Veo's
cloth sway and camera inertia look more natural than what H3 gives on its own.
