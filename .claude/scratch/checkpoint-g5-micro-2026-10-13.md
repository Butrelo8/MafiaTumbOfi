# Checkpoint — MTO path B, G5 (micro on top of the new v5 plates), 2026-10-13 02:30 CST

## Goal
G5: approved micro + rose re-pasted and retouched against the new G4 plates (desktop + vertical), user approves in the
window. Then G6 (10 s nave loops, chain of ticket 16) as an overnight batch, only if `scripts/puerta-tanda.sh` passes.
Stop before G7. Commit + one-line report to meltingship after G5 and when the batch launches. Don't touch entrega/maestros.

## Done (committed, dev)
- Step 0 d4ff452, G1 dd32e44, G2 2b1d93d, G3 68b37ae, G4 adcdcce, hook note 5e05ed4; visual-lab b95eb74.
- G4 plates: `tmp/props-06/nave_g4_esc.png` (1712×944), `nave_g4_vert.png` (704×1280), MoGe disparity
  `nave_g4_esc_disp.png` / `nave_g4_vert_disp.png` (copies in `entrega/placas/`). Ticket 06 has G1–G4 bullets at the end.

## G5 so far (uncommitted, all in `tmp/micro/g5/`)
- Micro composed with the loop's own script on 3-frame mkvs of the new plates (`g5/real_g2_s2.mkv`, `g5/real_g3c_s2.mkv`):
  - Desktop: `TOPE=1.2 ROSA=mascara_rosa.png GUIT=0.78,0.99,0.64,0.72 micro_viva_v.py placa_micro_rosa.png
    mascara_micro_ajustada.png g5/real_g2_s2.mkv g5/esc_micro.mkv` (run from `tmp/micro/`) → `g5/esc_micro.png`.
    Ring gain 1.43/1.37/1.26 (old setup 1.07/1.04/1.04); p99 micro 68.2 vs guitar 27.5 before cap → cap = 1.2×27.5 = 33
    (old cap 1.2×38 = 45.6): **new desktop micro will end ~28 % darker than approved** because the new guitar is darker.
  - Vertical (run from `tmp/micro/movil/`): `GANA_ORO=1.26 TOPE=1.2 ROSA=mascara_rosa_v.png GUIT=0.37,0.49,0.36,0.51
    ARRIBA=235 micro_viva_v.py placa_micro_vb_s4_suj.png mascara_trasplante.png ../g5/real_g3c_s2.mkv ../g5/vert_micro.mkv`.
    Ring gain 0.59–0.68 (old 0.84); micro p99 30.6–33.7 vs guitar 43.1 (cap doesn't act). Old approved ratio was 1.49×.
  - Reference runs on the old plates: `g5/old_esc_micro.png`, `g5/old_vert_micro.png`.
- **Vertical clash:** pila moved speaker + red candle (`veladora_3` 270–290 × 354–387 px) up; the pasted micro grille comes
  down to ~355 px and touches the candle. Maquette (`MOVIL["micro"]` = (0.609, 3.8, 1.62) in `blender/transicion.py:35`)
  puts the grille at y 272–345 (pasted one is bigger). Variants raised in 2D: `g5/vert_micro_up20.png`, `_up35.png`
  (made by shifting `pm_up<dy>.png`, `mascara_trasplante_up<dy>.png`, `mascara_rosa_v_up<dy>.png`, `ARRIBA=235−dy`).
  Sheet: scratchpad `g5/micro_vert_alturas.jpg` (as is | +20 | +35). Not yet shown to the user.
- Desktop: no clash (grille 945–1023 × 392–514; sahumador starts x 1141, veladora_3 x 1074).

## Next
1. Show the user `micro_vert_alturas.jpg` and `micro_esc.jpg` (scratchpad g5/); ask: vertical height (as is / +20 / +35),
   and brightness rule (keep TOPE relative to the new darker guitar → dimmer micro, or raise TOPE / GANA_ORO to match the
   approved absolute level: old desktop final ≈ oro 41.6 vs guitar 27.8 after LOOK+halación; vertical 42.7 vs 28.6).
2. If the vertical micro moves: update `MOVIL["micro"]` z to match (needed by G7's tracked layer), shift the trasplant files
   for real, and the disparity: desktop focus map = `nave_g4_esc_disp.png` with micro silhouette set near
   (like `tmp/micro/rosa3d/disp_rosa.py`, FOCO_D 0.97); vertical = `nave_g4_vert_disp.png` with micro silhouette = 0.60.
3. Commit G5 (ticket 06 bullet + entrega placas with micro) → one line to meltingship.
4. G6: ticket 16 chain from `tmp/micro/largo/capas240/construir.sh` (desktop) and `tmp/micro/movil/armar_micro_v.sh`
   (vertical), pointed at the new plates: `llevar.py` takes the real plate (`placa_real_s2b_nr.png` → `nave_g4_esc.png`);
   H3 (needs new H3 runs on the new plates, ~18 min each), new humo/llamas masks for the pila composition, GUIT boxes above.
   `scripts/puerta-tanda.sh comfy` before queuing; launch in background only if it passes.

## Open
- Brightness decision (above) is the user's.
- Smoke/flame masks (`mascara_humo*.png`, `mascara_llamas.png`) were drawn for the pre-pila plates: likely need redoing
  (sahumador now on the speaker). Check before the batch.
- `/mnt/e/ComfyUI/CLAUDE.md` line 55 is wrong (killing the hung powershell kills gen.sh): told meltingship, not edited.

## Don't lose
- ComfyUI at `http://172.20.96.1:8188`, already running (started via WMI). Local LLM servers stopped (`oc-up`).
- MoGe via `tmp/props-06/g4/moge.sh <in> <out>`; Klein real via `tmp/props-06/g4/klein_real.sh` (prompt without "no people").
- Real plate chain: DLSS NR `/mnt/e/tools/video2dlssnr-1.4.1/out/video2dlssnr.exe --nr-run --in <win> --out <win> --nr-color 0`.
- Report file: `/home/black/.cache/cc-deck/reports/all/apedrone-1791873480.md`; send only to "meltingship".
