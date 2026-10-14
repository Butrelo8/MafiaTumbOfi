/**
 * Los espacios del santuario, en orden de gesto. Cada uno trae su fondo por formato (escritorio 16:9,
 * vertical 9:16): un loop, una imagen quieta o nada (negro). `ida` va al espacio siguiente y `vuelta`
 * vuelve de él; sin ida o vuelta reproducible el cambio cruza por negro.
 *
 * Un video es una lista de fuentes, de la más ligera a la más pesada (AV1 → HEVC → H.264, ticket 05); el
 * navegador se queda con la primera que dice poder reproducir. Las que aún no existen no se listan.
 *
 * Provisional (2026-10-13): todo es de antes de la pila (`entrega/`). Los renders finales reemplazan
 * los archivos con el mismo nombre. La sacristía es el loop de 10 s en los dos formatos (la vertical es
 * un recorte de la de escritorio). Camarín, cripta y atrio: loops del 07 con look; sus idas, de Flow.
 */

export interface Fuente {
  src: string
  type: string
  /** Peldaño de 2560×1440: sólo para pantallas de más de 1920 px físicos (`paraPantalla`). */
  grande?: boolean
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

// Peldaño de 2560×1440 de escritorio (2026-10-14, docs/2026-10-14-resolucion-1440.md): Lanczos desde los maestros,
// AV1 y HEVC de cada pieza (`scripts/escalera-2560.sh`), delante de las de 1920. Nivel 5.0 (AV1 12, HEVC 150).
const tipoGrande = { av1: 'av01.0.12M.08', hevc: 'hvc1.1.6.L150.90' }
function grande(formato: Formato, nombre: string): Fuente[] {
  if (formato !== 'escritorio') return []
  return (['av1', 'hevc'] as const).map((codec) => ({
    src: `/video/escritorio-2560/${nombre}-${codec}.mp4`,
    type: `video/mp4; codecs="${tipoGrande[codec]}"`,
    grande: true,
  }))
}

// En un loop el H.264 se llama como el espacio (`nave.mp4`) y los demás códecs lo llevan detrás
// (`vestidor-av1.mp4`); las transiciones siempre llevan el códec en el nombre (`ida-av1.mp4`), como en `entrega/`.
function loop(formato: Formato, nombre: string, codecs: Array<'av1' | 'hevc' | 'h264'> = ['h264']): Fuente[] {
  return grande(formato, nombre).concat(codecs.map((codec) => ({
    src: `/video/${formato}/${nombre}${codec === 'h264' ? '' : `-${codec}`}.mp4`,
    type: `video/mp4; codecs="${tipo[formato][codec]}"`,
  })))
}

function transicion(formato: Formato, nombre: string, codecs: Array<'av1' | 'hevc' | 'h264'>): Fuente[] {
  return grande(formato, nombre).concat(codecs.map((codec) => ({
    src: `/video/${formato}/${nombre}-${codec}.mp4`,
    type: `video/mp4; codecs="${tipo[formato][codec]}"`,
  })))
}

const negro: Record<Formato, Fondo> = { escritorio: {}, vertical: {} }
const todos: Array<'av1' | 'hevc' | 'h264'> = ['av1', 'hevc', 'h264']

export const espacios: Espacio[] = [
  { id: 'inicio', nombre: 'Inicio', hero: true, fondo: negro },
  {
    id: 'quienes',
    nombre: 'Quiénes somos',
    fondo: {
      escritorio: {
        loop: loop('escritorio', 'nave', todos),
        ida: transicion('escritorio', 'ida', ['av1', 'hevc', 'h264']),
        vuelta: transicion('escritorio', 'vuelta', ['av1']),
      },
      vertical: {
        loop: loop('vertical', 'nave'),
        ida: transicion('vertical', 'ida', ['av1', 'hevc', 'h264']),
        vuelta: transicion('vertical', 'vuelta', ['av1', 'h264']),
      },
    },
  },
  {
    id: 'musica',
    nombre: 'Música',
    fondo: {
      escritorio: {
        loop: loop('escritorio', 'sacristia'),
        ida: transicion('escritorio', 'musica-ida', todos),
        vuelta: transicion('escritorio', 'musica-vuelta', todos),
      },
      vertical: { loop: loop('vertical', 'sacristia') },
    },
  },
  // Camarín, cripta y atrio (ticket 07). Las idas son de Flow, sólo de escritorio; la vertical cruza por
  // negro. El grupo no lleva ida ni vuelta: la de Flow no cae en ningún cuadro del loop de la cripta
  // (mejor media 3.1, contra 0.75 de la vuelta nave/sacristía) y la vuelta termina en otro camarín (27).
  {
    id: 'grupo',
    nombre: 'El grupo',
    fondo: {
      escritorio: { loop: loop('escritorio', 'vestidor', todos) },
      vertical: { loop: loop('vertical', 'vestidor', todos) },
    },
  },
  {
    id: 'contratacion',
    nombre: 'Contratación',
    fondo: {
      escritorio: {
        loop: loop('escritorio', 'cripta', todos),
        ida: transicion('escritorio', 'contratacion-ida', todos),
        vuelta: transicion('escritorio', 'contratacion-vuelta', todos),
      },
      vertical: { loop: loop('vertical', 'cripta', todos) },
    },
  },
  {
    id: 'cierre',
    nombre: 'Cierre',
    fondo: {
      escritorio: { loop: loop('escritorio', 'atrio', todos) },
      vertical: { loop: loop('vertical', 'atrio', todos) },
    },
  },
]
