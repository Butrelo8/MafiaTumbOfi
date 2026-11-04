# Eagle review: /mnt/e/Cursor Projects/MTO/tmp/07/fasth3/clips/oner_l2g_s31.mkv

Mode motion, 209 frames 1920x1080; brief: Ticket 07 cripta→atrio one-take, 209 native frames: A (crypt→stairs, f0–101, repaired) + B anchored on A f102–106 (f102–208). Known: odd/even speed judder in B f105–180 (7↔11, 12↔18 px/f); gate passage f118–128.; 8 events + 6 spread frames.

## Findings

| # | severity | confidence | category | frames | box | fix |
| --- | --- | --- | --- | --- | --- | --- |
| 3 | major | medium | boiling | f75-83 | 0 858 255 200 | Segment A (unchanged from the repaired A shown nowhere yet): the phone dial and the stone mottling re-render frame to frame (also f21-30 on the window-arch stones). The user's earlier 'stones keep moving / phone wobbling' complaint; render-time only. |
| 1 | major | high | timing | f105-180 | frame | Odd/even speed judder in segment B (per-frame median DIS 7/11, 12/18 px/f): render-time only; mid-motion start of B causes it, the 5-frame AddGuide anchor weakened it but did not remove it. Next lever: longer anchor (22 frames). |
| 2 | minor | medium | morph | f127-131 | 621 0 1000 330 | Passing under the top arch: the dark ceiling is low-detail blobs that reshape frame to frame and its lower edge peels open onto the church facade instead of sliding with parallax. Same family as the accepted take's gate passage (revisar morph FAIL on every one-take so far). |

## Checked

| category | result | confidence | density |
| --- | --- | --- | --- |
| anatomy | none | high | 8 events (strips + 3 crops) + 6 spread frames; no std/rgb |
| materials | none | low | 8 events (strips + 3 crops) + 6 spread frames; no std/rgb |
| text | none | high | 8 events (strips + 3 crops) + 6 spread frames; no std/rgb |
| geometry | none | medium | 8 events (strips + 3 crops) + 6 spread frames; no std/rgb |
| physics | none | medium | 8 events (strips + 3 crops) + 6 spread frames; no std/rgb |
| lighting | none | medium | 8 events (strips + 3 crops) + 6 spread frames; no std/rgb |
| compositing | none | low | 8 events (strips + 3 crops) + 6 spread frames; no std/rgb |
| period-brand | none | medium | 8 events (strips + 3 crops) + 6 spread frames; no std/rgb |
| morph | findings | medium | 8 events (strips + 3 crops) + 6 spread frames; no std/rgb |
| flicker | none | medium | 8 events (strips + 3 crops) + 6 spread frames; no std/rgb |
| strobe | none | high | 8 events (strips + 3 crops) + 6 spread frames; no std/rgb |
| boiling | findings | medium | 8 events (strips + 3 crops) + 6 spread frames; no std/rgb |
| popping | none | medium | 8 events (strips + 3 crops) + 6 spread frames; no std/rgb |
| rigid-bend | none | low | 8 events (strips + 3 crops) + 6 spread frames; no std/rgb |
| permanence | none | medium | 8 events (strips + 3 crops) + 6 spread frames; no std/rgb |
| timing | findings | high | 8 events (strips + 3 crops) + 6 spread frames; no std/rgb |
| seam | none | high | 8 events (strips + 3 crops) + 6 spread frames; no std/rgb |
