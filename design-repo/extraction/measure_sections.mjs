// Re-measure tool (optional; R9). Captures, for every route, the document-order list of
// sections (semantic id, top, height, flow) at 1440 / 768 / 390px, plus computed-style
// histograms (colours, type, radius) at 1440px. Output is text-free geometry/values only.
//
//   PLAYWRIGHT_DIR=<dir containing node_modules/playwright> \
//   CLONE_URL=http://localhost:5191 node extraction/measure_sections.mjs > out.json
//
// The browser module is resolved from PLAYWRIGHT_DIR (or the current working directory);
// no absolute machine path is stored in this repository.
import { createRequire } from 'module';
import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';

const here = path.dirname(fileURLToPath(import.meta.url));
const req = createRequire(path.join(process.env.PLAYWRIGHT_DIR || process.cwd(), 'package.json'));
const { chromium } = req('playwright');
const base = process.env.CLONE_URL || 'http://localhost:5191';
const { routes } = JSON.parse(fs.readFileSync(path.join(here, '..', 'templates', 'routes.json'), 'utf8'));
const { sections } = JSON.parse(fs.readFileSync(path.join(here, 'section-selectors.json'), 'utf8'));
const VIEWPORTS = [1440, 768, 390];

const browser = await chromium.launch();
const out = { measuredWith: 'headless chromium via playwright', baseUrlKind: 'local clone dev server', settleMs: 6500, viewports: VIEWPORTS, routes: {}, histograms: {} };

for (const r of routes) {
  out.routes[r.path] = {};
  for (const vw of VIEWPORTS) {
    const page = await browser.newPage({ viewport: { width: vw, height: 900 }, isMobile: vw < 650, hasTouch: vw < 650 });
    await page.goto(base + r.path, { waitUntil: 'networkidle', timeout: 90000 });
    await page.waitForTimeout(6500);
    // Scroll through once so lazy images load and layout settles, then return to top.
    const h0 = await page.evaluate(() => document.documentElement.scrollHeight);
    for (let y = 0; y < h0; y += 800) { await page.evaluate((v) => window.scrollTo(0, v), y); await page.waitForTimeout(120); }
    await page.evaluate(() => window.scrollTo(0, 0));
    await page.waitForTimeout(800);
    const data = await page.evaluate((secs) => {
      const flowOf = (el) => {
        for (let n = el; n && n !== document.body; n = n.parentElement) {
          const p = getComputedStyle(n).position;
          if (p === 'fixed') return 'fixed';
          if (n === el && p === 'absolute') return 'absolute';
        }
        return 'in-flow';
      };
      const found = [];
      for (const [id, s] of Object.entries(secs)) {
        document.querySelectorAll(s.selector).forEach((el) => {
          const b = el.getBoundingClientRect();
          found.push({ id, top: Math.round(b.top + window.scrollY), height: Math.round(b.height), flow: flowOf(el) });
        });
      }
      found.sort((a, b) => a.top - b.top);
      return { pageHeight: document.documentElement.scrollHeight, sections: found };
    }, sections);
    out.routes[r.path][String(vw)] = data;
    if (vw === 1440) {
      const hist = await page.evaluate(() => {
        const H = { color: {}, backgroundColor: {}, borderColor: {}, fill: {}, stroke: {}, fontFamily: {}, fontSize: {}, fontWeight: {}, lineHeight: {}, letterSpacing: {}, fontVariationSettings: {}, borderRadius: {} };
        const add = (k, v) => { if (!v || v === 'normal' && k !== 'fontVariationSettings' && k !== 'lineHeight' && k !== 'letterSpacing') return; H[k][v] = (H[k][v] || 0) + 1; };
        for (const el of document.querySelectorAll('body *')) {
          const cs = getComputedStyle(el);
          if (cs.display === 'none' || cs.visibility === 'hidden') continue;
          const hasText = [...el.childNodes].some((n) => n.nodeType === 3 && n.textContent.trim());
          if (hasText) {
            add('color', cs.color); add('fontFamily', cs.fontFamily.split(',')[0].replace(/"/g, '').trim()); add('fontSize', cs.fontSize);
            add('fontWeight', cs.fontWeight); add('lineHeight', cs.lineHeight); add('letterSpacing', cs.letterSpacing); add('fontVariationSettings', cs.fontVariationSettings);
          }
          if (cs.backgroundColor !== 'rgba(0, 0, 0, 0)') add('backgroundColor', cs.backgroundColor);
          if (parseFloat(cs.borderTopWidth) > 0) add('borderColor', cs.borderTopColor);
          if (el instanceof SVGElement) { if (el.getAttribute('fill') && el.getAttribute('fill') !== 'none') add('fill', el.getAttribute('fill').toUpperCase()); if (el.getAttribute('stroke')) add('stroke', el.getAttribute('stroke').toUpperCase()); }
          if (cs.borderTopLeftRadius !== '0px') add('borderRadius', cs.borderTopLeftRadius);
        }
        return H;
      });
      for (const [k, m] of Object.entries(hist)) {
        out.histograms[k] = out.histograms[k] || {};
        for (const [v, c] of Object.entries(m)) out.histograms[k][v] = (out.histograms[k][v] || 0) + c;
      }
    }
    await page.close();
  }
  process.stderr.write(`measured ${r.path}\n`);
}
await browser.close();
process.stdout.write(JSON.stringify(out, null, 1));
