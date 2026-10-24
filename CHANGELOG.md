# Changelog

Changes are grouped using [Keep a Changelog](https://keepachangelog.com/en/1.1.0/) and versioned using [Semantic Versioning](https://semver.org/).

## [Unreleased]

### Changed
- **Breaking:** the single `op55` skill is now a set of eight skills installed together: the entry `op55-mode` (playbooks `create-cue` and `revise-cue`), `op55-compose`, `op55-render`, `op55-verify`, `resolve-op55-tools` and three principles. The entry is `/op55-mode` in Claude Code and `$op55-mode` in Codex instead of `/op55`.
- **Breaking:** the scripts moved from `skills/op55/scripts/` to `skills/resolve-op55-tools/scripts/`, and the fonts from `skills/op55/assets/fonts/` to `skills/resolve-op55-tools/assets/fonts/`. The render engine, the score API and the approved hashes are unchanged.

### Added
- `DESIGN.md`, `skillset.json` and the skillset checks (`scripts/check.py`, `scripts/selftest.py`, `scripts/install_smoke.py`), run in CI as the `skillset` job.

### Removed
- `skills/op55/`.

To migrate, run `npx skills@1.7.4 add ynginkim/op55` again and remove the old copy with `npx skills@1.7.4 remove op55` (add `-g` for a global install). Callers that hard-code `.claude/skills/op55/scripts` should use `resolve-op55-tools/scripts`. Pass showreel the script folder as `OP55_SCRIPTS` (see `skills/resolve-op55-tools/references/showreel-contract.md`).

## [0.1.0] - 2026-10-24

### Added
- Contribution, conduct, security, support, and release-readiness documentation.
- A development version source and explicit release verification checklist.

### Changed
- README installation and third-party license guidance reviewed for reproducibility and scope.

This is the first versioned code release. Earlier development history remains available in Git. Cross-repository integration and model/media quality are not guaranteed by structural or installation checks.
