# Flow job4 — sacristía → camarín (ticket 07, plan 1: push into the painting that opens like a door)

Flow side only; nothing is spent until a drone runs `STEPS.md`. Frames and numbers: `frames_check.txt`.

## Reference

- **Match:** `jessejames 015` (`/mnt/e/ComfyUI/references/the-assassination-of-jesse-james-by-the-coward-robert-ford/015.jpg`),
  a door opening from a black surround onto a lit room, the one the plan names; and job2's mechanics: one shot, black
  for about half a second, the black clears onto the exact end frame.
- **Change on purpose:** the door is the framed painting over the turntable, its canvas is nearly black already (so
  it is a natural occluder), and the room behind is the warm candlelit dressing room.

## Why the camera is not lateral here

Plan 1 asks to **push into the picture**; a sideways move cannot put a painting hanging on the far wall on the lens
without the painting moving by itself. So the camera glides forward and a little up (a dolly, "without any zoom": job1
failed on its occluder, not on the push). Job2's other lessons are kept literally: forced black for about half a
second, no new objects, lights, lens flare, cyan, people or text. Added: "the painted figure does not move" (the
canvas has a faint figure Veo could animate).

## Variants (one generation, so one is sent)

| Variant | Occluder | Verdict |
|---|---|---|
| **A · dolly toward the painting; the canvas fills the frame and swings open** | the painting already in frame | **Sent.** The user's plan, and a near-black occluder that fills the lens by the camera's own move |
| B · lateral glide, the painting swings open toward the lens (job2 style) | the painting, moving by itself | Rejected for the same reason as job1's variant B: it hangs too far to reach the lens, so the painting would have to fly at the camera |
| C · the wall lamp blooms to white, then the dressing room | light | Rejected: a flash is a new light and a lens flare, and the end must stay dark-on-dark |

## Risks to check afterwards (scene drone)

Frame 0 = start.png (it is a loop frame, so the disc and lamp phase are frame 0's), last good frame = end.png (job2 cut
at 184). The push could morph the dresser into the mirror's dresser instead of passing through black: look at the
frames where the canvas covers 70–100 % with `../cobertura.py out/cuadros` (job2: 86 % under luma 20, never 90 %).
The sacristía's neon at the right edge is the likeliest thing to be invented into the camarín as a light.
