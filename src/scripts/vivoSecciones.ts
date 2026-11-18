// /vivo-secciones: the live scene. The truck is held at the origin and the world (one road period, cloned and wrapped) moves
// under it, as the Cycles run does (blender/ruta.py), so the camera rides along for free. Cars pass in both carriageways,
// the screen truck plays a video, the band idles (clips baked from the Tripo v5 rigs). Section buttons move the camera
// between the six montaje stops along vivoRuta's path; scroll does nothing.
// Query: ?respaldo forces the no-WebGL fallback. ?f=0 freezes world phase, band pose and video at 0 (for the side-by-side), ?parada=N starts at stop N (0-5).
// Load order (2026-11-18, "make it swift"): poster at once -> truck + world (first frame) -> cast -> cars and signs -> video.
// Static meshes are merged per rigid parent at load (scripts/vivo-optimizar.mjs already dropped the heavy parts).
import {
  WebGLRenderer, Scene, PerspectiveCamera, Group, Mesh, Object3D, Vector3, Color, FogExp2, AgXToneMapping, SRGBColorSpace,
  AnimationMixer, LoopPingPong, CatmullRomCurve3, VideoTexture, MeshStandardMaterial, MeshBasicMaterial, SpotLight, PointLight, HemisphereLight,
  PMREMGenerator, Box3, Matrix4, BufferGeometry, BufferAttribute, InstancedMesh, DataTexture, type Material, type Texture, type SkinnedMesh,
  type InterleavedBufferAttribute,
} from 'three'
import { GLTFLoader, type GLTF } from 'three/examples/jsm/loaders/GLTFLoader.js'
import { DRACOLoader } from 'three/examples/jsm/loaders/DRACOLoader.js'
import { RoomEnvironment } from 'three/examples/jsm/environments/RoomEnvironment.js'
import { mergeGeometries } from 'three/examples/jsm/utils/BufferGeometryUtils.js'
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
// phone tier, fixed before the context exists (antialias can't change later); the frame probe can only lower the DPR
const TELEFONO = matchMedia('(pointer: coarse)').matches || innerWidth < 700

export async function arrancar() {
  const canvas = document.getElementById('lienzo') as HTMLCanvasElement
  const botones = [...document.querySelectorAll<HTMLButtonElement>('nav button')]
  const gl2 = document.createElement('canvas').getContext('webgl2')
  if (!gl2 || q.has('respaldo')) return respaldo() // ?respaldo: the no-WebGL path on purpose (revisar under SwiftShader)

  const t0 = performance.now()
  const renderer = new WebGLRenderer({ canvas, antialias: true, powerPreference: 'high-performance', preserveDrawingBuffer: FIJO })
  let dpr = Math.min(devicePixelRatio, TELEFONO ? 1.25 : 1.5)
  renderer.setPixelRatio(dpr)
  renderer.toneMapping = AgXToneMapping
  renderer.outputColorSpace = SRGBColorSpace
  const scene = new Scene()
  scene.background = new Color(0x05060a)
  scene.fog = new FogExp2(0x07080c, 0.012)
  scene.environment = new PMREMGenerator(renderer).fromScene(new RoomEnvironment(), 0.04).texture
  scene.environmentIntensity = 0.12
  const cam = new PerspectiveCamera(40, 1, 0.03, 320) // the fog leaves e^-9 at 250 m

  const draco = new DRACOLoader().setDecoderPath('/vivo/draco/')
  const loader = new GLTFLoader().setDRACOLoader(draco)
  const cargar = (u: string) => loader.loadAsync(u)
  const [d, escena, mundo] = await Promise.all([
    fetch('/vivo/vivo.json').then((r) => r.json() as Promise<Datos>), cargar('/vivo/escena.glb'), cargar('/vivo/mundo.glb'),
  ])

  // ---- truck, dressing, screen truck (escena.glb): held still, the truck sways
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
  const pantallaBase = pantalla.position.clone()
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

  // ---- the world: road3 as built, moved under the truck and wrapped every period as ruta.py does
  const vias = new Group()
  scene.add(vias)
  vias.add(mundo.scene)
  // pole sweep on the truck: a real light only at the two poles nearest the cab, following the world
  const posPostes = d.postes.map(b2t) // road3 has one real pole light (luz_poste); the other poles are emissive only
  const postes = posPostes.slice(0, 2).map(() => new PointLight(0xffc98a, 40, 26, 2))
  postes.forEach((p) => scene.add(p))

  // ---- the screen: a video texture, its source set once the rest has loaded
  const video = Object.assign(document.createElement('video'), { muted: true, loop: true, playsInline: true, preload: 'auto', crossOrigin: 'anonymous' })
  const vt = new VideoTexture(video)
  vt.colorSpace = SRGBColorSpace
  // ?sinpantalla: a flat dark panel instead of the video (screenshots never show the band footage on the screen)
  const SIN = q.has('sinpantalla')
  let pantallas = 0
  raiz.traverse((o) => {
    const m = (o as Mesh).material as MeshStandardMaterial | undefined
    if (m && /^u_led_\d|pantalla_lateral|led_lado/i.test(m.name)) {
      (o as Mesh).material = SIN ? new MeshBasicMaterial({ color: 0x1a1d24 }) : new MeshBasicMaterial({ map: vt, toneMapped: false, color: new Color(0.85, 0.85, 0.85) })
      o.userData.solo = true
      pantallas++
    }
  })

  // merge the static meshes under each rigid parent (wheels spin, the screen truck moves, the truck sways)
  const rigidos = new Set<Object3D>([raiz, camion, pantalla, ...ruedas, vias])
  for (const g of rigidos) fusionar(g, (o) => rigidos.has(o))

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

  // ---- streamed parts, filled in after the first frame
  const mezclas: AnimationMixer[] = []
  const autos: { x: number; z: number; v: number; vQuiere: number; mismo: boolean; modelo: number; hueco: number }[] = []
  const flotas: InstancedMesh[][] = [] // per car model, one InstancedMesh per merged material
  const M = new Matrix4(), GIRO = new Matrix4().makeRotationY(Math.PI)

  // ---- loop
  const medida = { frameMs: [] as number[], renderMs: [] as number[], ttff: 0, calls: 0, tris: 0, ir, video: false, cargado: false,
    fases: {} as Record<string, number>, dpr, telefono: TELEFONO, sondeo: '',
    clips: [] as string[], ruedas: ruedas.length, pantallas, autos: 0, el: video, escena: scene,
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
  const sonda: number[] = []

  function cuadro(ahora: number) {
    const dt = Math.min(0.05, (ahora - antes) / 1000)
    if (medida.frameMs.length > 4000) medida.frameMs.length = medida.renderMs.length = 0
    medida.frameMs.push(ahora - antes)
    antes = ahora
    const vivo = !FIJO && !reducido
    if (vivo) tiempo += dt
    // world and wheels
    const z = (tiempo * d.velocidad) % d.periodo
    vias.position.z = z
    for (const r of ruedas) r.rotation.x -= vivo ? (dt * d.velocidad) / 0.45 : 0
    if (vivo) {
      camion.rotation.z = 0.004 * Math.sin(tiempo * 1.9) + 0.002 * Math.sin(tiempo * 4.3)
      camion.rotation.x = 0.0025 * Math.sin(tiempo * 1.3 + 1)
      camion.position.y = 0.008 * Math.sin(tiempo * 7.1)
    }
    for (const m of mezclas) m.setTime(FIJO ? 0 : tiempo)
    // the two poles nearest the cab carry a real light (no allocation per frame)
    let a0 = -1, a1 = -1
    for (let i = 0; i < posPostes.length; i++) {
      const di = Math.abs(posPostes[i].z + z)
      if (a0 < 0 || di < Math.abs(posPostes[a0].z + z)) { a1 = a0; a0 = i } else if (a1 < 0 || di < Math.abs(posPostes[a1].z + z)) a1 = i
    }
    ;[a0, a1].forEach((k, i) => { if (k >= 0 && postes[i]) postes[i].position.copy(posPostes[k]).setZ(posPostes[k].z + z) })
    // traffic
    for (const a of autos) {
      if (a.mismo) { // keep 18 m behind the screen truck when it is in the same lane
        const dz = a.z - pantalla.position.z
        const misma = Math.abs(pantalla.position.x - a.x) < 2.2
        a.v = misma && dz > 0 && dz < 18 + 6 ? 0 : a.vQuiere
      }
      if (vivo) a.z -= a.v * dt
      if (a.mismo ? a.z < -420 : a.z > 140) reciclar(a, false)
      M.makeTranslation(a.x, 0, a.z)
      if (!a.mismo) M.multiply(GIRO)
      for (const im of flotas[a.modelo]) im.setMatrixAt(a.hueco, M)
    }
    for (const f of flotas) for (const im of f) im.instanceMatrix.needsUpdate = true
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
    // frame probe once everything is in: median over 60 frames above 20 ms -> DPR 1 and the pole lights off
    if (medida.cargado && !medida.sondeo && sonda.push(medida.frameMs.at(-1)!) > 60) {
      const med = [...sonda].sort((x, y) => x - y)[30]
      medida.sondeo = `mediana ${med.toFixed(1)} ms`
      if (med > 20 && !FIJO) {
        dpr = Math.min(dpr, 1); renderer.setPixelRatio(dpr); ajustar(); medida.dpr = dpr
        postes.forEach((p) => (p.visible = false))
        medida.sondeo += ' -> dpr 1, sin postes'
      }
    }
    if (primero) {
      primero = false
      medida.ttff = performance.now()
      canvas.classList.add('listo')
      document.documentElement.dataset.listo = '1'
      console.info('[vivo] first frame', Math.round(medida.ttff), 'ms; load', Math.round(medida.ttff - t0))
      resto().catch((e) => console.error('[vivo] streamed parts', e))
    }
    requestAnimationFrame(cuadro)
  }
  requestAnimationFrame(cuadro)

  // ---- after the first frame: cast, then cars and signs, then the video. Each part compiles its shaders before it shows.
  async function resto() {
    const listo = async (o: Object3D) => { await renderer.compileAsync(o, cam, scene) }
    const reparto = await cargar('/vivo/reparto.glb')
    vidrios(reparto.scene)
    for (const c of reparto.animations) { // one mixer per rig: the four rigs share bone names
      const rig = reparto.scene.getObjectByName(`${c.name}_v5_rig`)
      if (!rig) continue
      const mz = new AnimationMixer(rig)
      const a = mz.clipAction(c)
      if (/diego/i.test(c.name)) a.setLoop(LoopPingPong, Infinity) // his sip clip seams 87 cm at f240 (exportar.log)
      a.play()
      mezclas.push(mz)
    }
    const enCamion = reparto.scene.getObjectByName('camion') // the rigs riding the truck hang from an empty of that name
    await listo(reparto.scene)
    if (enCamion) for (const h of [...enCamion.children]) camion.add(h)
    for (const h of [...reparto.scene.children]) if (h !== enCamion) raiz.add(h)
    medida.clips = reparto.animations.map((c) => c.name)
    medida.fases.reparto = performance.now()

    const [coches, portico, arco] = await Promise.all([
      Promise.all(['basic', 'high', 'short', 'taxi'].map((m) => cargar(`/vivo/coche_${m}.glb`))),
      cargar('/vivo/portico_b.glb'), cargar('/vivo/arco_c.glb'),
    ])
    // signs once per period, every copy in one mesh per material (the far plane and fog cover k -1..2)
    const carteles = new Group()
    for (let k = -1; k < 3; k++) for (const [s, y] of [[portico, 120], [arco, 24]] as const) {
      const c = s.scene.clone()
      c.position.z = -(y + k * d.periodo)
      carteles.add(c)
    }
    fusionar(carteles, () => false)
    // traffic: one InstancedMesh per car model and merged material; the tint goes in the instance colour
    const tinte = [0x8a1c1c, 0x1d3f7a, 0xd8d8d8, 0x202020, 0x6b6b6b, 0xc9a227]
    const plan = [...[0, 1, 2, 3].map((i) => ({ mismo: true, i })), ...[0, 1, 2, 3, 4].map((i) => ({ mismo: false, i: i + 4 }))]
    const porModelo = coches.map(() => 0)
    for (const p of plan) autos.push({ x: 0, z: 0, v: 0, vQuiere: 0, mismo: p.mismo, modelo: p.i % coches.length, hueco: porModelo[p.i % coches.length]++ })
    const flota = new Group()
    coches.forEach((g, m) => {
      fusionar(g.scene, () => false)
      g.scene.updateMatrixWorld(true)
      const inv = new Matrix4().copy(g.scene.matrixWorld).invert()
      const ims: InstancedMesh[] = []
      g.scene.traverse((o) => {
        const me = o as Mesh
        if (!me.isMesh) return
        const geo = me.geometry.clone().applyMatrix4(new Matrix4().multiplyMatrices(inv, me.matrixWorld))
        const im = new InstancedMesh(geo, me.material, porModelo[m])
        im.frustumCulled = false // the instances move; the bounds from the first frame would cull them
        const mat = me.material as MeshStandardMaterial
        const tintable = mat.vertexColors || (!mat.emissiveMap && (mat.emissive?.getHex() ?? 0) === 0) // merged body: lamps stay lit through the emissive lookup
        if (tintable) autos.forEach((a, i) => { if (a.modelo === m) im.setColorAt(a.hueco, new Color(i % 3 ? tinte[i % tinte.length] : 0xffffff)) })
        ims.push(im)
      })
      flotas[m] = ims
      flota.add(...ims)
    })
    autos.forEach((a, i) => reciclar(a, true, i))
    await listo(carteles); await listo(flota)
    vias.add(carteles)
    scene.add(flota)
    medida.autos = autos.length
    medida.fases.coches = performance.now()

    video.src = '/vivo/pantalla.mp4'
    if (SIN) { /* no video */ } else if (!FIJO && !reducido) await video.play().then(() => (medida.video = true)).catch(() => {})
    else video.load()
    medida.fases.video = performance.now()
    medida.cargado = true
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
}

/** Cycles thin glass -> see-through dark sheets (lab/vivo did the same). */
function vidrios(o: Object3D) {
  o.traverse((m) => {
    const mat = (m as Mesh).material as Material & { name: string } | undefined
    if (mat && /vidrio|mica|glass|pet/i.test(mat.name)) Object.assign(mat, { transparent: true, opacity: 0.15, depthWrite: false })
  })
}

/** Merges the static meshes under `g` (not past a node where `corta` is true) into as few meshes as it can, in g's local
 * space. Every untextured standard material on one side goes into a single mesh: its colour moves to the vertex colours, its
 * roughness, metalness and emissive to two small per-material lookup textures read through the uv. Textured and transparent
 * meshes merge per material. Skips skinned meshes, meshes without normals and `userData.solo`. */
function fusionar(g: Object3D, corta: (o: Object3D) => boolean) {
  g.updateMatrixWorld(true)
  const inv = new Matrix4().copy(g.matrixWorld).invert()
  const grupos = new Map<string, { mat: Material; geos: BufferGeometry[] }>()
  const planos = new Map<number, { mat: MeshStandardMaterial; geos: [BufferGeometry, number][] }>() // side -> geometries + lookup row
  const filas: MeshStandardMaterial[] = []
  const quitar: Mesh[] = []
  const rel = new Matrix4()
  const visitar = (o: Object3D) => {
    if (o !== g && corta(o)) return
    const m = o as Mesh
    const mat = m.material as MeshStandardMaterial
    if (m.isMesh && !(m as SkinnedMesh).isSkinnedMesh && !(m as InstancedMesh).isInstancedMesh && !Array.isArray(mat)
      && m.geometry.attributes.normal && !m.userData.solo && !m.morphTargetInfluences) {
      const plano = mat.isMeshStandardMaterial && !mat.transparent && !mat.map && !mat.emissiveMap && !mat.normalMap && !mat.roughnessMap
        && !mat.metalnessMap && !mat.aoMap && !mat.alphaMap && !mat.lightMap && !m.geometry.attributes.color && !mat.flatShading
      const src = m.geometry
      const n = src.attributes.position.count
      const geo = new BufferGeometry()
      geo.setAttribute('position', f32(src.attributes.position))
      geo.setAttribute('normal', f32(src.attributes.normal))
      if (!plano) geo.setAttribute('uv', src.attributes.uv ? f32(src.attributes.uv) : new BufferAttribute(new Float32Array(n * 2), 2))
      else {
        const c = new Float32Array(n * 3)
        for (let i = 0; i < n; i++) c.set([mat.color.r, mat.color.g, mat.color.b], i * 3)
        geo.setAttribute('color', new BufferAttribute(c, 3))
      }
      const idx = src.index ? Array.from(src.index.array) : Array.from({ length: n }, (_, i) => i)
      rel.multiplyMatrices(inv, m.matrixWorld)
      if (rel.determinant() < 0) for (let i = 0; i < idx.length; i += 3) [idx[i + 1], idx[i + 2]] = [idx[i + 2], idx[i + 1]] // mirrored: keep the winding
      geo.setIndex(idx)
      geo.applyMatrix4(rel)
      if (plano) {
        let p = planos.get(mat.side)
        if (!p) planos.set(mat.side, (p = { mat: new MeshStandardMaterial({ vertexColors: true, side: mat.side, roughness: 1, metalness: 1 }), geos: [] }))
        let f = filas.indexOf(mat)
        if (f < 0) f = filas.push(mat) - 1
        p.geos.push([geo, f])
      } else {
        let e = grupos.get(mat.uuid)
        if (!e) grupos.set(mat.uuid, (e = { mat, geos: [] }))
        e.geos.push(geo)
      }
      quitar.push(m)
    }
    for (const h of o.children) visitar(h)
  }
  visitar(g)
  for (const m of quitar) m.removeFromParent()
  for (const { mat, geos } of grupos.values()) {
    const merged = mergeGeometries(geos)
    if (merged) g.add(new Mesh(merged, mat))
  }
  if (!planos.size) return
  // lookup rows: G roughness, B metalness (three's roughness/metalness maps); emissive RGB scaled to the brightest
  const N = filas.length
  const em = filas.map((f) => f.emissive.clone().multiplyScalar(f.emissiveIntensity))
  const tope = Math.max(1e-6, ...em.flatMap((c) => [c.r, c.g, c.b]))
  const rm = new Uint8Array(N * 4), ed = new Uint8Array(N * 4)
  filas.forEach((f, i) => {
    rm.set([255, Math.round(f.roughness * 255), Math.round(f.metalness * 255), 255], i * 4)
    ed.set([em[i].r / tope * 255, em[i].g / tope * 255, em[i].b / tope * 255, 255].map(Math.round), i * 4)
  })
  const tabla = (a: Uint8Array) => Object.assign(new DataTexture(a, N, 1), { needsUpdate: true }) // NoColorSpace: linear values
  const tRM = tabla(rm), tE = tope > 1e-5 ? tabla(ed) : null
  for (const { mat, geos } of planos.values()) {
    for (const [geo, f] of geos) {
      const uv = new Float32Array(geo.attributes.position.count * 2)
      for (let i = 0; i < uv.length; i += 2) { uv[i] = (f + 0.5) / N; uv[i + 1] = 0.5 }
      geo.setAttribute('uv', new BufferAttribute(uv, 2))
    }
    Object.assign(mat, { roughnessMap: tRM, metalnessMap: tRM })
    if (tE) Object.assign(mat, { emissiveMap: tE, emissive: new Color(1, 1, 1), emissiveIntensity: tope })
    const merged = mergeGeometries(geos.map(([geo]) => geo))
    if (merged) g.add(new Mesh(merged, mat))
  }
}

function f32(a: BufferAttribute | InterleavedBufferAttribute) {
  const n = a.count, s = a.itemSize, out = new Float32Array(n * s)
  for (let i = 0; i < n; i++) for (let k = 0; k < s; k++) out[i * s + k] = k === 0 ? a.getX(i) : k === 1 ? a.getY(i) : k === 2 ? a.getZ(i) : a.getW(i)
  return new BufferAttribute(out, s)
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
