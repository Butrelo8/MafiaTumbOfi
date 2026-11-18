// /vivo-secciones: the live scene. The truck is held at the origin and the world (one road period, cloned and wrapped) moves
// under it, as the Cycles run does (blender/ruta.py), so the camera rides along for free. Cars pass in both carriageways,
// the screen truck plays a video, the band idles (clips baked from the Tripo v5 rigs). Section buttons move the camera
// between the six montaje stops along vivoRuta's path; scroll does nothing.
// Query: ?respaldo forces the no-WebGL fallback. ?f=0 freezes world phase, band pose and video at 0 (for the side-by-side), ?parada=N starts at stop N (0-5).
import {
  WebGLRenderer, Scene, PerspectiveCamera, Group, Mesh, Object3D, Vector3, Color, FogExp2, AgXToneMapping, SRGBColorSpace,
  AnimationMixer, LoopPingPong, CatmullRomCurve3, VideoTexture, MeshStandardMaterial, MeshBasicMaterial, SpotLight, PointLight, HemisphereLight,
  PMREMGenerator, Box3, type Material, type Texture,
} from 'three'
import { GLTFLoader, type GLTF } from 'three/examples/jsm/loaders/GLTFLoader.js'
import { DRACOLoader } from 'three/examples/jsm/loaders/DRACOLoader.js'
import { RoomEnvironment } from 'three/examples/jsm/environments/RoomEnvironment.js'
import { ruta, duracion, fovVertical, type Parada, type V3 } from '../lib/vivoRuta'

interface Datos {
  camaras: Parada[]; camion: { min: V3; max: V3 }; cabina: { min: V3; max: V3 }; parabrisas: number
  periodo: number; velocidad: number; postes: V3[]; pantalla: V3[]; carriles: { mismo: number[]; contrario: number[] }
  faros: { pos: V3; mira: V3 }[]; ruedas: string[]
}

const b2t = ([x, y, z]: V3) => new Vector3(x, z, -y) // Blender (Z up, +Y forward) -> three.js (Y up, -Z forward)
const q = new URLSearchParams(location.search)
const FIJO = q.has('f')
const reducido = matchMedia('(prefers-reduced-motion: reduce)').matches

export async function arrancar() {
  const canvas = document.getElementById('lienzo') as HTMLCanvasElement
  const botones = [...document.querySelectorAll<HTMLButtonElement>('nav button')]
  const gl2 = document.createElement('canvas').getContext('webgl2')
  if (!gl2 || q.has('respaldo')) return respaldo() // ?respaldo: the no-WebGL path on purpose (revisar under SwiftShader)

  const t0 = performance.now()
  const renderer = new WebGLRenderer({ canvas, antialias: true, powerPreference: 'high-performance', preserveDrawingBuffer: FIJO })
  renderer.setPixelRatio(Math.min(devicePixelRatio, 1.75))
  renderer.toneMapping = AgXToneMapping
  renderer.outputColorSpace = SRGBColorSpace
  const scene = new Scene()
  scene.background = new Color(0x05060a)
  scene.fog = new FogExp2(0x07080c, 0.012)
  scene.environment = new PMREMGenerator(renderer).fromScene(new RoomEnvironment(), 0.04).texture
  scene.environmentIntensity = 0.12
  const cam = new PerspectiveCamera(40, 1, 0.03, 900)

  const draco = new DRACOLoader().setDecoderPath('/vivo/draco/')
  const loader = new GLTFLoader().setDRACOLoader(draco)
  const cargar = (u: string) => loader.loadAsync(u)
  const [d, escena, mundo, coches, portico, arco] = await Promise.all([
    fetch('/vivo/vivo.json').then((r) => r.json() as Promise<Datos>),
    cargar('/vivo/escena.glb'), cargar('/vivo/mundo.glb'),
    Promise.all(['basic', 'high', 'short', 'taxi'].map((m) => cargar(`/vivo/coche_${m}.glb`))),
    cargar('/vivo/portico_b.glb'), cargar('/vivo/arco_c.glb'),
  ])

  // ---- truck, cast, screen truck (escena.glb): held still, the truck sways
  const raiz = escena.scene
  scene.add(raiz)
  const camion = raiz.getObjectByName('camion')!
  // GLTFLoader sanitizes names (rueda0.001 -> rueda0001), so match the prefix instead of vivo.json's exact names
  const pantalla = raiz.getObjectByName('pantalla_camion')!
  raiz.updateMatrixWorld(true)
  const halladas: Object3D[] = []
  raiz.traverse((o) => { if (/^rueda\d/i.test(o.name) && !/^rueda\d/i.test(o.parent?.name ?? '')) halladas.push(o) })
  // spin about the hub: a separated wheel keeps the truck's origin, so each one hangs from a pivot at its own centre
  const ruedas = halladas.map((r) => {
    const piv = new Object3D()
    r.parent!.add(piv)
    piv.position.copy(r.parent!.worldToLocal(new Box3().setFromObject(r).getCenter(new Vector3())))
    piv.updateMatrixWorld()
    piv.attach(r)
    return piv
  })
  const ejes = ruedas.map((r) => ({ r }))
  const pantallaBase = pantalla.position.clone()
  const mezcla = new AnimationMixer(raiz)
  for (const c of escena.animations) {
    const a = mezcla.clipAction(c)
    if (/diego/i.test(c.name)) a.setLoop(LoopPingPong, Infinity) // his sip clip seams 87 cm at f240 (exportar.log)
    a.play()
  }
  vidrios(raiz)

  // live lights that travel with the truck: two headlamps, the cab dome (vivo.json gives world positions)
  raiz.updateMatrixWorld(true)
  const local = (p: V3) => camion.worldToLocal(b2t(p))
  for (const f of d.faros) {
    const s = new SpotLight(0xffe2b0, 60, 70, 0.42, 0.55, 1.6)
    s.position.copy(local(f.pos)); s.target.position.copy(local(f.mira))
    camion.add(s, s.target)
  }
  const domo = new PointLight(0xffb070, 0.6, 2.5, 2)
  domo.position.copy(local([1.72, 0.2, 2.05]))
  camion.add(domo)
  scene.add(new HemisphereLight(0x223044, 0x0a0806, 0.25))

  // ---- the world: road3 as built (y -384..768 m, six periods), moved under the truck and wrapped every period as ruta.py
  // does; the signs repeat once per period so the wrap never shows
  const vias = new Group()
  scene.add(vias)
  vias.add(mundo.scene)
  for (let k = -2; k < 4; k++) {
    for (const [s, y] of [[portico, 120], [arco, 24]] as const) {
      const c = s.scene.clone()
      c.position.z = -(y + k * d.periodo)
      vias.add(c)
    }
  }
  // pole sweep on the truck: a real light only at the two poles nearest the cab, following the world
  const posPostes = d.postes.map(b2t) // road3 has one real pole light (luz_poste); the other poles are emissive only
  const postes = posPostes.slice(0, 2).map(() => new PointLight(0xffc98a, 40, 26, 2))
  postes.forEach((p) => scene.add(p))

  // ---- traffic: a pool of cars per carriageway, recycled along the endless road
  const autos: { o: Object3D; x: number; z: number; v: number; vQuiere: number; mismo: boolean }[] = []
  const tinte = [0x8a1c1c, 0x1d3f7a, 0xd8d8d8, 0x202020, 0x6b6b6b, 0xc9a227]
  const nuevo = (mismo: boolean, i: number) => {
    const g = coches[i % coches.length].scene.clone(true)
    g.traverse((o) => {
      const m = (o as Mesh).material as MeshStandardMaterial | undefined
      if (m && !m.emissiveMap && m.emissive?.getHex() === 0 && i % 3) { (o as Mesh).material = m.clone(); ((o as Mesh).material as MeshStandardMaterial).color.multiply(new Color(tinte[i % tinte.length])) }
    })
    if (!mismo) g.rotation.y = Math.PI
    scene.add(g)
    const a = { o: g, x: 0, z: 0, v: 0, vQuiere: 0, mismo }
    reciclar(a, true, i)
    autos.push(a)
  }
  const azar = (i: number) => (Math.sin(i * 127.1 + 311.7) * 43758.5453) % 1
  let semilla = 1
  function reciclar(a: (typeof autos)[number], primera: boolean, i = semilla++) {
    const r = Math.abs(azar(i))
    if (a.mismo) { // overtakes on the truck's side: starts behind, 3..11 m/s faster than the truck
      a.x = d.carriles.mismo[0]; a.vQuiere = 3 + 8 * r
      a.z = primera ? 40 - 260 * r : 60 + 40 * r
    } else { // oncoming: 25..33 m/s plus the truck's own
      a.x = d.carriles.contrario[Math.floor(r * 2) % d.carriles.contrario.length]; a.vQuiere = -(d.velocidad + 25 + 8 * r)
      a.z = primera ? -400 * r : -380 - 60 * r
    }
    a.v = a.vQuiere
  }
  for (let i = 0; i < 4; i++) nuevo(true, i)
  for (let i = 0; i < 5; i++) nuevo(false, i + 4)

  // ---- the screen: a live video texture
  const video = Object.assign(document.createElement('video'), { src: '/vivo/pantalla.mp4', muted: true, loop: true, playsInline: true, preload: 'auto', crossOrigin: 'anonymous' })
  const vt = new VideoTexture(video)
  vt.colorSpace = SRGBColorSpace
  // ?sinpantalla: a flat dark panel instead of the video (screenshots never show the band footage on the screen)
  const SIN = q.has('sinpantalla')
  let pantallas = 0
  raiz.traverse((o) => {
    const m = (o as Mesh).material as MeshStandardMaterial | undefined
    if (m && /^u_led_\d|pantalla_lateral|led_lado/i.test(m.name)) {
      (o as Mesh).material = SIN ? new MeshBasicMaterial({ color: 0x1a1d24 }) : new MeshBasicMaterial({ map: vt, toneMapped: false, color: new Color(0.85, 0.85, 0.85) })
      pantallas++
    }
  })

  // ---- camera moves
  const paradas = d.camaras
  let actual = Math.min(5, Math.max(0, Number(q.get('parada') ?? 0)))
  botones.forEach((b, k) => b.setAttribute('aria-current', String(k === actual)))
  let mov: { curva: CatmullRomCurve3; mira: V3[]; lens: number[]; t0: number; dur: number; de: number; a: number } | null = null
  const mira = new Vector3()
  let lens = paradas[actual].lens
  const pantallaDe = new Vector3(), pantallaA = new Vector3()
  const pantallaEn = (i: number) => b2t(d.pantalla[i]).add(pantallaBase)
  pantalla.position.copy(pantallaEn(actual))
  const colocar = (p: Parada) => { cam.position.copy(b2t(p.pos)); mira.copy(b2t(p.mira)); lens = p.lens }
  colocar(paradas[actual])
  const status = document.createElement('p')
  status.setAttribute('role', 'status')
  status.style.cssText = 'position:fixed;width:1px;height:1px;overflow:hidden;clip:rect(0 0 0 0)'
  document.body.append(status)

  function ir(i: number) {
    if (i === actual && !mov) return
    botones.forEach((b, k) => b.setAttribute('aria-current', String(k === i)))
    status.textContent = 'Escena: ' + botones[i].textContent
    const desde: Parada = { pos: t2b(cam.position), mira: t2b(mira), lens }
    pantallaDe.copy(pantalla.position); pantallaA.copy(pantallaEn(i))
    const de = actual
    actual = i
    if (reducido || FIJO) { colocar(paradas[i]); pantalla.position.copy(pantallaA); mov = null; return }
    const r = ruta(desde, paradas[i], d.camion, d.cabina, d.parabrisas)
    mov = { curva: new CatmullRomCurve3(r.pos.map(b2t), false, 'centripetal'), mira: r.mira, lens: r.lens, t0: performance.now(), dur: duracion(r.largo) * 1000, de, a: i }
  }
  const t2b = (v: Vector3): V3 => [v.x, -v.z, v.y]
  botones.forEach((b, i) => b.addEventListener('click', () => ir(i)))
  document.querySelector('nav')!.addEventListener('keydown', (e) => {
    const k = botones.indexOf(document.activeElement as HTMLButtonElement)
    const n = e.key === 'ArrowRight' ? k + 1 : e.key === 'ArrowLeft' ? k - 1 : e.key === 'Home' ? 0 : e.key === 'End' ? 5 : null
    if (n === null || k < 0) return
    e.preventDefault()
    const j = (n + 6) % 6
    botones[j].focus(); ir(j)
  })

  // ---- loop
  const medida = { frameMs: [] as number[], renderMs: [] as number[], ttff: 0, calls: 0, tris: 0, ir, video: false,
    clips: escena.animations.map((c) => c.name), ruedas: ruedas.length, pantallas, autos: autos.length, el: video,
    estado: () => ({ cam: cam.position.toArray(), z: autos.map((a) => a.z), rueda: ruedas[0]?.rotation.x ?? 0, vias: vias.position.z }) }
  ;(window as unknown as { __vivo: typeof medida }).__vivo = medida
  let antes = performance.now(), tiempo = 0, primero = true
  const ease = (t: number) => (t < 0.5 ? 4 * t * t * t : 1 - (-2 * t + 2) ** 3 / 2)
  function ajustar() {
    const w = innerWidth, h = innerHeight
    renderer.setSize(w, h, false)
    cam.aspect = w / h
  }
  addEventListener('resize', ajustar)
  ajustar()

  function cuadro(ahora: number) {
    const dt = Math.min(0.05, (ahora - antes) / 1000)
    medida.frameMs.push(ahora - antes)
    antes = ahora
    const vivo = !FIJO && !reducido
    if (vivo) tiempo += dt
    // world and wheels
    const z = (tiempo * d.velocidad) % d.periodo
    vias.position.z = z
    for (const { r } of ejes) r.rotation.x -= vivo ? (dt * d.velocidad) / 0.45 : 0
    if (vivo) {
      camion.rotation.z = 0.004 * Math.sin(tiempo * 1.9) + 0.002 * Math.sin(tiempo * 4.3)
      camion.rotation.x = 0.0025 * Math.sin(tiempo * 1.3 + 1)
      camion.position.y = 0.008 * Math.sin(tiempo * 7.1)
    }
    mezcla.setTime(FIJO ? 0 : tiempo)
    // the two poles nearest the cab carry a real light
    const cerca = posPostes.map((p) => p.clone().setZ(p.z + z)).sort((a, b) => Math.abs(a.z) - Math.abs(b.z))
    postes.forEach((l, i) => l.position.copy(cerca[i]))
    // traffic
    for (const a of autos) {
      if (a.mismo) { // keep 18 m behind the screen truck when it is in the same lane
        const dz = a.z - pantalla.position.z
        const misma = Math.abs(pantalla.position.x - a.x) < 2.2
        a.v = misma && dz > 0 && dz < 18 + 6 ? 0 : a.vQuiere
      }
      if (vivo) a.z -= a.v * dt
      if (a.mismo ? a.z < -420 : a.z > 140) reciclar(a, false)
      a.o.position.set(a.x, 0, a.z)
    }
    // camera
    if (mov) {
      // the rAF stamp can precede the click's performance.now(): clamp at 0 (a negative u read past the curve's points)
      const u = Math.min(1, Math.max(0, (ahora - mov.t0) / mov.dur)), e = ease(u)
      cam.position.copy(mov.curva.getPointAt(e))
      const j = e * (mov.mira.length - 1), j0 = Math.floor(j), f = j - j0, j1 = Math.min(j0 + 1, mov.mira.length - 1)
      mira.copy(b2t(mov.mira[j0]).lerp(b2t(mov.mira[j1]), f))
      lens = mov.lens[j0] + (mov.lens[j1] - mov.lens[j0]) * f
      pantalla.position.lerpVectors(pantallaDe, pantallaA, e)
      if (u >= 1) mov = null
    }
    const aspecto = cam.aspect
    cam.fov = aspecto >= 1 ? fovVertical(lens, aspecto) : (2 * Math.atan(Math.tan(0.75 * Math.atan(18 / lens)) / aspecto) * 180) / Math.PI
    cam.updateProjectionMatrix()
    cam.lookAt(mira)
    const r0 = performance.now()
    renderer.render(scene, cam)
    medida.renderMs.push(performance.now() - r0)
    medida.calls = renderer.info.render.calls
    medida.tris = renderer.info.render.triangles
    if (primero) {
      primero = false
      medida.ttff = performance.now()
      canvas.classList.add('listo')
      document.documentElement.dataset.listo = '1'
      console.info('[vivo] first frame', Math.round(medida.ttff), 'ms; load', Math.round(medida.ttff - t0))
      if (SIN) { /* no video */ } else if (!FIJO && !reducido) video.play().then(() => (medida.video = true)).catch(() => {})
      else video.load()
    }
    requestAnimationFrame(cuadro)
  }
  requestAnimationFrame(cuadro)
}

/** Cycles thin glass -> see-through dark sheets (lab/vivo did the same). */
function vidrios(o: Object3D) {
  o.traverse((m) => {
    const mat = (m as Mesh).material as Material & { name: string } | undefined
    if (mat && /vidrio|mica|glass/i.test(mat.name)) Object.assign(mat, { transparent: true, opacity: 0.15, depthWrite: false })
  })
}

function respaldo() {
  const img = document.getElementById('respaldo') as HTMLImageElement
  if (reducido) return
  const v = Object.assign(document.createElement('video'), { src: '/prototipo/bucle.mp4', poster: img.src, muted: true, loop: true, playsInline: true, autoplay: true })
  v.id = 'respaldo'
  v.setAttribute('aria-hidden', 'true')
  img.replaceWith(v)
}

export type { GLTF, Texture }
