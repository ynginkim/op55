// lib/sampler.mjs: sampled instruments. A score declares parts in `export const ensemble = { name: part }`; each part is one
// SoundFont preset (or drum kit) and is played by spessasynth_core, offline, with its built-in effects off. The dry stereo
// goes into the same Mixer as the synth voices, so reverb, delay, levels, mastering and the beat grid stay shared.
//
// part   { bank: 'gm'|'upright'|'grand', preset: 48 | 'Pizzicato' | { program, bankMSB, bankLSB }, drums?: bool, kit?: 0,
//          pan?: -1..1, gain?: 1, sends?: { plate, hall, delay }, transpose?: 0, bendRange?: 2, lead?: 0 }
//          lead = seconds to play the whole part early (a DAW's negative track delay) when its samples swell in slowly
// events (in compose's `events[name]`, any order):
//   note { t, dur, midi, vel = 0.8 }               vel 0..1 -> MIDI 1..127; drums: midi = GM drum key (36 kick, 38 snare, 42 hat...)
//   cc   { t, cc: 'expression'|'mod'|'sustain'|'volume'|'pan'|'brightness'|<0..127>, value: 0..1 }
//   bend { t, bend: -1..1 }                         in units of bendRange semitones
// Timing is sample-exact: rendering stops at every event's sample and the event is applied before the next sample.
import { readFileSync } from 'node:fs';
import { SpessaSynthProcessor, SoundBankLoader, InterpolationTypes } from '../vendor/spessasynth_core.mjs';
import { SR } from './dsp.mjs';
import { BANKS, requireBank } from './banks.mjs';

const CC = { volume: 7, pan: 10, expression: 11, mod: 1, modulation: 1, sustain: 64, pedal: 64, brightness: 74, cutoff: 74, resonance: 71, attack: 73, release: 72 };
const DRUM_CH = 9, MEL_CH = 0, BLOCK = 128, CHUNK = SR;
const bankCache = new Map();

export function loadBank(id) {
  if (!bankCache.has(id)) bankCache.set(id, SoundBankLoader.fromArrayBuffer(readFileSync(requireBank(id)).buffer));
  return bankCache.get(id);
}

export function listPresets(id) {
  return loadBank(id).presets
    .map(p => ({ program: p.program, bankMSB: p.bankMSB, bankLSB: p.bankLSB, drums: p.isDrum, name: p.name.trim() }))
    .sort((a, b) => (a.drums - b.drums) || (a.program - b.program) || (a.bankMSB - b.bankMSB) || (a.bankLSB - b.bankLSB));
}

// number -> GM program (bank 0); object -> as given; string -> exact name, else the first name containing it (case-insensitive)
export function resolvePreset(id, spec, drums = false) {
  if (spec == null) return { program: 0, bankMSB: 0, bankLSB: 0 };
  if (typeof spec === 'number') return { program: spec, bankMSB: 0, bankLSB: 0 };
  if (typeof spec === 'object') return { program: spec.program ?? 0, bankMSB: spec.bankMSB ?? 0, bankLSB: spec.bankLSB ?? 0 };
  const all = listPresets(id).filter(p => p.drums === drums), q = String(spec).toLowerCase();
  const hit = all.find(p => p.name.toLowerCase() === q) || all.find(p => p.name.toLowerCase().includes(q));
  if (!hit) throw new Error(`bank ${id}: no ${drums ? 'drum kit' : 'preset'} matching "${spec}" (try: node scripts/banks.mjs ${id})`);
  return hit;
}

const v7 = x => Math.max(0, Math.min(127, Math.round(x * 127)));

// Render one part into the mixer under stem `name`. `gain` already includes the score's mix multiplier.
export function renderPart(mx, name, part, events, gain) {
  const bankId = part.bank || 'gm';
  if (!BANKS[bankId]) throw new Error(`ensemble.${name}: unknown bank "${bankId}"`);
  const drums = !!part.drums, ch = drums ? DRUM_CH : MEL_CH;
  const synth = new SpessaSynthProcessor(SR, { effectsEnabled: false, eventsEnabled: false, maxBufferSize: BLOCK });
  synth.soundBankManager.addSoundBank(loadBank(bankId), 'main');
  synth.setSystemParameter('autoAllocateVoices', true);
  synth.setSystemParameter('interpolationType', InterpolationTypes.hermite);

  const ops = [];   // [sample, order, fn]; order keeps note-offs before note-ons on the same sample
  const lead = part.lead || 0;
  const at = (t, order, fn) => ops.push([Math.max(0, Math.round((t - lead) * SR)), order, ops.length, fn]);
  at(0, 0, () => {
    if (drums) synth.programChange(ch, part.kit ?? 0);
    else {
      const p = resolvePreset(bankId, part.preset, false);
      synth.controllerChange(ch, 0, p.bankMSB); synth.controllerChange(ch, 32, p.bankLSB); synth.programChange(ch, p.program);
    }
    const br = part.bendRange ?? 2;    // RPN 0: pitch-bend sensitivity
    synth.controllerChange(ch, 101, 0); synth.controllerChange(ch, 100, 0); synth.controllerChange(ch, 6, br); synth.controllerChange(ch, 38, 0);
    synth.controllerChange(ch, 101, 127); synth.controllerChange(ch, 100, 127);
  });
  const tr = part.transpose || 0, dur0 = drums ? 0.25 : null;
  // a MIDI note-off releases every voice of that pitch, so a held note must end where the same pitch is struck again
  // (otherwise its late note-off would cut the new one): clip each note to the next onset of its pitch.
  const nextOn = new Map(), until = new Map();
  [...events].filter(e => e.cc == null && e.bend == null).sort((a, b) => b.t - a.t).forEach(e => {
    const m = e.midi + tr;
    if (nextOn.has(m)) until.set(e, nextOn.get(m));
    nextOn.set(m, e.t);
  });
  for (const e of events) {
    if (e.cc != null) {
      const n = typeof e.cc === 'number' ? e.cc : CC[e.cc];
      if (n == null) throw new Error(`ensemble.${name}: unknown cc "${e.cc}"`);
      at(e.t, 1, () => synth.controllerChange(ch, n, v7(e.value)));
    } else if (e.bend != null) {
      at(e.t, 1, () => synth.pitchWheel(ch, Math.max(0, Math.min(16383, Math.round(8192 + e.bend * 8191)))));
    } else {
      if (e.midi == null || e.t == null) throw new Error(`ensemble.${name}: a note needs t and midi`);
      const m = e.midi + tr, vel = Math.max(1, v7(e.vel ?? 0.8)), d = e.dur ?? dur0;
      if (d == null) throw new Error(`ensemble.${name}: a note needs dur`);
      at(e.t, 2, () => synth.noteOn(ch, m, vel));
      at(until.has(e) ? Math.min(e.t + d, until.get(e)) : e.t + d, 0, () => synth.noteOff(ch, m));
    }
  }
  ops.sort((a, b) => a[0] - b[0] || a[1] - b[1] || a[2] - b[2]);

  const N = mx.N, cl = new Float32Array(CHUNK), cr = new Float32Array(CHUNK);
  const sends = part.sends || { plate: 0.04, hall: 0.22 }, pan = part.pan || 0;
  let pos = 0, k = 0;
  while (pos < N) {
    const len = Math.min(CHUNK, N - pos);
    cl.fill(0); cr.fill(0);
    let off = 0;
    while (off < len) {
      while (k < ops.length && ops[k][0] <= pos + off) ops[k++][3]();
      const next = k < ops.length ? ops[k][0] - pos : len;
      const n = Math.min(BLOCK, len - off, Math.max(1, next - off));
      synth.process(cl, cr, off, n);
      off += n;
    }
    mx.put(name, pos, len === CHUNK ? cl : cl.subarray(0, len), len === CHUNK ? cr : cr.subarray(0, len), gain, pan, sends);
    pos += len;
  }
  return { bank: bankId, notes: events.filter(e => e.cc == null && e.bend == null).length };
}

export function creditsFor(ensemble) {
  const ids = [...new Set(Object.values(ensemble || {}).map(p => p.bank || 'gm'))];
  return ids.map(id => ({ bank: id, title: BANKS[id].title, license: BANKS[id].license, credit: BANKS[id].credit }));
}
