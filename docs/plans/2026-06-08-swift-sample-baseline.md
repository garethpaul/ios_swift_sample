# iOS Swift Sample Baseline Plan

status: completed

## Context

`ios_swift_sample` is a legacy Swift iOS app that queries the public iTunes
Search API, parses JSON, and renders results in a table view. Full build and
runtime validation still needs macOS/Xcode, but the repository can enforce a
static baseline on Linux.

## Objectives

- Preserve the iTunes search to table-view sample flow.
- Keep the public HTTPS iTunes endpoint explicit and avoid credentials or private endpoints.
- Avoid crashes from malformed URLs, failed connections, invalid JSON, missing result arrays, and missing artwork URLs.
- Keep committed app/test plists and Interface Builder files parseable.
- Add a reproducible `make check` entry point for source, project, plist, storyboard, asset, and documentation guardrails.

## Verification

- `make check`
- `python3 scripts/check-baseline.py`
- `git diff --check`
