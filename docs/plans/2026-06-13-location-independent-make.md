# Location-Independent Swift Sample Verification

status: in progress

## Context

Absolute Makefile invocations resolve `scripts/check-baseline.py` relative to
the caller instead of the checkout, so documented verification aliases fail
outside the repository directory.

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

## Risk And Rollback

This changes verification path resolution only. Rollback restores the relative
Make recipe and removes its checker, plan, and documentation contracts.
