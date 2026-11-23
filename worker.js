// Workers Static Assets ignora Range: contesta 200 con el archivo entero. iOS Safari pide
// bytes=0-1 antes de reproducir un <video> y sin 206 se niega; el hero queda en opacity 0
// (se revela con `loadeddata`) y la portada se ve vacía. El rango se resuelve aquí.
// Solo corre para /video/*, /prototipo/* (la ruta y el bucle de la escena son <video> con rango), /vivo/*.mp4 (la pantalla de /vivo-secciones, VideoTexture), /wa/* (toques de WhatsApp, wa.js) y /e (eventos de clic, e.js) (run_worker_first en wrangler.jsonc); el resto lo sirven los assets.
// El rango se recorta del stream (se saltan los bytes previos y se cancela el origen al terminar el rango):
// ni memoria ni CPU crecen con el tamaño del archivo y los primeros bytes salen de inmediato.
// Sin Content-Length en el origen cae a cargar el archivo completo.
import { wa } from './wa.js'
import { e } from './e.js'

export default {
  async fetch(request, env, ctx) {
    const path = new URL(request.url).pathname
    if (path.startsWith('/wa/')) return wa(request, env, ctx)
    if (path === '/e') return e(request, env)
    // El Range NO se le pasa a ASSETS: con él devuelve un cuerpo vacío en cache MISS.
    // Se pide el archivo entero y el rango se recorta aquí.
    const headersIn = new Headers(request.headers)
    headersIn.delete('Range')
    const response = await env.ASSETS.fetch(new Request(request.url, { method: 'GET', headers: headersIn }))
    if (response.status !== 200) return response

    const headers = new Headers(response.headers)
    headers.set('Accept-Ranges', 'bytes')

    const range = /^bytes=(\d*)-(\d*)$/.exec((request.headers.get('Range') || '').trim())
    if (!range) return new Response(response.body, { status: 200, headers })

    const known = Number(response.headers.get('Content-Length'))
    const buffered = known > 0 ? null : await response.arrayBuffer()
    const size = buffered ? buffered.byteLength : known
    const [, from, to] = range
    const start = from === '' ? size - Number(to) : Number(from)
    const end = from === '' || to === '' ? size - 1 : Number(to)
    const last = Math.min(end, size - 1)

    if (from === '' && to === '') return new Response(buffered ?? response.body, { status: 200, headers })
    if (start < 0 || start >= size || start > last) {
      headers.set('Content-Range', `bytes */${size}`)
      return new Response(null, { status: 416, headers })
    }

    headers.set('Content-Range', `bytes ${start}-${last}/${size}`)
    headers.set('Content-Length', String(last - start + 1))
    return new Response(buffered ? buffered.slice(start, last + 1) : slice(response.body, start, last - start + 1), { status: 206, headers })
  },
}

// Un stream de `length` bytes que empieza `start` bytes dentro de `body`; al completarlos cierra la salida y cancela el origen.
function slice(body, start, length) {
  let skip = start, left = length
  return body.pipeThrough(new TransformStream({
    transform(chunk, controller) {
      if (skip >= chunk.byteLength) { skip -= chunk.byteLength; return }
      const part = chunk.subarray(skip, skip + left)
      skip = 0; left -= part.byteLength
      controller.enqueue(part)
      if (left <= 0) controller.terminate()
    },
  }))
}
