# Split at the black vs one world vs Veo vs the RIFE comparators (2026-10-16, redflagdrone)

**User verdict, 2026-10-16 16:14 (eagle.sh view of `partido_A_s2s3_rife` against `s5_rife`, and `partido_B_s1s3_rife`
against `atrio_s3_rife`): the split is the recipe now.** Both split versions show less waviness on the walls and the other
surfaces than the current clips. The phone still waves when it moves, and that is the one thing left to fix (section
"Round 4: the phone" below). Calibration note: warp.py said the opposite. Its full-frame warp_hf median rated the split
worse on both pairs (A 0.464 against 0.421, B 0.485 against 0.389), and the eye rated it better. So the full-frame
warp_hf median does not track the wall waviness the user sees, and it should not decide a pick on its own.

Question: does splitting each hard transition at its black beat into two easy first+last-frame clips remove the
morph/waviness that every single-clip take (local, pod, Veo 3.1 Fast) shows? A second test (downbadship, 07:01) adds
**one world**: start frame only, no locked end, the door/arch treated as a real opening the camera pushes through.

**Outcome: no, the split does not remove the waviness.** Structurally it matches the comparators (no revisar FAIL row,
hidden-cut passes, morph 0, ends ≤ 1.7, lands on the real end plates; s5_rife and atrio_s3_rife also have 0 FAIL rows),
which Veo and the pod takes did not. Median warp is worse than the comparators' (A 0.464 vs 0.421, B 0.485 vs 0.389),
p90 is better (A 0.542 vs 0.582, B 0.776 vs 1.128); against Veo it wins on pair A and ties (median) / loses (p90) on B.
The black is longer on A: 57 RIFE frames ≥ 90 % dark vs s5_rife's 25 (B: 39 vs 46), so part of A's lower p90 may be
frames with nothing to boil, not cleaner motion. One world gives the lowest warp of everything measured (0.371 / 0.47 on both), but it
**strobes every 4th frame** (revisar FAIL, confirmed on the full-rate strip) and ends in rooms that are not MTO's
(end 16.0 / 22.7 vs ≤ 4). Nothing here is the user's eye yet: warp.py is not calibrated against it, and the user's
verdict decides (A/B commands at the end).

## Reference
Matched: the comparators `clips/s5_rife.mkv` (pair A) and `clips/atrio_s3_rife.mkv` (pair B): FastH3 8-step, 1920×1088,
107 native frames, RIFE 4.26 ×2 → 213; their prompts (`prompts/A_puerta_107.txt`, `C_atrio_107.txt`) and their pace
(door covers at ~f46 native, arch at ~f60). The key's look: s5's own door frame at f44 (dark vertical wood).
Changed on purpose: two 56-frame clips (17·3+5, 2.3 s each) instead of one 107, joined by a hard cut inside dark frames.

## Keys (`partido/llave.py`, sheet `partido/hojas/llaves_{A,B}.jpg`, gamma 2.2 to show texture)
Each variant darkened by a linear gain to p95 luma 17, so ≥ 95 % of pixels sit under revisar's DARK 20 (hidden-cut
needs ≥ 90 % for ≥ 5 frames); saved at 1080 (revisar) and 1088 (4 px replicated, as `pod/inputs`).
| pair | variant | how | dark | kept |
|---|---|---|---|---|
| A | **Klein s1** | `preset_edit` on the start frame: "close the wardrobe door, its dark panels fill the frame, nearly black" (2 MP, lanczos), then darkened (gain 0.47) | 97.7 % | **yes**: a readable panelled door at native sharpness, like s5's own f44 |
| A | Klein s2 | same, seed 2 | 96.6 % | brighter centre seam |
| A | crop1 | start frame x1560 y700 360×203 (lower wardrobe planks) ×5.3 | 98.3 % | soft from the upscale |
| A | crop2 | start frame x1600 y440 320×180 (door + jacket sleeve) | 100 % | a white sleeve in the key |
| B | Klein s1/s2 | same route: "inside the dark archway, stone and first steps fill the frame" | 96.5 % | invent a second vault with steps: more for the model to morph through |
| B | **crop1** | crypt start x1440 y330 480×270 (the archway's own inner stone) ×4, gain 0.90 | 97.2 % | **yes**: clip 1 becomes a push into the plate's real geometry |
| B | crop2 | x1320 y260 600×338, includes the lit arch rim | 96.9 % | rim forces a very low gain (0.32) |
Keys: `partido/keys/key{A,B}.png`; ComfyUI `input/mto_fasth3/partido_key{A,B}_1088.png`.

## Seed screen (960×544×56, seeds 1–3, `partido.sh screen`, sheet `partido/hojas/screen.jpg`)
All 12 halves: start 1.9–2.7, end 1.3–2.0 (all pass). Sharpness FAILs are the 960 render (0.1–0.2 ×) and the soft key.
- A1 (start → door): s1 dips to pure black then fades the key up; **s2** least novel (3.9 %), door swings onto the key; s3 7.0 % novel.
- A2 (door → crypt): s1/s2 slide the door aside like a wipe; **s3** no novel flag, the crypt fades up from the dark.
- B1 (crypt → arch): **s1** the arch rim passes and the stone fills (novel 1.6 %); s2 similar; s3 a dark mass slides in from the right.
- B2 (arch → street): s1 a half-stone/half-street frame at f10 (wipe); s2/s3 hold dark then fade up. **s3** kept. Their
  crawl/flicker FAIL is the fade-up counted as "static area" (luma 4→24 monotonic, no oscillation).

## Finals (1920×1088×56 ×2 per pair, ~205 s each; join; RIFE 4.26 ×2)
Join (`partido.sh final`): 56 + 56 → 107 native by keeping clip 1 f0–53 and clip 2 f3–55, cut only after checking both
sides are ≥ 90 % dark in revisar's frames.tsv (A 98.9 / 98.6 %, B 97.6 / 98.5 %); then the comparators' own path: PNG
.mov → RIFE ×2 → 213. Luma across the cut: A 3.3 → 3.4, B 4.1 → 3.5 (B2's own render dips to 0.7 at joined f58 = B2 f7 and
steps to 5.1 at joined f59, inside the dark). Halves: A1 s2 start 1.7 / end 1.3, A2 s3 1.5 / 1.6, B1 s1 1.6 / 1.7, B2 s3 1.9 / 1.2;
B1 end sharpness 3.19 × and B2 start 2.70 × the key = the model is sharper than the soft crop key, not a defect.

One world (`partido.sh unmundo`, `prompts/U_{A,B}.txt`, `encolar.py` `SIN_FIN=1`): screen 960×544×107 seeds 1–3, all
start 1.7–2.0, all end in a different room (A: a lit brick alcove crypt, end 13.9–18.3; B: a gothic cathedral street,
end ~22.6). Kept A s2 (full-black pass at f60, closest end 13.9) and B s2 (the only dark pass ≥ 90 %, f56); 1080×107
(334–336 s) + RIFE. At 1080 B s2's dark pass did not come back (darkest = f0, 83 %).

## Numbers (revisar on the 213-frame clips; warp_hf full frame over frames with speed > 0.5 px/f at 960, med / p90, not verified against the eye)
| pair | take | revisar FAIL rows | hidden-cut | warp med / p90 | speed med |
|---|---|---|---|---|---|
| A | **split** `partido_A_s2s3_rife` | **none** (start 1.7, end 1.6, morph 0) | pass, 57 f (f88–144) | 0.464 / **0.542** | 0.53 |
| A | one world `partido_u_A_s2_rife` (`--inicio` only) | **strobe** f80–92 (step 12.1) | (end 16.0 info) | **0.371 / 0.473** | 3.15 |
| A | Veo 3.1 Fast | hidden-cut (88 % max) | fail | 0.516 / 0.635 | 2.46 |
| A | comparator s5 + RIFE | none (0 FAIL) | pass | 0.421 / 0.582 | 0.71 |
| B | **split** `partido_B_s1s3_rife` | **none** (start 1.6, end 1.2, morph 0) | pass, 39 f (f83–121) | 0.485 / **0.776** | 0.45 |
| B | one world `partido_u_B_s2_rife` (`--inicio` only) | **strobe** f61–68 (step 5.4) | (end 22.7 info) | **0.371 / 0.448** | 3.77 |
| B | Veo 3.1 Fast | morph 18 f (dissolve f147–164) | — | 0.488 / 0.597 | 1.07 |
| B | comparator s3 + RIFE | none (0 FAIL) | pass | 0.389 / 1.128 | 2.26 |
Table: `partido/warp/tabla.txt`. With `--fin` the one-world clips also FAIL end, hidden-cut, morph (61 / 13 f) and
novel 12 %: info only, since they never aim at the plates (`revisar/partido_u_*_rife_confin/`).
Speed caveat: the split clips spend many frames dark or nearly still (speed med 0.45–0.53), the one-world clips move the
whole time (3.2–3.8): warp compares unlike motion, as the pod table already did.
The one-world strobe is real, not the light changing: native luma A f34–52 `38 38 39 57 39 40 42 57 62 40 42 58 41 …`
(every 4th frame +18) and on those frames the framing jumps too (`partido/hojas/uA_estrobo_f36_51.jpg`: f37, 41, 45, 49);
B `19 19 14 25 25 16 26 27 18 …`. A 4-frame cadence matches H3's temporal latent stride (guess, not verified).

## Gemini look pass (gemini-frames, gemini-3.5-flash-lite, 12 fps; `--res medium` was passed but ~7.4k prompt tokens for ~107 frames is the low rate, 66/frame; model observations, not measurements)
Prompt `partido/gemini/pregunta_{A,B}.txt`, replies `partido/gemini/partido{,_u}_{A,B}.md`.
- Split A: "one continuous move", dark 4.0–5.1 s; **major** boiling on the door wood 2.0–2.9 s and the crypt stone 5.5–6.6 s,
  the moonbeam haze churns to the end; no morph; lands on the crypt.
- Split B: "fade through black" (dark 3.6–4.8 s), two spaces bridged by a dark beat; minor boiling on crypt stone 0–3 s and
  rain / car highlights; no morph; lands on the street.
- One world A: push-through past the jackets, dark 5.8–6.0 s; **major** morph of the embroidered jacket 5.5–5.7 s; minor
  boiling elsewhere; "lands in ROOM B" (it is a different crypt).
- One world B: one continuous move, minor boiling throughout; "lands in ROOM B" (a different church).
Gemini missed the one-world strobe and called the wrong rooms right: it does not replace revisar or the user's eye.
The first one-world call got HTTP 503 on both Lite models; a retry a few minutes later worked.

## Files
- Split: `partido/clips/partido_A_s2s3_rife.mkv`, `partido/clips/partido_B_s1s3_rife.mkv` (ffv1 1920×1080, 213 f); native
  joins `partido_{A_s2s3,B_s1s3}.mkv`; halves `partido_{A1_s2,A2_s3,B1_s1,B2_s3}.mkv`.
- One world: `partido/clips/partido_u_{A,B}_s2_rife.mkv` (213 f), native `partido_u_{A,B}_s2.mkv`.
- revisar per clip `partido/revisar/<clip>/`; warp `partido/warp/*.npz`; logs `partido/hojas/{final,ufinal}_{A,B}.log`.
- Frames: ComfyUI `output/mto_fasth3/partido_*`. Script `partido/partido.sh`, keys `partido/llave.py`.

## For the user's A/B (eagle.sh view is only the player here; the eagle-eye findings pass was dropped, user 07:37)
```
~/projects/visual-lab/scripts/eagle.sh view "/mnt/e/Cursor Projects/MTO/tmp/07/fasth3/partido/clips/partido_A_s2s3_rife.mkv" "/mnt/e/Cursor Projects/MTO/tmp/07/fasth3/clips/s5_rife.mkv"
~/projects/visual-lab/scripts/eagle.sh view "/mnt/e/Cursor Projects/MTO/tmp/07/fasth3/partido/clips/partido_B_s1s3_rife.mkv" "/mnt/e/Cursor Projects/MTO/tmp/07/fasth3/clips/atrio_s3_rife.mkv"
~/projects/visual-lab/scripts/eagle.sh view "/mnt/e/Cursor Projects/MTO/tmp/07/fasth3/partido/clips/partido_u_A_s2_rife.mkv" "/mnt/e/Cursor Projects/MTO/tmp/07/fasth3/partido/clips/partido_A_s2s3_rife.mkv"
~/projects/visual-lab/scripts/eagle.sh view "/mnt/e/Cursor Projects/MTO/tmp/07/fasth3/partido/clips/partido_u_B_s2_rife.mkv" "/mnt/e/Cursor Projects/MTO/tmp/07/fasth3/partido/clips/partido_B_s1s3_rife.mkv"
```

## Not done
No guitar paste, grade, COSTURA or congelar on any of these; one seed per half at 1080 (the screen picks); no eagle-eye pass.

# Round 3: the 4-frame strobe, then the hybrid (2026-10-16 08:23–09:10, downbadship's queue)

## The strobe in the start-frame-only path
Tool: `partido/fase4.py` (per clip: luma residual vs a 5-frame running median, and a framing jump = the change in
phase-correlation shift between neighbours, each averaged by frame index mod 4; "strength" = max − min across the 4
phases; dark frames excluded).
| clip | what | luma by phase 0..3 | luma strength | jump by phase 0..3 | jump strength | revisar strobe |
|---|---|---|---|---|---|---|
| `partido_u_A_s2` | I2V 1920×1088×107, VSA (the bad take) | +0.69 **+2.40** +0.70 −0.07 | 2.47 | 1.73 2.43 **8.96** 8.50 | 7.23 | FAIL |
| `partido_u_B_s2` | same, pair B | **−0.93** +0.42 +0.15 −0.29 | 1.36 | 0.95 1.17 0.79 0.49 | 0.68 | FAIL |
| `partido_u_A_s2_denso` | same seed, dense attention (`DENSO=1`, 480 s) | −0.78 0 −1.12 +0.14 | 1.26 | 0.63 0.72 1.08 0.50 | **0.58** | FAIL, worse (37.7, irregular dips) |
| `partido_u_A_s2_keep25` | same seed, VSA keeps 25 % (`KEEP=25`, 348 s) | +0.62 +2.13 −0.04 +0.56 | 2.18 | 1.46 1.66 9.53 8.70 | 8.07 | FAIL |
| `partido_uscr_A_s{1,2}`, `uscr_B_s2` | same prompts, 960×544×107 | ±0.04 | 0.06–0.13 | — | — | pass |
| `partido_hA1_vsa_s2` | I2V 1920×1088×**56**, VSA (nearly static) | ±0.07 | 0.10 | — | 0.09 | pass |
| **`partido_hA1b_s3`** | I2V 1920×1088×56, VSA, **moving** (peak 27 px/f) | −0.27 +0.18 +0.18 −0.19 | 0.45 | 4.47 3.84 4.86 5.31 | 1.47 | **pass** |
| `partido_hB1_s3` | I2V 1920×1088×56, VSA, moving | ±0.2 | 0.20 | 3.15 1.12 0.99 3.03 | 2.17 | pass |
| s5 / s3 1080 FLF, split halves | first+last frame, 107 or 56 | ≤ 0.31 | ≤ 0.31 | — | ≤ 0.72 (B1 s1 2.00) | pass |
**Cause, as far as the evidence goes.** Measured: a 4-frame period, phase-locked to the frame index (A: phase 1 bright
and jumped, B: phase 0 dim). Inference, not verified: 4 frames is the H3 VAE's temporal compression, so the likely
mechanism is neighbouring latent frames disagreeing and the decoder drawing each disagreement as a jump at a latent
boundary. Where those boundaries fall (frame counts are 17n+5, not 1+4k) I did not check. It shows only in start-frame-only renders at 1920×1088×107 (~55k tokens, the 12 GB ceiling): not at 960×107, not at
1080×56, not in any 1080 first+last-frame take. Ruled out: the VAE decode window (no tiled-decode fallback in
`comfy.err.log`; the same decode is clean on FLF), an upscale node (there is none: frames are native 1920×1088, `medir`
only crops 4 px), RIFE (the pop is in the native frames), and the amount of VSA sparsity (keep 25 % = same pop). Dense
attention removes the periodic pop but breaks the take another way (irregular exposure dips; FastH3 is distilled with
VSA, so dense is off its distribution). VSA's cubes are 4×4×4 tokens (`nodes_sparse_attention.py` VSA_CUBE); if one
token is one latent frame in time, its temporal tile is 16 video frames, not 4 (that mapping is not checked). **Not pinned to one parameter**: the candidates left are the
length/token count itself with only a start anchor, and VSA's interaction with it.
**Fix used**: keep the start-frame-only clip at 56 frames (1920×1088×56, default VSA). Confirmed on a clip that moves:
`partido_hA1b_s3` peaks at 27 px/f, revisar strobe pass, no phase lock. (`partido_hA1_vsa_s2` also passed, but it barely
moves: weak evidence on its own.)

## Hybrid (`partido.sh hibrido`, prompts `partido/prompts/H_{A1,A1b,B1}.txt`)
Clip 1 = start frame only, 56 frames, the camera pushes into the wardrobe / through the arch into the dark; clip 2 = the
split's locked second half already rendered (`partido_A2_s3`, `partido_B2_s3`: key → real end). Join as the split: drop
a frames from clip 1's tail and 5 − a from clip 2's head (first a in 2, 1, 3, 0, 4, 5 with both sides ≥ 90 % dark) →
107 → RIFE ×2 → 213.
- Screen 960×544×56 seeds 1–3 (`partido/hojas/hibrido_screen.jpg`): all strobe pass. A s3 pushes past the jackets and ends
  90–100 % dark; B s3 through the arch into the stairwell, 94–98 %; B s2 never dark enough (82–88 %), B s1 ends on lit stairs.
- **Pair A at 1080 stalls with `H_A1.txt`**: seeds 2, 3 and 1 all keep the room still and only dim the wardrobe interior
  (dark max 62 / 70 / 61 %; s3 and s1 also crawl/flicker FAIL on that static area), against a moving push at 960 in all
  three. The join guard stopped both. `H_A1b.txt` (push from 0.8 s, "without slowing", black stated from 1.6 s) fixed it on
  the first try: s3 reaches 99 % dark, join A1b f0–53 + A2 f3–55 (98.9 / 98.6 %).
- Pair B at 1080 with `H_B1.txt` s3 worked as screened: join B1 f0–52 + B2 f2–55 (91.5 / 98.2 %).
- Luma across the cut (native): A f53 4.0 → f54 3.4 (flat); **B f52 8.9 → f53 3.8**, a 5-level step: clip 1's tail is
  brightening as the stairwell appears (6.0, 6.7, 8.9) when it is cut to clip 2's dark head. Look there in the A/B.

| pair | take | revisar FAIL rows | hidden-cut | warp med / p90 | speed med |
|---|---|---|---|---|---|
| A | **hybrid** `partido_h_Ab_s3_rife` | **none** (start 1.7, end 1.6, morph 1) | pass, 52 f (f93–144) | 0.531 / 0.823 | 0.94 |
| A | split `partido_A_s2s3_rife` | none | pass, 57 f | 0.464 / 0.542 | 0.53 |
| A | one world `partido_u_A_s2_rife` | strobe | — | 0.371 / 0.473 | 3.15 |
| A | Veo 3.1 Fast | hidden-cut | fail | 0.516 / 0.635 | 2.46 |
| A | comparator s5 + RIFE | none | pass, 25 f | 0.421 / 0.582 | 0.71 |
| B | **hybrid** `partido_h_B_s3_rife` | **none** (start 1.6, end 1.2, morph 0) | pass, 32 f (f90–121) | 0.527 / 0.802 | 0.26 |
| B | split `partido_B_s1s3_rife` | none | pass, 39 f | 0.485 / 0.776 | 0.45 |
| B | one world `partido_u_B_s2_rife` | strobe | — | 0.371 / 0.448 | 3.77 |
| B | Veo 3.1 Fast | morph 18 f | — | 0.488 / 0.597 | 1.07 |
| B | comparator s3 + RIFE | none | pass, 46 f | 0.389 / 1.128 | 2.26 |
Table: `partido/warp/tabla_hibrido.txt`. **Read: the hybrid keeps the split's clean structure (no FAIL, real ends) but is
the wavier of the two on both pairs and has the highest median of all the takes.** Its loo_hf (residual against the
neighbours' interpolation) is also the highest (A 0.644 / 1.179, B 0.675 / 1.198), i.e. frame-to-frame redraws, not just
motion. Not verified against the eye.

Gemini (Lite; observation only, and it missed the round-2 strobe, so a "none" from it proves nothing):
- Hybrid A (`partido/gemini/partido_h_A.md`): a continuous move through the wardrobe as a portal, dark 4.4–5.4 s;
  **major** wobble on the wood 2.2–3.0 s and **major** morph/boil of the jackets 3.4–4.4 s; minor crawl on the crypt.
- Hybrid B (`partido/gemini/partido_h_B.md`): a dip to black 4.6–4.9 s; minor boiling on stone, telephone, wet car/street.

## Files (round 3)
- Hybrid: `partido/clips/partido_h_Ab_s3_rife.mkv`, `partido/clips/partido_h_B_s3_rife.mkv` (213 f); native joins
  `partido_h_{Ab,B}_s3.mkv`; clips 1 `partido_h{A1b,B1}_s3.mkv`.
- Strobe tests: `partido/clips/partido_u_A_s2_{denso,keep25}.mkv`, `partido_hA1_vsa_s2.mkv`; script `partido/fase4.py`;
  `encolar.py` gained `KEEP=` (VSA keep %).

## For the user's A/B (round 3)
```
~/projects/visual-lab/scripts/eagle.sh view "/mnt/e/Cursor Projects/MTO/tmp/07/fasth3/partido/clips/partido_h_Ab_s3_rife.mkv" "/mnt/e/Cursor Projects/MTO/tmp/07/fasth3/partido/clips/partido_A_s2s3_rife.mkv"
~/projects/visual-lab/scripts/eagle.sh view "/mnt/e/Cursor Projects/MTO/tmp/07/fasth3/partido/clips/partido_h_B_s3_rife.mkv" "/mnt/e/Cursor Projects/MTO/tmp/07/fasth3/partido/clips/partido_B_s1s3_rife.mkv"
~/projects/visual-lab/scripts/eagle.sh view "/mnt/e/Cursor Projects/MTO/tmp/07/fasth3/partido/clips/partido_h_Ab_s3_rife.mkv" "/mnt/e/Cursor Projects/MTO/tmp/07/fasth3/clips/s5_rife.mkv"
~/projects/visual-lab/scripts/eagle.sh view "/mnt/e/Cursor Projects/MTO/tmp/07/fasth3/partido/clips/partido_h_B_s3_rife.mkv" "/mnt/e/Cursor Projects/MTO/tmp/07/fasth3/clips/atrio_s3_rife.mkv"
```

# Round 4: the phone (2026-10-16 16:14–17:00, frfrdrone)

**User verdict, 2026-10-16 17:22: the phone fix is approved on both pairs ("B looks fine, no sticker").** The chosen
clips are `partido/clips/partido_B_s1s3_rife_telk0sh5.mkv` for pair B and `partido/clips/partido_A_s2s3_rife_telk0f.mkv`
for pair A.

**Result: pasting the crypt plate's own phone over the split clips fixes the phone and leaves the walls untouched.**
On pair B, where the phone slides across the frame during the pan, the best paste brings the phone's warp below the
current clip's and keeps every revisar row passing. On pair A, where the phone sits almost still at the end, the paste
removes most of the phone's frame-to-frame boil, but the warp number cannot show it (explained below). Reseeding the
phone's half did not help: the best new seed screened well at 960 and came out worse at 1080. The user approved both
pastes at 17:22 after the A/B whose commands are at the end of this section.

## Where the phone is
The phone is the gold rotary telephone on the crypt altar, plate mask `in/mascara_tel_cripta.png` (box x922 y547,
124×85 px at 1920×1080). The crypt is the end of pair A and the start of pair B, so the phone appears in one half of each:

- Pair A, half A2 (door → crypt): visible from about f136 to the last frame, f212. It enters from behind a dark edge that
  sweeps across it until about f142, then the camera settles and the phone barely moves (0.4 px per frame at 960).
- Pair B, half B1 (crypt → arch): visible from f0 to about f62, sliding left as the camera pans, up to 25 px per frame at
  960. This is the "waves when it moves" the user saw: on the 1:1 strip the dial and body melt into a smear from f40 on.

Sheet: `partido/tel/donde.jpg`.

## A phone-only number
`partido/tel/warp_tel.py` tracks the plate's phone through the clip (the same ECC tracker as `telefono_pega.py`), carries
the plate mask with it, and runs warp.py's own residual (warp_hf and loo_hf, at 960 as warp.py does) inside that mask
only. `NUCLEO=1` measures the phone body without its outline.

On the plain clips it is consistent with the verdict (the split did not fix the phone): it rates the split's phone wavier
than the comparators' on both pairs. The user has not compared phone against phone, so that ranking itself is not
confirmed by eye.

| pair | clip | phone warp_hf, median / p90 |
|---|---|---|
| A | split `partido_A_s2s3_rife` | 0.338 / 0.377 |
| A | comparator `s5_rife` | 0.158 / 0.334 |
| A | Veo 3.1 Fast (720p, upscaled to measure) | 0.239 / 0.325 |
| A | hybrid `partido_h_Ab_s3_rife` | 0.338 / 0.377 (same half A2 as the split, so the same number: a sanity check) |
| B | split `partido_B_s1s3_rife` | 0.359 / 0.457 |
| B | comparator `atrio_s3_rife` | 0.317 / 0.387 |
| B | Veo 3.1 Fast (720p, upscaled to measure) | 0.326 / 0.453 |
| B | hybrid `partido_h_B_s3_rife` | 0.404 / 0.525 |

Its limit showed up on pair A. A rigid paste of a still phone should score near zero, yet it stayed at 0.32 even on the
body alone. At 960 the phone is about 62×43 px and moves less than a pixel per frame, so flow error and resampling set a
floor around 0.3 whatever the content. A second measure does not have that floor: `telefono_pega.py`'s own "boil",
the mean frame-to-frame change of the phone's fine detail after warping each frame back into plate coordinates. Both
numbers are in the tables below. Neither has been checked against the user's eye on a paste yet.

## Candidates, pair B
All pastes are on the 213 RIFE frames of the split, so the clip, its length and its walls are the split's.
Reseed = new seeds of half B1, screened at 960 (seeds 4–6 beside the existing 1–3), the best promoted to 1080 and
joined with the split's own B2 s3 exactly as `partido.sh final` does (cut in black: 96.5 % and 98.5 % dark).

| candidate | phone warp_hf, median / p90 | phone boil | revisar FAIL rows |
|---|---|---|---|
| plain split | 0.359 / 0.457 | 5.57 | none |
| comparator s3 | 0.317 / 0.387 | 5.79 | none |
| reseed B1 s6 at 1080 (`partido_B_s6_s3_rife`) | 0.395 / 0.486 | 7.03 | none |
| reseed s6 plus paste | 0.332 / 0.398 | 1.51 | none |
| paste, original settings (`_tel`) | 0.283 / 0.391 | 1.77 | none |
| paste with gain (`_telg`) | 0.280 / 0.383 | 1.59 | none |
| paste with shutter 0.5 (`_telsh5`) | 0.283 / 0.395 | 1.93 | none |
| paste with gain, no sharpening (`_telk0`) | 0.256 / 0.365 | 0.87 | none |
| **paste with gain, no sharpening, shutter 0.5 (`_telk0sh5`)** | **0.244 / 0.326** | **0.83** | **none (eagle.sh)** |

Kept: `partido/clips/partido_B_s1s3_rife_telk0sh5.mkv`. It has the lowest phone numbers of everything measured, below the
current clip s3. On the strip it is the only paste whose blur matches the wall's motion blur in the fast frames f56–f61;
with the default shutter 0.2 the phone reads sharper than its surroundings there. Its revisar rows equal the split's
(start 1.6, end 1.2, hidden-cut 39 frames, morph 0); the only changed row is the novel share, 0.9 % → 0.7 %.

Why "no sharpening": the paste matches its sharpness to the take frame by frame, and RIFE's in-between frames are softer
than the native ones, so the sharpening amount alternated on every frame (0 / 0.25 on A) and climbed to 2.0 during B's
pan, copying the take's boil instead of its focus. With it off, the phone's warp and boil both drop.

Why the reseed lost: at 960, B1 s3 and s6 tied for the lowest phone median (0.372 and 0.373, against the split's own s1
at 0.507 / 0.827). s6 was promoted for its lower p90 (0.498) and its even pan (at most 4.2 px per frame, against s3's
19.8). At 1080 the same seed scored worse than the split. The earlier lesson holds: the 960 screen picks a
prompt and seed, not the 1080 result.

Screen numbers: phone warp_hf median at 960, native 56 frames (`partido/tel/scr/`). The split uses B1 s1 and A2 s3.

| half | s1 | s2 | s3 | s4 | s5 | s6 |
|---|---|---|---|---|---|---|
| B1 | 0.507 | 0.526 | 0.372 | 0.461 | 0.546 | **0.373** (promoted) |
| A2 | 0.350 | 0.217 | **0.160** (the split's own) | 0.345 | 0.320 | 0.294 |

For A2 the split's seed was already the best of six, so nothing was promoted.

## Candidates, pair A
The phone is pasted backwards in time (the tracker starts from the last frame, which matches the plate). Boil is
measured over the frames each paste covers, so the split's own value is 4.02 over f136–f212 (for the first three pastes)
and 3.83 over f143–f212 (for the kept one); s5's is over its whole phone span, f99–f212.

| candidate | phone warp_hf, median / p90 | phone boil | revisar FAIL rows | defect |
|---|---|---|---|---|
| plain split | 0.338 / 0.377 | 3.83 | none | — |
| comparator s5 | 0.158 / 0.334 | 2.55 | none | — |
| paste, original settings | not measured | — | — | phone 16–20 levels too bright through the fade-up, and pasted into 12 black frames |
| paste with gain | 0.345 / 0.406 | 1.90 | none | drawn over the dark edge f136–f141 |
| paste with gain, no sharpening | 0.320 / 0.347 | 0.98 | none | drawn over the dark edge f136–f141 |
| **the same, pasted only from f143, fading in to f150 (`_telk0f`)** | **0.320 / 0.344** | **1.09** | **none (eagle.sh)** | — |

Kept: `partido/clips/partido_A_s2s3_rife_telk0f.mkv`. Its revisar rows equal the split's (start 1.7, end 1.6,
hidden-cut 57 frames, morph 0, novel 0.8 % at f154, same box as the split). Over f136–f142 the clip shows the take's own
phone behind the moving edge; the paste fades in from f143 to full at f150. What it does not fix: the moonbeam haze that
churns around and behind the phone (Gemini flagged it in round 1). The paste touches only the phone.

## Changes to the tools
`telefono_pega.py` (all off by default, so earlier runs reproduce):
- `GANANCIA=1`: the pasted phone takes the take's own phone brightness frame by frame (Savitzky-Golay 9/2). Needed when
  the scene fades up from black.
- `HASTA=<frame>` and `FUNDE=<frames>`: stop pasting at a frame (in input order) and fade the paste out over the frames
  before it. Needed when something in the take passes in front of the phone.
New in `partido/tel/`: `warp_tel.py` (phone-only warp), `tira_tel.py` (1:1 strip that follows the phone, plus an H.264
mp4 of the same crops), `screen_tel.sh` (half reseed at 960), `final_tel.sh` (B1 at 1080, joined with B2 s3, RIFE),
`medir_cand.sh` (revisar plus phone warp per candidate), `medir_todo.sh` (phone warp on the comparators).

## Evidence
- Strips, one tile per frame, 1:1 crops following the phone: `partido/tel/tira_B_cand.jpg` (split, `_telk0`,
  `_telk0sh5`, f0–f62) and `partido/tel/tira_A_k0f.jpg` (split, `_telk0f`, f136–f212); the same crops in motion:
  `partido/tel/tira_B_cand.mp4`, `partido/tel/tira_A_k0f.mp4`.
- revisar: `partido/revisar/eagle_partido_{A_s2s3_rife_telk0f,B_s1s3_rife_telk0sh5}/` (eagle.sh evidence built, the
  eagle-eye findings pass not run: dropped by the user at 07:37). Other candidates: `partido/revisar/<clip>/`.
- Per-frame phone numbers: `partido/tel/*.tsv`; body-only: `partido/tel/nucleo/`.

## For the user's A/B: best paste against the plain split
```
~/projects/visual-lab/scripts/eagle.sh view "/mnt/e/Cursor Projects/MTO/tmp/07/fasth3/partido/clips/partido_B_s1s3_rife_telk0sh5.mkv" "/mnt/e/Cursor Projects/MTO/tmp/07/fasth3/partido/clips/partido_B_s1s3_rife.mkv"
~/projects/visual-lab/scripts/eagle.sh view "/mnt/e/Cursor Projects/MTO/tmp/07/fasth3/partido/clips/partido_A_s2s3_rife_telk0f.mkv" "/mnt/e/Cursor Projects/MTO/tmp/07/fasth3/partido/clips/partido_A_s2s3_rife.mkv"
```
What to look at: on B, the phone during the pan (0.0–2.6 s) and whether it looks pasted on (a "sticker") in the fastest
frames around 2.4 s; on A, the phone's entry around 5.9–6.3 s and its rest to the end. If B looks pasted on, the next
variant is a longer shutter (0.7) or a paste that ends a few frames earlier.

## Not done
No grade, COSTURA or congelar. The pastes were made on the RIFE frames, not on the native frames before RIFE; that is the
order the final clip needs, but a re-run of RIFE on top of them would redo the phone. No new 1080 seed for A2.
