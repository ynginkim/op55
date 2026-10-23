// lib/banks.mjs: the SoundFont banks op55 knows about, where they live on disk, and how to fetch them.
// Banks are never committed to the repo. `node scripts/setup.mjs` downloads them once into the cache directory
// ($OP55_BANKS, else $XDG_CACHE_HOME/op55/banks, else ~/.cache/op55/banks) and checks every file's SHA-256.
import { existsSync } from 'node:fs';
import { homedir } from 'node:os';
import { join } from 'node:path';

// Primary source: a copy in this repo's GitHub release (gzip, so Node can unpack it without system tools; GeneralUser's
// author asks redistributors to serve their own copy). Fallback: the author's original archive, unpacked with `tar`.
const RELEASE = 'https://github.com/ynginkim/op55/releases/download/banks-v1';

export const BANKS = {
  gm: {
    title: 'GeneralUser GS 2.0.3',
    what: 'Full General MIDI + GS set (128 programs, variation banks, 13 drum kits). The default orchestra.',
    file: 'GeneralUser-GS-2.0.3.sf2', bytes: 32319396,
    sha256: '9575028c7a1f589f5770fccc8cff2734566af40cd26ed836944e9a5152688cfe',
    license: 'GeneralUser GS License v2.0: free for private and commercial music.',
    credit: null,
    sources: [
      { url: `${RELEASE}/GeneralUser-GS-2.0.3.sf2.gz`, unpack: 'gzip' },
      { url: 'https://raw.githubusercontent.com/mrbumpy409/GeneralUser-GS/97049183643d5fc5a9322a69c5b09efb667c6c3a/GeneralUser-GS.sf2', unpack: 'none' },
    ],
    default: true,
  },
  upright: {
    title: 'Upright Piano KW (FreePats, 2022-02-21)',
    what: 'Kawai upright recorded in a living room. Stereo, 2 velocity layers. Warm, close, a little lo-fi.',
    file: 'UprightPianoKW-20220221.sf2', bytes: 57377848,
    sha256: 'd9f5157720963671906727ca2e12b3293fd822c831bb0de477dd1c5f3ad37108',
    license: 'CC0 1.0 (public domain).',
    credit: null,
    sources: [
      { url: `${RELEASE}/UprightPianoKW-20220221.sf2.gz`, unpack: 'gzip' },
      { url: 'https://freepats.zenvoid.org/Piano/UprightPianoKW/UprightPianoKW-SF2-20220221.7z', unpack: 'tar', member: /\.sf2$/i },
    ],
    default: true,
  },
  grand: {
    title: 'Salamander Grand Piano V3 (2020-06-02)',
    what: 'Yamaha C5, 16 velocity layers, 48 kHz 24-bit. The best free concert grand. Big: ~300 MB download, 1.2 GB on disk, ~1.8 GB RAM while rendering.',
    file: 'SalamanderGrandPiano-V3-20200602.sf2', bytes: 1266462334,
    sha256: '712d0e681efbe5203a8014e9b3e84168f1908c82f2f6fb13bd2c77d6d72c70b7',
    license: 'CC BY 3.0: credit required.',
    credit: 'Salamander Grand Piano by Alexander Holm (CC BY 3.0)',
    sources: [
      { url: `${RELEASE}/SalamanderGrandPiano-V3-20200602.sf2.gz`, unpack: 'gzip' },
      { url: 'https://freepats.zenvoid.org/Piano/SalamanderGrandPiano/SalamanderGrandPiano-SF2-V3%2B20200602.tar.xz', unpack: 'tar', member: /\.sf2$/i },
    ],
    default: false,
  },
};

export function bankDir() {
  if (process.env.OP55_BANKS) return process.env.OP55_BANKS;
  return join(process.env.XDG_CACHE_HOME || join(homedir(), '.cache'), 'op55', 'banks');
}

export function bankPath(id) {
  const b = BANKS[id];
  if (!b) throw new Error(`unknown bank "${id}" (have: ${Object.keys(BANKS).join(', ')})`);
  return join(bankDir(), b.file);
}

export function requireBank(id) {
  const p = bankPath(id);
  if (!existsSync(p)) throw new Error(`bank "${id}" is not installed. Run: node <skill>/scripts/setup.mjs ${id}`);
  return p;
}
