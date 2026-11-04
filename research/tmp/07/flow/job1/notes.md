# Flow job1 — camarín → cripta (ticket 07, plan 1)

A/B test: Google Flow (Veo, frames to video) against the local H3 transition (method of ticket 17). This is the Flow side.

## Frames

- `start.png` = `tmp/07/e3/out/e3_vestidor_silla_s11_00001_.png` (approved camarín plate, guitar on the chair)
- `end.png` = `tmp/07/e3/out/e3_cripta_s22_00001_.png` (approved cripta plate)
- The plates are 1696×944 (1.797:1), not exactly 16:9. Both go through the same transform, with no other change:
  scale to 1080 px high with lanczos (1940×1080), then crop 10 px from each side to 1920×1080 (0.5 % of the width).
  The H3 side of the A/B must use the same transform so the two clips compare pixel for pixel:

  ```bash
  ffmpeg -i PLATE.png -vf "scale=-2:1080:flags=lanczos,crop=1920:1080" -pix_fmt rgb24 OUT.png
  ```

## Reference

- **Match:** seanaiux T21, the Leonardo pull-back that joins clips under a robe filling the whole frame
  (`~/projects/visual-lab/web/designer-fichas/seanaiux/trans-le1-robe-chain.jpg`; family C, "soft occluder": the join
  falls where the occluder fills the frame for ~5–6 frames).
- **Change on purpose:** a push forward instead of a pull-back; the cloth is the dark stage clothing already hanging in
  the camarín's wardrobe (plan 1 names the wardrobe as the occluder); candlelit v5 look, arriving under the crypt's cold
  moonbeam.

## Prompt variants (one generation only, so one is sent)

| Variant | Occluder | Verdict |
|---|---|---|
| **A · push into the wardrobe, jackets across the lens** | stage jackets already in the plate | **Sent.** The camera's own move makes the cloth cross the lens, so nothing has to move by itself, and the object is already in frame |
| B · locked camera, the wardrobe door swings shut | the open right-hand door | Rejected: the door stands ~3 m from the camera; it can only fill the lens if it moves toward the camera on its own |
| C · copal smoke plume rises across the lens | smoke | Rejected: no smoke source in the camarín plate, so it would be a new object |

## Budget

The user has 90 credits: one generation at Fast, no retries without asking the user. Steps: `STEPS.md`.
