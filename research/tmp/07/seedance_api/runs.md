# Seedance API test 1: 2.0 mini on the two worst MTO pairs + cripta loop probe (2026-10-18)

Seed: `mothership/docs/queue/2026-10-18-seedance-api-test.md`, plus the mothership's addition (Phase 0 items 3–4 of
`mothership/docs/queue/2026-10-16-paid-flf-test.md`). Submit script:
`/home/black/projects/visual-lab/comfyui/skills/seedance/submit.py` (`--dry-run` first; `--only <name>` runs one).
Status: failed. All three ran on 2026-10-18 01:43 for $1.143 (108,900 tokens each, 121 frames). A and B **ignored the last
frame**: each ends on a new scene drawn from the LAND text, not the plate. The loop keeps its geometry, but the light
drifts +3 luma levels and does not close. Evidence: `medir_api.txt`, `revisar/{A,B,L}/table.tsv`, `ver/last_vs_plate.jpg`,
`ver/L_seam_f0_f120.jpg`; results table at the end of this file.

**Parameters (same for all three; in the body, never in the text):** `dreamina-seedance-2-0-mini-260615`, 720p
(1280×720), 5 s, `ratio: adaptive` (forced for first+last frame), `generate_audio: false`, `watermark: false`,
`return_last_frame: true`, strict `first_frame` / `last_frame` roles, no reference images (playbook R1–R3).
Cost per run from `clipcost.py`: 108,000 tokens × $3.5/M = **$0.378**; three runs **$1.134** (cap in the script: $1.20).

## References: what each run matches and what it changes on purpose

- **Ends:** the same plates the local FastH3 takes and the RunPod session used: camarín = `fasth3/in/start.png`,
  cripta = `fasth3/in/start_cripta.png` (= `end_nuevo.png` = `look/maestros/cripta_esc.mkv` f0, PSNR inf),
  atrio = `fasth3/in/end_atrio.png` (= `atrio_esc` f0). They are scaled 1920×1080 → 1280×720 (ffmpeg `flags=area`) into
  this folder, because the 2.0 FAQ ties stretch/squash to input ≠ output size (playbook R4). This is the one input
  change from the 1.5 pro A2 run, which landed 2.1 % stretched from 1920×1080 anchors.
- **Geography:** the approved local takes, `fasth3/partido/clips/partido_A_s2s3_rife_telk0f.mkv` (camarín → cripta)
  and `partido_B_s1s3_rife_telk0sh5.mkv` (cripta → atrio), approved by the user 2026-10-14 17:22. Each glides right and
  passes through black (the wardrobe door for A, the archway for B), so the paid take can be compared shot for shot.
- **Changed on purpose:**
  - **No timecodes.** 2.0 "does not respond to timestamps" (R9). The fixed blocks below replace the `[0s-1.5s]` lines.
  - **No architecture in the transit.** The 1.5 pro A2 prompt said "descending dark stone steps into a vaulted crypt",
    and the model invented an arch. A and B fill the gap only with darkness and with things visible in one of the two
    frames ("What fixes invented content", fixes 1 and 3).
  - **No content-negative list.** Lists like "no new objects…" are unproven, and A2's did not stop the arch (R10, C6,
    C7). The only negative is the behaviour "no cuts" (C5).
  - **No sound line**, because audio is off (R13).
- **Loop:** the graded cripta master f0 at both ends. It is not `seedance_loop/cripta_loop_f0.png`, the frame the
  1.5 pro loop used, which measures PSNR 28 against the master. The loop has to close on the plate that cuts in, so
  this run does not compare 1:1 with `seedance_loop/cripta_s15pro_loop.mp4`.

## Fixed block structure (one fact per block, the same order in every prompt)

`SHOT` one continuous shot + look in one positive line · `START` the first frame (subject, positions, light, camera
height) · `MOVE` one camera move with speed and direction + what passes through frame (only darkness or things in one
of the two frames) · `LAND` the last frame (composition, subjects and their positions) · `KEEP` what stays continuous.
For the loop, `MOVE` lists the only things that move. This is the playbook's FLF template (R6, R15) with its timecodes
replaced by blocks for 2.0.

Two drafts per transition were compared before picking:

| Run | Draft kept | Draft dropped and why |
| --- | --- | --- |
| A | Glide right → the open wardrobe's own door swings shut across the lens → black → moonbeam fades up → settle on the altar | "Fade through black" with no door. Dropped because the approved take uses the door, the door is in frame 1, and a fade with no motivation tends to read as the dissolve that revisar flags. The playbook's risk note (a door swing can show a door frame) applies; the novel-colours row will catch it. |
| B | Glide right past the altar → into the dark archway at the right edge → black → the portal's warm glow fades up in the rain → settle | The local prompt's "steps climb into darkness". Dropped because the steps are in neither frame, the same failure as A2's arch. |

## Measurement plan (written before any spend)

Same tools and rows as the 1.5 pro A2 measurement (`seedance/medicion.md`) and the RunPod session
(`fasth3/veredicto.md` › RunPod session 1). Everything runs at Seedance's native 1280×720. The baselines are scaled
down with `flags=area` and never upscaled (medicion.md › same scale).

| # | Check | Tool | Pass ("fixed") | Baseline it must meet |
|---|---|---|---|---|
| 1 | Start / end match, hidden cut, morph, strobe, novel colours, sharpness | `scripts/revisar.sh <clip> --inicio <first_1280> --fin <last_1280>` | 0 FAIL rows; start / end ≤ 4. The black beat is intended: its hidden-cut run may not be longer than the approved take's. | A telk0f: start 1.7, end 1.6, hidden-cut 57 f (2.4 s at 24 fps), morph 0. B telk0sh5: start 1.6, end 1.2, hidden-cut 39 f (1.6 s), morph 0. Both 0 FAIL. |
| 2 | Landing on the plate | ECC affine of the last frame vs the end plate (`seedance/landing3.py`, adapted to these 1280 anchors; no watermark box, `watermark: false`) | x and y scale within ±0.5 %, centre displacement < 2 px, luma gap ≤ the baseline's | 1.5 pro A2 failed this row: x 1.021, luma 14.3 vs 16.9. The baseline sits at scale 1.000. |
| 3 | End difference | mean 8-bit and % px > 8, last frame vs plate | ≤ the baseline's | A: 2.49 / 4.8 % (telk0f, its A2 span; medicion.md row 5). B: measure telk0sh5 the same way first. |
| 4 | Invented scenery (the arch problem) | revisar's novel-colours row + frames through the black beat at full rate (`scripts/comparar.sh cuadro`) | novel ≤ the baseline's, and nothing in the transit that is in neither frame | A: 0.8 % (telk0f); B: 0.7 % (telk0sh5). 1.5 pro A2 (the arch): 4.6 % against 1.5 % for its A2-only span |
| 5 | Waviness / boil (the user's complaint) | `visual-lab/scripts/experiments/warp.py` (warp_hf median / p90 on moving frames) + `fasth3/hervor.py`; per-object nboil at rest with `seedance/medir.py` (candles, door, altar) | ≤ the approved take at matched camera speed. These rows are *not verified* against the eye (partido.md), so they only support row 6. | A2 baseline: warp_hf 0.413 / 0.573, door nboil 0.396, candles 0.139 |
| 6 | The eye | A/B against the approved take: `scripts/eagle.sh view <seedance.mp4> <approved.mkv>` | The user picks Seedance, or calls it equal with less wobble | — |
| 7 | Final check | `scripts/eagle.sh <clip> --inicio … --fin …` (+ skill `eagle-eye` on a FAIL) | exit 0 | — |
| L | Loop seam | `scripts/revisar.sh <loop> --loop`, `scripts/comparar.sh costura`, then `scripts/eagle.sh <loop> --loop` | seam row pass and eagle exit 0. Also: the stone, altar and phone hold (warp at rest ≈ 0) and only the flames and dust move. | local `loop-locked-plate` v1 (exact by construction) |

**What counts as "fixed":** a transition is fixed when rows 1–4 pass and row 6 goes to Seedance. That means it lands on
the plate, invents no scenery, and the user sees less wobble than the approved take. Row 5 numbers support the call but
cannot make it alone. If rows 2–4 pass and 5–6 do not, the paid model has fixed the landing but not the wobble, and that
is the expected outcome per the synthesis. The loop is "usable" only when row L passes; otherwise the composited plate
stays the route.

Before any of this, read the result's `usage.completion_tokens` against 108,000, and count frames with ffprobe
(`duration` in the response is floor(frames / 24)).

---

## Run A_camarin_cripta

```json
{"name": "A_camarin_cripta", "model": "dreamina-seedance-2-0-mini-260615", "resolution": "720p", "duration": 5,
 "first": "camarin_1280.png", "last": "cripta_1280.png", "cost_usd": 0.378}
```

```text
One continuous shot, no cuts. Low-key and dark, deep black shadows: warm amber candlelight in the dressing room, cold blue moonlight in the crypt.
Start: a dim dressing room at eye level, a gilded mirror between two warm wall sconces on the left, three small red candles on a carved chest of drawers, a guitar leaning on a chair, and on the right a tall dark wooden wardrobe standing open with stage jackets hanging inside.
Move: the camera glides slowly to the right toward the open wardrobe; its dark wooden door swings shut across the lens and the frame goes black; out of the black a cold moonbeam fades up and the camera slows to a stop.
Land: a stone altar with an old golden telephone between two red candles, slightly left of centre at eye level, a cold moonbeam with drifting dust falling from a high barred window above it.
Keep: the same eye-level camera height, slow speed and low-key light from start to end.
```

## Run B_cripta_atrio

```json
{"name": "B_cripta_atrio", "model": "dreamina-seedance-2-0-mini-260615", "resolution": "720p", "duration": 5,
 "first": "cripta_1280.png", "last": "atrio_1280.png", "cost_usd": 0.378}
```

```text
One continuous shot, no cuts. Low-key and dark, deep black shadows: cold blue moonlight in the crypt, warm orange light and light rain in the street.
Start: a stone altar with an old golden telephone between two red candles, slightly left of centre at eye level, a cold moonbeam with drifting dust from a high barred window, and a dark stone archway at the right edge.
Move: the camera glides slowly to the right past the altar into the dark archway; the frame goes black; out of the black the warm glow of an arched church doorway fades up through falling rain and the camera slows to a stop.
Land: an old stone church at night, its arched doorway glowing warm orange behind an iron gate, a parked SUV with red tail lights on the right, a street lamp at the top right, light rain and mist.
Keep: the same eye-level camera height, slow speed and low-key light from start to end.
```

## Run L_cripta_loop

```json
{"name": "L_cripta_loop", "model": "dreamina-seedance-2-0-mini-260615", "resolution": "720p", "duration": 5,
 "first": "cripta_1280.png", "last": "cripta_1280.png", "cost_usd": 0.378}
```

```text
Locked-off camera, one continuous fixed shot, no cuts. Low-key and dark, deep black shadows, cold blue moonlight, warm candlelight.
Start: a stone altar with an old golden telephone between two red candles, slightly left of centre at eye level, a cold moonbeam from a high barred window, a dark stone archway at the right edge.
Move: only two things move: the two candle flames flicker gently, and fine dust drifts slowly through the moonbeam. Stone, altar, telephone and window stay perfectly still.
Land: the same frame as the start.
Keep: camera position, framing and light identical from start to end.
```

## Run A1s (added 2026-10-18 02:40: A's prompt-only control)

Question: was A's failure the prompt or the model? A1s is run A byte for byte (same model, frames, 720p, 5 s, silent,
strict roles) except for the prompt. It sends one motion sentence in the strict-role shape of BytePlus's own
first+last-frame examples (playbook `visual-lab/comfyui/seedance-prompting.md` › "When to use Seedance", point 3):
one camera move (R7), only things in frame 1 plus darkness, and nothing from the end frame. A's MOVE line is not reused
as is, because its "cold moonbeam fades up" is end-frame text. Replaces A15 (1.5 pro on free tokens, `runs_15pro.md`),
which the account cannot call: 404 on `seedance-1-5-pro-251215`. Cap $0.40.

| Draft | Text | Kept? |
| --- | --- | --- |
| 1 | One continuous shot: the camera glides slowly to the right into the dark open wardrobe, passes through black, and slows to a stop. | **Kept.** It is the approved take's path (glide right through the wardrobe into black), it names only frame-1 content, and "passes through black" gives the black beat a motive inside the move. |
| 2 | One continuous shot: the camera glides slowly to the right through the dark room. | Dropped: nothing motivates the black beat, and an unmotivated change tends to read as the dissolve revisar flags. |
| 3 | The open wardrobe's door swings shut across the lens as the camera glides slowly to the right. | Dropped: two motions (door + camera), and the door swing invites a door frame that is in neither plate (playbook risk note). |

```json
{"name": "A1s", "model": "dreamina-seedance-2-0-mini-260615", "resolution": "720p", "duration": 5,
 "first": "camarin_1280.png", "last": "cripta_1280.png", "cost_usd": 0.378}
```

```text
One continuous shot: the camera glides slowly to the right into the dark open wardrobe, passes through black, and slows to a stop.
```

---

## Results (2026-10-18, scored against the measurement plan above)

Clips (1280×720, 24 fps, 121 frames, h264): `A_camarin_cripta_cgt-20261018154326-z2mbk.mp4`,
`B_cripta_atrio_cgt-20261018154330-mzld9.mp4`, `L_cripta_loop_cgt-20261018154334-hbqng.mp4` (each with `_last.png`).
Cost from `seedance_log.jsonl`: 3 × 108,900 tokens = **$1.143** (the estimate of 108,000 assumed 120 frames; the clips have 121).
Raw numbers: `medir_api.txt` (`medir_api.py`), `revisar_{A,B,L}.log`.

**What happened.** A and B start on the plate (start diff 2.3 and 2.5) and pass through black as written. After the
black, each draws a new scene from the LAND text and stays there. A ends in a symmetrical crypt with a barred window
centred over a pedestal altar. B ends at a gothic church with a different SUV. Neither returns to the plate
(`ver/last_vs_plate.jpg`, top row clip | plate). The API echoes no frame roles (`GET tasks/{id}` shows seed 66083,
ratio 16:9, no last frame), so whether the last frame was read and outweighed, or not used at all, is **unknown**.

| # | Check | A camarín → cripta | B cripta → atrio | Approved (A / B) |
|---|---|---|---|---|
| 1 | revisar | **FAIL**: end 14.7 (≤ 4), sharpness-end 0.04. Start 2.3 pass, hidden-cut 17 f ≤ 57 pass, morph 9 pass, strobe 0 | **FAIL**: end 21.1. Start 2.5 pass, hidden-cut 22 f ≤ 39 pass, morph 0, strobe 0 | 0 FAIL / 0 FAIL |
| 2 | Landing (ECC on the end plate) | **FAIL**: cc 0.61, scale 0.68 × 2.24, i.e. no registration, a different scene | **FAIL**: cc 0.56, scale 1.26 × 1.78 | cc 0.998, scale 1.000 / cc 0.999, 1.000 |
| 3 | End diff (mean / % px > 8) | **FAIL** 22.72 / 73.7 %, luma 24.7 vs 16.9 | **FAIL** 23.73 / 80.2 %, luma 35.3 vs 25.8 | 2.49 / 4.8 % · 2.38 / 5.1 % |
| 4 | Invented scenery (revisar novel) | **FAIL** 15.6 % (f67–120 full frame) | **FAIL** 18.7 % (f74–120 full frame) | 0.8 % / 0.7 % |
| 5 | Waviness, warp_hf med / p90 on moving frames · hervor mean / p90 (*n.v.*) | **worse**: 0.500 / 0.855 · 0.510 / 0.809 at 2.36 px/f | **worse**: 0.622 / 1.155 · 0.508 / 0.907 at 7.62 px/f | 0.380 / 0.474 · 0.281 / 0.399 at 0.57 / 0.424 / 0.707 · 0.230 / 0.482 at 0.45 |
| 6 | The eye | not asked: rows 2–4 already fail | not asked | — |
| 7 | eagle.sh | not run: revisar already exits 1 on the same flags, and the cause is located (rows 2–4) | not run | — |

Row 5 is confounded by speed: Seedance moves 4× (A) and 17× (B) faster than the approved takes, and over different scenery.

**Loop L (cripta, same frame twice):** **FAIL**.
- revisar seam 4.43 against a threshold ≤ 1.19 (median step 0.43). `comparar.sh costura`: seam 4.57 vs median 0.49, max 2.18.
- Last frame vs plate: 4.01 / 14.3 %. The geometry holds (ECC scale 1.0009 / 0.9997, centre 0.1 px; median speed 0.06 px/f).
- What drifts is the light: luma goes 14.5 at f0 → 18.0 at f60 → 17.5 at f120. The seam diff is 7.7–10.1 in the centre
  column (moonbeam and altar top) and 1.0–1.2 at the left (`ver/L_seam_f0_f120.jpg`: f0 | f120, diff heat map,
  crops ×2.5).
- Passes: crawl 0.15, flicker 0.41, strobe 0, novel 0.2 %. The first run passed `--inicio`/`--fin` as well and got a
  hidden-cut FAIL. Rerun as the plan states (`--loop` only, `revisar/L_loop/`): hidden-cut n/a, seam 4.43 FAIL.
  `eagle.sh --loop` gives the same verdict (`eagle_L.log`). eagle-eye was not run on any clip, because revisar
  already locates each failure.
- Verdict: unusable as a loop. The composited plate (`loop-locked-plate` v1) stays the route.

**Fixed?** No, on all three. On 2.0 mini, a first + last frame pair of *different* scenes does not land: this measured
the opposite of what the transition needs, so the waviness question (rows 5–6) never comes up.
Open, not run: is it mini or the prompt? Test 1 would be one run of A with only SHOT + MOVE (no START / LAND / KEEP
description that can compete with the frames), $0.38. Test 2 would be the same prompt on 2.0, $0.76, or on 1.5 pro, which did land
within 2.1 % in the A2 run.

### Run A1s: the prompt-only control (2026-10-18 02:41, $0.381)

Clip `A1s_cgt-20261018164143-tsfdh.mp4` (+ `_last.png`): 1280×720, 24 fps, 121 frames, 108,900 tokens = **$0.381**
(cap $0.40). Same body as A; the prompt is one 23-word motion sentence with no end-frame text (run section above).
Raw numbers: `medir_a1s.txt` (`medir_a1s.py`, `medir_api.py` limited to A1s and A), `revisar_A1s.log`,
`revisar/A1s/table.tsv`. Frames: `ver/A1s_strip_vs_plate.jpg` (f0, 30, 50, 70, 95, 120 over the cripta plate).

**What happened.** It starts on the plate (2.3), glides right into the wardrobe, and goes black at f50–58 (hidden-cut
f53–58). It then opens on a **new, symmetrical crypt** (pillars and arches, a pedestal altar centred under a barred
skylight) and pushes in on the altar to f120. The prompt names none of the crypt, so the phone, the two red candles and
the moonbeam can only have come from the `last_frame` image. Mini reads the last frame but uses it as a subject reference,
not as the frame to land on: the composition, the camera and the architecture are its own. The ending is further from the
plate than A's: luma 38.7 against 16.9, because the beam floods the floor.

| # | Check | A1s (one sentence) | A (block prompt) | Approved telk0f |
|---|---|---|---|---|
| 1 | revisar | **FAIL**: end 17.5 (≤ 4), sharpness-end 0.25. Start 2.3 pass, hidden-cut 6 f pass, morph 0 pass, strobe 0 | **FAIL**: end 14.7, sharpness-end 0.04. Start 2.3, hidden-cut 17 f, morph 9 | 0 FAIL |
| 2 | Landing (ECC on the end plate) | **FAIL**: cc 0.39, scale 1.07 × 2.03, centre 431 px | **FAIL**: cc 0.61, scale 0.68 × 2.24, centre 408 px | cc 0.998, 1.000 / 1.000 |
| 3 | End diff (mean / % px > 8) | **FAIL** 31.00 / 81.2 %, luma 38.7 vs 16.9 | **FAIL** 22.72 / 73.7 %, luma 24.7 vs 16.9 | 2.49 / 4.8 % |
| 4 | Invented scenery (revisar novel) | **FAIL** 10.3 % (f57–120, box x 0.23–0.77) | **FAIL** 15.6 % (f67–120, full frame) | 0.8 % |
| 5 | warp_hf med / p90 · hervor (*n.v.*) | 0.465 / 0.743 · 0.467 / 0.681 at 4.11 px/f | 0.500 / 0.855 · 0.510 / 0.809 at 2.36 px/f | 0.380 / 0.474 · 0.281 / 0.399 at 0.57 |

**Verdict: not the end-frame text; mini or the black beat, n = 1 each.** With the end-frame text removed, mini still
lands on a scene of its own, just as far from the plate (end 31.0 vs 22.7, no ECC registration in either). The prompt
changed what was invented, not whether it was invented. Both runs kept a black beat ("passes through black", f53–58 here),
so this does not separate mini from the beat structure, and neither run was seeded. In practice it backs playbook point
1: don't use 2.0 mini for a pair of two different scenes. Still open: 2.0 or 2.5 on the same pair, or mini with no
black beat. 1.5 pro returns a 404 on this account (`runs_15pro.md`), and the mothership reports 1.0 pro unavailable too,
so the earlier 1.5 pro landing (A2, 2.1 % stretch) can't be rechecked here for free.

## L at 4K (2026-10-18, local, $0; the user approved L by eye at 720p)

Output: `L_cripta_loop_cgt-20261018154334-hbqng_4k.mp4` (3840×2160, 24 fps, 121 f, h264 ~4.8 Mbps), RTX VSR ×3.0 at
quality HIGH (`preset_4k`, `1.quality=HIGH`), 56 s on the GPU. Variants, numbers and crops are in `up4k/`
(`comparar_4k.py` → `comparar_4k.txt`; `revisar_{rtx,rtxhigh,fvsr}.log`).

| Variant | Time | Seam @1280 (source 4.57) | PSNR @1280 vs source | revisar sharpness-base (0.5–2) | crawl-base (≤ 1.5) | Kept? |
|---|---|---|---|---|---|---|
| RTX ×3 ULTRA (`preset_4k` default) | ~60 s | 4.57 | 43.8 | 2.39 FAIL | 1.04 | no: same picture as HIGH, a bit more temporal HF |
| **RTX ×3 HIGH** | 56 s | 4.54 | 44.1 | 2.49 FAIL | **0.85** | **yes**: most faithful, least shimmer |
| FlashVSR ×2 → RTX ×1.5 (`preset_4k_detail`) | ~270 s | 4.73 | 33.9 | 25.05 FAIL | 1.25 | no: invents cratered stone texture and changes the picture (detail ×bicubic 18–31 vs 2–3) |

SeedVR2 (`preset_upscale` → `preset_4k`) was not run. `comfyui-notes.md` records it on a dark MTO plate as
over-sharpened carvings, a yellower grade and shimmering invented detail, plus a near-frozen frame every 4.

- **Seam:** unchanged by the upscale (revisar 4.47 at 4K against source 4.43; ≤ 1.19 FAIL on both). It comes from the
  source's light drift (above), not from the 4K.
- **Detail:** sharpness-base FAIL means RTX sharpens to ~2.5× a lanczos upscale. On the 100 % crops (`up4k/pair_*.png`,
  lifted copies `*_lifted.png`), edges are a little crisper and the stone is the source's own soft texture. It is not
  waxy, and no detail was added (first look, not verified).
