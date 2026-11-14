// Seek smoothness of the scroll-scrubbed clips in lab/scrub/index.html (Playwright Chromium, phone viewport, CPU throttled).
//   node lab/scrub/medir-scrub.mjs http://127.0.0.1:3107/lab/scrub/ [throttle=4] clip.mp4 ...
// Prints one TSV row per clip and throttle: bytes, seek latency p50/p95 (ms), seeks requested / overtaken, frames presented
// while scrolling (rVFC) and the mean gap between scroll target and presented frame (s).
import { chromium } from "/home/black/projects/visual-lab/web/skills/diseccion/scripts/node_modules/playwright-core/index.mjs";

const [base, thr = "4", ...clips] = process.argv.slice(2);
const pct = (a, p) => { const s = [...a].sort((x, y) => x - y); return s.length ? s[Math.min(s.length - 1, Math.floor(p * s.length))] : NaN; };
const browser = await chromium.launch();
console.log(["clip", "cpu_x", "MB", "seek_p50_ms", "seek_p95_ms", "pedidos", "adelantados", "cuadros", "fps_scroll", "desfase_medio_s", "h264"].join("\t"));
for (const clip of clips) {
  for (const rate of [1, Number(thr)]) {
    const ctx = await browser.newContext({ viewport: { width: 390, height: 844 }, deviceScaleFactor: 2, isMobile: true, hasTouch: true });
    const page = await ctx.newPage();
    const cdp = await ctx.newCDPSession(page);
    await cdp.send("Emulation.setCPUThrottlingRate", { rate });
    await page.goto(`${base}?clip=${clip}`);
    await page.waitForFunction(() => window.__scrub.listo, null, { timeout: 30000 });
    await page.evaluate(() => { const S = window.__scrub; S.lat = []; S.pedidos = S.adelantados = S.cuadros = 0; S.desfase = []; });
    const t0 = Date.now();
    for (let i = 0; i < 240; i++) {  // ~4 s of steady wheel scrolling, down the whole track (500vh)
      await page.evaluate(() => scrollBy(0, (document.documentElement.scrollHeight - innerHeight) / 240));
      await page.waitForTimeout(16);
    }
    const secs = (Date.now() - t0) / 1000;
    await page.waitForTimeout(500);
    const S = await page.evaluate(() => window.__scrub);
    const mean = S.desfase.reduce((a, b) => a + b, 0) / (S.desfase.length || 1);
    console.log([clip, rate, (S.bytes / 1e6).toFixed(3), pct(S.lat, 0.5).toFixed(1), pct(S.lat, 0.95).toFixed(1), S.pedidos, S.adelantados,
      S.cuadros, (S.cuadros / secs).toFixed(1), mean.toFixed(3), S.puede].join("\t"));
    await ctx.close();
  }
}
await browser.close();
