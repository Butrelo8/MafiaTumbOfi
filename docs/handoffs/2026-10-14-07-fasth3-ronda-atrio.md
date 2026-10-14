# Handoff — ticket 07, FastH3 quality round + cripta → atrio (shookdrone, 2026-10-14 10:05 CST)

Seed: `/home/black/projects/mothership/docs/queue/2026-10-14-fasth3-successor.md`, then vibeship's messages (user
decisions relayed). Every number and file: `tmp/07/fasth3/veredicto.md` › "Quality round" and below. Nothing committed.
**Paused by the user (10:02): no new renders until the prep lands** (MTO asset map + visual-lab numbered recipes and
gotchas backlog; then Eagle Eye). ComfyUI is up, queue empty.

## Recipe as I'd number it: transition-fasth3 v1
1. **Ends = graded loop f0** of both rooms (`look/maestros/<sala>_esc.mkv` f0), padded to 1920×1088 by edge replicate
   (4 px top/bottom), under a NEW filename in `ComfyUI/input/mto_fasth3/` (LoadImage caches by name). Pixel-diff the PNG
   against the current master's f0 before every batch (the old cripta end went stale after the phone re-master).
2. **Prompt** in the 4.5 s timeline (`prompts/A_puerta_107.txt`, `C_atrio_107.txt`): glide → occluder fills the frame,
   black "a quarter of a second" → reveal and rest on the final frame; no new objects/lights/people.
3. **Seed screen**: 4–5 seeds at 960×544×**107** (same length as the final), FastH3 8-step, VSA 10 % (`encolar.py`),
   ~85 s each warm. Board + 24 fps grid → the user picks the structure. Reject: people, slid-in panels, mirror changes,
   morph > ~4, black > ~25 native frames. The 1080 take can still move the structure (atrio s3: black f43–60 → f62–84).
4. **Final**: the pick at 1920×1088×107 (~6.5–9 min), then **RIFE 4.26 ×2** (core `FrameInterpolate`,
   `interp.py rife_v4.26`, 35–45 s) → 213 f. GIMM-r (ds 0.5) only if RIFE shows a measurable door/edge defect GIMM fixes
   (user saw no difference on s5).
5. **Measure**: `medir.sh` (`INICIO=`/`FINAL=` for other rooms) → revisar; `detalle.py` for detail while moving; prop NCC
   vs plate (`medir_guitarra.py`, `telefono.py`).
6. **Bent thin props**: paste the plate's prop (`guitarra.py`: GrabCut mask, ECC affine, gain, 180° blur, feather σ 0.88
   measured per masks/RECETA.md; `ECC_MIN`, `HALO`/`HALO_DESDE` when the take's prop sits off the mask near the occluder).
7. **Stopping rule**: done when 2 more seeds don't beat the best on the numbers and by the user's eye. Two native halves
   joined in the black (`ronda.sh mitades`) only on a real defect (morph, bad door).
Not worth it on 12 GB (measured): base H3 fl2va (19.5 min, static camera, 37-f black, less detail);
1600×928×192 with exact_kv (OOM, crashes ComfyUI); GIMM at ds 1.0 (OOM).

## State
- **Camarín → cripta: s5 + RIFE + guitar paste** = `tmp/07/fasth3/clips/s5_rife_guitarra_h20.mkv` (213 f): start 1.6,
  end 1.4, black 25 (f85–109) with no ramp, morph 1; headstock NCC 0.99 f0–73 (raw 0.60/0.28). Sent:
  `ab/s5_guitarra_antes_despues_2x{,_mitad}.mp4`. **Waiting for the user's OK.**
- **Cripta → atrio (replaces Flow job3)**: screen s1–s5 (`screen/atrio_tablero_107.jpg`, s2 has a walking person);
  s1 and s3 rendered at 1080 + RIFE (`clips/atrio_s{1,3}_rife.mkv`). s1: end 1.3, black 14, novel 3.0 %; s3: end 1.2,
  black 46 (long), shows the steps. Sent: `ab/ab_atrio_s1_vs_s3_rife.mp4`. **Waiting for the user's pick.** Phone holds
  by eye; `telefono.py` NCC unusable on these (parallax, blur): check it again on the pick (stabilised strip, as job3's
  `estab.py`). If the pick is s3, the 46-frame black needs a ramp (the camarín recipe: every 2nd frame fading, every 3rd
  in pure black) or two more seeds per the stopping rule.

## Remaining queue (one at a time, one GPU)
1. Cripta → atrio: user pick → phone check/paste if it bends → finals.
2. Sacristía → camarín (job4): same recipe, ends = `sacristia`/nave? loop f0 per the ticket (check `look/armar.sh`).
3. E6–E8, desktop and vertical 9:16.
Then for each locked transition: grade only from the swap on, COSTURA (target loop 228–239 crossfade + 0–19 raw), ladder,
congelar, `public/` (user's OK; H3 licence note for US audiences in the old handoff).

## Files touched (all in `tmp/07/fasth3/`, gitignored tmp)
`encolar.py` (BASE/SINK/INI/FIN, new ends default), `medir.sh` (new end, INICIO/FINAL), `guitarra.py` (σ 0.88, ECC_MIN,
HALO), new `ronda.sh interp.py medir_interp.py ab_s5.sh telefono.py`, prompts `mitad{1,2}_negro.txt C_atrio_107.txt`,
`in/{end_1088_nuevo,end_928_nuevo,negro_1088,start_cripta*,end_atrio*,mascara_tel_cripta}.png`.
Outside: `/mnt/e/ComfyUI/CLAUDE.md` (two gotcha lines), ComfyUI-GIMM-VFI node + pip `cupy-cuda13x[ctk] yacs easydict`,
models `frame_interpolation/rife_v4.26{,_heavy}`, `interpolation/gimm-vfi/*`. Report:
`~/.cache/cc-deck/reports/all/shookdrone-1791985407.md`.
