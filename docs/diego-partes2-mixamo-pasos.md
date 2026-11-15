# Browser steps: Mixamo rig + four clips for Diego rebuilt from parts (2026-11-14)

## Retry (22:45): rig the proxy instead

The first run (frfrbrowser-1794716583) did step 0 (`old_Idle.fbx` = "Standing Idle") but the Auto-Rigger bounced
`diego_partes2.fbx` twice (274k faces, four overlapping shells joined, no error shown). Retry steps 1 and 2 with a
**rig proxy**: the same skin voxel-remeshed into one closed surface, 90k faces, no textures (grey in Mixamo):

- Upload FBX (1.9 MB): `E:\Cursor Projects\MTO-skibididrone\blender\assets\reparto\partes2\mixamo\diego_partes2_proxy3.fbx`
- Same frame, so **the same markers** (table below) and the same guide image apply.
- **The owner places the markers himself** (owner, 22:36). The drone uploads, then STOPS at the marker screen and
  waits; the marker table and `diego_partes2_markers.png` are the owner's reference. After the owner rigs, the drone
  downloads the rig and the clips.
- It is under the 10 MB `file_upload` cap; if the tool still refuses the path, the owner picks it by hand.
- Name the rig download `diego_partes2_proxy3_mixamo.fbx`; the four clips as in step 2 (`p2_*.fbx`), downloaded on
  this proxy character. Skip step 0 (done).

For the Windows browser drone, in the owner's Chrome, signed in to Mixamo. Never type account details; if a login is
asked, stop and report. Same settings as the 11-14 run (`coldbrowser-1794702965`), except where marked **new**.

## Files

- Upload FBX (14.0 MB, 206,161 verts, 274,835 faces, 1.0 m frame, Y-up, faces front, textures embedded at 1024²):
  `E:\Cursor Projects\MTO-skibididrone\blender\assets\reparto\partes2\mixamo\diego_partes2.fbx`
- Marker guide (1024 × 1280): `E:\Cursor Projects\MTO-skibididrone\blender\assets\reparto\partes2\mixamo\diego_partes2_markers.png`
- Plain front view: `E:\Cursor Projects\MTO-skibididrone\blender\assets\reparto\partes2\mixamo\diego_partes2_front.png`
- The file is over Claude in Chrome's 10 MB `file_upload` cap, so **the owner picks the file by hand** in Mixamo's
  upload dialog, as last time.

## 0. First, while the OLD Diego is still the active character (**new**)

If `diego_rerig` (uploaded 11-14 ~19:00) is still the active character: search **"Idle"**, pick the plain standing
breathing idle (write down its exact name), tick In Place if offered, and download it: FBX Binary, **With Skin**, 30 fps,
Keyframe Reduction none. Rename the download to `old_Idle.fbx`. If `diego_rerig` is no longer active, skip this step
and say so; do not re-upload it.

## 1. Upload and rig the new character

- Upload Character → the owner drops `diego_partes2.fbx`. The model is a bald body in white briefs with spread-finger
  hands, front-facing, upright, A-pose (arms ~30° below horizontal, palms down, thumbs forward). No rotation should be
  needed.
- **Markers** (Diego faces you, so his left is on the screen's right). Guide pixels in `diego_partes2_markers.png`:
  soles at y = 1222, head top at y = 86 (the head is 1.0 m tall; heights below are fractions from the soles).

  | marker | guide px | height | side offset | where on screen |
  |---|---|---|---|---|
  | chin | (512, 525) | 60 % | 0 | centre line, where the jaw meets the neck |
  | groin | (512, 927) | 25 % | 0 | centre line, the crotch of the white briefs, where the legs part |
  | wrists | (213, 737) / (810, 735) | 42 % | ±25.6 % | the narrow ring where the forearm meets the palm (just before the hand widens) |
  | elbows | (281, 696) / (742, 694) | 45 % | ±19.8 % | on the arm's centre line, halfway armpit → wrist (estimate: no crease) |
  | knees | (441, 1029) / (580, 1031) | 18 % | ±5.8 % | middle of each leg, halfway crotch → ankle (estimate) |

- **Skeleton LOD: Standard Skeleton (65)** (the default, with finger bones). Use Symmetry on.
- After rigging, write down whether the preview's hands show **separate fingers bending** (one still close-up of a hand
  in the preview). This is the point of the new mesh: the old one got one chain per hand.
- Download the rig: FBX Binary, Pose **Original Pose (.fbx)**, With Skin. Rename it to `diego_partes2_mixamo.fbx`.

## 2. Four clips on the new character

Search each by its exact name from the 11-14 run, take the same result, tick In Place if offered, leave the sliders at
their defaults (Guitar Playing: Style 100, Guitar Position 100), and download: FBX Binary, With Skin, 30 fps, Keyframe
Reduction none. Rename each download (the old files of the same name are in Downloads):

| search | pick | rename to |
|---|---|---|
| Sitting Drinking | "Sitting Drinking" (the seated one) | `p2_sitting_drinking.fbx` |
| Driving | "Driving" | `p2_driving.fbx` |
| Guitar Playing | the first "Guitar Playing" result (standing strum) | `p2_guitar_playing.fbx` |
| Idle | the same idle as in step 0 (**new**) | `p2_idle.fbx` |

## Report

≤ 6 lines: the Windows path of each file, the exact idle name, the finger-bone observation, rig time, and one
screenshot path of the placed markers. `paths:` line with every file.
