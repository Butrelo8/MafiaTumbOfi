/**
 * Los espacios del santuario, en orden de gesto. Cada uno trae su fondo por formato (escritorio 16:9,
 * vertical 9:16): un loop, una imagen quieta o nada (negro). `ida` va al espacio siguiente y `vuelta`
 * vuelve de él; sin ida o vuelta reproducible el cambio cruza por negro.
 *
 * Un video es una lista de fuentes, de la más ligera a la más pesada (AV1 → HEVC → H.264, ticket 05); el
 * navegador se queda con la primera que dice poder reproducir. Las que aún no existen no se listan.
 *
 * Provisional (2026-10-13): todo es de antes de la pila (`entrega/`). Los renders finales reemplazan
 * los archivos con el mismo nombre. Falta el loop de la sacristía de escritorio: mientras tanto, el
 * último cuadro de la ida. El de la vertical es el de 5 s del 2026-10-05.
 */

export interface Fuente {
  src: string
  type: string
}

export interface Fondo {
  loop?: Fuente[]
  quieta?: string
  ida?: Fuente[]
  vuelta?: Fuente[]
}

export type Formato = 'escritorio' | 'vertical'

export interface Espacio {
  id: string
  nombre: string
  /** El hero lleva su propio video dentro de la sección. */
  hero?: boolean
  fondo: Record<Formato, Fondo>
}

// Perfil y nivel de cada archivo, sacados con ffprobe: 1920×1080 es nivel 4.0 (AV1 08, HEVC 120,
// H.264 High 5.0); 704×1280, nivel 3.1 (AV1 05, HEVC 93, H.264 High 3.1).
const tipo = {
  escritorio: { av1: 'av01.0.08M.08', hevc: 'hvc1.1.6.L120.90', h264: 'avc1.640032' },
  vertical: { av1: 'av01.0.05M.08', hevc: 'hvc1.1.6.L93.90', h264: 'avc1.64001F' },
}

// Los loops sólo existen en H.264 y se llaman como el espacio (`nave.mp4`); las transiciones llevan el
// códec en el nombre (`ida-av1.mp4`), como en `entrega/`.
function loop(formato: Formato, nombre: string): Fuente[] {
  return [{ src: `/video/${formato}/${nombre}.mp4`, type: `video/mp4; codecs="${tipo[formato].h264}"` }]
}

function transicion(formato: Formato, nombre: string, codecs: Array<'av1' | 'hevc' | 'h264'>): Fuente[] {
  return codecs.map((codec) => ({
    src: `/video/${formato}/${nombre}-${codec}.mp4`,
    type: `video/mp4; codecs="${tipo[formato][codec]}"`,
  }))
}

const negro: Record<Formato, Fondo> = { escritorio: {}, vertical: {} }

export const espacios: Espacio[] = [
  { id: 'inicio', nombre: 'Inicio', hero: true, fondo: negro },
  {
    id: 'quienes',
    nombre: 'Quiénes somos',
    fondo: {
      escritorio: {
        loop: loop('escritorio', 'nave'),
        ida: transicion('escritorio', 'ida', ['av1', 'hevc', 'h264']),
        vuelta: transicion('escritorio', 'vuelta', ['av1']),
      },
      vertical: {
        loop: loop('vertical', 'nave'),
        ida: transicion('vertical', 'ida', ['av1', 'hevc', 'h264']),
        vuelta: transicion('vertical', 'vuelta', ['h264']),
      },
    },
  },
  {
    id: 'musica',
    nombre: 'Música',
    fondo: {
      escritorio: { quieta: '/video/escritorio/sacristia.webp' },
      vertical: { loop: loop('vertical', 'sacristia') },
    },
  },
  // Camarín, cripta y atrio (ticket 07): sobre negro hasta que lleguen sus loops.
  { id: 'grupo', nombre: 'El grupo', fondo: negro },
  { id: 'contratacion', nombre: 'Contratación', fondo: negro },
  { id: 'cierre', nombre: 'Cierre', fondo: negro },
]
