# Handoff: ticket 07, cripta → atrio one-take, the longer version (rizzdrone, packed 2026-10-14 21:35 CST)

For a fresh `visual` drone, readable cold. All work files are in `tmp/07/fasth3/` (gitignored); every number is in
`tmp/07/fasth3/veredicto.md` from "One-take screen 2026-10-14" on. Earlier handoff: `docs/handoffs/2026-10-14-07-oner-screen.md`.
ComfyUI queue is empty; nothing is running.

## Goal (the user's choice (d), 18:26)
A longer cripta → atrio one-take with no blackout: the same route as the accepted take (crypt → right-hand archway → steps →
lit arch with an open iron gate → street, ending on the atrio loop's f0 framing). It is built as **two native 107-frame FastH3
renders joined through frame 48 of `oner_lento_s12`** (213 native frames = 8.9 s at 24p with no RIFE, or 17.7 s with RIFE
×2). The user's words: "go with d, the longer 9 s transition; 3 if necessary; we can increase speed ourselves if any". They'd
rather retime faster in post than see a speed surge. If two segments still surge at the gate, use three (two s12 frames).
Note: every video shown to the user today was RIFE ×2 (213 f at 24p = 8.9 s). I first told them 4.5 s, then corrected it.

## User rules (from vibeship/downbadship relays)
- Show the user only takes that pass the gate (up to 3), beside the current best. No post fixes on new takes until they pick.
- **Current best = (ii)+blur**: `clips/oner_placa_obt_rife.mkv`. It's the accepted 1080 take + plate detail transfer + 180°
  flow blur. It still strobes at native f30–50 (the strobe can't be fixed in post; see the lessons below).
- Stop before grade / COSTURA / `public/`. One GPU job at a time; check the ComfyUI queue and `nvidia-smi.exe` first.
- If a take is too slow, offer a uniform retime (×1.25/×1.5, RIFE frames kept), not new renders.

## Gate: `tmp/07/fasth3/puerta_lenta.py <clip.mkv>...`
- Strobe: max |full-frame YAVG − 7-frame median trend| ≤ 5. The accepted take scores 17.3, so it fails.
- Jerk: max |Δ median DIS flow| ÷ median moving speed ≤ 0.6.
- Boil (`hervor`): printed for information only. It did NOT reproduce the user's ranking.
- Plus: join speed continuity ±10 % (check by hand from the speed curve around the join frame), and a 1:1 full-rate strip of
  f0–60 (crop 320×270 at 800,300; see veredicto for the ffmpeg line).
- Ends: `medir.sh <prefix>` with `INICIO=`/`FINAL=` exported (default ends are the camarín's!).

## State of every segment (both pinned to `in/mid_s12_f48_1088.png` = s12 f48, the slowest, steadiest frame, 11.2 px/f)
| piece | file (clips/) | ends | gate | note |
|---|---|---|---|---|
| A s12 (crypt → f48) | oner_l2a_s12.mkv | 1.7 / 1.5 | FAIL strobe 14.3 | slow, even, 5–6 px/f; 1-frame dark dropouts at f29–30, 34–35, 38 |
| **A s12 repaired** | **oner_l2a_s12_rep.mkv** (PNGs `out/l2a_s12_rep/`) | as A s12 | **PASS** (strobe 1.5, jerk 0.19) | dropouts replaced by RIFE in-betweens (28→31, 33→36, 37→39; outputs `a12_*` in ComfyUI output). Not yet shown to the user |
| B s12 (f48 → atrio) | oner_l2b_s12.mkv | 1.2 / 2.0 | FAIL jerk 1.42 | odd/even judder (6↔10 → 12↔23 px/f): not repairable, reseed |
| A s21, A s22, B s21, B s22 | oner_l2{a,b}_s2{1,2}.mkv | start 27.5 / end 23 FAIL | — | **VOID**: rendered with the wrong ends (the script didn't export INI/FIN; fixed now). Ignore, don't use |
Joined s12 (A+B, unrepaired): `clips/oner_l2_s12.mkv` (213 f), FAIL.

## Exact next step
1. Reroll **B only** with the correct ends: `cd tmp/07/fasth3 && ./lento2_semillas.sh 21 22` renders both A and B. To save
   ~13 min, comment out the A line and render B only (prompt `prompts/oner_lento2_b.txt`, ~6.3 min/seed at 1920×1088×107).
2. Gate each B (`puerta_lenta.py`); also check B's first frames continue A's speed at the join (A ends ~6–7 px/f at f100–106).
3. Join A s12 repaired (107) + the passing B without its f0 (106) = 213 native. Gate the joined take, then RIFE ×2
   (`interp.py rife_v4.26`, about 1 min). Show the user: native 8.9 s and RIFE 17.7 s, beside s12 (`oner_lento_s12_rife`)
   and (ii)+blur, at full speed, plus a 1:1 f0–60 strip. Offer the retime. Then wait.
4. If no B passes after ~4 seeds, ask (via the mothership) whether to show the best failing pair, flagged, or go to three segments.

## User verdicts today (their words)
- Screen pick: "b adelante s2 73 has the best animation" (f73). The 1080 render changed the route, so f73 was lost; the user accepted the 1080 path.
- 1080 take: "the seed is good but it presents a lot of details lost between first part of the transition."
- Plate transfer ± grain: "still distorted frames from 0:02 all the way till the stairs, just a little less".
- Halves through a Z-Image still: "is worse now every frame now".
- Diagnosis question: "warping and wobble, the stones keep moving. All complicated textures in the wall, phone, are wobbling when a fast motion goes by."
- (ii)+blur: "motion blur looks better, combine it with the deflicker; we still have some wobbling left in the first seconds."
- Combined (deflicker + blur + faded plate): "the combined take looks worse."
- Slow reroll s12: they picked (d), quoted above.

## Lessons (also in visual-lab `comfyui/recipes/transition-oner-v1.md`)
- The 960 screen picks a prompt+seed, not a path: the 1080 render takes another route.
- Post can't repair a strobing/boiling FastH3 take. Fix it at render time; judge at full speed by eye. Flow metrics, Laplacian and single-frame crops disagreed with the user three times.
- With 107 frames fixed, prompting "slow" redistributes speed (slow start, surge at the gate); a longer clip is the fix.
- One-frame dropouts at a slow pace (5–6 px/f) repair cleanly with RIFE in-betweens; at a fast pan (~36 px/f) they turn to mush.
- Strobe check for moving cameras: grindsetdrone (visual-lab Eagle round 3) has this take as its test case.

## Scripts (tmp/07/fasth3/)
`oner.sh` (stages A, B, final, mitad1, zmitades, lento, lento2; it exports the cripta/atrio ends), `lento2_semillas.sh` (segment
reroll, now exports the ends), `encolar.py` (FastH3 FL2V; INI/FIN pick the end PNGs in ComfyUI `input/mto_fasth3/`),
`interp.py` (RIFE; `MULT=` sets the factor), `medir.sh` (glob `${p}_?????_.png`), `puerta_lenta.py` (gate), `tira.sh`
(full-rate strip), `hervor.py`, `temporal.py`, `detalle_curva.py`, `detalle_placa.py` ((ii)), `obturador.py` (180° blur),
`destello.py`, `grano_valle.py`, `zrefine_mid.py`, `fiel.py`. Prompts: `prompts/oner_lento_107.txt`, `oner_lento2_{a,b}.txt`.
ComfyUI outputs: `/mnt/e/ComfyUI/ComfyUI/output/mto_fasth3/<prefix>_NNNNN_.png`.
Eagle ledger: be8ff46e2c12, cbfdf58bdba0 (screen, unjudged), add7ababf5e2 (1080, #1 real, not blind).
