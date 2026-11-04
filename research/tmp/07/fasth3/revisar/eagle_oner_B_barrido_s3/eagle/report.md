# Eagle review: clips/oner_B_barrido_s3.mkv

Mode motion, 107 frames 1920x1080; brief: One continuous camera move, no blackout: vaulted crypt (altar, golden phone, moonbeam) -> stone archway/steps -> out to the rainy street -> rests on the church portal, iron gate and SUV framing. Judge: morph through the doorway, new objects/lights/people, rigid-bend of the SUV/gate/phone, popping.; 2 events + 6 spread frames.

## Findings

| # | severity | confidence | category | frames | box | fix |
| --- | --- | --- | --- | --- | --- | --- |
| 1 | major | medium | popping | f58-63 | 1108 590 332 288 | the iron gate right of the portal fades in over the stone in place (faint f58-59, solid by f62; seen on a full-rate crop in eagle/scratch/reja.png), no parallax entry; dark and mid-move, may hide at speed: judge at 24 fps, or keep the plate's gate from ~f56 in the splice |
| 2 | minor | low | compositing | f44-56 | frame | a blue lit barred window on the church wall top-left during the arrival (f44-56) is not in the end framing; leaves frame by f57, reads as off-screen wall; accept by eye |

## Checked

| category | result | confidence | density |
| --- | --- | --- | --- |
| anatomy | none | high | 2 events + 6 frames (no people; full-rate strip f24-87) |
| materials | none | medium | 2 events + 6 frames |
| text | none | high | 2 events + 6 frames |
| geometry | none | medium | 2 events + 6 frames |
| lighting | none | medium | 2 events + 6 frames; the warm streaks f38-44 are the prompted whip, no new lamps |
| compositing | findings | low | 2 events + 6 frames |
| period-brand | none | medium | 2 events + 6 frames |
| morph | none | medium | 2 events + 6 frames + full-rate arrival f44-67; revisar morph 0 |
| flicker | none | medium | 2 events + 6 frames |
| popping | findings | medium | 2 events + 6 frames + full-rate gate crop f56-67 |
| rigid-bend | none | medium | 2 events + 6 frames (phone f24-32, SUV f56-67) |
| permanence | none | medium | 2 events + 6 frames |
| timing | none | medium | 2 events + 6 frames; jump rises and falls smoothly through the whip f14-47 |
| seam | none | high | not a loop: n/a |
