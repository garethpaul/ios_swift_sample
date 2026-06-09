# Artwork URL Tests Plan

status: completed

## Context

The sample only loads artwork from HTTPS `mzstatic.com` URLs parsed from the
iTunes response. That boundary is deterministic and should be covered by focused
unit assertions instead of generated XCTest placeholders.

## Objectives

- Replace generated XCTest placeholders with focused artwork URL tests.
- Cover accepted HTTPS `mzstatic.com` and subdomain URLs.
- Cover rejected HTTP, untrusted host, and malformed URL values.
- Keep artwork loading local to the documented public iTunes response boundary.
- Extend the static baseline so artwork URL tests remain visible without Xcode.

## Verification

- `make check`
- `python3 scripts/check-baseline.py`
- `git diff --check`
