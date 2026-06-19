# Location-Independent Swift Sample Verification

status: completed

## Context

Absolute Makefile invocations previously resolved `scripts/check-baseline.py`
relative to the caller instead of the checkout, so documented verification
aliases failed outside the repository directory.

## Scope

1. Derive the checkout root from the loaded Makefile.
2. Invoke the baseline checker from that root for every Make alias.
3. Add exact Makefile, completed-plan, external-run, and guidance contracts.
4. Preserve network, artwork, tests, project metadata, and workflow behavior.

## Verification Plan

- Run all four Make gates from the checkout and through an absolute Makefile
  path from a temporary directory.
- Run checker compilation, project metadata parsing, and diff checks.
- Reject root-derivation, checker-invocation, plan-status, plan-evidence, and
  documentation mutations independently.
- Inspect intended paths, secret patterns, conflict markers, and generated
  artifacts before commit.

## Work Completed

- Derived the checkout root from the loaded Makefile and invoked the baseline
  checker by absolute path.
- Added exact Makefile, completed-plan, external-run, and synchronized guidance
  contracts without changing network, artwork, tests, project, or workflow files.

## Verification Completed

- All four Make gates passed from the checkout.
- All four Make gates passed from `/tmp` through the absolute Makefile path.
- `python3 -m py_compile scripts/check-baseline.py`, project metadata parsing,
  and `git diff --check` passed.
- Local validation reported that `xcodebuild` was unavailable and therefore ran
  the static legacy baseline only.
- Five isolated hostile mutations were rejected: root derivation, checker
  invocation, plan status, plan evidence, and documentation guidance.

## Risk And Rollback

This changes verification path resolution only. Rollback restores the relative
Make recipe and removes its checker, plan, and documentation contracts.
