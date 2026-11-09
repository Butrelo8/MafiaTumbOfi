// Live scene: one truck held still, the world scrolls under it; camera moves between the stops in escena.json.
import {
  WebGLRenderer, Scene, PerspectiveCamera, Group, Mesh, PlaneGeometry, MeshStandardMaterial, MeshBasicMaterial,
  TextureLoader, RepeatWrapping, SRGBColorSpace, EquirectangularReflectionMapping, PMREMGenerator, FogExp2, Color,
  SpotLight, PointLight, DirectionalLight, Vector3, AgXToneMapping, CanvasTexture, AdditiveBlending,
  type Texture,
} from 'three'
import { GLTFLoader } from 'three/examples/jsm/loaders/GLTFLoader.js'
import { HDRLoader } from 'three/examples/jsm/loaders/HDRLoader.js'
import cfg from '../lib/escena.json'

type Preset = keyof typeof cfg.presets
type Stop = (typeof cfg.paradas)[number]
const M = cfg.mundo
const SPEED = M.recorrido_loop / M.loop_s // m/s, same as the Cycles loop
const MOVE_S = 1.6

export interface Escena {
  ir(id: string): void
  preset(p: Preset): Promise<void>
  frameTimes: number[]
  parar(): void
}

export async function iniciar(canvas: HTMLCanvasElement, opts: { reducido: boolean; preset: Preset; parada: string }): Promise<Escena> {
  const renderer = new WebGLRenderer({ canvas, antialias: true, powerPreference: 'high-performance' })
  renderer.setPixelRatio(Math.min(devicePixelRatio, 1.75))
  renderer.toneMapping = AgXToneMapping
  renderer.outputColorSpace = SRGBColorSpace
  const scene = new Scene()
  const cam = new PerspectiveCamera(40, 1, 0.1, 3000)
  const pmrem = new PMREMGenerator(renderer)
  const tex = new TextureLoader()

  const [gltf] = await Promise.all([new GLTFLoader().loadAsync('/escena/escena.glb')])
  const raiz = gltf.scene
  const ruedas = ['BackWheels', 'FrontWheel_L', 'FrontWheel_R'].map((n) => raiz.getObjectByName(n)!).filter(Boolean)
  const camion = raiz.getObjectByName('camion')!
  const cerros = raiz.getObjectByName('cerros') as Mesh
  scene.add(camion, cerros)
  ;(cerros.material as MeshStandardMaterial).fog = false

  // one tramo of props, cloned along the road; the whole group wraps every M.tramo metres
  const tramo = new Group()
  for (const o of [...raiz.children]) if (o !== camion && o !== cerros) tramo.add(o)
  const mundo = new Group()
  scene.add(mundo)
  const charco = charcoTex()
  const matCharco = new MeshBasicMaterial({ map: charco, transparent: true, blending: AdditiveBlending, depthWrite: false, fog: true })
  const lamparas: MeshStandardMaterial[] = []
  tramo.traverse((o) => { const m = (o as Mesh).material as MeshStandardMaterial; if (m?.name === 'lampara') lamparas.push(m) })
  const postes: SpotLight[] = []
  for (let k = -2; k < 10; k++) {
    const t = k === 0 ? tramo : tramo.clone()
    t.position.z = -k * M.tramo
    const c = new Mesh(new PlaneGeometry(16, 16), matCharco)
    c.rotation.x = -Math.PI / 2
    c.position.set(3.4, 0.03, -8)
    t.add(c)
    if (k === 0 || k === 1) { // real light only for the two poles that pass the truck
      const s = new SpotLight(0xffffff, 0, 28, 1.1, 0.7, 1.4)
      s.position.set(3.95, 8.7, -8)
      s.target.position.set(3.0, 0, -8)
      t.add(s, s.target)
      postes.push(s)
    }
    mundo.add(t)
  }

  // road and ground: textured planes whose texture scrolls (seamless: tile lengths divide the loop distance)
  const rep = (t: Texture, x: number, y: number, srgb = false) => {
    t.wrapS = t.wrapT = RepeatWrapping; t.repeat.set(x, y); t.anisotropy = 8
    if (srgb) t.colorSpace = SRGBColorSpace
    return t
  }
  const LARGO = 640
  const roadMaps = await Promise.all(['carretera.jpg', 'carretera-normal.jpg', 'carretera-rugosidad.jpg'].map((f) => tex.loadAsync(`/escena/${f}`)))
  roadMaps.forEach((t, i) => rep(t, 1, LARGO / M.losa, i === 0))
  const road = new Mesh(new PlaneGeometry(8, LARGO), new MeshStandardMaterial({ map: roadMaps[0], normalMap: roadMaps[1], roughnessMap: roadMaps[2] }))
  road.rotation.x = -Math.PI / 2
  road.position.set(0, 0.015, -LARGO / 2 + 120)
  const groundMap = rep(await tex.loadAsync('/escena/terreno.jpg'), 3000 / 4, 3000 / 4, true)
  const ground = new Mesh(new PlaneGeometry(3000, 3000), new MeshStandardMaterial({ map: groundMap, color: new Color(0.22, 0.19, 0.16), roughness: 1 }))
  ground.rotation.x = -Math.PI / 2
  scene.add(road, ground)

  // truck lights
  const faros = [-0.62, 0.62].map((dx) => {
    const s = new SpotLight(0xffffff, 0, 70, 0.5, 0.55, 1.2)
    s.position.set(M.carril_x + dx, 0.85, -M.largo_camion / 2 - 0.05)
    s.target.position.set(M.carril_x + dx * 3, 0, -M.largo_camion / 2 - 25)
    scene.add(s, s.target)
    return s
  })
  const calaveras = new PointLight(0xff2a1a, 0, 6, 2)
  calaveras.position.set(M.carril_x, 0.9, M.largo_camion / 2 + 0.3)
  const luna = new DirectionalLight(0xffffff, 0)
  scene.add(calaveras, luna)

  // presets
  const hdrCache: Record<string, Texture> = {}
  async function preset(p: Preset) {
    const P = cfg.presets[p]
    if (!hdrCache[P.hdri]) {
      const h = await new HDRLoader().loadAsync(`/escena/${P.hdri}.hdr`)
      h.mapping = EquirectangularReflectionMapping
      hdrCache[P.hdri] = h
    }
    const h = hdrCache[P.hdri]
    scene.background = h
    scene.environment = pmrem.fromEquirectangular(h).texture
    scene.backgroundIntensity = P.cielo_intensidad
    scene.environmentIntensity = P.cielo_intensidad * 2
    scene.fog = new FogExp2(P.niebla.color, P.niebla.densidad)
    renderer.toneMappingExposure = P.exposicion
    faros.forEach((s) => { s.color.set(P.faros.color); s.intensity = P.faros.intensidad * 6; s.distance = P.faros.alcance })
    calaveras.color.set(P.calaveras.color); calaveras.intensity = P.calaveras.intensidad
    luna.color.set(P.luna.color); luna.intensity = P.luna.intensidad * 3
    luna.position.set(...(P.luna.dir as [number, number, number])).multiplyScalar(50)
    postes.forEach((s) => { s.color.set(P.postes.color); s.intensity = P.postes.intensidad * 220 })
    lamparas.forEach((m) => (m.emissiveIntensity = P.postes.encendidos ? 6 : 0))
    matCharco.color.set(P.postes.color).multiplyScalar(P.postes.intensidad * 0.35)
  }
  await preset(opts.preset)

  // camera stops
  const fovFor = (fov: number) => {
    const a = cam.aspect
    return a >= 1 ? fov : (2 * Math.atan(Math.tan((fov * Math.PI) / 360) / a) * 180) / Math.PI
  }
  const get = (id: string) => cfg.paradas.find((s) => s.id === id) ?? cfg.paradas[0]
  let desde: Stop = get(opts.parada), hacia: Stop = desde, t0 = -1
  const pos = new Vector3(), mira = new Vector3(), a = new Vector3(), b = new Vector3()
  function pose(s: Stop, s2: Stop, k: number) {
    const e = k < 0.5 ? 4 * k * k * k : 1 - Math.pow(-2 * k + 2, 3) / 2
    pos.lerpVectors(a.fromArray(s.pos), b.fromArray(s2.pos), e)
    mira.lerpVectors(a.fromArray(s.mira), b.fromArray(s2.mira), e)
    cam.position.copy(pos)
    cam.fov = fovFor(s.fov + (s2.fov - s.fov) * e)
    cam.updateProjectionMatrix()
    cam.lookAt(mira)
  }
  function ir(id: string) {
    const s = get(id)
    if (s === hacia) return
    desde = hacia; hacia = s
    t0 = opts.reducido ? -1 : performance.now()
    if (opts.reducido) desde = s
  }

  function resize() {
    const w = canvas.clientWidth, h = canvas.clientHeight
    renderer.setSize(w, h, false)
    cam.aspect = w / h
  }
  addEventListener('resize', resize)
  resize()

  const frameTimes: number[] = []
  let last = performance.now(), recorrido = 0
  const speed = opts.reducido ? 0 : SPEED
  const radio = 0.474 // wheel radius printed by blender/escena.py (RADIO)
  function frame(now: number) {
    const dt = Math.min((now - last) / 1000, 0.1)
    frameTimes.push(now - last)
    if (frameTimes.length > 600) frameTimes.shift()
    last = now
    recorrido += speed * dt
    mundo.position.z = recorrido % M.tramo
    road.material.map!.offset.y = roadMaps[1].offset.y = roadMaps[2].offset.y = (recorrido / M.losa) % 1
    groundMap.offset.y = (recorrido / 4) % 1
    for (const r of ruedas) r.rotation.x = -(recorrido / radio) % (Math.PI * 2)
    const k = t0 < 0 ? 1 : Math.min((now - t0) / (MOVE_S * 1000), 1)
    if (k >= 1) { desde = hacia; t0 = -1 }
    pose(desde, hacia, k)
    renderer.render(scene, cam)
  }
  renderer.setAnimationLoop(frame)
  document.addEventListener('visibilitychange', () => {
    renderer.setAnimationLoop(document.hidden ? null : (n) => frame(n))
    last = performance.now()
  })
  return { ir, preset, frameTimes, parar: () => renderer.setAnimationLoop(null) }
}

function charcoTex() {
  const c = document.createElement('canvas')
  c.width = c.height = 128
  const g = c.getContext('2d')!
  const r = g.createRadialGradient(64, 64, 0, 64, 64, 64)
  r.addColorStop(0, 'rgba(255,255,255,1)')
  r.addColorStop(0.45, 'rgba(255,255,255,0.35)')
  r.addColorStop(1, 'rgba(255,255,255,0)')
  g.fillStyle = r
  g.fillRect(0, 0, 128, 128)
  return new CanvasTexture(c)
}
