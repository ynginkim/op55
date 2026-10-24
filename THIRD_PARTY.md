# Third-party code and sounds

The op55 code is MIT (see `LICENSE`). These parts come from elsewhere.

## Vendored code

| Component | Version | License | Where |
| --- | --- | --- | --- |
| [spessasynth_core](https://github.com/spessasus/spessasynth_core) by spessasus | 4.3.22 | Apache-2.0 | `skills/op55/scripts/vendor/spessasynth_core.mjs`, license in `spessasynth_core.LICENSE` |
| [fflate](https://github.com/spessasus/spessasynth_core/tree/99f294d997dea0f2691738c97586c6a3d289fe7d/src/externals/fflate), Copyright (c) 2023 Arjun Barrett (embedded by spessasynth_core) | as included in spessasynth_core 4.3.22 | MIT | same bundle, full license in `skills/op55/scripts/vendor/fflate.LICENSE` |
| [stb-vorbis](https://www.npmjs.com/package/stb-vorbis) (bundled inside the above, decodes SF3) | 0.0.6 | Apache-2.0 | same bundle, license in `stb-vorbis.LICENSE` |

The bundle is an unmodified esbuild bundle of the npm package (see `skills/op55/scripts/vendor/README.md`).

## Fonts (used by `preview.py`)

| Font | License | Where |
| --- | --- | --- |
| [Instrument Serif](https://github.com/Instrument/instrument-serif) Italic | SIL Open Font License 1.1 | `skills/op55/assets/fonts/InstrumentSerif-Italic.ttf`, `OFL-InstrumentSerif.txt` |
| [JetBrains Mono](https://github.com/JetBrains/JetBrainsMono) (variable weight) | SIL Open Font License 1.1 | `skills/op55/assets/fonts/JetBrainsMono-wght.ttf`, `OFL-JetBrainsMono.txt` |

## SoundFont banks (downloaded by `setup.mjs`, never committed)

| Bank | Author | License | Use in your videos |
| --- | --- | --- | --- |
| GeneralUser GS 2.0.3 | S. Christian Collins | GeneralUser GS License v2.0 | Free for private and commercial music. The author asks redistributors to serve their own copy, which is why op55's release hosts one (with the CC0 upright) |
| Upright Piano KW (2022-02-21) | FreePats project | CC0 1.0 | Free, no attribution needed |
| Salamander Grand Piano V3 (2020-06-02) | Alexander Holm | CC BY 3.0 | Free, **credit required**: "Salamander Grand Piano by Alexander Holm (CC BY 3.0)". `music.meta.json` lists it when a cue uses it |

Third-party banks retain their own terms; op55's MIT license does not relicense them or guarantee rights in every rendered output. Review the original notices before redistribution or commercial distribution. GeneralUser's author explicitly notes uncertainty about the origin of some samples; this project does not independently clear those rights.

Bank provenance and distribution notices are in [`licenses/banks/`](licenses/banks/). `tools/release-banks.sh` includes these notices as separate release assets when run. Adding this source change does not establish that an existing release has been repaired. Salamander is downloaded separately, and its required attribution must be preserved in outputs that use it.

Reviewed code provenance: spessasynth_core 4.3.22 npm metadata identifies commit `99f294d997dea0f2691738c97586c6a3d289fe7d`; stb-vorbis 0.0.6 identifies [`2c5f11f028192b5580650ffd79d49ca3019a32fb`](https://github.com/spessasus/stb-vorbis/tree/2c5f11f028192b5580650ffd79d49ca3019a32fb). Their published npm archives and these source trees contain no separate NOTICE file. The embedded fflate MIT notice is retained separately because the published spessasynth_core archive contains its code without a standalone fflate license file.

## Art

`assets/art/*` were generated with Codex's built-in imagegen from the prompts in `tools/art/prompts/`. Typography and the spectrogram card are composited by `tools/art/compose.mjs`.

## Music

The *Eroica* example quotes the opening idea of Ludwig van Beethoven's Symphony No. 3 in E-flat, Op. 55 (1804), which is in the public domain. The arrangement is new.

## Community document

The Contributor Covenant text in `CODE_OF_CONDUCT.md` retains its stated Creative Commons Attribution 4.0 license and attribution; it is not relicensed MIT.
