# Version and release policy

`VERSION` is the repository version source. A version string alone does not publish a Git tag or release. Do not interpret a document or a draft PR as a published release.

Use `vMAJOR.MINOR.PATCH` tags. Before 1.0, a breaking contract change increments MINOR; compatible additions increment MINOR and compatible fixes increment PATCH. Breaking changes include renamed/removed skills or playbooks, changed input/output formats, installation paths, required resources, or command/file contracts. Document migrations explicitly.

## Release checklist

- [ ] Review and merge the approved implementation; rerun checks on the exact release commit.
- [ ] Check source notices, bundled resources, secrets, and third-party redistribution terms.
- [ ] Verify clean installation at the intended ref and record runtime/tool versions.
- [ ] Verify cross-repository compatibility at exact commit SHAs, including optional integrations.
- [ ] Change VERSION to the release number and move Unreleased entries to a dated changelog section.
- [ ] Review release notes and obtain maintainer approval to publish.
- [ ] Create the tag and GitHub release at the verified commit; do not move published tags.
- [ ] Reinstall using the published tag and record the result.

Keep bank/resource release tags separate from code releases. In op55, `banks-v1` identifies resource distribution and is not the skillset's semantic version. Publish required license attachments alongside resources.

## Reproducible installation

The pinned [`skills@1.7.4` installer](https://github.com/vercel-labs/skills/blob/v1.7.4/package.json) requires Node.js >= 22.20.0. This installer requirement is separate from the op55 renderer's Node.js >= 18 requirement.

The skills installer parses a quoted `owner/repo#REF` as a Git ref. `@name` selects a skill, not a version. Use a published tag or full 40-character commit SHA; do not advertise a tag before it exists. Pin the installer itself, for example `npx skills@1.7.4 add 'owner/repo#FULL_COMMIT_SHA'`, replacing the source with the verified repository and SHA.

The `1.7.4` parser and clone behavior were reviewed in [source-parser.ts](https://github.com/vercel-labs/skills/blob/v1.7.4/src/source-parser.ts) and [git.ts](https://github.com/vercel-labs/skills/blob/v1.7.4/src/git.ts). Private repositories still require existing Git access; do not create or paste access tokens into commands, documents, or issues.
