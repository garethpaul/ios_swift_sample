---
title: "fix: Protect the Make repository root"
type: fix
date: 2026-06-17
execution: code
status: completed
---

# fix: Protect the Make repository root

## Summary

Make the checkout-derived repository root authoritative even when a caller
passes a hostile `ROOT` value on the command line. Preserve all existing gate
aliases and search-request behavior while extending the maintained static
contract and documentation to cover the override boundary.

## Problem Frame

The Makefile derives `ROOT` from `MAKEFILE_LIST`, but GNU Make command-line
variables override a normal `:=` assignment. An external invocation such as
`make -f /path/to/Makefile check ROOT=/tmp` therefore tries to execute
`/tmp/scripts/check-baseline.py` instead of the checker in the checkout. The
current baseline only verifies the assignment text and does not reject this
runtime failure.

## Requirements

- R1. Every Make alias must resolve the checker relative to the loaded
  Makefile, regardless of a command-line `ROOT` value.
- R2. Existing `lint`, `test`, `build`, and `check` behavior must remain
  unchanged for normal repository and external-directory invocations.
- R3. The static baseline must require the authoritative override form and
  reject a weakened normal assignment.
- R4. Maintainer guidance and completed plan evidence must record the hostile
  override boundary and actual verification.
- R5. Search request construction, XCTest declarations, networking behavior,
  Xcode metadata, and hosted workflow behavior must remain unchanged.

## Key Technical Decisions

- KTD1. Use GNU Make's `override` directive on the existing derived root. This
  keeps the current path derivation and prevents command-line replacement
  without introducing shell-specific path logic.
- KTD2. Extend `scripts/check-baseline.py` rather than adding a second test
  runner. The baseline already owns exact Makefile and documentation contracts.
- KTD3. Keep this change stacked on the search-request policy branch because
  that branch is already pushed and otherwise fails its required external gate.

## Implementation Units

### U1. Make the derived root authoritative

- **Files:** `Makefile`
- **Requirements:** R1, R2, R5
- Replace the normal root assignment with the authoritative override form while
  preserving all aliases and the absolute checker invocation.

### U2. Add mutation-sensitive maintenance contracts

- **Files:** `scripts/check-baseline.py`,
  `scripts/test-make-root-override-contract.py`, `Makefile`
- **Requirements:** R3, R4, R5
- Require the exact override directive, its baseline assertion, this completed
  plan, and synchronized guidance through an independently invoked contract so
  removal or weakening fails the portable gate.

### U3. Record the verification boundary

- **Files:** `README.md`, `CHANGES.md`,
  `docs/plans/2026-06-17-002-fix-make-root-override-protection-plan.md`
- **Requirements:** R4, R5
- Document that absolute-Makefile gates remain checkout-relative even with a
  hostile command-line root, then record the actual completed validation.

## Verification Strategy

- Run `make check` from the repository root.
- Run the absolute Makefile gate from `/tmp` with `ROOT=/tmp`.
- Run isolated mutations for removing `override`, restoring a normal
  assignment, weakening the checker contract, and removing plan/guidance
  evidence.
- Audit the exact intended diff, generated artifacts, secret-like additions,
  worktree cleanliness, and upstream equality before delivery.
- Treat Xcode execution as hosted evidence because this Linux host lacks a
  compatible toolchain.

## Scope Boundaries

### In Scope

- Make root precedence, its portable checker contract, and synchronized
  verification guidance.

### Out of Scope

- Search networking changes, XCTest behavior, Xcode project changes, workflow
  event changes, or modernization of the legacy Swift networking stack.

## Risks And Rollback

The change depends on GNU Make semantics already used by the repository's
hosted and local gates. Rollback restores the normal assignment and removes the
new contracts, but also restores the demonstrated hostile-override failure.

## Verification Completed

- The repository-root `make check` gate passed.
- The absolute Makefile gate passed from `/tmp` with a hostile `ROOT=/tmp` override.
- Six isolated mutations were rejected: removing `override`, using the wrong
  derived root, hiding the authoritative text in a comment beside a normal
  assignment, weakening the checker contract, removing completed-plan
  evidence, and removing maintainer guidance.
- The exact intended diff, generated-artifact scan, secret-like addition scan,
  and whitespace audit passed; Xcode-dependent execution remains a hosted
  validation boundary on this Linux host.
