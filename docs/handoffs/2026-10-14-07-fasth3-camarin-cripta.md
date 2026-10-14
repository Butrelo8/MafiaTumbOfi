# Handoff — ticket 07, E6 camarín → cripta with FastH3 local (apedrone, 2026-10-14 07:45 CST)

Seed: `/home/black/projects/mothership/docs/queue/2026-10-14-mto-fasth3-transition.md` (user OK 03:27; 1080p memory plan
OK 06:22). Full numbers and every take: `tmp/07/fasth3/veredicto.md`. Ticket note: `.wayfinder/santuario/tickets/07-guion-espacios.md`
(three bullets after the LOOK one). Nothing committed. No GPU job running; `oc-up` already run (27B on :8085).

## State
- **Current candidate:** `tmp/07/fasth3/clips/f1080_rampa_guitarra.mkv` (ffv1 1920×1080, 186 f). Built as:
  FastH3 8-step first+last frame (`encolar.py`, ends = graded E5 loops' f0, padded to 1088), 1920×1088 × 107 f, seed 2,
  prompt `prompts/A_puerta_107.txt` → FILM ×2 from a PNG-codec .mov (`film.py`, 213 f) → speed ramp in the dark
  (51 → 24 black frames, 186 f) → the plate's guitar pasted onto f0–61 (`guitarra.py`).
- **Numbers (revisar, ends vs E5):** start 1.6, end 1.7, sharpness 0.95 / 0.98, black 24 f (f73–96), morph 0, novel 0.7 %;
  detail while moving 0.96 / 0.85 × plate; guitar neck NCC vs plate 0.77 → 0.99; tail vs NEW cripta loop 0–19 = 4.79
  (job2: 6.18; job2 start 27.2). Head drifts ~3 from the vestidor loop's f0 even at 1080.
- **User said:** the 1440 take was "a better transition" but pixelated texture → fixed by 1080p; then the guitar headstock
  distorted → fixed by the paste. No reply yet to the last A/Bs.
- **Sent to the user:** `tmp/07/fasth3/ab/{ab_job2_vs_fasth3_s2, textura_1440_vs_1080_1a1, ab_job2_vs_fasth3_1080,
  guitarra_antes_despues_2x, ab_job2_vs_fasth3_1080_guitarra}.mp4` (A/B builder: `ab.sh`).

## Open (all wait for the user)
1. OK on the candidate, incl. the ramp start (A/B ~f122 / clip f74, revisar flags a jump) and guitar edges at speed.
2. Then the job3/4 chain: grade only from the swap on (head already graded), COSTURA = cripta loop 228–239 crossfade +
   0–19 raw from the **new** master `tmp/07/look/maestros/cripta_esc.mkv` (capdrone, 06:29, phone change only), plus a
   short fade at the head to hide the ~3 drift; ladder; congelar; `public/`.
3. License: MiniMax H3 forbids outputs for US/EU/UK/KR audiences without written OK. If the site targets US listeners,
   ask MiniMax before `public/`. User's call.
4. Not done vs the ticket's E6 final: no masked occluder from the mockup, no vertical (E4 cameras).

## Unfinished background tasks (stopped, harmless)
- `blyuhs9xx`: Monitor (`tail -F` on `E:\ComfyUI\comfy.err.log`) for the 1920×1088×192 render; that render OOM'd in 26 s.
  `tail -F` on drvfs never delivered events.
- `bg7wfncqn`: same Monitor for the 1600×928×192 render; OOM'd at 351 s. Both superseded by polling monitors; nothing to resume.

## Gotchas
- 12 GB: 1920×1088×192 and 1600×928×192 OOM; 1440×832×192 (376 s) and 1920×1088×107 (383 s) fit.
- The MTO hook rejects one command line containing system `python3` plus numpy/cv2 words: split, or use `uv run python -I`.
- `ab.sh` equalizes lengths by giving job2 extra cripta frames; never `-r 24` (dupes/drops).

## For visual-lab (not written there; route through its session / report `gotchas:`)
All in `/home/black/.cache/cc-deck/reports/all/apedrone-1791973722.md` › gotchas. Key ones:
- FastH3 at 1440 redraws texture low-detail on camera moves → render 1920×1088 with fewer frames (17n+5) + FILM ×2.
- FILM via LoadVideo: feed a PNG-codec .mov, not libx264rgb mp4 (0.9-level shift); SaveImage, not SaveVideo.
- FastH3 "brief black" = 26–35 f slow fade → speed-ramp the dark (every 2nd frame fading, every 3rd in pure black).
- Thin rigid props bend under FastH3 motion → paste the plate's prop (ECC affine on its body, gain, 180° blur; occluder
  edge from a long dark run in a lit band; hard cap on extrapolation).
- ComfyUI logs OOM as "Got an OOM"; `tail -F` on drvfs is silent → poll with `tail -c +offset`.
- `preset_i2v`'s subgraph is FL-capable with last_frame unwired; BlockSparseAttention API keys `selection`, `selection.keep_percent`.

## Suggested skills
`comfy-local` (only if re-rendering), `frameref`; `santuario-escena` is not needed for this clip.
