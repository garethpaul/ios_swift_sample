# Bounded Artwork Response

status: pending

## Context

Artwork URLs are restricted to HTTPS `mzstatic.com` hosts and stale cell
results are rejected, but `NSData(contentsOfURL:)` buffers the full response
before decoding. A trusted host can still return an unexpectedly large or
non-image body and exhaust memory.

## Requirements

- Stream artwork with a 1 MiB cap instead of buffering an unbounded response.
- Require a successful HTTP status and JPEG or PNG MIME type before accepting
  body data.
- Complete each request at most once and preserve background image decoding,
  main-thread UI assignment, and current-row/cell identity checks.
- Add focused source tests and mutation-sensitive static contracts.

## Scope Boundaries

- Do not add caching, persistence, third-party dependencies, broader artwork
  hosts, or synchronous main-thread networking.
- Do not claim live network or UIKit execution without Xcode.

## Work Completed

Pending implementation.

## Verification Completed

Pending implementation and validation.
