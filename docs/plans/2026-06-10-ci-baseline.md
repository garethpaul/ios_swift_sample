# CI Baseline

status: completed

## Context

The repository had a local static `make check` baseline for the legacy Swift
sample, but no hosted workflow ran it for pushes and pull requests.

## Changes

- Added a GitHub Actions workflow that installs Python 3.12 and runs
  `make check`.
- Extended the static checker and docs so the hosted CI path stays visible.

## Verification

- `make check`
