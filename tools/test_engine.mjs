import { test } from 'node:test';
import assert from 'node:assert/strict';
import { spawnSync } from 'node:child_process';
import { mkdtempSync, writeFileSync, existsSync, rmSync, statSync } from 'node:fs';
import { tmpdir } from 'node:os';
import { dirname, join, resolve } from 'node:path';
import { fileURLToPath } from 'node:url';

const root = resolve(dirname(fileURLToPath(import.meta.url)), '..');
const render = join(root, 'skills/resolve-op55-tools/scripts/render.mjs');

function fixture({ duration = 2.5, levels, composeLevels } = {}) {
  const exported = levels ? `export const levels = ${JSON.stringify(levels)};\n` : '';
  const returned = composeLevels ? `levels: ${JSON.stringify(composeLevels)},` : '';
  return `export const grid = { bpm: 60, t0: 0.5, beatsPerBar: 1, firstDownbeat: 0 };
export const duration = ${duration};
export const seed = 'levels-duration';
export const space = {
  plate: { len: 0.03, rtLow: 0.03, rtMid: 0.03, rtHigh: 0.02, early: [], gain: 0.2 },
  hall: { len: 0.03, rtLow: 0.03, rtMid: 0.03, rtHigh: 0.02, early: [], gain: 0.2 },
  delay: { sixteenths: 1, fb: 0, lp: 2000, wet: 0 },
};
${exported}export function compose() {
  return {
    events: { pad: [{ t0: 0, t1: ${duration}, notes: [57], att: 0.005, rel: 0.01, kind: 'soft', gain: 0.5 }] },
    ${returned}
  };
}
`;
}

function renderScore(source) {
  const dir = mkdtempSync(join(tmpdir(), 'op55-engine-'));
  const score = join(dir, 'score.mjs');
  const wav = join(dir, 'music.wav');
  const meta = join(dir, 'music.meta.json');
  const analysis = join(dir, 'analysis.json');
  writeFileSync(score, source);
  try {
    const proc = spawnSync(process.execPath, [render, '--score', score, '--out', wav], {
      encoding: 'utf8',
      timeout: 120000,
    });
    const output = `${proc.stdout || ''}${proc.stderr || ''}`;
    return {
      status: proc.status,
      output,
      wavExists: existsSync(wav),
      wavBytes: existsSync(wav) ? statSync(wav).size : 0,
      metaExists: existsSync(meta),
      analysisExists: existsSync(analysis),
    };
  } finally {
    rmSync(dir, { recursive: true, force: true });
  }
}

function assertRejected(result, expected) {
  const problems = [];
  if (result.status === 0) problems.push('exit 0');
  if (result.wavExists) problems.push('wrote wav');
  if (result.metaExists) problems.push('wrote meta');
  if (result.analysisExists) problems.push('wrote analysis');
  if (!result.output.includes(expected)) problems.push(`missing ${JSON.stringify(expected)}`);
  assert.deepEqual(problems, [], `${problems.join(', ')}\n${result.output}`);
}

function assertRendered(result) {
  assert.equal(result.status, 0, result.output);
  assert.equal(result.wavExists, true, result.output);
  assert.ok(result.wavBytes > 44, result.output);
  const match = result.output.match(/wrote .* I (-?\d+\.\d+) LUFS/);
  assert.ok(match, result.output);
  const lufs = Number(match[1]);
  assert.ok(Math.abs(lufs + 13) < 0.05, `LUFS ${lufs}\n${result.output}`);
}

test('levels.end past duration rejects the render and writes nothing', () => {
  const result = renderScore(fixture({ levels: { points: [[0, -6]], end: 3 } }));
  assertRejected(result, 'levels.end bar 3 (3.5 s) is past duration 2.5 s');
});

test('an intermediate levels.points bar past duration rejects the render and writes nothing', () => {
  const result = renderScore(fixture({ levels: { points: [[0, -6], [3, 0], [1, -1]], end: 2 } }));
  assertRejected(result, 'levels.points bar 3 (3.5 s) is past duration 2.5 s');
});

test('the only levels.points bar past duration rejects the render and writes nothing', () => {
  const result = renderScore(fixture({ levels: { points: [[4, -2]] } }));
  assertRejected(result, 'levels.points bar 4 (4.5 s) is past duration 2.5 s');
});

test('levels.end exactly at duration renders finite loudness near the target', () => {
  const result = renderScore(fixture({ levels: { points: [[0, -6]], end: 2 } }));
  assertRendered(result);
});

test('levels returned by compose with no end renders finite loudness near the target', () => {
  const result = renderScore(fixture({ composeLevels: { points: [[0, -5], [1, -2]] } }));
  assertRendered(result);
});

test('levels.end returned by compose past duration rejects the render and writes nothing', () => {
  const result = renderScore(fixture({ composeLevels: { points: [[0, -6]], end: 3 } }));
  assertRejected(result, 'levels.end bar 3 (3.5 s) is past duration 2.5 s');
});
