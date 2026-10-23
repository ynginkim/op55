// eroica.score.mjs: "Op. 55 in 55 seconds". A hybrid orchestral cue built on the opening idea of Beethoven's Symphony No. 3
// in E-flat, Op. 55 "Eroica" (1804, public domain): two hammer-blow chords, then a cello theme that is nothing but the E-flat
// triad, which slips to a C-sharp. Taken at Beethoven's own 1817 metronome mark (dotted half = 60), one bar of 3/4 lasts
// exactly one second, so the 55 bars below last 55 seconds and bar k starts at t0 + k.
//
//   node scripts/setup.mjs                               # once: gm + upright banks
//   node scripts/render.mjs --score scripts/examples/eroica.score.mjs --out /path/eroica.wav
//
// Shows: sampled orchestra parts (strings, celli, basses, horns, brass, timpani, flute, upright piano) on the shared grid,
// expression swells with ccRamp, sustain pedal, a hemiola against the bar line, and synth layers (sub, kick, boom, riser,
// shimmer) mixed underneath the orchestra.

export const title = 'Op. 55 in 55 seconds';
export const seed = 'eroica-v1';
export const key = 'E-flat major';
export const grid = { bpm: 180, t0: 0.5, beatsPerBar: 3, firstDownbeat: 0 };   // bar k = 0.5 + k seconds
export const duration = 57.0;

export const sections = [
  { bar: 0, name: 'Hammer', energy: 0.9 },
  { bar: 2, name: 'Theme', energy: 0.4 },
  { bar: 14, name: 'Rise', energy: 0.65 },
  { bar: 22, name: 'Hemiola', energy: 0.85 },
  { bar: 30, name: 'Breath', energy: 0.3 },
  { bar: 38, name: 'Finale', energy: 1.0 },
  { bar: 50, name: 'Coda', energy: 0.8 },
];
export const accents = [
  { bar: 0, name: 'Hammer 1', strength: 0.8 },
  { bar: 1, name: 'Hammer 2', strength: 0.8 },
  { bar: 22, name: 'Hemiola', strength: 0.7 },
  { bar: 38, name: 'Finale', strength: 1 },
  { bar: 50, name: 'Coda hammer 1', strength: 0.8 },
  { bar: 51, name: 'Coda hammer 2', strength: 0.8 },
];
export const levels = { points: [[0, -1], [2, -9], [14, -5], [22, -2.5], [30, -10], [38, 0], [50, -2], [52, -3.5]], end: 55 };
export const master = { lufs: -14.5, fadeOut: [55.3, 56.9] };   // a dynamic orchestral cue keeps its transients a little below the -13 default
export const space = { hall: { len: 4.2, rtLow: 3.2, rtMid: 2.7, rtHigh: 1.5 } };   // a larger room for an orchestra

export const ensemble = {
  violins: { bank: 'gm', preset: 'Fast Strings', pan: -0.35, sends: { hall: 0.34, plate: 0.03 } },
  violas: { bank: 'gm', preset: 'Fast Strings', pan: 0.1, sends: { hall: 0.3 } },
  tremolo: { bank: 'gm', preset: 'Tremolo Strings', pan: -0.2, sends: { hall: 0.34 } },
  celli: { bank: 'gm', preset: 'Cello', pan: 0.3, sends: { hall: 0.3 } },
  basses: { bank: 'gm', preset: 'Double Bass', pan: 0.4, sends: { hall: 0.25 } },
  horns: { bank: 'gm', preset: 'French Horns', pan: -0.05, sends: { hall: 0.42 } },
  brass: { bank: 'gm', preset: 'Brass Section', pan: 0.15, sends: { hall: 0.32 } },
  timp: { bank: 'gm', preset: 'Timpani', pan: 0.05, sends: { hall: 0.28 } },
  flute: { bank: 'gm', preset: 'Flute', pan: -0.2, sends: { hall: 0.36 } },
  keys: { bank: 'upright', preset: 0, pan: 0, sends: { hall: 0.24, plate: 0.05 } },
};
export const mix = { violins: 1.0, violas: 0.8, tremolo: 0.7, celli: 1.25, basses: 0.9, horns: 1.0, brass: 0.8, timp: 1.1, flute: 0.8, keys: 1.1 };

// chords: [bass MIDI, upper voices]
const C = {
  Eb: [39, [55, 58, 63]], EbG: [43, [55, 58, 63]], Cm: [36, [55, 60, 63]], Ab: [44, [56, 60, 63]],
  Fm: [41, [56, 60, 65]], Fm7: [41, [56, 60, 63, 65]], Bb: [46, [58, 62, 65]], Bb7: [46, [56, 58, 62, 65]],
  Bb7D: [38, [56, 58, 62, 65]], Bbsus: [46, [58, 63, 65]],
};
// one chord per bar
const HARM = [
  'Eb', 'Eb',                                                         // 0-1 hammer
  'Eb', 'Eb', 'Eb', 'Eb', 'Eb', 'Bb7', 'Eb', 'Eb', 'Eb', 'Eb', 'Ab', 'Bb7',   // 2-13 theme (bar 6 holds Eb under the C#)
  'Eb', 'Cm', 'Ab', 'Bb', 'EbG', 'Ab', 'Fm7', 'Bb7',                 // 14-21 rise
  'Cm', 'Cm', 'Ab', 'Ab', 'Fm', 'Fm', 'Bb7D', 'Bb7',                 // 22-29 hemiola
  'Ab', 'Fm', 'EbG', 'Bbsus', 'Ab', 'Fm7', 'Bbsus', 'Bb7',           // 30-37 breath
  'Eb', 'Eb', 'Ab', 'Ab', 'Cm', 'Ab', 'Bb', 'Bb', 'Eb', 'Ab', 'Bb7', 'Bb7',   // 38-49 finale
  'Eb', 'Eb', 'Eb', 'Eb', 'Eb',                                       // 50-54 coda
];
// the theme as [beat offset in bar, length in beats, MIDI] per bar; transpose for other voices
const THEME = [
  [[0, 2, 51], [2, 1, 55]],            // Eb . G
  [[0, 2, 51], [2, 1, 46]],            // Eb . Bb
  [[0, 1, 51], [1, 1, 55], [2, 1, 58]],  // Eb G Bb
  [[0, 3, 63]],                        // Eb (octave)
];

export function compose({ bar, BEAT, makeRng, ccRamp }) {
  const E = { violins: [], violas: [], tremolo: [], celli: [], basses: [], horns: [], brass: [], timp: [], flute: [], keys: [],
    pad: [], bass: [], kick: [], tick: [], fx: [], bell: [] };
  const hum = makeRng('humanize');
  const H = k => C[HARM[k]];
  const LEAD = 0.005;   // sampled ff chords reach half their level ~5 ms after note-on: strike sync points that much early
  const n = (part, k, b, beats, midi, vel, { exact = false, legato = 0 } = {}) =>
    E[part].push({ t: bar(k, b) + (exact ? -LEAD : hum.range(-0.006, 0.006)), dur: beats * BEAT - 0.03 + legato, midi, vel: Math.min(1, vel + (exact ? 0 : hum.range(-0.04, 0.04))) });
  const theme = (part, k0, shift, vel, opts) => THEME.forEach((row, i) => row.forEach(([b, len, m]) => n(part, k0 + i, b, len, m + shift, vel, opts)));

  // ---- hammer chords: bars 0, 1 and again 50, 51 (exact timing: these are the cue's sync points) ----
  const hammer = k => {
    const o = { exact: true };
    for (const m of [63, 67, 70, 75]) n('violins', k, 0, 0.9, m, 0.92, o);
    for (const m of [51, 55, 58, 63]) n('brass', k, 0, 0.9, m, 0.85, o);
    for (const m of [51, 58, 63]) n('horns', k, 0, 0.9, m, 0.95, o);
    n('celli', k, 0, 0.9, 39, 1.0, o); n('celli', k, 0, 0.9, 51, 1.0, o); n('basses', k, 0, 0.9, 27, 1.0, o);
    n('timp', k, 0, 0.6, 39, 0.72, o); n('timp', k, 0, 0.6, 46, 0.5, o);
    E.fx.push({ type: 'boom', t: bar(k) + 0.004, midi: 27, dec: 0.7, gain: 0.18 });   // peaky layers stay small: the limiter
    E.kick.push({ t: bar(k), vel: 0.35 });                                              // would flatten the hammer otherwise
  };
  hammer(0); hammer(1); hammer(50); hammer(51);

  // ---- 2-13 theme: celli carry it; violas/violins pulse in eighths underneath; the C# moment empties the stage ----
  theme('celli', 2, 0, 0.62);
  n('celli', 6, 0, 1, 62, 0.62); n('celli', 6, 1, 2, 61, 0.7);        // D, then the C#
  n('celli', 7, 0, 3, 62, 0.6);                                       // ...resolving to D over Bb7
  theme('celli', 8, 0, 0.66); theme('violins', 8, 12, 0.42);           // second time: violins double an octave up
  n('celli', 12, 0, 3, 56, 0.66); n('celli', 13, 0, 3, 58, 0.7);       // Ab, Bb: cadence into the rise
  n('violins', 12, 0, 3, 72, 0.45); n('violins', 13, 0, 3, 74, 0.5);
  for (let k = 2; k < 14; k++) {
    if (k === 6) continue;                                            // hush under the C#
    const [b, up] = H(k);
    for (let e = 0; e < 6; e++) n('violas', k, e / 2, 0.42, up[e % up.length] + (k < 8 ? 0 : 12), e % 2 ? 0.26 : 0.34);
    n('basses', k, 0, 2.6, b - 12, 0.6);
    E.bass.push({ t: bar(k), dur: 2.6 * BEAT, midi: b - 12, vel: 0.55, style: 'sub', gain: 0.55 });
  }
  n('basses', 6, 0, 3, 27, 0.5);                                      // only a low Eb holds under the C#

  // ---- 14-21 rise: violins take the theme an octave up, horns and celli sustain, timpani mark the phrase ----
  theme('violins', 14, 12, 0.6);
  [[18, [[0, 2, 67], [2, 1, 70]]], [19, [[0, 2, 68], [2, 1, 72]]], [20, [[0, 1, 68], [1, 1, 65], [2, 1, 68]]], [21, [[0, 3, 70]]]]
    .forEach(([k, row]) => row.forEach(([b, len, m]) => n('violins', k, b, len, m, 0.66)));
  for (let k = 14; k < 22; k++) {
    const [b, up] = H(k);
    up.slice(0, 3).forEach(m => n('horns', k, 0, 3, m, 0.55, { legato: 0.04 }));
    n('celli', k, 0, 3, b, 0.6, { legato: 0.04 }); n('basses', k, 0, 3, b - 12, 0.6, { legato: 0.04 });
    E.bass.push({ t: bar(k), dur: 2.9 * BEAT, midi: b - 12, vel: 0.6, style: 'sub', gain: 0.6 });
    if (k === 14 || k === 18) n('timp', k, 0, 1, b < 42 ? b : b - 12, 0.7, { exact: true });
  }
  for (let i = 0; i < 12; i++) n('timp', 21, i / 4, 0.25, 46, 0.35 + 0.05 * i, { exact: true });   // roll into the hemiola
  E.violins.push(...ccRamp('expression', bar(14), bar(21, 2), 0.55, 1));
  E.horns.push(...ccRamp('expression', bar(14), bar(21, 2), 0.5, 1));

  // ---- 22-29 hemiola: tutti stabs every two beats, so the accents cross the 3/4 bar line (Beethoven's own trick) ----
  for (let beat = 0; beat < 24; beat += 2) {
    const k = 22 + Math.floor(beat / 3), b = beat % 3, [bs, up] = H(k), v = beat % 6 === 0 ? 1.0 : 0.85;
    for (const m of up) { n('brass', k, b, 0.8, m, v, { exact: true }); n('violins', k, b, 0.7, m + 12, v, { exact: true }); }
    n('basses', k, b, 0.8, bs - 12, v, { exact: true });
    E.kick.push({ t: bar(k, b), vel: v * 0.5 });
    if (beat % 6 === 0) n('timp', k, b, 0.6, bs < 42 ? bs : bs - 12, 0.7, { exact: true });
  }
  for (let k = 22; k < 30; k++) {
    const [bs] = H(k);
    for (let e = 0; e < 6; e++) n('celli', k, e / 2, 0.4, bs + (e % 2 ? 12 : 0), 0.55 + (e === 0 ? 0.15 : 0));   // driving eighths
    E.bass.push({ t: bar(k), dur: 2.8 * BEAT, midi: bs - 12, vel: 0.65, style: 'round', gain: 0.5 });
  }

  // ---- 30-37 breath: upright piano alone with a string bed; the flute remembers the theme; a riser pulls us back ----
  E.keys.push({ t: bar(30), cc: 'expression', value: 0.9 });
  for (let k = 30; k < 38; k++) {
    const [bs, up] = H(k), arp = [bs + 12, up[0] + 12, up[1] + 12, up[2] + 12, up[1] + 12, up[0] + 12];
    E.keys.push({ t: bar(k) - 0.02, cc: 'sustain', value: 0 }, { t: bar(k) + 0.01, cc: 'sustain', value: 1 });   // re-pedal each bar
    arp.forEach((m, e) => n('keys', k, e / 2, 0.5, m, e === 0 ? 0.5 : 0.36));
    up.forEach(m => n('violins', k, 0, 3, m, 0.32, { legato: 0.05 }));
    n('basses', k, 0, 3, bs - 12, 0.4, { legato: 0.05 });
  }
  E.keys.push({ t: bar(38) - 0.05, cc: 'sustain', value: 0 });
  E.violins.push({ t: bar(30), cc: 'expression', value: 0.45 }, ...ccRamp('expression', bar(36), bar(38), 0.45, 0.9));
  [[32, 0, 2, 75], [32, 2, 1, 79], [33, 0, 2, 75], [33, 2, 1, 70], [34, 0, 1, 75], [34, 1, 1, 79], [34, 2, 1, 82], [35, 0, 3, 87]]
    .forEach(([k, b, len, m]) => n('flute', k, b, len, m - 12, 0.5));
  for (let i = 0; i < 12; i++) n('timp', 37, i / 4, 0.25, 46, 0.25 + 0.06 * i, { exact: true });
  E.fx.push({ type: 'riser', t: bar(36), t1: bar(38), f0: 300, f1: 7000, q: 1.3, gain: 0.07 });

  // ---- 38-49 finale: the horns get the theme (as in the symphony), tremolo strings and a kick drive it home ----
  theme('horns', 38, 12, 0.85); theme('celli', 38, 0, 0.8);
  [[42, [[0, 2, 72], [2, 1, 75]]], [43, [[0, 2, 68], [2, 1, 72]]], [44, [[0, 1, 70], [1, 1, 74], [2, 1, 77]]], [45, [[0, 3, 70]]],
    [46, [[0, 2, 67], [2, 1, 70]]], [47, [[0, 2, 68], [2, 1, 72]]], [48, [[0, 1, 74], [1, 1, 72], [2, 1, 70]]], [49, [[0, 3, 74]]]]
    .forEach(([k, row]) => row.forEach(([b, len, m]) => { n('horns', k, b, len, m - 12, 0.85); n('violins', k, b, len, m + 12, 0.7); }));
  for (let k = 38; k < 50; k++) {
    const [bs, up] = H(k);
    up.forEach(m => n('tremolo', k, 0, 3, m + 12, 0.7, { legato: 0.05 }));
    n('basses', k, 0, 3, bs - 12, 0.8, { legato: 0.04 });
    n('brass', k, 0, 0.9, up[0], 0.75, { exact: true }); n('brass', k, 0, 0.9, up[1], 0.75, { exact: true });
    n('timp', k, 0, 0.6, bs < 42 ? bs : bs - 12, 0.6, { exact: true });
    for (let b = 0; b < 3; b++) E.kick.push({ t: bar(k, b), vel: b ? 0.35 : 0.6 });
    for (let e = 1; e < 6; e += 2) E.tick.push({ t: bar(k, e / 2), type: 'hat', vel: 0.35, pan: 0.2 });
    E.bass.push({ t: bar(k), dur: 2.9 * BEAT, midi: bs - 12, vel: 0.7, style: 'round', gain: 0.55, duck: 0.5 });
  }
  E.tremolo.push(...ccRamp('expression', bar(46), bar(49, 2.5), 0.7, 1));
  for (let i = 0; i < 12; i++) n('timp', 49, i / 4, 0.25, 46, 0.35 + 0.035 * i, { exact: true });

  // ---- 50-54 coda: the opening hammers return; one long Eb chord rings out with a soft shimmer and bell ----
  for (const m of [51, 55, 58, 63, 67, 70]) n('violins', 52, 0, 8, m, 0.55);
  for (const m of [51, 58, 63]) n('horns', 52, 0, 7, m, 0.5);
  n('celli', 52, 0, 8, 39, 0.55); n('basses', 52, 0, 8, 27, 0.55);
  n('keys', 52, 0, 8, 39, 0.45); n('keys', 52, 0, 8, 51, 0.4); n('keys', 52, 0.02, 8, 58, 0.35);
  E.keys.push({ t: bar(52) + 0.01, cc: 'sustain', value: 1 });
  for (let i = 0; i < 18; i++) n('timp', 52, i / 4, 0.25, 39, 0.5 - 0.025 * i, { exact: true });
  E.violins.push(...ccRamp('expression', bar(52, 1), bar(55), 0.9, 0.3));
  E.horns.push(...ccRamp('expression', bar(52, 1), bar(55), 0.9, 0.3));
  E.fx.push({ type: 'shimmer', t: bar(52), dec: 1.1, gain: 0.022 });
  E.bell.push({ t: bar(52), midi: 87, vel: 0.35, dec: 2.8 });
  E.bass.push({ t: bar(52), dur: 2.5, midi: 27, vel: 0.6, style: 'sub', gain: 0.6 });

  return {
    events: E,
    // hold the breath for the last eighth before each big arrival
    automation: (t, g) => ([bar(22), bar(38), bar(50)].some(a => t >= a - BEAT / 2 && t < a) ? g - 3 : g),
  };
}
