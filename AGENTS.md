# AGENTS.md

## Repository purpose

`garethpaul/ios_swift_sample` is a legacy Swift iOS sample that searches the
public iTunes Search API and renders result artwork.

## Project structure

- `Makefile` - repository verification targets
- `scripts` - baseline checks and helper scripts
- `docs` - plans, notes, and generated README assets
- `SwiftExample.xcodeproj` - Xcode project
- `Screenshots` - checked-in app preview images
- `SwiftExample` - application source, storyboards, assets, and metadata
- `SwiftExampleTests` - XCTest coverage and test metadata

## Development commands

- Install dependencies: no repository-specific install command is documented.
- Full baseline: `make check`
- Local Apple development: `open SwiftExample.xcodeproj`
- If a command above skips because a platform toolchain is missing, verify on a machine with that SDK before claiming platform behavior is tested.

## Coding conventions

- Language mix noted in the README: Swift (4).
- Preserve legacy Xcode project settings and signing assumptions unless the change is explicitly about modernization.

## Testing guidance

- Test-related files detected: `docs/plans/2026-06-08-artwork-url-tests.md`, `docs/plans/2026-06-09-result-array-tests.md`, `SwiftExampleTests/SwiftExampleTests.swift`
- Start with the narrowest relevant test or Make target, then run `make check` before handing off if the change is not documentation-only.
- Keep README verification notes in sync when commands, fixtures, or supported toolchains change.

## PR / change guidance

- Keep diffs focused on the requested repository and avoid unrelated modernization or formatting churn.
- Preserve public APIs, sample behavior, file formats, and documented environment variables unless the task explicitly changes them.
- Update tests, README notes, or docs/plans when behavior, security posture, or validation commands change.
- Call out skipped platform validation, legacy toolchain assumptions, and any risky files touched in the final summary.

## Safety and gotchas

- No required secret or credential file was identified in the repository scan. If you add integrations later, keep secrets out of git.
- Do not add private endpoints, API credentials, tokens, signing material, `.env` files, or machine-local Xcode configuration to source control.
- Keep the sample on the documented public HTTPS iTunes Search API unless endpoint changes are reviewed separately. Network, artwork URL, and JSON failure handling should avoid console logging private data, arbitrary URL schemes, and forced unwraps.
- This is a legacy Apple platform sample. Xcode, Swift, and deployment target
  versions must remain aligned with the checked-in project.
- Run `make lint`, `make test`, `make build`, and `make check` before pushing changes to Swift sources, plists, storyboards, assets, Xcode project metadata, or security docs.
- See `SECURITY.md` for vulnerability reporting and safe research guidance.

## Agent workflow

1. Inspect the README, Makefile, manifests, and the files directly related to the request.
2. Make the smallest source or docs change that satisfies the task; avoid generated, vendored, or local-environment files unless required.
3. Run the narrowest useful validation first, then `make check` or the documented package/platform gate when available.
4. If a required SDK, service credential, or external runtime is unavailable, record the skipped command and why.
5. Summarize changed files, commands run, and remaining risks or follow-up validation.
