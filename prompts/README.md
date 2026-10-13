# Prompts de H3 y Klein por ticket

Texto final que cada script de `tmp/` mandó a `gen.sh`, ya resuelto (las cadenas de sustituciones entre scripts
quedan aplanadas). Un archivo por salida de ComfyUI (`mto/<nombre>_sNN`). Se pasa con
`scripts/loop-vivo.sh klein|h3 prompts/<ticket>/<nombre>.txt …`. Generado el 2026-10-12 ejecutando cada script
con `gen.sh`, `ffmpeg` y `cp` simulados.

| Archivo | Script de origen (`tmp/`) | Preset | Semillas | Parámetros |
|---|---|---|---|---|
| `12-contrabajo/h3v12_A.txt` | `contrabajo-12/` | `preset_posevideo_ff` | 7 | `12.width=1280 12.height=704 12.length=141 15.steps=20` |
| `12-contrabajo/h3v12b_A.txt` | `contrabajo-12/` | `preset_posevideo_ff` | 7 | `12.width=1280 12.height=704 12.length=141 15.steps=20` |
| `12-contrabajo/h3v12c_A.txt` | `contrabajo-12/` | `preset_posevideo_ff` | 7 | `12.width=1280 12.height=704 12.length=141 15.steps=20` |
| `12-contrabajo/h3v12d_A.txt` | `contrabajo-12/` | `preset_posevideo_ff` | 7 | `12.width=1280 12.height=704 12.length=141 15.steps=20` |
| `12-contrabajo/nave12.txt` | `contrabajo-12/` | `preset_edit` | 11 22 33 | `75/80.upscale_method=lanczos 75/80.megapixels=1.56` |
| `12-contrabajo/nave12b.txt` | `contrabajo-12/` | `preset_edit` | 11 22 33 | `75/80.upscale_method=lanczos 75/80.megapixels=1.56` |
| `12-contrabajo/nave12c_B.txt` | `contrabajo-12/` | `preset_edit` | 11 22 33 | `75/80.upscale_method=lanczos 75/80.megapixels=1.56` |
| `12-contrabajo/nave12c_C.txt` | `contrabajo-12/` | `preset_edit` | 11 22 33 | `75/80.upscale_method=lanczos 75/80.megapixels=1.56` |
| `12-contrabajo/nave12d.txt` | `contrabajo-12/` | `preset_edit` | 11 22 33 | `75/80.upscale_method=lanczos 75/80.megapixels=1.56` |
| `13-placa-y-capas/h3p13.txt` | `placa-13/` | `preset_posevideo_ff` | 7 | `12.width=1280 12.height=704 12.length=141 15.steps=40 10.end_percent=0.5` |
| `13-placa-y-capas/h3p13b.txt` | `placa-13/bancas/` | `preset_posevideo_ff` | 7 | `12.width=1280 12.height=704 12.length=141 15.steps=40 10.end_percent=0.5` |
| `13-placa-y-capas/h3p13d.txt` | `placa-13/capillas/` | `preset_posevideo_ff` | 7 | `12.width=1280 12.height=704 12.length=141 15.steps=40 10.end_percent=0.5` |
| `13-placa-y-capas/h3p13c.txt` | `placa-13/muros/` | `preset_posevideo_ff` | 7 | `12.width=1280 12.height=704 12.length=141 15.steps=40 10.end_percent=0.5` |
| `13-placa-y-capas/nave13.txt` | `placa-13/bancas/` | `preset_edit` | 11 22 33 | `75/80.upscale_method=lanczos 75/80.megapixels=1.56` |
| `13-placa-y-capas/nave13c.txt` | `placa-13/capillas/` | `preset_edit` | 11 22 33 | `75/80.upscale_method=lanczos 75/80.megapixels=1.56` |
| `13-placa-y-capas/muro_tezontle.txt` | `placa-13/muros/` | `preset_edit` | 22 | `75/80.upscale_method=lanczos 75/80.megapixels=1.62` |
| `13-placa-y-capas/muro_almagre.txt` | `placa-13/muros/` | `preset_edit` | 22 | `75/80.upscale_method=lanczos 75/80.megapixels=1.62` |
| `13-placa-y-capas/muro_ahumada.txt` | `placa-13/muros/` | `preset_edit` | 22 | `75/80.upscale_method=lanczos 75/80.megapixels=1.62` |
| `13-placa-y-capas/muro_tez2.txt` | `placa-13/muros/` | `preset_edit` | 22 33 | `75/80.upscale_method=lanczos 75/80.megapixels=1.62` |
| `11-navegacion-por-gesto/h3v4_A.txt` | `transicion-4/` | `preset_posevideo_ff` | 7 | `12.width=864 12.height=480 12.length=260 15.steps=20` |
| `11-navegacion-por-gesto/h3v4_B.txt` | `transicion-4/` | `preset_posevideo_ff` | 7 | `12.width=864 12.height=480 12.length=260 15.steps=20` |
| `17-transiciones-micro-v5/h3e17_T1.txt` | `micro/trans_esc/` | `preset_posevideo_ff` | 7 | `12.width=1280 12.height=704 12.length=39 15.steps=20` |
| `17-transiciones-micro-v5/h3e17_T3r.txt` | `micro/trans_esc/` | `preset_posevideo_ff` | 7 | `12.width=1280 12.height=704 12.length=39 15.steps=20` |
| `17-transiciones-micro-v5/sac17.txt` | `micro/trans_esc/` | `preset_edit_ref` | 11 22 33 | `92/111.megapixels=1.56 92/85.megapixels=1.56` |
| `06-movil/h3viva06.txt` | `movil-06/viva/` | `preset_posevideo_ff` | 7 | `12.width=704 12.height=1280 12.length=141 15.steps=40 10.end_percent=0.5` |
| `06-movil/nave06v.txt` | `movil-06/` | `preset_edit` | 11 22 33 | `75/80.upscale_method=lanczos 75/80.megapixels=1.56` |
| `06-movil/sac06v.txt` | `movil-06/` | `preset_edit` | 11 22 33 | `75/80.upscale_method=lanczos 75/80.megapixels=1.56` |
| `06-movil/sacdark06v.txt` | `movil-06/` | `preset_edit` | 11 22 33 | `75/80.upscale_method=lanczos 75/80.megapixels=1.56` |
| `06-movil/nave06r.txt` | `movil-06/` | `preset_edit_ref` | 11 22 33 | `92/111.megapixels=1.56 92/85.megapixels=1.56` |
| `06-movil/nave06alto.txt` | `movil-06/` | `preset_edit_ref` | 11 22 33 | `92/111.megapixels=1.56 92/85.megapixels=1.56` |
| `06-movil/sac06alto.txt` | `movil-06/` | `preset_edit` | 11 22 33 | `75/80.upscale_method=lanczos 75/80.megapixels=1.56` |
| `06-movil/sacdark06alto.txt` | `movil-06/` | `preset_edit` | 11 22 33 | `75/80.upscale_method=lanczos 75/80.megapixels=1.56` |
| `06-movil/h3m06_T1.txt` | `movil-06/` | `preset_posevideo_ff` | 7 | `12.width=704 12.height=1280 12.length=39 15.steps=20` |
| `06-movil/h3m06_T3r.txt` | `movil-06/` | `preset_posevideo_ff` | 7 | `12.width=704 12.height=1280 12.length=39 15.steps=20` |
| `06-movil/nave06sub.txt` | `movil-06/` | `preset_edit_ref` | 11 22 33 | `92/111.megapixels=1.56 92/85.megapixels=1.56` |
| `06-movil/nave13sub.txt` | `movil-06/` | `preset_edit_ref` | 11 22 33 | `92/111.megapixels=1.56 92/85.megapixels=1.56` |
| `06-movil/nave06piso.txt` | `movil-06/` | `preset_edit_ref` | 11 22 33 | `92/111.megapixels=1.56 92/85.megapixels=1.56` |
| `06-movil/nave13piso.txt` | `movil-06/` | `preset_edit_ref` | 11 22 33 | `92/111.megapixels=1.56 92/85.megapixels=1.56` |
| `06-movil/nave13pila3.txt` | `movil-06/` | `preset_edit` | 11 22 33 | `75/80.upscale_method=lanczos 75/80.megapixels=1.56` |
| `06-movil/nave06pila3.txt` | `movil-06/` | `preset_edit_ref` | 11 22 33 | `92/111.megapixels=1.56 92/85.megapixels=1.56` |
| `06-movil/nave13props.txt` | `props-06/` | `preset_edit` | 11 22 33 | `75/80.upscale_method=lanczos 75/80.megapixels=1.56` |
| `06-movil/nave06props.txt` | `props-06/` | `preset_edit_ref` | 11 22 33 | `92/111.megapixels=1.56 92/85.megapixels=1.56` |
| `06-movil/micro_v.txt` | `micro/movil/` | `preset_edit` | 11 | `75/80.megapixels=4 75/80.upscale_method=lanczos` |
| `06-movil/micro_v2.txt` | `micro/movil/` (`PROMPT=prompt_klein_v2.txt klein_v.sh`) | `preset_edit` | por llamada | `75/80.megapixels=4 75/80.upscale_method=lanczos` |
| `16-loops-de-10s/h3_calmo_260.txt` | `micro/largo/` (`reconstruir_10s.sh`, `prompt_calmo.txt`) | `preset_posevideo_ff` | 7 | `12.width=928 12.height=512 12.length=260 15.steps=40 10.end_percent=0.5` |
| `07-guion-espacios/real_{vestidor,cripta,atrio}.txt` | `07/produccion/` (`real07.sh`; esqueleto de `mto_placa_real_s2b.json`) | `preset_edit` | 2 3 | `75/80.upscale_method=lanczos 75/80.megapixels=4` |
| `07-guion-espacios/h3_{vestidor,cripta,atrio}_{esc,movil}.txt` | `07/e5/` (`e5.sh` → `loop-vivo.sh h3`, DUR=10; esqueleto de `h3_calmo_260`) | `preset_posevideo_ff` | 7 | escritorio `12.width=928 12.height=512`, móvil `512×928`; `12.length=260 15.steps=40 10.end_percent=0.5` |

## Fuera de ComfyUI

- `07-guion-espacios/flow-job1/`: prueba A/B con Google Flow (Veo, *frames to video*, Fast, una generación) de la
  transición camarín → cripta. `prompt.txt` se pega tal cual; `STEPS.md` lo sigue un drone de navegador; `notes.md`
  dice de qué placas salen los cuadros y la transformación a 1920×1080. Copia de trabajo y salida en `tmp/07/flow/job1/`.
- `07-guion-espacios/flow-job2/`: el reintento (OK del usuario 05:57) con los mismos cuadros: oclusión total a negro,
  cámara sólo lateral, sin objetos ni luces nuevas. `STEPS.md` es para la UI nueva de Flow (agente de chat). Copia
  de trabajo en `tmp/07/flow/job2/`; los archivos para subir en `C:\Users\black\Downloads\flow-job2\`.
