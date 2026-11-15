#!/bin/bash
# parts_dance.sh SUF ...: the stiff-piece binding (split + hull covers swept over the dance + cover normals + seams) on a
# rig's wham10 dance blend (rig_trellis$SUF/dance_trellis.blend), pass-2 settings. Columns (a) _p3 and (b) _mx of the
# binding test. Outputs: assets/reparto/diego_trellis_{refit,juntas,juntasn}${SUF}d.blend, mixskin/out/{split,covers,joints}${SUF}d.*
P="/mnt/e/Cursor Projects/MTO-colddrone/blender/partes"; A="/mnt/e/Cursor Projects/MTO-colddrone/blender/assets/reparto"
R="/mnt/e/Cursor Projects/MTO-colddrone/blender/render/reparto/partes/diego"; O="$P/mixskin/out"; B=/mnt/e/Blender/blender.exe; w() { wslpath -w "$1"; }
mkdir -p "$O"; cd "$P"
for S in "$@"; do D=${S}d
  SHOULDER=armhole PIN=1 WELD=1e-5 GARMENT='{"hem":0.275,"cuff":0.078}' WSLENV=SHOULDER:PIN:WELD:GARMENT \
    $B -b "$(w "$R/rig_trellis$S/dance_trellis.blend")" --python split.py -- "$(w "$A/diego_trellis_refit$D.blend")" "$(w "$O/split$D.json")" > "$O/split$D.log" 2>&1
  grep -E "Error" "$O/split$D.log"; echo "split $D done"
  COVERS='{"collar":"hull","hem":"hull","shoulder":"hull","elbow":"hull","wrist":"band","hip":"hull","knee":"hull","cuff":"hull"}' FRAMES=1-299:3 WSLENV=COVERS:FRAMES \
    $B -b "$(w "$A/diego_trellis_refit$D.blend")" --python covers.py -- "$(w "$O/split$D.json")" "$(w "$A/diego_trellis_juntas$D.blend")" "$(w "$O/covers$D.json")" > "$O/covers$D.log" 2>&1
  grep -E "@@COVERS|Error" "$O/covers$D.log" | cut -c1-300
  $B -b "$(w "$A/diego_trellis_juntas$D.blend")" --python cover_normals.py -- "$(w "$O/split$D.json")" "$(w "$A/diego_trellis_juntasn$D.blend")" 2>&1 | grep -E "COVERNORMALS|Error"
  $B -b "$(w "$A/diego_trellis_juntasn$D.blend")" --python joints.py -- "$(w "$O/split$D.json")" "$(w "$O/joints$D.json")" 1-299:1 > "$O/joints$D.log" 2>&1
  tail -2 "$O/joints$D.log" | cut -c1-600; echo "PARTS $D done"
done
