# Artwork URL Boundary Plan

status: completed

## Context

`ios_swift_sample` parses artwork URLs from the public iTunes Search API response and loads them into table view cells. The sample already handles missing artwork values, but the parsed string should not be allowed to select arbitrary URL schemes or hosts.

## Objectives

- Keep the visible iTunes search sample behavior unchanged.
- Accept only HTTPS artwork URLs on `mzstatic.com` hosts.
- Leave artwork empty when a parsed artwork URL is missing, malformed, non-HTTPS, or outside the expected host boundary.
- Extend `make check` so future table rendering changes preserve the artwork URL boundary.

## Verification

- `make check`
- `python3 scripts/check-baseline.py`
- `git diff --check`
