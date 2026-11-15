#!/bin/bash
# parts_klein.sh <out dir> [part ...]: Diego's per-part images with Klein (preset_edit, Lanczos input), two seeds per part.
# Inputs: diego.png, plus in/diego_{head,hand}_crop.png from crops.py. Every input gets its own file name (LoadImage cache).
set -u
OUT=$1; shift; IN=$(dirname "$OUT")/in; SRC="/mnt/e/Cursor Projects/MTO/comfy-out/para-subir/diego.png"
G=~/.claude/skills/comfy-local/scripts/gen.sh
KEEP="Keep the exact same camera, framing, scale, position, soft clay 3D cartoon style, lighting and the plain light grey background."
declare -A P I
P[body]="Remove his t-shirt, trousers, necklace, sneakers and hair. Show the same cartoon man wearing only plain white briefs, barefoot, with a smooth bald head. Keep the exact same pose with the arms out, the same body proportions, face and skin color. $KEEP"
I[body]=$SRC
P[head]="Remove the hair completely, leaving a smooth bald skin-colored scalp, and remove the necklace and the t-shirt so only the head and a short neck remain. Make the upper eyelids clearly sculpted 3D lids that stick out over the eyeballs. Keep the face, eyes, eyebrows, nose, mouth, ears and skin color the same. $KEEP"
I[head]=$IN/diego_head_crop.png
P[hair]="Show only his dark hair, as a hollow hairpiece seen from the front: remove the face, ears, head, body and clothes completely. Keep the hair's exact shape, color, size and position. $KEEP"
I[hair]=$SRC
P[shirt]="Show only the black t-shirt as worn by an invisible person (ghost mannequin product shot): remove the head, hair, arms, hands, necklace, trousers, shoes and the whole body. Keep the t-shirt's exact shape, size, sleeves, color and position, with the open neck and sleeve holes. $KEEP"
I[shirt]=$SRC
P[pants]="Show only the black trousers with the rolled cuffs as worn by an invisible person (ghost mannequin product shot): remove the head, hair, t-shirt, arms, hands, shoes and the whole body. Keep the trousers' exact shape, size, color and position, with the open waist. $KEEP"
I[pants]=$SRC
P[shoes]="Show only the pair of white sneakers: remove the person, the trousers and everything else. Keep both sneakers' exact shape, size, color and position on the floor. $KEEP"
I[shoes]=$SRC
P[hand]="Show a single cartoon left hand on its own, seen from the back with the palm facing away from the camera, fingers pointing up, all five fingers spread wide apart with clear gaps between them, the thumb out to the side, and a short wrist stub cut flat at the bottom. Same skin color and soft clay 3D cartoon style, plain light grey background."
I[hand]=$IN/diego_hand_crop.png
parts=${@:-body head hair shirt pants shoes hand}
for p in $parts; do
  for s in 11 22; do
    t0=$(date +%s)
    cp "${I[$p]}" "$IN/k_${p}_$s.png"
    $G preset_edit "$OUT" "76.image=$IN/k_${p}_$s.png" "75.text=${P[$p]}" "75.noise_seed=$s" "75/80.upscale_method=lanczos" "9.filename_prefix=d2_${p}_s$s" 2>&1 | grep -E 'OK|->|ERROR|falló' 
    echo "@@ $p s$s $(( $(date +%s) - t0 ))s"
  done
done
