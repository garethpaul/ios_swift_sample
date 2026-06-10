# Network Activity Indicator Lifecycle

status: completed

## Context

The sample turns on the global network activity indicator before starting the
iTunes lookup and clears it when API results arrive. If the view disappears
before the legacy connection completes, the indicator can remain visible even
though this screen is no longer active.

## Completed Scope

- Cleared the network activity indicator from `viewWillDisappear`.
- Kept API completion clearing the indicator after parsed or empty results.
- Extended the static baseline and docs so the indicator lifecycle remains
  explicit without adding credentials, private endpoints, or persistence.

## Verification

- `make check`
- `python3 scripts/check-baseline.py`
- `git diff --check`
