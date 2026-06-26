# Artwork Disappearance Generation Plan

status: completed

## Problem

Cancelling the owned artwork requests when the results view disappears does not
cancel image decoding that was already dispatched after a request completed.
Because `viewWillDisappear` left `artworkGeneration` unchanged, that queued work
could still satisfy the main-thread generation guard and publish after
navigation.

## Decision

- Advance `artworkGeneration` before cancelling artwork requests during view
  disappearance.
- Preserve the existing request cancellation, cell identity, URL authority,
  response-size, image-dimension, and main-thread publication boundaries.
- Extend the static baseline and its mutation suite so removing or reordering
  the invalidation fails `make check`.

## Files

- `SwiftExample/ViewController.swift`
- `scripts/check-baseline.py`
- `scripts/test-check-baseline.py`
- `README.md`
- `SECURITY.md`
- `VISION.md`
- `CHANGES.md`

## Verification Completed

- The new baseline assertion failed before the implementation change.
- The focused baseline passed after advancing the generation before
  cancellation.
- Three isolated hostile mutations were rejected, including removal of the
  disappearance invalidation.
- `make lint`, `make test`, `make build`, `make check`, and the absolute
  Makefile gate from `/tmp` with `ROOT=/tmp` passed.
- Xcode was unavailable on the Linux host, so project build and test execution
  remains a hosted macOS validation boundary.

## Scope Boundaries

This change does not modernize the legacy networking APIs, alter iTunes search
behavior, change artwork acceptance limits, or add new UI behavior. It only
invalidates publication ownership when the current results view disappears.
