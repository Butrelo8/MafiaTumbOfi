# STEPS — Google Flow job1 (camarín → cripta), for a browser drone

Follow these steps in order. **Budget: the user has 90 credits. You make ONE generation. Never press Generate a second
time, and never use Retry, Regenerate, Extend, Jump to, Upscale or Add to scene.** If anything below does not match
what you see, STOP, take a screenshot into `out/`, and report instead of guessing. Flow's labels change between
versions: where a label is given with alternatives, any of them is fine; anything else is a stop.

Files (job folder `tmp/07/flow/job1/` in the MTO repo):

| File | WSL path | Windows path (for the browser's file dialog) |
|---|---|---|
| start frame | `/mnt/e/Cursor Projects/MTO/tmp/07/flow/job1/start.png` | `E:\Cursor Projects\MTO\tmp\07\flow\job1\start.png` |
| end frame | `/mnt/e/Cursor Projects/MTO/tmp/07/flow/job1/end.png` | `E:\Cursor Projects\MTO\tmp\07\flow\job1\end.png` |
| prompt | `/mnt/e/Cursor Projects/MTO/tmp/07/flow/job1/prompt.txt` | `E:\Cursor Projects\MTO\tmp\07\flow\job1\prompt.txt` |
| output folder | `/mnt/e/Cursor Projects/MTO/tmp/07/flow/job1/out/` | `E:\Cursor Projects\MTO\tmp\07\flow\job1\out\` |

Both frames are 1920×1080 PNG (16:9).

## 0. Account (hard stop)

Chrome has two Google accounts. This job runs **only** on the account `av.ivan.8` (`/u/1/` in the URL, **90
credits**). If Flow opens on any other account (for example `bube.ncio8`, `/u/0/`, 50 credits), or the balance
shown is anything other than 90, STOP and report. Do not switch accounts by yourself and do not continue on another
account.

## 1. Open Flow

1. Open `https://labs.google/fx/tools/flow`. If it asks you to sign in, STOP and report (the user has to sign in).
2. Read the credit balance (top right, or in the profile/account menu). Write it as the first line of
   `out/credits.txt`: `before: <number>`. If it is not 90 (step 0), STOP.
3. Create a **New project**.

## 2. Set up frames to video

1. In the prompt bar, open the mode menu and choose **Frames to Video** (alternatives: "Frames to video",
   "Start and end frames"). Not "Text to Video", not "Ingredients to Video".
2. Click the **first frame** slot (left "+") → Upload → pick `start.png`. If a crop dialog appears, choose
   **Landscape / 16:9**, leave the crop box covering the whole image, and confirm ("Crop and save" or similar).
3. Click the **last frame** slot (right "+") → Upload → pick `end.png`, same crop rule.
4. Check the thumbnails: first = a candlelit dressing room with a gold mirror and a guitar on a chair; last = a stone
   crypt with a gold telephone under a light beam. If they are swapped, swap them back (or remove and re-upload).

## 3. Settings (before typing the prompt)

Open the settings panel (tune / sliders icon next to the prompt bar) and set:

| Setting | Value | If not available |
|---|---|---|
| Model / quality | the option with **Fast** in its name (e.g. "Veo 3.1 - Fast") | STOP: never pick "Quality" (it costs several times more) |
| Outputs per prompt | **1** (the default is often 2 or 4) | STOP |
| Aspect ratio | **Landscape (16:9)** | STOP |

Take a screenshot of the open settings panel and save it as `out/settings.png`.

## 4. Prompt and generate (once)

1. Paste the full contents of `prompt.txt` into the prompt box, verbatim (one paragraph, no changes).
2. Before clicking, read the credit cost shown on or near the Generate button. Add it to `out/credits.txt` as
   `cost shown: <number>`. If it is higher than the balance, or above 30, STOP and report.
3. Click **Generate** (arrow button) **once**.
4. Wait for the clip to finish (usually 1–3 minutes). Do not click anything else in the prompt bar while it runs.
   If it fails ("couldn't generate", policy message, error), screenshot to `out/error.png` and STOP: do **not** retry.

## 5. Download

1. Hover the finished clip → **Download** (download arrow, or the "⋮" menu → Download).
2. Choose **Original size** (usually 720p). If a larger size ("Upscaled", "1080p") is offered **for free** you may
   also download it; if it shows a credit cost or you cannot tell, skip it.
3. The browser saves to the Windows Downloads folder. Move the file into the job folder:

   ```bash
   ls -t /mnt/c/Users/black/Downloads/*.mp4 | head -3
   mv "/mnt/c/Users/black/Downloads/<newest file>.mp4" "/mnt/e/Cursor Projects/MTO/tmp/07/flow/job1/out/job1_flow.mp4"
   ```
   If you also took the larger size, save it as `out/job1_flow_1080.mp4`.
4. Read the credit balance again and add `after: <number>` to `out/credits.txt`.
5. Check the file: `ffprobe -v error -show_entries stream=width,height,r_frame_rate:format=duration -of csv=p=0
   "/mnt/e/Cursor Projects/MTO/tmp/07/flow/job1/out/job1_flow.mp4"` and paste the output into your report.

## 6. Report

One line per item: path of the mp4, its size/fps/duration, credits before/after/cost, and anything that did not
match these steps. Do not judge or edit the clip; the scene drone compares it with the H3 version.
