// Workers Static Assets ignora Range: contesta 200 con el archivo entero. iOS Safari pide
// bytes=0-1 antes de reproducir un <video> y sin 206 se niega; el hero queda en opacity 0
// (se revela con `loadeddata`) y la portada se ve vacía. El rango se resuelve aquí.
// Solo corre para /video/* (run_worker_first en wrangler.jsonc); el resto lo sirven los assets.
// ponytail: carga el archivo completo en memoria. El hero pesa 10 MB contra un límite de 128 MB;
// si entra un video grande, pasarlo a R2.
export default {
  async fetch(request, env) {
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

    const body = await response.arrayBuffer()
    const size = body.byteLength
    const [, from, to] = range
    const start = from === '' ? size - Number(to) : Number(from)
    const end = from === '' || to === '' ? size - 1 : Number(to)
    const last = Math.min(end, size - 1)

    if (from === '' && to === '') return new Response(body, { status: 200, headers })
    if (start < 0 || start >= size || start > last) {
      headers.set('Content-Range', `bytes */${size}`)
      return new Response(null, { status: 416, headers })
    }

    headers.set('Content-Range', `bytes ${start}-${last}/${size}`)
    headers.set('Content-Length', String(last - start + 1))
    return new Response(body.slice(start, last + 1), { status: 206, headers })
  },
}
