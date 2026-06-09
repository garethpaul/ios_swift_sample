# Result Array Tests Plan

status: completed

## Context

`SearchResultsViewController.didRecieveAPIResults` treats the iTunes response
`results` value as the source of table rows. The controller already clears table
data when that value is missing or malformed, but that behavior should be pinned
by focused tests instead of relying only on static source checks.

## Objectives

- Cover accepted API result arrays replacing table data.
- Cover malformed API result payloads clearing stale table data.
- Preserve the existing empty-result and partial-render behavior.
- Extend the static baseline so result array tests remain visible without
  Xcode.
- Document the result-array coverage beside the network and table rendering
  guardrails.

## Verification

- `make check`
- `python3 scripts/check-baseline.py`
- `git diff --check`
