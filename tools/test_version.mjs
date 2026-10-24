import { test } from 'node:test';
import assert from 'node:assert/strict';
import { spawnSync } from 'node:child_process';
import { readFileSync } from 'node:fs';
import { dirname, join, resolve } from 'node:path';
import { fileURLToPath } from 'node:url';

const root = resolve(dirname(fileURLToPath(import.meta.url)), '..');

// VERSION is the repository version source; the installed skill carries the same number in metadata.version.
test('VERSION, metadata.version and render.mjs --version agree', () => {
  const version = readFileSync(join(root, 'VERSION'), 'utf8').trim();
  const front = readFileSync(join(root, 'skills/resolve-op55-tools/SKILL.md'), 'utf8').match(/^---\n([\s\S]*?)\n---/)[1];
  assert.equal(front.match(/^metadata:\n {2}version: "([^"]+)"$/m)?.[1], version);
  const run = spawnSync(process.execPath, [join(root, 'skills/resolve-op55-tools/scripts/render.mjs'), '--version'], { encoding: 'utf8' });
  assert.equal(run.status, 0);
  assert.equal(run.stdout.trim(), `op55 ${version}`);
});
