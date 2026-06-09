# UI Result Main Thread

status: completed

## Context

`SearchResultsViewController.didRecieveAPIResults` updates table data, reloads
the table view, and clears the network activity indicator. Those UIKit updates
should run on the main thread even if a future API caller invokes the delegate
from a background queue.

## Objectives

- Detect off-main API result delivery at the UI boundary.
- Re-dispatch API result handling to the main queue before mutating UI state.
- Preserve existing empty-result and partial-render behavior.
- Extend the static baseline so the main-thread UI guard remains visible without
  Xcode.
- Document the guard alongside the networking and table rendering baseline.

## Verification

- `make check`
- `python3 scripts/check-baseline.py`
- `git diff --check`
