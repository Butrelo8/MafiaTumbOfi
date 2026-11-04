# 07, camarín → cripta: FastH3 local (first + last frame) vs Flow job2 (2026-10-14)

**Latest verdict, 2026-10-16 16:14 (user, eagle.sh view): the split at the black is the recipe for both transitions.**
`partido/clips/partido_A_s2s3_rife.mkv` (camarín → cripta) and `partido/clips/partido_B_s1s3_rife.mkv` (cripta → atrio)
show less waviness on the walls and other surfaces than the current clips (`clips/s5_rife.mkv`, `clips/atrio_s3_rife.mkv`),
but the phone still waves when it moves. warp.py's full-frame median had rated the split worse (A 0.464 against 0.421,
B 0.485 against 0.389): the eye and that number disagree, so it is not a pick criterion. Phone fix (16:14–17:00): the
plate's phone pasted over the split, `partido/clips/partido_B_s1s3_rife_telk0sh5.mkv` and
`partido/clips/partido_A_s2s3_rife_telk0f.mkv`, 0 revisar FAIL rows. **Approved by the user at 17:22 on both pairs
("B looks fine, no sticker"): these two are the chosen clips**, `_telk0sh5` for cripta → atrio and `_telk0f` for
camarín → cripta. Details in `partido.md` ("Round 4: the phone").

**Verdict: FastH3 wins as the E6 candidate for `grupo-ida`, pending the user's look at the A/B.** It starts and ends on
the graded E5 loops (job2 starts on the old camarín: 27.5 vs 3.4), it has the plan 1 geography (the wardrobe's own door
shuts, then the camera tilts down into the cripta), it reaches full black (29 frames, f73–101), shows no two-room frames,
and its tail sits closer to the cripta loop (4.25 vs 6.18). It costs nothing per clip. It is **not** the E6 final as the
ticket defines it: there is no masked occluder from the mockup and no `maskedmerge`; the door is the model's, and the
COSTURA (cripta loop 228–239 crossfaded + 0–19 raw) is a congelar step that has not been done.

## Reference
Matched: Flow job2 (the provisional E6): the camera's sideways speed, ~7.5–8 s, a dark occluder, no new lights.
Changed on purpose: the occluder is the wardrobe's own door (ticket 07, plan 1), then the camera goes down into the
cripta; ends = the graded E5 loops' f0 (`look/maestros/{vestidor,cripta}_esc.mkv`), not the pre-production plates.

## Setup
FastH3 8-step (the subgraph "First Last Frame to Video (FastVideo FastH3)" from `preset_i2v.json`, rebuilt in API format
with `last_frame` wired: `encolar.py`), 192 frames (17·11+5), 8 steps, res_multistep, VSA 10 %. Ends padded to the
32-px grid by edge smear and cropped back to 16:9 (`medir.sh`), then lanczos to 1920 for revisar.
Sizes on the 4070 Ti 12 GB: **1920×1088 OOM** in the first dense steps (26 s); **1600×928 OOM** mid-sampling (351 s);
**1440×832 fits: 376 s** (64 s first step, ~31 s/step after). Seed screen 960×544: ~150 s. 1440 kept the screen's take
structure for seed 2 (door, black, descent); seed 1 changed.

## Variants (prompts in `prompts/`)
| take | ends (start / end) | black ≥ 90 % | morph | novel | read |
|---|---|---|---|---|---|
| screen A s1 (door prompt) | 1.7 / 1.8 | 35 (f103–137) | 0 | f2–101 | panel slides in, crypt fades in at its final framing |
| screen A s2 | 1.8 / 2.0 | 31 (f92–122) | 0 | f2–89, f122–173 | **the wardrobe door swings shut, descent into the vault** |
| screen B s1 (lateral prompt) | 1.8 / 1.6 | 35 (f102–136) | 3 (f92–94) | f2–97 | as A s1 |
| screen B s2 | 1.8 / 1.8 | 28 (f99–126) | 7 (f89–95) | f21–98 | both rooms at the edges |
| **1440 A s2 (kept)** | 1.8 / 1.6 (best cut f187, drift 0.1) | **29 (f73–101)** | **0** | 3.5 % max; f15–72, f119–133 | door + descent, as screen s2 |
| 1440 A s1 | 1.8 / 1.9 | 26 (f68–93) | 0 | 1.2 % max; f26–61, f133–141 | a room door with a lever handle (invented, off-period) |
Kept 1440 A s2: it is the only take whose occluder is the wardrobe door itself; s1's door brings invented hardware, and
its tail and end are worse (5.20 / 1.9).

## A/B numbers (revisar.sh with the graded E5 ends, and `look/costuras.py`)
| | job2 (graded master, 185 f) | FastH3 1440 A s2 (192 f) |
|---|---|---|
| start vs vestidor loop f0 (revisar) | **27.2 FAIL** | 1.8 |
| f0 vs vestidor loop f0 (mean 8-bit / px > 8) | 27.5 / 53.6 % | 3.4 / 11.0 % (the 1440 → 1920 round trip alone is 0.8 / 1.3 %, so ~2.6 is the H3 head's own drift: the congelar step has to absorb it, e.g. a short fade from the loop's f0) |
| end (revisar) | 2.2 | 1.6 |
| last frame vs cripta f0 | 3.76 / 12.5 % | 3.01 / 8.4 % |
| tail (last 20) vs cripta loop 0–19 | 6.18 | **4.25** |
| black ≥ 90 % | 14 (f85–98) | 29 (f73–101) |
| morph | 0 | 0 |
| novel | 6.9 % max; f0–68, f95–175 | 3.5 % max; f15–72, f119–133 |
| sharpness at the ends (× plate) | 0.90 / 0.43 | 0.46 / 0.52 (rendered at 1440; RTX ×1.33 would go in congelar) |

**Not yet good:** the black lasts 29 frames (~1.2 s), longer than the ~5–6 the ticket asks for; the prompt asked for a
quarter second and every take gave 26–35. The vault top catches light the plate doesn't have during the tilt-down
(f119–133), so the cripta settles in view, shorter than job2's (f94–176). The ends are soft at 1440 (0.46–0.52 × plate).
The stairs are implied by the tilt, not shown. No vertical (E4 cameras) was attempted.

## Files
- Kept: `clips/f1440_A_puerta_s2.mkv` (ffv1 1920×1080, 192 f; source PNGs `E:\ComfyUI\ComfyUI\output\mto_fasth3\f1440_A_puerta_s2_*.png`)
- Other takes: `clips/{screen_*,f1440_A_puerta_s1}.mkv`; revisar per take in `revisar/`; job2 vs E5 in `revisar/job2_vs_e5/`
- A/B at speed: `ab/ab_job2_vs_fasth3_s2.mp4` (`ab.sh`, 1920×540, 288 f, frame counters); screen board `screen/tablero_screen.jpg`

## If the user OKs it (not done)
Same chain as job3/job4: the head is already graded (its f0 is the graded loop's f0, job4 lesson), so grade only from
the swap on, never the whole clip twice; RTX to 1920; COSTURA (cripta 228–239 crossfaded + 0–19 raw); ladder;
congelar; `public/`. Possibly a second pass for a shorter black (prompt or a 1440 seed sweep).

## License
MiniMax H3 Community License (section 5): outputs may not be used for audiences in the US, EU, UK or South Korea without
MiniMax's written authorization. MTO is a Mexican band and the site is Spanish-first, but a public website is reachable
everywhere, and a regional Mexican band's audience likely includes the US. Whether the site counts as targeting the US
is the user's call; if it does, ask MiniMax before this clip goes to `public/`. Flow (Veo) job2 has no such clause.

## Texture on motion: 1080p native + FILM (2026-10-14, after the user: "on motion it tends to pixelate texture")
At 1440 the model redraws texture at low detail while the camera moves: smooth plaster with wormy relief strokes, blotchy
vault stone (`pix/crops_1440.png`). Not the codec, not VSA: a dense-attention rerun (`DENSO=1`, 501 s) keeps the same
texture and invents a framed photo in the mirror (`pix/crops_1440_denso.png`; camarín detail 0.32 × plate).
**Fix: 1920×1088, 107 frames (17n+5 nearest to the plan's ~97), 383 s, no OOM; FILM ×2 → 213 frames** (memory plan of
06:22). Prompt timeline compressed to 4.5 s (`prompts/A_puerta_107.txt`), seed 2. FILM must read a PNG-codec .mov
(`film.py`): from a lossless libx264rgb mp4 every frame shifts ~0.9 levels; from the .mov the originals stay byte-exact.

| | 1440 kept | 1080 + FILM (213) | 1080 + FILM, ramp in the dark (186, `clips/f1080_film2_rampa.mkv`) |
|---|---|---|---|
| start / end (revisar) | 1.8 / 1.6 | 1.6 / 1.7 | 1.6 / 1.7 |
| sharpness at the ends (× plate) | 0.46 / 0.52 | **0.95 / 0.91** | 0.95 / 0.91 |
| detail while moving, median (× plate; `detalle.py`) | 0.46 / 0.34 | **0.96 / 0.85** | same frames |
| black ≥ 90 % | 29 | 51 (f73–123; pure black only f87–98) | **24 (f73–96)** |
| morph / novel | 0 / 3.5 % | 0 / 0.7 % | 0 / 0.7 % |
| tail vs cripta loop 0–19 (new master, 06:29) | 4.25 (old master) | 4.79 | 4.79 |
| f0 vs vestidor loop f0 | 3.4 | 3.1 | 3.1 |
The ramp takes every 2nd frame while the door darkens and the cripta fades up, every 3rd in pure black (f73–123 →
24 frames). revisar flags a jump at its start (f74): judge at speed. The 1080 take reveals the cripta almost at its
final framing (slight push), not the tilt-down of the 1440 take, and its vault does not over-light. FILM in-betweens on
the door read as motion blur at 1:1 (`pix/film_puerta_saltos.jpg`); slight smear where the edge crosses the white
jacket. The head drift (3.1) persists at native 1080p, so it is the model's, not the resize: the splice must fade it.
A/Bs: `ab/textura_1440_vs_1080_1a1.mp4` (1:1 centre crop), `ab/ab_job2_vs_fasth3_1080.mp4` (full frame vs job2).

## The guitar (2026-10-14, user: "on the guitar the top part distorts when transferring")
The model redraws the headstock while the camera moves (peg count, angle, a hook at the top of the neck, f27–57).
Fix (`guitarra.py`, CPU, the job3 phone method): the plate's guitar (polygon + GrabCut mask,
`pix/guitarra_diag/mascara_sobre_placa.png`) tracked onto the take with ECC affine on the body (0.98–0.996 through f56),
per-channel gain from the take's light on the body (0.8–1.25, 5-frame median), 180° motion blur, 1.2 px feather. When
the door covers the body (ECC < 0.95, f57) the affine is extrapolated linearly and the paste is cut at the door edge
(first column of 150 dark ones in the lit wall band y 380–580: 1180 → 951); it stops at f62.
Neck + headstock vs plate (NCC in plate coordinates, f0–56, `medir_guitarra.py`): **0.771 median, 0.446 min → 0.990,
0.982**. Only f0–61 change (f62–185 byte-identical). revisar unchanged: start 1.6, end 1.7, black 24 (f73–96), morph 0.
Clip: `clips/f1080_rampa_guitarra.mkv`. A/Bs: `ab/guitarra_antes_despues_2x.mp4`, `ab/ab_job2_vs_fasth3_1080_guitarra.mp4`.

## Quality round (shookdrone, 2026-10-14 08:00–09:30; seed `mothership/docs/queue/2026-10-14-fasth3-successor.md`)
Scripts: `ronda.sh` (screen / interp / base / mitades / canario), `interp.py`, `medir_interp.py`; `encolar.py` gained
`BASE=1 STEPS=`, `SINK=`, `INI=`/`FIN=`. **Fix:** every take before this round was conditioned on the OLD cripta f0
(`end_1088.png`, 0.4 % px differ: the phone); `encolar.py` now uses `end_{1088,928}_nuevo.png` (new master 06:29) and
`medir.sh` measures against `end_nuevo.png`.

1. **Seed screen** 960×544×107, `A_puerta_107` (`screen/tablero_107.jpg`, `screen/screen107_rejilla.mp4`):
   | seed | black ≥90 % | morph | novel | read |
   |---|---|---|---|---|
   | s2 | 19 (f44–62) | 12 | 1.3 % | the current take's structure |
   | s3 | 24 | 6 | 5.0 % | white panel slides in, mirror content changes |
   | s4 | 18 | 7 | 6.0 % | white panel, mirror changes |
   | **s5** | **16 (f38–53)** | 4 | 1.5 % | real studded wooden door shuts, cripta near its final framing |
   | s6 | 35 | 1 | 1.2 % | black too long, cripta late |
   s5 at 1920×1088×107 (`clips/f1080_107_nuevo_s5.mkv`, new end): start 1.6, end **1.4** (best cut f102), black **12**
   (f43–54, no ramp needed after ×2), morph 1, novel 0.8 %, detail moving 1.01 / 0.93 × plate. Same take s2 re-measured
   against the new end: start 1.6, end 1.7, black 25, morph 0, detail 1.05 / 0.89.
2. **Interpolators** on the s2 native take. Holdout = interpolate the 54 even frames, compare each odd frame with the
   real one (motion 2× the real use). Door window f22–43; crop 640² where the edge crosses the jacket.
   | | door PSNR / SSIM | crop PSNR / SSIM | crop sharpness pred/real | whole take SSIM | real ×2: in-between / neighbours (median, min) | time 107→213 |
   |---|---|---|---|---|---|---|
   | FILM | 33.04 / 0.913 | 35.01 / 0.889 | 0.81 | 0.962 | 0.84, 0.44 | 51 s (holdout 54→107) |
   | RIFE 4.26 | 36.35 / 0.922 | 37.18 / 0.906 | 0.77 | 0.949 | 0.78, 0.56 | 35 s |
   | RIFE 4.26 heavy | 36.67 / 0.921 | 37.19 / 0.905 | 0.68 | 0.950 | 0.74, 0.51 | 34 s |
   | GIMM-r (ds 0.5) | 38.25 / 0.946 | 39.28 / 0.941 | 0.54 | 0.962 | 0.64, 0.41 | 112 s |
   | GIMM-f (ds 0.5) | 38.45 / 0.941 | 39.00 / 0.930 | 0.53 | 0.956 | 0.64, 0.40 | 199 s |
   GIMM at ds 1.0 OOMs on 1920×1088 (all four jobs). GIMM is the most accurate but the softest (PSNR rewards blur);
   RIFE 4.26 is the middle: +3.3 dB on the door over FILM and a less soft worst frame. User's eye decides:
   `ab/interp_puerta_1a1{,_mitad}.mp4`.
3. **Base H3 fl2va**, 1920×1088×107, 20 steps, seed 2, no VSA (`clips/f1080_107_base20_s2.mkv`, 19 min 31 s,
   55 s/step): start 2.2, end 1.6 (f97), black **37** (f33–69), morph 0, novel 0.1 %, detail 0.83 / 0.93. Camera nearly
   static f0–20, then a dark panel snaps across. No gain over FastH3 for this shot at 6× the time.
4. **Two native halves:** prepared (`ronda.sh mitades`, joined in the black), not run: s5 already gives a 12-frame black.
5. **Canary** 1600×928×192, `sink_conditioning: exact_kv`, llama-server down: **OOM at 236 s** (CUDA OOM, 0 bytes free,
   554 MiB allocated by torch), then `cudaErrorIllegalAddress` in `reset_cast_buffers` → ComfyUI aborted (Fatal Python
   error). exact_kv buys nothing; 1600×928×192 stays out of reach on 12 GB.
6. **s5 + ×2** (`clips/s5_rife.mkv`, `clips/s5_film.mkv`, 213 f): start 1.6, end 1.4 (f204), black **25 (f85–109) with no
   ramp**, morph 1, novel 0.8–0.9 %. revisar's "jump" at f68/f81 is the door edge wiping (`pix/s5_rife_f64-87.jpg`, even
   sweep). No guitar paste yet (`guitarra.py` is take-specific: re-derive). A/B at speed vs the current candidate:
   `ab/ab_actual_vs_s5_rife.mp4`. Waiting for the user: s2 or s5; FILM / RIFE / GIMM.

## s5 chosen (user, via vibeship 09:34); RIFE vs GIMM on s5
Holdout on s5's own native take (door f31–47): RIFE 4.26 34.43 dB / SSIM 0.886, sharpness 0.77 × real, 43 s (107→213);
GIMM-r ds 0.5 35.34 / 0.915, 0.52, 117 s. Both: start 1.6, end 1.4, black 25 (f85–109), morph 1. A/B:
`ab/ab_s5_rife_vs_gimm.mp4`, `ab/ab_s5_recortes_1a1{,_mitad}.mp4` (door | guitar at 100 %). Guitar paste waits for the pick.

# Cripta → atrio (replaces Flow job3), 2026-10-14
Ends = graded loop f0 (`in/start_cripta{,_1088}.png` = cripta_esc f0, `in/end_atrio{,_1088}.png` = atrio_esc f0; the
atrio loop is built from `e5/v5/prep/placa.png`, not `placa_atrio_v3`). Prompt `prompts/C_atrio_107.txt` (job3's,
in the 107-frame timeline). Screen 960×544×107 (`screen/atrio_tablero_107.jpg`, `screen/atrio_screen107_rejilla.mp4`):
| seed | start / end | black ≥90 % | morph | novel | read |
|---|---|---|---|---|---|
| s1 | 1.5 / 1.4 | 30 (f54–83) | 0 | 2.3 % | pans to arches + climbing steps (job3 geography); black long |
| s2 | 1.7 / 1.4 | 15 | 0 | 3.3 % | a person walks past the gate (f62–75): out |
| s3 | 1.7 / 1.4 | 18 (f43–60) | 0 | 1.1 % | cleanest |
| s4 | 1.7 / 1.5 | 15 | 0 | 3.2 % | atrio slides in |
| s5 | 1.6 / 1.5 | 21 | 0 | 1.9 % | — |
s3 and s1 queued at 1920×1088×107 ahead of the user's pick.

## Camarín → cripta candidate: s5 + RIFE 4.26 + guitar paste (user: RIFE default, 09:49)
`clips/s5_rife_guitarra_h20.mkv` (213 f): `guitarra.py` with the measured feather σ 0.88 (masks/RECETA.md, was 1.2),
`ECC_MIN=0.85`, `HALO=20` from f55. Raw s5 headstock NCC vs plate: 0.60 at f41, 0.43 at f66, 0.28 at f70. The plain
paste left a ghost body edge from f~60 (s5 draws the body offset near the door; ECC still 0.95), so a 20 px halo of the
plate's own surroundings ramps in from f55 (8 frames). Pasted NCC 0.99 f0–73 (f74+ = the door). revisar: start 1.6,
end 1.4, black 25 (f85–109), morph 1, novel 0.8 %. A/B `ab/s5_guitarra_antes_despues_2x{,_mitad}.mp4`; waits for the user.
Cripta → atrio at 1920×1088×107 + RIFE (213 f): **s1** start 1.9, end 1.3, black 14 (f115–128), morph 0, novel 3.0 %;
**s3** start 1.7, end 1.2, black 46 (f124–169), morph 0, novel 3.4 %, shows the climbing steps. 1080 structure differs
from the 960 screen (s3 black moved f43–60 → f62–84 native). Phone: shape and dial hold by eye in both; `telefono.py`
NCC is not usable here (f0 already 0.77: FastH3 head softer than the plate; then parallax + motion blur). A/B
`ab/ab_atrio_s1_vs_s3_rife.mp4`; waits for the user. Renders stopped (user, 10:02: prep first).

## One-take screen 2026-10-14 (rizzdrone; seed mothership/docs/queue/2026-10-14-atrio-oner.md)
Ends = maestros f0 (PSNR inf vs `look/maestros/{cripta,atrio}_esc.mkv` f0). 960×544×107, FastH3 8-step, ~64 s/take warm.
Boards: `screen/oner_tablero_{A,B}.jpg` (columns = f0 15 30 45 55 65 75 90 106; tile labels show the column index, not the
frame), grids `screen/oner_rejilla_{A,B}.mp4` (24 fps, + atrio_screen s1/s3). Full-rate strips: `screen/tira_oner_*.png`
(`tira.sh`, FILAS=8 → f24–87). Eagle Eye: `revisar/eagle_oner_B_{adelante_s2,barrido_s3}/eagle/report.md`.
**Arm A (blackout, C_atrio_107, s6–9)**: all start 1.6–1.7 / end 1.4–1.5, morph 0.
- s9: longest glide along the arcade, black 28 (f61–88), novel 2.3 % — best of A. s6: a real wall wipes in from the right,
  black 24 (f63–86), novel 1.2 %, reveal is a slow fade-up. s7: the altar fades out in place (no occluder), black 29.
  s8: **reject**, a person walks at the gate f67–87. None shows the steps the way s1/s3 do: by the stopping rule A does not
  beat s1/s3.
**Arm B (one-take, B_{adelante,atras,barrido}_107 × s1–3)**: start 1.7–1.9 / end 1.6–2.3; revisar morph/hidden-cut fail by
design (no black), judged on the strips + Eagle Eye.
- **adelante s2**: real path (pan to stairs f35, climb, out a doorway f45–52, glide along the wall to the portal f53–70).
  Eagle Eye 3 minor: cloud bank → mountain f86–106, end snap (jump 4.18 at f105 vs ~2.6), a 2nd street lamp off-frame f45–64.
- **barrido s3**: whip across warm-lit stone f38–44 (3 f ≥ 90 % dark), lateral arrival, morph 0, novel 1.8 %. Eagle Eye: the
  gate fades in place f58–63 (major, medium), a lit window off-frame f44–56.
- barrido s2: stairs → 1-frame dark wipe → street at final framing; morph 0, almost a cut. adelante s3: candelabrum (new light) on
  the steps, door-edge wipe; usable.
- Rejects: adelante s1 (candlelit corridor + other church facade, novel 21 %), atras s1/s2 (crypt inside the arch becomes the
  portal interior = doorway morph; new candelabra; posterized), atras s3 (exposure strobe f54–73), barrido s1 (portal appears
  inside the crypt next to the stairs).
- Mitades not run: the path fits 107 f on 3–4 takes.
Recipe draft: visual-lab `comfyui/recipes/transition-oner-v1.md`. Stop: user picks before any 1080/RIFE/paste/grade.
**1080 of the pick (user 16:04: adelante s2, "f73 has the best animation")**: `oner.sh final` → `clips/oner_f1080_adelante_s2{,_rife}.mkv`
(380 s + RIFE 53 s). start 2.0 / end 1.4, sharpness 0.93 / 0.96, end settles (jump ≤ 0.9 f96–106, no snap), RIFE 213 f.
**Structure moved**: up the stairs, portal + SUV seen through an arch at the top f60–71, push through it f71–76, land; the screen's
side-doorway exit + glide along the wall (and its f73) is not in it. Sent: `ab/oner_adelante_s2_screen_vs_1080.mp4` (frame-exact
from the PNGs), `ab/oner_f73_triptico.png`, `screen/tira_oner_f1080_adelante_s2.png`. Waiting: accept / upscale the 960 / re-roll.
eagle.sh evidence built (`revisar/eagle_oner_f1080_adelante_s2_rife/`), findings pass held until the structure is accepted.
medir.sh glob fixed to `${p}_?????_.png` (the `_rife_` PNGs were swallowed: 320 frames).
**Detail of the first part (user 16:24 accepted the 1080 path: "a lot of details lost between first part")**
- detalle_curva.py (÷ cripta plate, native): 1080 f0 0.98, f15 0.56, f24 0.33, f40–49 0.13; ÷ atrio trough 0.60 at f50–59, ~1.0
  from f67. 1:1 crops: grain gone by f16, phone cord → straight rod. Eagle run add7ababf5e2 (2 findings; #1 materials marked
  real with the user's words, NOT blind).
- Fix (i) cripta f0 → 1080 f72, 73 native frames + 1080 f73–106 (`oner.sh mitad1 2`, 264 s): the model compresses the crypt
  glide (stairs at f24 instead of f40), worse f24–39 (0.17/0.13 vs 0.33/0.24), leopard-blur stairwell; join clean. Dropped.
- Fix (ii) `detalle_placa.py` (plate luma HF through SIFT homography, mid-band local NCC gate): coverage 59 % f0 → 9 % f24 → 0
  from f30; f10–19 0.59→0.67, smoother decay; coil, dial and grain back at f8–20. `grano_valle.py` (grain matched to the plates,
  native f26–74): trough grain 0.45–0.8 → 0.9–1.4. RIFE both → `clips/oner_placa{,_grano}_v1_rife.mkv`. Sent:
  `ab/oner_detalle_antes_vs_placa.mp4`, `ab/oner_detalle_placa_vs_grano.mp4`, `ab/oner_detalle_f32_f110.png`. Waiting: pick.
**Halves through a Z-Image still (user 16:49 "still distorted frames from 0:02 till the stairs, just a little less"; still OK 17:04)**
- Still: native f55 (17n+5: 56 + 56; f45 impossible), `zrefine_mid.py` Z-Image base img2img d0.40 (61 s); `fiel.py` vs take
  frame: layout 3.5, edge F1 0.77 (d0.30 0.85 soft, d0.50 0.69 drifts); porous stone on 1:1 crops. `in/zmid_f55_d40_1088.png`.
- `oner.sh zmitades 2`: 210 + 208 s; joined `clips/oner_zunido_s2.mkv` 111 f, RIFE 221 f. start 1.6 / end 1.5, same route.
  Stairwell clearly sharper (÷ atrio f50–69 0.78–0.81 vs 0.60–0.75); crypt part ~same. Seam: speed dip native f56–57 (jump 8.0,
  6.5 vs ~10–15), RIFE f111–114. (ii) re-run adds only f0–9 → dropped; grain gap remains (0.52–0.6 vs 0.8–1.2), optional.
  Sent: `ab/oner_zmitades_vs_actual{,_1a1}.mp4`. Waiting: pick (+ grain?), then Eagle on the pick.
**User 17:18 on the halves take: "is worse now every frame now"** → rejected; current best stays (ii) on the accepted take. No Eagle
run existed on it (nothing to log in the ledger). **Measures disagreed with the eye**: detalle_curva (Laplacian) and 1:1 crops
of single frames said the stairwell was better; they judge stills, not motion. `temporal.py` (DIS flow, residual after motion
compensation, new vs current, medians per 10 f): camera speed f0–9 3.8 vs 0.4 px/f (no ease-in from the loop), f10–29 9.6–13.4
vs 2.6–7.3; low-band warp residual f0–29 1.6–2.4 vs 0.3–1.1 (3–5×); HF boil 2.4–3.0 vs 1.8–2.6; speed jerks f60–79 8–16 vs ~1;
luma flash f70–79 96 vs 50 (overexposed arch wall). No pop at the still (HF f50–59 2.58 both). Lesson: judge detail fixes on
motion (temporal.py warp/boil/jerk), never on single-frame crops or Laplacian.
**User 17:19: "warping and wobble, the stones keep moving ... when a fast motion goes by"** (texture boiling under fast motion).
- Native vs RIFE (`hervor.py --rife`): interpolated frames 0.95–0.96 × the sharpness of their native neighbours (small pulse);
  boil per native step ~0.5, per RIFE half-step ~0.33 → the wobble is in the FastH3 render, not RIFE. Interpolator swap won't fix it.
- Candidate metric `hervor.py` (flow-compensated detail-band residual on textured regions, normalised by detail energy), native:
  halves 0.417/0.505/0.568/0.613/0.583/0.513/0.596/0.509/0.439/0.409/0.411 (f0–109 by 10), original 0.348/0.397/0.491/
  0.708/0.840/0.637/0.536/0.495/0.422/0.392/0.169, (ii) = original ±0.007. Means tie (0.506). It localises the original's
  defect (peak f30–49 = RIFE 0:02 → stairs) and the halves' worse f0–29/f60–109, but scores the halves better f30–59 and can't
  separate (ii) from the original → **fails the user's ranking (halves > original > (ii)); not added to revisar.**
- Eagle: boiling belongs under flicker/permanence in motion mode; add7ababf5e2 marked materials, none of its categories named
  boiling: the checklist should name "texture boiling under motion" explicitly (lead for brainrotdrone's calibration).
**Fix (b) motion blur (vibeship 17:22) + a finding**
- `obturador.py`: per-frame DIS velocity, 180° shutter (samples ±¼ v), ramp 0 at f0/f106 (seams exact); v95 40–127 px/f over
  f30–84 → blur up to ~63 px. RIFE → `clips/oner_placa_obt_rife.mkv` (213 f, start 2.3, end 1.4). hervor 0.506 → 0.451.
  Sent: `ab/oner_placa_vs_obturador{,_1a1}.mp4`, `ab/oner_f30_49_1a1_placa_vs_obturador.png`.
- **The accepted take strobes at f30–50**: the model alternates two renderings of the arcade (pale lit stone f31–32, 34–35, 41–42,
  45–46; dark f30, 33, 36–40, 43–44) while the camera moves smoothly (`screen/estrobo_f30_37.png`). Full-frame luma 37→53→52→39→
  53→55→41…58→68→53→45→62→60→47→37→55→42 (±15, ~40 %). The halves take has no strobe there (luma 45→35 smooth). Blur does not
  fix it. revisar's flicker row reads n/a (static area 0 %), so no current check sees a strobe during a camera move.
- Metric v2 (low-band warp × speed): dropped. Any term that sees this strobe ranks the original worse than the halves take
  (orig lf f40–49 23 vs 2.8), against the user's ranking; the user's "halves worse" is driven by pacing/jerks, the original's
  complaint by the strobe. One scalar can't hold both. Lesson: for a moving camera, a full-frame luma step check
  (|ΔYAVG| frame to frame vs the local trend) catches the strobe; it belongs in revisar as a candidate when the camera moves.
**Deflicker + combined (user 17:34: "motion blur looks better, combine it with the deflicker; some wobbling left in the first seconds")**
- `destello.py` (low band only from flow-warped clean neighbours) fixed luma but not the alternating arcade geometry (+ an
  orange ghost at f41 from the warp). Replaced instead every flash run by RIFE in-betweens of its clean neighbours
  (interp.py MULT=3/4): 31–32 ← 30/33, 34–35 ← 33/36, 41–43 ← 40/44, 45–47 ← 44/48, 49–50 ← 48/51. Luma f24–56 now
  34→46→35 smooth (was ±15). 1:1 fixed-region strip f30–49: the arcade progresses without alternation.
- f0–30: no luma alternation (29→37 monotonic). Source of the early wobble partly (ii): its added layer's flow-compensated
  'pop' rose 0.5–0.75 (f0–7) → 0.8–1.0 (f12–20) → 1.2–1.4 (f22–29) as the NCC gate dropped in and out. (ii) v2 = global fade
  6→14 (`detalle_placa.py ... 6 14`, out/placa_v2): added layer 1.3 → 0.34 by f13, gone f14. Remaining early wobble is the
  model's (cord coil → rod, shimmer as the pan speeds up).
- Combined = (ii) v2 f0–30 + RIFE-fixed flash frames + obturador.py → `clips/oner_combo_v1{,_rife}.mkv` (213 f, start 2.3,
  end 1.4). Sent: `ab/oner_combo_vs_obt{,_1a1}.mp4`, `ab/oner_f0_29_1a1_antes_despues.png`. Waiting: user's word, then Eagle.
**User 17:53: "the combined take looks worse."** Current best stays (ii)+blur (`clips/oner_placa_obt_rife.mkv`, the user's last
positive word). Most likely cause: the RIFE fills. 11 of the 20 frames in f31–50 became in-betweens across 3–4-frame gaps
during a ~36 px/f (1080) pan (108–144 px per gap): soft, dim, low-contrast blends, stacked with the shutter blur. Detail band
f40–49 2.51 → 0.97 (temporal.py hf); per-frame speed stays continuous (17–19 px/f), so it is not a stall. The flicker was
traded for a mushy patch where the stairs open. (ii) v2's fade (f9–14, amplitude ≤ 1 level) is secondary. Again every flow
metric (lf 21.5 → 4.2, jerk 0.72 → 0.47) called it better.

### Lesson of the whole chain (17:00–17:53)
Post fixes cannot repair a strobing/boiling FastH3 take. Each one traded the defect for another the eye minds as much:
plate HF transfer pops as its gate fails; grain adds texture, not shape; a sharpened keyframe re-render changes pacing and
jerks; shutter blur helps but cannot remove flicker; replacing flash frames with interpolations turns a strobe into mush.
The only post step the user liked was the motion blur. Fix it at render time (a seed/setting that doesn't strobe, denser
attention or more steps through the fast part, a slower move, or a shot that keeps the camera off fine texture at speed),
and judge every candidate at full speed by eye: flow metrics, Laplacian and single-frame crops all disagreed with the user
three times today.
**Slow-glide reroll (user 17:55), 1080×107 direct, `prompts/oner_lento_107.txt`, seeds 2/11/12/13 (`oner.sh lento`, 354–375 s
each)**: ends 1.7–1.9 / 1.3–1.4. Gate `puerta_lenta.py` (calibrated: accepted take fails strobe 17.3):
- s2: strobe 16.6 at f76, jerk 1.87 → FAIL. s11: strobe 4.0 ok, jerk 1.03; new wall candle sconces at the gate f72–80 and a
  pale stone arcade f48–57 → reject. s12: strobe 0.9 (best), jerk 1.04 (surge 27.6→40.7→6.3 px/f at f75–85 through the gate);
  f0–60 1:1 steady. s13: strobe 2.8, jerk 1.84 (surge 18→39 at f55).
- **None passes the jerk limit.** The prompt slowed the first half (f0–50 ~10–15 px/f vs 14–21) but the route is the same in
  4.5 s, so the time saved returns as a surge at the gate (peaks 37–43 px/f, above the accepted take's 33). With 107 frames
  fixed, "slow" redistributes speed; it does not lower it. Strobe did improve (3 of 4 under 5).
**Option (d) segments (18:26–19:10)**: A s12 (crypt → s12 f48) slow and even, but dropouts f29–30/34–35/38 → repaired with RIFE
fills → `clips/oner_l2a_s12_rep.mkv` PASSES (strobe 1.5, jerk 0.19). B s12 odd/even judder, fail. Seeds 21/22 for A and B: VOID
(lento2_semillas.sh didn't export INI/FIN → camarín start / cripta end; start 27.5, end 23). Script fixed. Next: reroll B only.
Successor handoff: docs/handoffs/2026-10-14-07-oner-9s-successor.md.
**B reroll (brainrotdrone, 21:40–)**, ends INI=mid_s12_f48 FIN=atrio (all start 1.2–1.3 / end 1.6–2.0 pass). Void s21/s22 PNGs
moved to ComfyUI `output/mto_fasth3/void_l2_s2x/` (same prefix: new frames would have been globbed with them).
- `oner_lento2_b.txt` s21: jerk 1.68 f27, strobe 3.3. s22: jerk 1.78, strobe 36.1 at f48 (gate flash). s23: jerk 1.42, strobe 1.9.
  All dash and park: peak 27–31 px/f at f25–27, ~1–2 px/f from f60 on (prompt puts the gate at 2.2 s, the model rests after it).
- Per-frame DIS (scratchpad vcurva.py, f0–39): **every B seed alternates odd/even** (6/10, 7/11, 8/13 …) from f2; A rep and
  lento s12 f40+ are smooth. The void B (camarín start, B prompt) alternates too, void A does not → the judder follows B's
  prompt, not the start frame. Suspect: "From the first frame the camera is already gliding forward" (A and lento say "starts at
  rest and eases into the move").
- `oner_lento2_b2.txt` (gate at 3.4 s, climb fills 0–3.4 s) s31: motion spread to f80, peak 19.6, jerk 0.92 (from 1.4–1.8),
  strobe 2.3. Odd/even cadence still there (6/9, 5/9) → most of the remaining jerk.
- `oner_lento2_b3.txt` = b2 without "already gliding from the first frame", + "at one constant speed": s41 jerk 1.36, dash and
  park, still odd/even (9/18 → 18/33). s42 interrupted. b2 s32: jerk 1.30, dash and park, odd/even.
- **Correction**: the void B had INI=mid_s12_f48 too (only FIN was wrong), so it shares B's start. What every juddering render
  shares is a single **mid-motion start frame**; every render that starts at rest (A, void A, lento s12) is smooth. Prompt
  wording is not it. Three segments wouldn't help (a middle segment always starts mid-motion).
- Anchor test (downbadship OK, 22:21): `encolar.py` gained `GUIA=<video in input/>` (MiniMaxH3AddGuide clip at f0 instead of
  INI). Guide = A rep f102–106 (`input/oner_l2a_rep_cola5_png.mov`), FIN atrio, b2 prompt, seed 31 → `oner_l2bg_s31`. Join plan
  A f0–101 + B f0–106 = 209 f (8.7 s). B start reference for medir: `in/mid_l2a_rep_f102.png`. If it fails: stop, show b2 s31
  flagged + offer a 22-frame anchor (~8.0 s; user's call).
- **Anchored B `oner_l2bg_s31`**: ends 1.0 / 2.1; alone PASSES (strobe 3.9, jerk 0.60, peak 17.7 px/f, motion carries to f80
  instead of parking at f55). Odd/even still there but weaker (7/11, 6/9 px/f). Join A f0–101 + B (`unir_l2.sh`) →
  `clips/oner_l2g_s31.mkv` 209 f: join smooth (5–7 px/f across f101→102, full frames f100–107 continuous), but the joined take
  **FAILS jerk 1.09 at f130** (joined median 5.8 px/f, so B's odd/even step exceeds 0.6×). Strobe 3.4 ok. Same join with b2 s31
  (no anchor): jerk 1.43, peak 19.6 → the anchored one is the best failing pair. RIFE ×2: `clips/oner_l2g_s31_rife.mkv` (417 f,
  17.4 s). Eagle: hidden-cut + morph FAIL rows, same as every one-take (lento s12, (ii)+blur, 1080 adelante); morph 93/209 f vs
  45/107 s12. eagle-eye run 1dd86933910a (03f3c9364348 superseded: logged before all events were viewed): timing major (odd/even f105–180), boiling major (A: phone dial + stones f75–83, f21–30), morph minor (ceiling peels open f127–131). Per-frame cadence: `cadencia.py`.
  Shown flagged: `ab/oner_l2g_s31_vs_s12_obt.mp4`, `ab/oner_l2g_s31_{nativo,rife}.mp4`, `ab/oner_l2g_s31_f{0_63,100_163}_1a1.png`.

# RunPod session 1, 2026-10-15 (yappingdrone; seed mothership/docs/queue/2026-10-15-runpod-session1.md)
**What was really tested.** Local s3 (cripta → atrio) and s5 (camarín → cripta) were already native 1920×1088 at 107 frames
(PNG metadata); there was no 1440 → 1920 upscale to remove. The pod adds **192 native frames (8 s) instead of 107 + RIFE ×2**.
A new frame count changes the noise, so J1/J2 are new takes with the same seed, prompt (timeline scaled 4.5 → 8 s, as
A_puerta ↔ A_puerta_107) and ends, not de-waved s3/s5. Waviness numbers (`pod/warp_tabla.py` on visual-lab `warp.py`,
warp_hf full frame) are **not verified** against the eye and compare different takes at different speeds.
Pod: H100 80GB HBM3, CA-MTL-1, $3.99/h (RTX PRO 6000 CA-MTL-3: "no instances"). Deploy 22:33:11 → terminate 23:39:37,
**$4.43** (balance 10.00 → 5.57). Setup 361 s (deps 232, models 41 GB in 29 s, ComfyUI 79 s). Jobs `pod/jobs/`, frames
`pod/out/` + ComfyUI `output/mto_fasth3/pod_*`, A/Bs `pod/ab/` (each also as `_1a1` 960×540 crop), logs `pod/pod_logs/`.
| job | what | pod s | revisar | warp_hf med / p90 | read |
|---|---|---|---|---|---|
| J0 | boat 4 s 1 MP smoke | 126 cold (sampling 39) | — | — | SSIM 0.955 vs local: same shot |
| J1 | s3 recipe, 1920×1088×192 | 371 | start 1.7 / end 1.3, black 23 (f65–87), morph 11, **novel 12.3 %** | 0.505 / 0.690 | crypt glide speeds to 12 px/f, street ~static f96–191; a pale light shaft appears f100–110 |
| J1b | same at 1344×768 (≈1 MP) + lanczos (control) | 132 | 1.7 / 1.5, black 35, morph 0, novel 1.9 %, **sharpness-start FAIL 0.35** | 0.538 / 1.159 | soft (upscale); same waviness as J1 in the crypt |
| J2 | s5 recipe, 1920×1088×192 | 367 | 1.8 / 1.5, **hidden-cut FAIL (max 87 % dark f89)**, morph 6 | 0.481 / 0.589 | door → descending passage → crypt; moves 6× faster than s5 at similar warp |
| J3 | one-take, oner_lento ×15 s, seed 12, 362 f | 877 | 2.0 / 1.5, sharpness-end 1.15, strobe 0; hidden-cut + morph FAIL (expected, no blackout) | — | holds to the end (strip f330–361 stable); puerta_lenta jerk 0.66 f260 FAIL (brake at the gate), boil f0–60 0.42; passage stones posterized f244–259 |
| Q | J1 with **base fl2va, 20 steps, dense** (quality arm) | 1172 | 2.2 / 1.6, black 31, **morph 0, novel 0.8 %** | 0.521 / 1.194 | cleanest structure; crypt waviness same as J1; street fully static |
Baselines: s3 107 0.513 / 0.943, s3+RIFE 0.389 / 1.128, s5 107 0.459 / 0.658, s5+RIFE 0.421 / 0.582.
Read: native 192 does not show a waviness drop on the numbers (crypt 0.4–0.66 at 3–12 px/f in J1, J1b and Q alike). Q picked
as the quality arm because the wobble was measured in the FastH3 render (§ native vs RIFE above) and base fl2va dense removes
both the distillation and VSA. eagle.sh: Q exit 0; J3 exit 1 (hidden-cut/morph rows, as every one-take). eagle-eye findings
pass held until the user picks. Sheets for the eye: `pod/ab/J1_vs_s3rife`, `J1b_vs_J1`, `J2_vs_s5rife`,
`J3_vs_lento_s12_rife`, `base20_vs_J1`, `base20_vs_s3rife` (+`_1a1`); strips `pod/ab/J3_tira_f{244-275,330-361}.png`.
