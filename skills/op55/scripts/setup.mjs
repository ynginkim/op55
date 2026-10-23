#!/usr/bin/env node
// op55 setup: download the SoundFont banks the sampled parts play from, once, into the cache directory.
//
//   node <skill>/scripts/setup.mjs              # default banks: gm (32 MB) + upright piano (56 MB)
//   node <skill>/scripts/setup.mjs grand        # add the Salamander concert grand (~300 MB download)
//   node <skill>/scripts/setup.mjs --all
//   node <skill>/scripts/setup.mjs --check      # report only, download nothing (exit 1 if a default bank is missing)
//
// Needs Node >= 18 (global fetch). The fallback sources are .7z/.tar.xz archives unpacked with the system `tar`
// (bsdtar on macOS reads both; on Linux install p7zip for .7z). Files are checked against their SHA-256.
import { createHash } from 'node:crypto';
import { createReadStream, createWriteStream, existsSync, mkdirSync, readdirSync, renameSync, rmSync, statSync } from 'node:fs';
import { join } from 'node:path';
import { pipeline } from 'node:stream/promises';
import { Readable } from 'node:stream';
import { createGunzip } from 'node:zlib';
import { execFileSync } from 'node:child_process';
import { BANKS, bankDir, bankPath } from './lib/banks.mjs';

const args = process.argv.slice(2);
const check = args.includes('--check');
const ids = args.includes('--all') ? Object.keys(BANKS) : args.filter(a => !a.startsWith('--'));
const want = ids.length ? ids : Object.keys(BANKS).filter(k => BANKS[k].default);
for (const id of want) if (!BANKS[id]) { console.error(`unknown bank "${id}" (have: ${Object.keys(BANKS).join(', ')})`); process.exit(2); }

const dir = bankDir();
mkdirSync(dir, { recursive: true });
const mb = n => (n / 1048576).toFixed(1) + ' MB';

async function sha256(path) {
  const h = createHash('sha256');
  await pipeline(createReadStream(path), h);
  return h.digest('hex');
}

async function download(url, to) {
  const res = await fetch(url, { redirect: 'follow' });
  if (!res.ok || !res.body) throw new Error(`HTTP ${res.status}`);
  const total = Number(res.headers.get('content-length')) || 0;
  let got = 0, last = 0;
  const body = Readable.fromWeb(res.body);
  body.on('data', c => {
    got += c.length;
    if (process.stderr.isTTY && Date.now() - last > 500) { last = Date.now(); process.stderr.write(`\r  ${mb(got)}${total ? ' / ' + mb(total) : ''}   `); }
  });
  await pipeline(body, createWriteStream(to));
  if (process.stderr.isTTY) process.stderr.write('\r' + ' '.repeat(40) + '\r');
}

function findFile(root, re) {
  for (const e of readdirSync(root, { withFileTypes: true })) {
    const p = join(root, e.name);
    if (e.isDirectory()) { const r = findFile(p, re); if (r) return r; }
    else if (re.test(e.name)) return p;
  }
  return null;
}

async function fetchBank(id) {
  const b = BANKS[id], dest = bankPath(id), tmp = join(dir, `.${id}.part`);
  for (const src of b.sources) {
    try {
      console.log(`  from ${src.url}`);
      rmSync(tmp, { recursive: true, force: true });
      if (src.unpack === 'none') {
        await download(src.url, tmp);
      } else if (src.unpack === 'gzip') {
        await download(src.url, tmp + '.gz');
        await pipeline(createReadStream(tmp + '.gz'), createGunzip(), createWriteStream(tmp));
        rmSync(tmp + '.gz', { force: true });
      } else if (src.unpack === 'tar') {
        const arc = tmp + '.' + src.url.split('.').pop(), x = tmp + '.d';
        await download(src.url, arc);
        mkdirSync(x, { recursive: true });
        execFileSync('tar', ['-xf', arc, '-C', x], { stdio: 'inherit' });
        const member = findFile(x, src.member);
        if (!member) throw new Error(`no file matching ${src.member} in the archive`);
        renameSync(member, tmp);
        rmSync(arc, { force: true }); rmSync(x, { recursive: true, force: true });
      }
      const h = await sha256(tmp);
      if (b.sha256 && h !== b.sha256) throw new Error(`SHA-256 mismatch (got ${h})`);
      renameSync(tmp, dest);
      console.log(`  ok ${dest} (${mb(statSync(dest).size)}, sha256 ${h})`);
      return true;
    } catch (err) {
      console.log(`  failed: ${err.message}`);
      rmSync(tmp, { recursive: true, force: true });
    }
  }
  return false;
}

let missing = 0;
console.log(`op55 banks -> ${dir}`);
for (const id of want) {
  const b = BANKS[id], p = bankPath(id);
  if (existsSync(p) && (!b.sha256 || statSync(p).size === b.bytes)) { console.log(`✓ ${id.padEnd(8)} ${b.title}`); continue; }
  if (check) { console.log(`✗ ${id.padEnd(8)} ${b.title} (not installed: node scripts/setup.mjs ${id})`); if (b.default) missing++; continue; }
  console.log(`↓ ${id.padEnd(8)} ${b.title}  [${b.license}]`);
  if (!(await fetchBank(id))) { console.log(`✗ ${id}: every source failed`); missing++; }
}
for (const id of want) if (BANKS[id].credit && existsSync(bankPath(id))) console.log(`note: using "${id}" requires a credit line: ${BANKS[id].credit}`);
process.exit(missing ? 1 : 0);
