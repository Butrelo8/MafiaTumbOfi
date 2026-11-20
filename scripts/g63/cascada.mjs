#!/usr/bin/env node
// (PW=... CHROME=... WSLENV=PW:CHROME node.exe scripts/g63/cascada.mjs <url>)
// Waterfall on Fast 4G 390, cold cache: per request start / end (ms from navigation), bytes, and the first frame.
import { createRequire } from 'node:module'
const require = createRequire(import.meta.url)
const { chromium } = require(process.env.PW)
const [url] = process.argv.slice(2)
const browser = await chromium.launch({ executablePath: process.env.CHROME, args: ['--ignore-gpu-blocklist', '--autoplay-policy=no-user-gesture-required'] })
const ctx = await browser.newContext({ viewport: { width: 390, height: 844 }, deviceScaleFactor: 3, isMobile: true, hasTouch: true })
const page = await ctx.newPage()
const cdp = await ctx.newCDPSession(page)
await cdp.send('Network.enable')
await cdp.send('Network.setCacheDisabled', { cacheDisabled: true })
await cdp.send('Network.emulateNetworkConditions', { offline: false, latency: 165, downloadThroughput: 9e6 / 8, uploadThroughput: 1.5e6 / 8 })
const R = {}
let base = null
cdp.on('Network.requestWillBeSent', (e) => { base ??= e.timestamp; R[e.requestId] = { u: e.request.url.replace(/^https?:\/\/[^/]+/, '').slice(0, 60), s: (e.timestamp - base) * 1000 } })
cdp.on('Network.responseReceived', (e) => { if (R[e.requestId]) R[e.requestId].r = (e.timestamp - base) * 1000 })
cdp.on('Network.loadingFinished', (e) => { if (R[e.requestId]) { R[e.requestId].e = (e.timestamp - base) * 1000; R[e.requestId].n = e.encodedDataLength } })
const t0 = Date.now()
await page.goto(url, { waitUntil: 'commit' })
await page.waitForFunction(() => window.__vivo?.ttff > 0, null, { timeout: 300000, polling: 100 })
const ttff = await page.evaluate(() => window.__vivo.ttff)
const wall = Date.now() - t0
await page.waitForTimeout(500)
const rows = Object.values(R).sort((a, b) => a.s - b.s)
for (const r of rows) console.log(String((r.s | 0)).padStart(6), String(r.r | 0).padStart(6), String(r.e | 0).padStart(6), String(r.n ?? '').padStart(8), r.u)
console.log('TTFF', Math.round(ttff), 'wall', wall)
await browser.close()
