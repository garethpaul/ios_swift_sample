# Bounded Artwork Response

status: completed

## Context

Artwork URLs are restricted to HTTPS `mzstatic.com` hosts and stale cell
results are rejected, but `NSData(contentsOfURL:)` buffers the full response
before decoding. A trusted host can still return an unexpectedly large or
non-image body and exhaust memory.

## Requirements

- Stream artwork with a 1 MiB cap instead of buffering an unbounded response.
- Require a successful HTTP status, a final HTTPS `mzstatic.com` response URL,
  and a JPEG or PNG MIME type before accepting body data.
- Complete each request at most once and preserve background image decoding,
  main-thread UI assignment, and current-row/cell identity checks.
- Add focused source tests and mutation-sensitive static contracts.

## Scope Boundaries

- Do not add caching, persistence, third-party dependencies, broader artwork
  hosts, or synchronous main-thread networking.
- Do not claim live network or UIKit execution without Xcode.

## Work Completed

- Added an `NSURLConnection` data delegate that accepts successful JPEG or PNG
  responses from final HTTPS `mzstatic.com` URLs, rejects declared or
  accumulated bodies over 1 MiB, and completes each request at most once.
- Replaced `NSData(contentsOfURL:)` with the bounded request while preserving
  background image decoding and main-thread cell/result identity checks.
- Added focused XCTest source assertions, mutation-sensitive checker contracts,
  and maintenance/security documentation.

## Verification Completed

- `make lint`, `make test`, `make build`, and `make check` passed the complete
  static baseline; Xcode was unavailable on the local Linux host.
- `python3 -m py_compile scripts/check-baseline.py`, plist/XML/JSON parsing, and
  `git diff --check` passed.
- Eight isolated hostile mutations covering response size, HTTP status, final
  response host, MIME type, streamed accumulation, cancellation, idempotency,
  and focused test evidence were rejected.
