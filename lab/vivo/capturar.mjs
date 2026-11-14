// Frames of the live proof (lab/vivo/index.html?f=N) at 1280x720 for the side-by-side with the v3 Cycles frames, plus the
// WebGL renderer string, load time and render cost while scrolling.
//   node lab/vivo/capturar.mjs http://127.0.0.1:3107/lab/vivo/ <out_dir> [frames=0,96,191]
import { chromium } from "/home/black/projects/visual-lab/web/skills/diseccion/scripts/node_modules/playwright-core/index.mjs";

const [base, out, fl = "0,96,191"] = process.argv.slice(2);
const browser = await chromium.launch({ args: (process.env.ARGS || "").split(" ").filter(Boolean) });
const page = await browser.newPage({ viewport: { width: 1280, height: 720 } });
page.on("pageerror", (e) => console.log("ERROR", e.message));
for (const f of fl.split(",")) {
  await page.goto(`${base}?f=${f}`);
  await page.waitForFunction(() => window.__vivo?.listo, null, { timeout: 120000, polling: 500 }); console.error("listo", page.url());
  await page.waitForTimeout(1500);
  await page.evaluate(() => (document.getElementById("info").style.display = "none"));
  const png = await page.evaluate(() => document.getElementById("c").toDataURL("image/png"));  // canvas read: a page screenshot waits on a busy GPU loop
  (await import("node:fs")).writeFileSync(`${out}/vivo-f${f.padStart(3, "0")}.png`, Buffer.from(png.split(",")[1], "base64")); console.error("png", f);
}
await page.goto(base);
await page.waitForFunction(() => window.__vivo?.listo, null, { timeout: 120000, polling: 500 }); console.error("listo", page.url());
for (let i = 0; i < 120; i++) { await page.evaluate(() => scrollBy(0, 60)); await page.waitForTimeout(16); }  // mouse.wheel hangs on a busy WebGL loop
await page.waitForTimeout(1000);
const S = await page.evaluate(() => window.__vivo);
const pct = (a, p) => [...a].sort((x, y) => x - y)[Math.floor(p * (a.length - 1))];
console.log(JSON.stringify({ GPU: S.GPU, tris: S.tris, cargaMs: S.cargaMs, render_p50_ms: pct(S.render, 0.5), render_p95_ms: pct(S.render, 0.95), frame_p50_ms: pct(S.dt, 0.5), frame_p95_ms: pct(S.dt, 0.95) }));
await browser.close();
