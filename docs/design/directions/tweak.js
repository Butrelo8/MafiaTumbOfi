// Tweak bar for A Carretera (handoff-a-build.md step 1). Runs only with ?tweak in the URL; it only rewrites CSS custom
// properties and the hero media, so index.html keeps comparing A, B and C unchanged. Every knob is mirrored in the hash
// and "Copiar ajustes" gives the block to send back.
(() => {
  if (!new URLSearchParams(location.search).has('tweak')) return;

  // Bounds: gold hue and lightness stay near the logo's bevel (photo_palette.py on public/icon/mafiatumbada.webp:
  // gold-52 oklch(52% .065 85), gold-68 oklch(68% .052 86)); A's default is oklch(80% .13 82).
  const DEF = { hue: 82, light: 80, veil: 0.62, cara: 'saira-italica', nombre: 1, hora: 'noche', fondo: 'loop' };
  const CARAS = {
    'saira-italica': { label: 'Saira Condensed 800 itálica (A)', fam: '"Saira Condensed"', w: 800, s: 'italic' },
    'saira-recta': { label: 'Saira Condensed 800 recta', fam: '"Saira Condensed"', w: 800, s: 'normal' },
    'reddit': { label: 'Reddit Sans Condensed 900 (urielurbina)', fam: '"Reddit Sans Condensed"', w: 900, s: 'normal' },
  };
  // Dusk: frames of the live three.js scene (src/ truck page, preset atardecer, UI hidden, SwiftShader), not Cycles.
  const DUSK = { wide: '/docs/design/directions/atardecer/poster-1600x900.jpg', tall: '/docs/design/directions/atardecer/poster-720x1280.jpg' };
  const NIGHT = { wide: '/public/escena/poster-1600x900.jpg', tall: '/public/escena/poster-720x1280.jpg' };

  const st = { ...DEF };
  for (const [k, v] of new URLSearchParams(location.hash.slice(1))) if (k in DEF) st[k] = typeof DEF[k] === 'number' ? +v : v;

  const font = document.createElement('link');
  font.rel = 'stylesheet';
  font.href = 'https://fonts.googleapis.com/css2?family=Reddit+Sans+Condensed:wght@900&display=swap';
  document.head.append(font);

  const css = document.createElement('style');
  css.textContent = `
h1,h2,.disp,.rel b,.m h3{font-family:var(--disp),sans-serif!important;font-weight:var(--disp-w)!important;font-style:var(--disp-s)!important}
.hero h1{font-size:calc(clamp(64px,13vw,200px)*var(--nombre,1))}
html[data-fondo=poster] #loop{display:none}
.tw{position:fixed;right:12px;bottom:12px;z-index:20;max-width:min(360px,calc(100vw - 24px));font:400 15px/1.4 Saira,system-ui,sans-serif;color:var(--ink)}
.tw>button,.tw .row button{min-height:44px;padding:0 16px;border:2px solid var(--gold);background:#000;color:var(--ink);font:600 15px Saira,sans-serif;cursor:pointer}
.tw form{margin-top:8px;padding:14px;background:#000;border:1px solid oklch(100% 0 0/.25);display:grid;gap:10px;max-height:70svh;overflow:auto}
.tw form[hidden]{display:none}
.tw label,.tw legend{display:block;font-weight:600}
.tw input[type=range]{width:100%;min-height:44px;accent-color:var(--gold)}
.tw select{width:100%;min-height:44px;background:#000;color:var(--ink);border:1px solid oklch(100% 0 0/.4);font:inherit}
.tw fieldset{border:0;padding:0;display:flex;flex-wrap:wrap;gap:4px 14px}
.tw fieldset label{display:inline-flex;align-items:center;gap:6px;min-height:44px;font-weight:400}
.tw .row{display:flex;gap:8px;flex-wrap:wrap}
.tw output,.tw small{color:var(--muted)}
.tw .bad{color:oklch(75% .17 30)}
.tw textarea{width:100%;min-height:96px;background:#000;color:var(--ink);border:1px solid oklch(100% 0 0/.4);font:13px/1.4 ui-monospace,monospace}`;
  document.head.append(css);

  const caraOpts = Object.entries(CARAS).map(([k, c]) => `<option value="${k}">${c.label}</option>`).join('');
  const box = document.createElement('aside');
  box.className = 'tw';
  box.setAttribute('aria-label', 'Ajustes de la dirección A');
  box.innerHTML = `
<button type="button" aria-expanded="true" aria-controls="tw-f">Ajustes</button>
<form id="tw-f">
  <div><label for="tw-hue">Tono del dorado <output id="o-hue"></output></label><input id="tw-hue" name="hue" type="range" min="70" max="95" step="1"></div>
  <div><label for="tw-light">Luz del dorado <output id="o-light"></output></label><input id="tw-light" name="light" type="range" min="62" max="88" step="1"></div>
  <p id="tw-con" role="status" aria-live="polite"></p>
  <div><label for="tw-veil">Velo bajo el texto <output id="o-veil"></output></label><input id="tw-veil" name="veil" type="range" min="0.35" max="0.85" step="0.01"></div>
  <div><label for="tw-cara">Letra de títulos</label><select id="tw-cara" name="cara">${caraOpts}</select>
    <small>Reddit Sans no tiene itálica: pierde la inclinación del logo.</small></div>
  <div><label for="tw-nombre">Tamaño del nombre <output id="o-nombre"></output></label><input id="tw-nombre" name="nombre" type="range" min="0.6" max="1.3" step="0.05"></div>
  <fieldset><legend>Hora</legend>
    <label><input type="radio" name="hora" value="noche"> Noche</label>
    <label><input type="radio" name="hora" value="atardecer"> Atardecer</label></fieldset>
  <small id="tw-dusk">Atardecer: cuadro de la escena en vivo (three.js), no del render Cycles. No hay loop de atardecer: si lo eliges, se renderiza (unos 20 min). La pintura negra se ve plateada con esta luz.</small>
  <fieldset><legend>Fondo del inicio</legend>
    <label><input type="radio" name="fondo" value="loop"> Video en loop</label>
    <label><input type="radio" name="fondo" value="poster"> Imagen fija</label></fieldset>
  <div class="row"><button type="button" id="tw-copy">Copiar ajustes</button><button type="button" id="tw-reset">Restablecer</button></div>
  <label for="tw-out">Ajustes para enviar</label><textarea id="tw-out" readonly></textarea>
</form>`;
  document.body.append(box);
  const $ = (s) => box.querySelector(s), f = $('form'), root = document.documentElement;

  // WCAG 2 contrast via the browser's own oklch → sRGB (canvas), so the numbers match what renders.
  const cv = document.createElement('canvas').getContext('2d', { willReadFrequently: true });
  const rgb = (c) => { cv.clearRect(0, 0, 1, 1); cv.fillStyle = c; cv.fillRect(0, 0, 1, 1); return [...cv.getImageData(0, 0, 1, 1).data].slice(0, 3); };
  const lum = (c) => rgb(c).map((v) => (v /= 255) <= 0.04045 ? v / 12.92 : ((v + 0.055) / 1.055) ** 2.4).reduce((a, v, i) => a + v * [0.2126, 0.7152, 0.0722][i], 0);
  const ratio = (a, b) => { const [x, y] = [lum(a), lum(b)].sort((p, q) => q - p); return (x + 0.05) / (y + 0.05); };

  function apply() {
    const gold = `oklch(${st.light}% .13 ${st.hue})`, c = CARAS[st.cara] || CARAS[DEF.cara];
    const s = root.style;
    s.setProperty('--gold', gold);
    s.setProperty('--gold-deep', `oklch(${st.light - 18}% .11 ${st.hue - 12})`);
    s.setProperty('--veil', `rgb(0 0 0/${st.veil})`);
    s.setProperty('--disp', c.fam); s.setProperty('--disp-w', c.w); s.setProperty('--disp-s', c.s);
    s.setProperty('--nombre', st.nombre);
    root.dataset.fondo = st.hora === 'atardecer' ? 'poster' : st.fondo;
    const src = st.hora === 'atardecer' ? DUSK : NIGHT, tall = matchMedia('(max-width: 700px)').matches;
    document.querySelectorAll('.hero .poster, .contact > img').forEach((i) => (i.src = tall && i.classList.contains('poster') ? src.tall : src.wide));
    const v = document.getElementById('loop');
    if (v) root.dataset.fondo === 'poster' ? v.pause() : v.play().catch(() => {});
    $('#tw-dusk').hidden = st.hora !== 'atardecer';

    const g = ratio(gold, '#000');
    $('#tw-con').innerHTML = `Contraste dorado / negro (títulos y botón lleno): <b class="${g < 4.5 ? 'bad' : ''}">${g.toFixed(2)}:1</b>${g < 4.5 ? ', bajo 4.5:1, no pasa AA' : ''}. El velo sobre la imagen lo mide revisar.sh en el build.`;
    $('#o-hue').value = st.hue; $('#o-light').value = st.light + '%'; $('#o-veil').value = st.veil.toFixed(2); $('#o-nombre').value = '×' + st.nombre;
    for (const el of f.elements) {
      if (!el.name) continue;
      if (el.type === 'radio') el.checked = st[el.name] === el.value; else el.value = st[el.name];
    }
    const out = { direccion: 'A Carretera', ...st, dorado: gold, letra: c.label };
    $('#tw-out').value = JSON.stringify(out, null, 1);
    history.replaceState(null, '', '#' + new URLSearchParams(Object.entries(st)).toString());
  }

  f.addEventListener('input', (e) => {
    const el = e.target; if (!el.name) return;
    st[el.name] = typeof DEF[el.name] === 'number' ? +el.value : el.value;
    apply();
  });
  $('#tw-reset').addEventListener('click', () => { Object.assign(st, DEF); apply(); });
  $('#tw-copy').addEventListener('click', async () => {
    const t = $('#tw-out'); t.select();
    try { await navigator.clipboard.writeText(t.value); $('#tw-copy').textContent = 'Copiado'; } catch { $('#tw-copy').textContent = 'Selecciona y copia el texto'; }
  });
  $('.tw > button').addEventListener('click', (e) => {
    const open = e.currentTarget.getAttribute('aria-expanded') !== 'true';
    e.currentTarget.setAttribute('aria-expanded', open); f.hidden = !open;
  });
  if (matchMedia('(max-width: 700px)').matches) { $('.tw > button').setAttribute('aria-expanded', 'false'); f.hidden = true; }
  apply();
})();
