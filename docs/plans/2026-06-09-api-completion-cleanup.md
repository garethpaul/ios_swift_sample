# API Completion Cleanup Plan

status: completed

## Context

`APIController` retains response bytes while the iTunes request is loading and
then notifies the delegate with parsed or empty results. Success, malformed
JSON, failed connection, and malformed request paths should leave the controller
ready for a later search without retaining stale response data.

## Objectives

- Route parsed and empty API results through a single completion helper.
- Clear the retained response buffer after notifying the delegate.
- Preserve empty-result behavior for malformed requests, connection failures,
  non-dictionary JSON, and JSON parse errors.
- Extend the static baseline so API completion cleanup remains explicit.

## Verification

- `make check`
- `python3 scripts/check-baseline.py`
- `git diff --check`
