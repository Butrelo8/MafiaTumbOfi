# Flow job3 — cripta → atrio (ticket 07, plan 1: the one threshold)

Flow side only; nothing is spent until a drone runs `STEPS.md`. Frames and numbers: `frames_check.txt`.

## Reference

- **Match:** job2 (`veredicto.md`), the only Flow clip with no morph: one shot, an occluder that is already in the
  first frame, "completely black for about half a second", the black clears onto the exact end frame. Family C
  (soft occluder, seanaiux T21: `~/projects/visual-lab/web/designer-fichas/seanaiux/trans-le1-robe-chain.jpg`).
- **Change on purpose:** the occluder is not cloth but the dark stone archway at the right edge of the cripta frame,
  where steps climb out of the light (x 1430–1900, y 880–1080 in start.png); the end is outdoors, warm portal light
  instead of the cold moonbeam; the camera also rises a little (plan 1: climb and go out).

## Why "lateral camera" is not copied literally

Plan 1 says climb and go out. The camera still moves **to the right**, like job2, and that move is what carries the
dark arch (right edge) over the lens, so the lateral lesson holds; it adds a small rise for the steps. A straight push
into the arch was variant B.

## Variants (one generation, so one is sent)

| Variant | Occluder | Verdict |
|---|---|---|
| **A · glide right and rise into the right arch** | the arch and steps already in the frame | **Sent.** Same mechanics as job2 (a dark mass at one edge wipes across the lens); nothing has to appear |
| B · straight push-in to the arch | same arch | Rejected: job1's push-in morphed the next room in behind the cloth; the arch is far from the lens, so a pure push needs a long run to fill it |
| C · the moonbeam blows out to white, then the street | light | Rejected: it is a flash, invents a light and, with Veo, a lens flare; the brief forbids new lights and the end must be dark-on-dark |

## What to expect and check afterwards (scene drone, not the browser drone)

Frame 0 = start.png, last good frame = end.png (cut where it stops matching, job2 cut at 184); coverage with
`../cobertura.py out/cuadros` (job2: 86 % under luma 20, no frame ≥ 90 %); the cripta arrives colder than the plate in
job2, so check the street's warmth; both rooms at the edges in the middle frames. The end frame has no rain: the
prompt is silent on rain on purpose, and the loop's rain comes in with the dissolve into loop frames 0–19.
