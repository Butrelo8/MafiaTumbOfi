# Apagar o borrar luces del camión (G63)

Cada luz del G63 es ahora su propio objeto `luz_*`, dentro de la colección **luces** (antes estaban fundidas en la malla del
modelo). Lo que ocultes o borres en tu archivo queda fuera del sitio en vivo en la siguiente reconstrucción.

## Pasos
1. Abre en Blender `E:\tmp\mto-cabina-restos\colocar-luces.blend` (solo el camión).
2. En el Outliner, despliega la colección **luces**. Al hacer clic en un nombre, la luz se marca en la vista.
3. Para quitar una luz: haz clic en su ojo (ocultar) o selecciónala y pulsa `X` → Borrar. Cualquiera de las dos vale.
   También cuentan el ícono de cámara y el de monitor si los tienes visibles.
4. Guarda (`Ctrl+S`). Puedes guardarlo con otro nombre.
5. Avísale al dron o a la nave nodriza: «leer luces de `<ruta de tu archivo>`». Ellos corren
   `blender/luces_leer.py` sobre tu archivo, que escribe `blender/props/luces.json`, y reconstruyen el vivo.

Para devolver una luz: vuelve a mostrarla (ojo), guarda y repite el paso 5.

## Las luces (izq = lado del conductor)
| Objeto | Qué es |
|---|---|
| `luz_faro_izq` / `_der` | Faro: proyector, aro LED y mica |
| `luz_tira_izq` / `_der` | Tira LED bajo cada faro |
| `luz_parachoques_izq` / `_der` | Luces bajas de la defensa delantera |
| `luz_aleta_izq` / `_der` | Direccional ámbar sobre cada salpicadera |
| `luz_lateral_izq` / `_der` | Marcador ámbar en el costado, delante de la puerta |
| `luz_espejo_izq` / `_der` | Direccional ámbar del espejo |
| `luz_calavera_izq` / `_der` | Calavera trasera |
| `luz_trasera_baja_izq` / `_der` | Luz pequeña bajo cada calavera |
| `luz_techo_izq` / `_der` | Mica de los huecos del techo (la barra de luces del techo es otro objeto, no está aquí) |
| `luz_cabina_lectura_izq` / `_der` | Lámparas de lectura delanteras, en el techo |
| `luz_cabina_lectura_tras_izq` / `_der` | Lámparas de lectura traseras |
| `luz_cabina_domo` | Luz de domo |
| `luz_cabina_pantalla` | Brillo de la pantalla COMAND del tablero |
| `luz_cuadro_izq` / `_der` | Brillo y mica de los dos relojes del tablero |
| `luz_volante_izq` / `_der` | Caras ámbar en los rayos del volante (restos del reparto de lámparas del 18-11; candidatas a borrar) |
| `luz_ambiente_puerta_izq` / `_der` | Tira roja ambiental, puerta delantera |
| `luz_ambiente_puerta_tras_izq` / `_der` | Tira roja ambiental, puerta trasera |
| `luz_ambiente_tablero` | Tira roja ambiental del tablero, lado copiloto |

Ninguna luz se ha borrado: todas siguen encendidas hasta que tú decidas.
