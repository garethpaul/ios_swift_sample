# Artwork Result Identity Guard

status: planned

## Context

Artwork downloads verify that the target cell is still visible at the original
index path. If API results reload while a download is in flight, that same row
and cell can represent a different app, allowing stale artwork to be assigned.

## Requirements

- Verify the current row remains in bounds and still exposes the same safe
  artwork URL before assigning a completed image.
- Preserve HTTPS/mzstatic URL restrictions, background loading, main-thread UI
  assignment, visible-cell identity checks, and empty fallback behavior.
- Add a testable row-URL identity helper, focused XCTest assertions, static
  ordering contracts, documentation, and completed verification evidence.

## Scope Boundaries

- Do not add caching, persistence, third-party dependencies, broader hosts, or
  synchronous main-thread networking.
- Do not claim live network or UIKit execution without Xcode.

## Verification

- All four Make gates, Python compilation, metadata parsing, and diff checks.
- Hostile mutations for missing bounds, unsafe URL reuse, missing equality,
  assignment-before-identity, focused tests, plan status, and evidence.
