# Changelog

Changes are grouped using [Keep a Changelog](https://keepachangelog.com/en/1.1.0/) and versioned using [Semantic Versioning](https://semver.org/).

## [Unreleased]

### Changed
- **Breaking:** the single `op55` skill is now a set of eight skills installed together: the entry `op55-mode` (playbooks `create-cue` and `revise-cue`), `op55-compose`, `op55-render`, `op55-verify`, `resolve-op55-tools` and three principles. The entry is `/op55-mode` in Claude Code and `$op55-mode` in Codex instead of `/op55`.
- **Breaking:** the scripts moved from `skills/op55/scripts/` to `skills/resolve-op55-tools/scripts/`, and the fonts from `skills/op55/assets/fonts/` to `skills/resolve-op55-tools/assets/fonts/`. The render engine, the score API and the approved hashes are unchanged.
- `skills/op55/references/showreel.md` is now `skills/resolve-op55-tools/references/output-contract.md`. It lists op55's public interface and the files op55 writes, and no longer describes any particular consumer. The skill docs and README no longer name a consumer either. The README credits say where op55 came from.

### Added
- `DESIGN.md`, `skillset.json` and the skillset checks (`scripts/check.py`, `scripts/selftest.py`, `scripts/install_smoke.py`), run in CI as the `skillset` job.
- `metadata.version` in `resolve-op55-tools/SKILL.md`, so an installed copy carries its version. `render.mjs --version` prints it, and `tools/test_version.mjs` checks it against `VERSION`.

### Removed
- `skills/op55/`.
- **Breaking:** `verify.py --mix` and `--mix-py`. They ran an external video mixer and summarised voice over bed per narration line. The video's own mix stage measures this.

### Fixed
- Rendering fails when a `levels.points` bar or `levels.end` is past `duration`, and the error names that field, the bar, its time, and `duration`.
- Rendering rejects zero-length or reversed `levels` spans with an error that names the bar and its start and end times.

To migrate, run `npx skills@1.7.4 add ynginkim/op55` again and remove the old copy with `npx skills@1.7.4 remove op55` (add `-g` for a global install). Callers that hard-code `.claude/skills/op55/scripts` should use `resolve-op55-tools/scripts` and pass it explicitly (as `OP55_SCRIPTS` when using an environment variable). Callers of `verify.py --mix` should read their mixer's own per-line check instead. The public interface is in `skills/resolve-op55-tools/references/output-contract.md`.

## [0.1.0] - 2026-10-24

### Added
- Contribution, conduct, security, support, and release-readiness documentation.
- A development version source and explicit release verification checklist.

### Changed
- README installation and third-party license guidance reviewed for reproducibility and scope.

This is the first versioned code release. Earlier development history remains available in Git. Cross-repository integration and model/media quality are not guaranteed by structural or installation checks.
