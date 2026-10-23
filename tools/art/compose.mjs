#!/usr/bin/env node
// Compose the README graphics from the generated art (tools/art/gen.sh) and a render of the Eroica example.
//   node tools/art/compose.mjs
// Needs playwright-core and a local Chrome (set OP55_PLAYWRIGHT=/path/to/node_modules/playwright-core if it is not
// resolvable from here) and ffmpeg. Writes assets/banner.jpg, assets/social.jpg, assets/eroica-spectrogram.jpg.
import { execFileSync } from 'node:child_process';
import { createRequire } from 'node:module';
import { existsSync, mkdirSync, readFileSync, writeFileSync } from 'node:fs';
import { dirname, join, resolve } from 'node:path';
import { fileURLToPath, pathToFileURL } from 'node:url';

const ROOT = resolve(dirname(fileURLToPath(import.meta.url)), '../..');
const A = join(ROOT, 'assets'), TMP = join(ROOT, '.regress', 'art');
mkdirSync(TMP, { recursive: true });
const require = createRequire(import.meta.url);
const { chromium } = require(process.env.OP55_PLAYWRIGHT || 'playwright-core');
const url = p => pathToFileURL(p).href;

const FONTS = `<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Instrument+Serif:ital@0;1&family=JetBrains+Mono:wght@400;600&family=Homemade+Apple&display=swap" rel="stylesheet">`;
const BASE = `*{margin:0;padding:0;box-sizing:border-box} body{background:#0a0908;color:#efe6d6;font-family:'JetBrains Mono',monospace;-webkit-font-smoothing:antialiased}
.serif{font-family:'Instrument Serif',serif} .red{color:#ff3b1f}`;

// a 3/4 beat grid: one tall tick per bar, two short ones per beat
const ticks = (bars, w) => Array.from({ length: bars * 3 + 1 }, (_, i) => {
  const x = (i / (bars * 3)) * w, bar = i % 3 === 0;
  return `<div style="position:absolute;left:${x.toFixed(1)}px;bottom:0;width:${bar ? 2 : 1}px;height:${bar ? 16 : 7}px;background:#ff3b1f;opacity:${bar ? 0.95 : 0.55}"></div>`;
}).join('');

function banner(W, H, hero, artFrac = 0.64) {
  const art = W * artFrac;
  return `<!doctype html><html><head>${FONTS}<style>${BASE}
  .wrap{position:relative;width:${W}px;height:${H}px;overflow:hidden}
  .art{position:absolute;left:0;top:0;width:${art}px;height:${H}px;background:url('${hero}') ${-W * 0.02}px center/cover no-repeat}
  .fade{position:absolute;left:${art * 0.55}px;top:0;width:${art * 0.46}px;height:${H}px;background:linear-gradient(90deg,rgba(10,9,8,0),#0a0908)}
  .type{position:absolute;right:${W * 0.05}px;top:${H * 0.12}px;text-align:right}
  .mark{font-size:${H * 0.47}px;line-height:.82;font-style:italic;letter-spacing:-.02em}
  .ded{font-family:'Homemade Apple',cursive;font-size:${H * 0.036}px;margin-top:${H * 0.05}px;color:#cdbfa6}
  .ded s{text-decoration-color:#ff3b1f;text-decoration-thickness:3px}
  .meta{font-size:${H * 0.026}px;letter-spacing:.18em;text-transform:uppercase;margin-top:${H * 0.05}px;color:#a99d8a}
  .meta b{color:#efe6d6;font-weight:600}
  .tag{font-size:${H * 0.05}px;margin-top:${H * 0.04}px;font-family:'Instrument Serif',serif;color:#efe6d6}
  .grid{position:absolute;left:${W * 0.05}px;right:${W * 0.05}px;bottom:${H * 0.07}px;height:18px}
  .rule{position:absolute;left:0;right:0;bottom:0;height:1px;background:#ff3b1f;opacity:.7}
  </style></head><body><div class="wrap"><div class="art"></div><div class="fade"></div>
  <div class="type"><div class="mark serif">op<span class="red">55</span></div>
  <div class="ded">Sinfonia grande, intitolata <s>Bonaparte</s></div>
  <div class="meta">Symphony Nº 3 · E♭ · <b>Op. 55</b> · 1804 &nbsp;→&nbsp; <b>Opus 5.5</b> · 2026</div>
  <div class="tag">Background music, composed in code<br>by a model that cannot hear.</div></div>
  <div class="grid"><div class="rule"></div>${ticks(55, W * 0.9)}</div></div></body></html>`;
}

function specCard(W, spec, meta) {
  const PAD = 56, SW = W - 2 * PAD, SH = 330, dur = meta.duration, x = t => PAD + (t / dur) * SW;
  const secs = meta.sections.map((s, i) => {
    const low = i > 0 && x(s.t) - x(meta.sections[i - 1].t) < 140;   // stagger labels that would collide
    return `<div class="sec" style="left:${x(s.t)}px"><span style="top:${low ? 16 : -2}px">${String(i + 1).padStart(2, '0')} ${s.name}</span></div>`;
  }).join('');
  const acc = meta.accents.map(a => `<div class="acc" style="left:${x(a.t) - 5}px"></div>`).join('');
  const bars = Array.from({ length: 56 }, (_, k) => `<div class="bt${k % 5 ? '' : ' big'}" style="left:${x(meta.grid.t0 + k * meta.grid.beat * 3)}px">${k % 5 ? '' : `<i>${k}</i>`}</div>`).join('');
  return `<!doctype html><html><head>${FONTS}<style>${BASE}
  .wrap{position:relative;width:${W}px;height:${SH + 190}px;padding:0}
  h1{position:absolute;left:${PAD}px;top:30px;font-weight:400;font-size:44px;font-style:italic}
  .facts{position:absolute;right:${PAD}px;top:44px;font-size:14px;letter-spacing:.14em;text-transform:uppercase;color:#a99d8a}
  .facts b{color:#efe6d6;font-weight:600}
  .spec{position:absolute;left:${PAD}px;top:110px;width:${SW}px;height:${SH}px;background:url('${spec}') center/100% 100% no-repeat;border-radius:2px}
  .sec{position:absolute;top:96px;height:${SH + 14}px;border-left:1px solid rgba(239,230,214,.55)}
  .sec span{position:absolute;left:6px;top:-2px;font-size:12px;letter-spacing:.12em;text-transform:uppercase;white-space:nowrap;color:#efe6d6;background:rgba(10,9,8,.55);padding:1px 4px}
  .acc{position:absolute;top:${110 + SH + 6}px;width:0;height:0;border-left:5px solid transparent;border-right:5px solid transparent;border-bottom:9px solid #ff3b1f}
  .bt{position:absolute;top:${110 + SH + 20}px;width:1px;height:6px;background:#6f6656}
  .bt.big{height:12px;background:#a99d8a} .bt i{position:absolute;top:14px;left:-6px;font-size:11px;font-style:normal;color:#a99d8a}
  .cap{position:absolute;left:${PAD}px;top:${110 + SH + 58}px;font-size:12px;letter-spacing:.12em;text-transform:uppercase;color:#6f6656}
  </style></head><body><div class="wrap"><h1 class="serif">Op. 55 in 55 seconds</h1>
  <div class="facts">E♭ major · 3/4 · <b>dotted half = 60</b> (Beethoven, 1817) · <b>1 bar = 1 s</b> · −14.5 LUFS · LRA 9.2</div>
  <div class="spec"></div>${secs}${acc}${bars}
  <div class="cap">spectrogram of the render · ▲ accents land within 3.4 ms of the grid · bar numbers below</div></div></body></html>`;
}

async function shot(browser, html, out, W, H) {
  const page = await browser.newPage({ viewport: { width: W, height: H }, deviceScaleFactor: 1 });
  const f = join(TMP, out.replace(/\W+/g, '_') + '.html');
  writeFileSync(f, html);
  await page.goto(url(f), { waitUntil: 'networkidle' });
  await page.evaluate(() => document.fonts.ready);
  await page.screenshot({ path: join(A, out), clip: { x: 0, y: 0, width: W, height: H }, type: 'jpeg', quality: 88 });
  await page.close();
  console.log('wrote', join(A, out));
}

const hero = join(A, 'art', 'hero.jpg');
const eroicaWav = join(ROOT, '.regress', 'eroica.wav'), eroicaMeta = join(ROOT, '.regress', 'eroica.meta.json');
if (!existsSync(eroicaWav)) throw new Error('render the example first: tools/regress.sh');
const spec = join(TMP, 'eroica_spec.png');
execFileSync('ffmpeg', ['-v', 'error', '-y', '-i', eroicaWav, '-lavfi',
  'showspectrumpic=s=1600x360:legend=0:fscale=log:start=40:stop=14000:color=magma:drange=72:scale=log', spec]);
const meta = JSON.parse(readFileSync(eroicaMeta, 'utf8'));

const browser = await chromium.launch({ channel: process.env.OP55_CHROME_CHANNEL || 'chrome', headless: true });
await shot(browser, banner(1600, 640, url(hero)), 'banner.jpg', 1600, 640);
await shot(browser, banner(1280, 640, url(hero), 0.52), 'social.jpg', 1280, 640);
await shot(browser, specCard(1600, url(spec), meta), 'eroica-spectrogram.jpg', 1600, 520);
await browser.close();
