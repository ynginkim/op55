#!/usr/bin/env node
// op55 banks: what is installed, and which presets a bank offers (to pick `preset` / `kit` for an ensemble part).
//
//   node <skill>/scripts/banks.mjs                 # installed banks
//   node <skill>/scripts/banks.mjs gm              # every preset in a bank: bankMSB:program  name
//   node <skill>/scripts/banks.mjs gm string       # presets whose name contains "string"
//   node <skill>/scripts/banks.mjs gm --drums      # drum kits (use the number as `kit`)
import { existsSync } from 'node:fs';
import { BANKS, bankDir, bankPath } from './lib/banks.mjs';
import { listPresets } from './lib/sampler.mjs';

const args = process.argv.slice(2), drums = args.includes('--drums');
const [id, q] = args.filter(a => !a.startsWith('--'));
if (!id) {
  console.log(`banks in ${bankDir()}`);
  for (const [k, b] of Object.entries(BANKS)) {
    console.log(`${existsSync(bankPath(k)) ? '✓' : '·'} ${k.padEnd(8)} ${b.title}\n           ${b.what}\n           license: ${b.license}${b.credit ? `  credit: "${b.credit}"` : ''}`);
  }
  console.log('\ninstall: node scripts/setup.mjs [gm upright grand | --all]');
  process.exit(0);
}
const seen = new Set();
const rows = listPresets(id).filter(p => p.drums === drums && (!q || p.name.toLowerCase().includes(q.toLowerCase())))
  .filter(p => !drums || (!seen.has(p.program) && seen.add(p.program)));   // GS and XG list each kit twice
for (const p of rows) console.log(`${drums ? `kit ${String(p.program).padStart(3)}` : `${String(p.bankMSB).padStart(3)}:${String(p.program).padStart(3)}`}  ${p.name}`);
if (!rows.length) console.log('no match');
