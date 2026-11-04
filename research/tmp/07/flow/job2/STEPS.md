# STEPS — Google Flow job2 (camarín → cripta, retry), for a browser drone

The user approved **one** retry (2026-10-13 05:57). **ONE generation, 20 credits.** Never Retry, Regenerate, Extend,
Upscale or "Always approve". If anything does not match what you see, STOP, take a screenshot into the output
folder and report instead of guessing. **The user presses send and Approve** (the auto-mode classifier blocks the
drone from doing both); you prepare everything up to that point and then ask them to do it.

Why a retry: in job1 the jackets never filled the frame, and the crypt morphed in behind them
(`tmp/07/flow/job1/veredicto.md`). This prompt forces full black for about half a second, a sideways-only move and
no new objects or lights.

Files (the frames are identical to job1's):

| File | Upload from (Windows) | Copy in the repo (WSL) |
|---|---|---|
| start frame | `C:\Users\black\Downloads\flow-job2\start.png` | `/mnt/e/Cursor Projects/MTO/tmp/07/flow/job2/start.png` |
| end frame | `C:\Users\black\Downloads\flow-job2\end.png` | `/mnt/e/Cursor Projects/MTO/tmp/07/flow/job2/end.png` |
| prompt | `C:\Users\black\Downloads\flow-job2\prompt.txt` | `/mnt/e/Cursor Projects/MTO/tmp/07/flow/job2/prompt.txt` |
| output | — | `/mnt/e/Cursor Projects/MTO/tmp/07/flow/job2/out/` |

If the browser tool refuses the upload path because it is outside the session's folders, ask the user to run
`/add-dir C:\Users\black\Downloads\flow-job2` (or the WSL path) and wait.

## 0. Account and balance (hard stop)

1. Open `https://labs.google/fx/tools/flow`, wait for the page to finish loading, then take a screenshot.
2. Open the avatar menu and **zoom the screenshot** to read it (a half-scale screenshot misread 90 as 50 in job1).
   The account must be **av.ivan.8** (`/u/1/` in the URL).
3. The balance must be **70**, or a higher number only if Flow states that the extra is the daily free credits.
   Any other account (for example bube.ncio8, `/u/0/`), a balance below 70, or a higher balance you cannot explain
   → STOP and report. Never switch accounts on your own.
4. Write `before: <number>` as the first line of `out/credits.txt`.

## 1. New project, attach the frames

1. Create a **New project**. It opens the chat-agent panel (there is no Frames to Video bar any more). Do **not** use
   the top "+" → New scene: it only creates an empty scene.
2. In the chat box, click **"+" → Add ingredients → Upload media** and attach `start.png`, then repeat for
   `end.png`. One file at a time, start first.
   - With claude-in-chrome, "Upload media" has no file input until it is clicked, so `file_upload` fails with
     "Element is not a file input". Workaround from job1: in `javascript_tool`, patch `HTMLInputElement.prototype.click`
     so the created input is appended to `document.body`; click Upload media, find the input's ref and `file_upload`
     to it. No native dialog opens.
3. Check the two thumbnails in order: first = a candlelit dressing room with a gold mirror and a guitar on a chair;
   second = a stone crypt with a gold telephone under a light beam.

## 2. Type the request (do not send)

Type this into the chat box exactly, with the full contents of `prompt.txt` pasted after "Prompt:" on one line:

```
Generate one video with Veo 3.1 Fast, 8 seconds, 720p, 16:9, x1 (one output). Use the first attached image as the start frame and the second attached image as the end frame. Prompt: <contents of prompt.txt>
```

Take a screenshot of the chat box with both thumbnails and the text, save it as `out/request.png`, then ask the user
to **press send**.

## 3. The confirm card

The agent replies with a confirmation and a card with **Approve / Always approve / Reject** and a cost.

- The card must show **Veo 3.1 Fast** and **20** credits (8 s, 720p, one output). If the model is different, the
  cost is not 20, or there is more than one output → have the user press **Reject**, then STOP and report.
- **Never** choose "Always approve". Keep the agent setting "Confirm before generating: Always": it is the spend
  guard.
- If the card is right, write `cost shown: 20` to `out/credits.txt` and ask the user to press **Approve**.
- If the generation fails or is refused: screenshot to `out/error.png` and STOP. **Do not retry.**

## 4. Download

1. The download icon on the clip in the grid does nothing visible. Open the clip (URL `/edit/<id>`), then use the
   download icon at the top right → **720p Original size**. Never "1080p Upscaled" (it is a paid upgrade).
2. The mp4 lands in `C:\Users\black\Downloads\` as a Chrome `*.tmp` file; it is a valid mp4. Take the newest one and
   check it before moving it:
   ```bash
   ls -t /mnt/c/Users/black/Downloads/*.tmp | head -3
   ffprobe -v error -show_entries stream=codec_type,width,height,r_frame_rate:format=duration -of csv=p=0 "<newest>.tmp"
   mv "<newest>.tmp" "/mnt/e/Cursor Projects/MTO/tmp/07/flow/job2/out/job2_flow.mp4"
   ```
   Expect 1280×720, 24 fps, 8.0 s plus an audio stream. A .tmp that ffprobe cannot read is a partial download:
   leave it and report it.
3. Read the balance again (zoom) and add `after: <number>` to `out/credits.txt`.

## 5. Report

One line per item: the mp4 path and its ffprobe output, credits before/cost/after, and anything that did not match
these steps. Do not judge or edit the clip; the scene drone compares it with job1 and with the plates.
