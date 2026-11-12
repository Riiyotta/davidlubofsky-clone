// Live-vs-clone parity capture (BASELINE R12). Captures the SAME scroll offsets on both
// sides at 1440x900 and records in-flow section boxes from the clone. Screenshots go to
// PARITY_OUT (an OS temp dir) and are never committed; parity_score.py turns them into
// text-free numbers in extraction/parity-results.json.
//
//   PLAYWRIGHT_DIR=<dir with node_modules/playwright> CLONE_URL=http://localhost:5191 \
//   LIVE_URL=<original site origin> PARITY_OUT=<temp dir> node extraction/parity_capture.mjs
//
// Determinism: wait for fonts + network idle, scroll the whole page once (lazy images),
// pause every <video> at t=0 (awaiting the seek) before each frame, identical waits on both
// sides. No consent banners exist on the source; nothing is clicked. Physics bodies use
// Math.random by design and cannot be frozen; affected sections are reported as exceptions.
import { createRequire } from 'module';
import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';

const here = path.dirname(fileURLToPath(import.meta.url));
const req = createRequire(path.join(process.env.PLAYWRIGHT_DIR || process.cwd(), 'package.json'));
const { chromium } = req('playwright');
const CLONE = process.env.CLONE_URL || 'http://localhost:5191';
const LIVE = process.env.LIVE_URL;
const OUT = process.env.PARITY_OUT;
if (!LIVE || !OUT) { console.error('set LIVE_URL and PARITY_OUT'); process.exit(2); }
fs.mkdirSync(OUT, { recursive: true });
const { routes } = JSON.parse(fs.readFileSync(path.join(here, '..', 'templates', 'routes.json'), 'utf8'));
const { sections } = JSON.parse(fs.readFileSync(path.join(here, 'section-selectors.json'), 'utf8'));
const STEP = 900;

const freezeVideos = (page) => page.evaluate(async () => {
  await Promise.all([...document.querySelectorAll('video')].map((v) => new Promise((res) => {
    v.pause();
    if (v.currentTime === 0) return res();
    v.addEventListener('seeked', res, { once: true });
    v.currentTime = 0;
    setTimeout(res, 1500);
  })));
});

async function prepare(browser, url) {
  const page = await browser.newPage({ viewport: { width: 1440, height: 900 } });
  await page.goto(url, { waitUntil: 'networkidle', timeout: 90000 });
  await page.evaluate(() => document.fonts.ready);
  await page.waitForTimeout(6500);
  const h = await page.evaluate(() => document.documentElement.scrollHeight);
  for (let y = 0; y < h; y += 700) { await page.evaluate((v) => window.scrollTo(0, v), y); await page.waitForTimeout(150); }
  await page.evaluate(() => window.scrollTo(0, 0));
  await page.waitForTimeout(1000);
  return { page, h };
}

const browser = await chromium.launch();
const meta = { step: STEP, viewport: [1440, 900], routes: {} };
for (const r of routes) {
  const slug = r.path === '/' ? 'home' : r.path.split('/')[2];
  const [clone, live] = await Promise.all([prepare(browser, CLONE + r.path), prepare(browser, LIVE + r.path)]);
  const boxes = await clone.page.evaluate((secs) => {
    const out = [];
    for (const [id, s] of Object.entries(secs)) {
      document.querySelectorAll(s.selector).forEach((el) => {
        let fixed = false;
        for (let n = el; n && n !== document.body; n = n.parentElement) if (getComputedStyle(n).position === 'fixed') fixed = true;
        if (fixed || getComputedStyle(el).position === 'absolute') return;
        const b = el.getBoundingClientRect();
        out.push({ id, top: Math.round(b.top + scrollY), height: Math.round(b.height) });
      });
    }
    return out.sort((a, b) => a.top - b.top);
  }, sections);
  const frames = [];
  for (let y = 0; y < Math.max(clone.h, live.h); y += STEP) {
    for (const [side, ctx] of [['clone', clone], ['live', live]]) {
      await ctx.page.evaluate((v) => window.scrollTo(0, v), y);
    }
    await Promise.all([clone.page.mouse.move(5, 5), live.page.mouse.move(5, 5)]);
    await Promise.all([clone.page.mouse.wheel(0, 1), live.page.mouse.wheel(0, 1)]);
    await new Promise((res) => setTimeout(res, 1300));
    await Promise.all([freezeVideos(clone.page), freezeVideos(live.page)]);
    const ys = {};
    for (const [side, ctx] of [['clone', clone], ['live', live]]) {
      ys[side] = await ctx.page.evaluate(() => Math.round(scrollY));
      await ctx.page.screenshot({ path: path.join(OUT, `${side}-${slug}-${y}.png`) });
    }
    frames.push({ y, scrollY: ys });
  }
  meta.routes[r.path] = { slug, pageHeight: { clone: clone.h, live: live.h }, boxes, frames };
  await clone.page.close(); await live.page.close();
  process.stderr.write(`captured ${r.path}\n`);
}
await browser.close();
fs.writeFileSync(path.join(OUT, 'capture.json'), JSON.stringify(meta, null, 1));
