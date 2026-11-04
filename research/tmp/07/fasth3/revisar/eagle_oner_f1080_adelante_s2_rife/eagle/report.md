# Eagle review: clips/oner_f1080_adelante_s2_rife.mkv

Mode motion, 213 frames 1920x1080; brief: none; 7 events + 6 spread frames.

## Findings

| # | severity | confidence | category | frames | box | fix |
| --- | --- | --- | --- | --- | --- | --- |
| 2 | major | medium | rigid-bend | f8-90 | 790 600 100 70 | the phone's coiled cord (f0) becomes a straight metal rod by f42 and stays one; hero prop; paste the plate's phone (paste-rigid-prop v1) or fix with the first-part re-render |
| 1 | major | high | materials | f16-134 | frame | detail collapses through the first part: f0-4 granular stone, altar grain and dial; by f42 the crypt stone is painted flat blocks with drawn mortar, the dial a blob; f52-120 crypt and stairwell stone read as stamped blotches; back to plate-level by ~f140 (SUV f166 clean). detalle_curva (native, x cripta plate): f0 0.98, f15 0.56, f24 0.33, f40-49 0.13; x atrio plate trough 0.60 at native f50-59, ~1.0 from f70. Fix: give the first part its own native render (two halves) or blend the cripta plate over the first frames |

## Checked

| category | result | confidence | density |
| --- | --- | --- | --- |
| anatomy | none | high | 7 events + 6 frames (no people) |
| materials | findings | high | 7 events + 6 frames |
| text | none | high | 7 events + 6 frames |
| geometry | none | medium | 7 events + 6 frames |
| lighting | none | medium | 7 events + 6 frames; the warm stairwell glow is the portal's own light |
| compositing | none | medium | 7 events + 6 frames; the portal seen through the arch (f119) is a camera move, not a dissolve |
| period-brand | none | medium | 7 events + 6 frames |
| morph | none | medium | 7 events + 6 frames |
| flicker | none | medium | 7 events + 6 frames |
| popping | none | medium | 7 events + 6 frames |
| rigid-bend | findings | medium | 7 events + 6 frames |
| permanence | none | medium | 7 events + 6 frames |
| timing | none | medium | 7 events + 6 frames; end settles, jump <= 0.9 native f96-106 |
| seam | none | high | not a loop: n/a |
