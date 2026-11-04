# Seedance API test 2: pair A on 1.5 pro free tokens, one-sentence prompt (2026-10-18)

Seed: `mothership/docs/queue/2026-10-18-seedance-15pro-free.md`. Submit script:
`/home/black/projects/visual-lab/comfyui/skills/seedance/submit.py` (`--dry-run` first; `--only A15`).
Status: failed (dropped 2026-10-18 02:40: the account cannot call 1.5 pro, 404 below; the mothership reports 1.0 pro is
unavailable too). Replaced by run A1s in `runs.md`: the same one-sentence prompt on 2.0 mini, paid ($0.38).

**Question.** Test 1 (`runs.md`) ran pair A on 2.0 mini with a ~165-word block prompt that described the end frame, and
the clip drew that text and never reached `last_frame`. A15 keeps the same pair and sends one motion sentence with no
end-frame text, in the strict shape of BytePlus's own first+last-frame examples (playbook
`visual-lab/comfyui/seedance-prompting.md` › "When to use Seedance", point 3). It runs on 1.5 pro, whose free quota
(2M tokens) makes it $0.

**Confound, stated before the run.** A15 changes both the model (mini → 1.5 pro) and the prompt (block → one sentence)
against A, so one clip cannot say which one mattered. The 1.5 pro A2 run (`../seedance/medicion.md`) is not the same pair:
it started on the closed wardrobe door, not the camarín. A15 is the first 1.5 pro run on A's exact frames. The free
control that isolates the prompt inside 1.5 pro is A's block prompt on 1.5 pro (proposed after A15, not run).

**Parameters (in the body, never in the text):** `seedance-1-5-pro-251215`, 480p (864×496), 5 s, `ratio: adaptive`,
`generate_audio: false`, `watermark: false`, `return_last_frame: true`, strict `first_frame` / `last_frame` roles, no
seed (random, as A). Estimate from `clipcost.py`: 50,220 tokens (×$1.2/M = $0.060 if it billed; A came in 0.8 % over
its estimate because it had 121 frames, not 120).

## References: what A15 matches and what it changes on purpose

- **Ends:** the same plates as A, from the 1920×1080 originals `../fasth3/in/start.png` (camarín) and
  `../fasth3/in/start_cripta.png` (cripta). 1.5 pro's 480p 16:9 output is 864×496 (aspect 1.742), not 16:9 (1.778). The
  anchors are scaled to 882×496 (`flags=area`) and centre-cropped 9 px a side to 864×496 (`camarin_864.png`,
  `cripta_864.png`), so the prep adds no stretch. A squash would have built a 1.0207 x-stretch into the anchors, which
  is the 2.07 % stretch A2 measured, and the landing row could not tell the model's stretch from ours.
- **Changed on purpose:** the prompt (one sentence, nothing from the end frame), the model and the resolution
  (480p, the cheapest free tokens). Everything else is A's body.

## Prompt drafts (one camera move each, R7; only things in frame 1, plus darkness)

| Draft | Text | Kept? |
| --- | --- | --- |
| 1 | One continuous shot: the camera glides slowly to the right into the dark open wardrobe, passes through black, and slows to a stop. | **Kept.** It is the approved take's path (glide right through the wardrobe into black), it names only frame-1 content, and "passes through black" gives the black beat a motive inside the move. |
| 2 | One continuous shot: the camera glides slowly to the right through the dark room. | Dropped: nothing motivates the black beat, and an unmotivated change tends to read as the dissolve revisar flags. |
| 3 | The open wardrobe's door swings shut across the lens as the camera glides slowly to the right. | Dropped: two motions (door + camera), and the door swing invites a door frame that is in neither plate (playbook risk note). |

## Run A15

```json
{"name": "A15", "model": "seedance-1-5-pro-251215", "resolution": "480p", "duration": 5,
 "first": "camarin_864.png", "last": "cripta_864.png", "cost_usd": 0.06}
```

```text
One continuous shot: the camera glides slowly to the right into the dark open wardrobe, passes through black, and slows to a stop.
```

## Measurement plan (same rows as A, all at 864×496)

A's numbers in `runs.md` were taken at 1280×720. For a fair A15 vs A, the A clip (mini) and the approved take
(`../fasth3/partido/clips/partido_A_s2s3_rife_telk0f.mkv`) are re-measured at 864×496 with the same area-downscale +
crop (scale to 882×496, crop 9 px a side). Nothing is upscaled.

| # | Check | Tool | Pass |
| --- | --- | --- | --- |
| 1 | revisar | `scripts/revisar.sh <A15.mp4> --inicio camarin_864.png --fin cripta_864.png` | 0 FAIL; end ≤ 4 |
| 2 | Landing | ECC affine, last frame vs `cripta_864.png` (`medir_15.py`) | scale x/y within ±0.5 %, centre < 2 px |
| 3 | End diff | mean 8-bit / % px > 8, last frame vs `cripta_864.png` | ≤ the approved take's |
| 4 | Invented scenery | revisar's novel-colours row | ≤ the approved take's |

Before measuring: `usage.completion_tokens` against 50,220, and the frame count with ffprobe.

## Results

**Submit 1 (2026-10-18 02:34): refused, nothing created or billed.** HTTP 404
`InvalidEndpointOrModel.NotFound`: "The model or endpoint seedance-1-5-pro-251215 does not exist or you do not have
access to it" (request id 0217923124780104e5823ec317b6ea9d3f5e181cf6332a558a22c; row in `seedance_log.jsonl`). The ID
matches every BytePlus page in the research, so the likely cause is that 1.5 pro is not activated on this account
(Model Activation). That is a guess until the console is checked.

(pending: activation, the run, then the user's billing check in the console)
