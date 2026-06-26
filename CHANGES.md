# Changes

## 2026-06-26

- **2026-06-26 10:36 PDT — Priority: correctness.** Invalidated the artwork
  result generation before view-disappearance cancellation so image decoding
  already queued from a completed request cannot publish after navigation.
  Updated `SwiftExample/ViewController.swift`, the baseline checker, mutation
  regression, maintainer guidance, and the completed implementation plan.
  All four local aliases, the hostile external-path gate, and three mutation
  checks passed; Xcode execution remains a hosted macOS boundary. Finding:
  cancelling owned requests alone cannot cancel decode work already dispatched.
  Blockers: none. Next action: publish the PR, verify hosted gates, and merge
  only the green SHA.
- Made the static baseline reject permissive HTTP artwork authorities and
  publication that bypasses the current artwork result generation.
- Added mutation regressions for both security-sensitive checks to `make check`.

## 2026-06-19

- Rejected empty, control-bearing, over-200-character, and over-800-byte iTunes
  search terms, and limited rendered API results to 200 rows.
- Rejected fragmented or over-2048-byte artwork URLs and inspected image
  metadata before decoding to stop compressed pixel bombs at the parsing seam.
- Added explicit API/artwork cancellation, result-generation ownership, stale
  callback rejection, and a weak API delegate to avoid background work and
  retain cycles after navigation or reloads.

## 2026-06-17

- Applied an uncached 15-second request policy to every iTunes search before
  starting its active connection.
- Protected checkout-relative verification from a hostile `ROOT=/tmp` override.

## 2026-06-14

- Required the exact final HTTPS iTunes search endpoint before accepting JSON
  response metadata or body chunks.
- Rejected artwork URL userinfo and explicit ports for initial and final
  `mzstatic.com` response authorities.
- Rejected artwork with nonpositive, over-8192-axis, or over-16-megapixel
  dimensions before assigning decoded images to reusable cells.

## 2026-06-13

- Made all Make verification aliases location-independent when invoked through
  an absolute Makefile path.
- Replaced unbounded artwork buffering with a bounded artwork response loader
  that accepts successful JPEG or PNG bodies up to 1 MiB and completes once.
- Guarded async artwork result identity against current row data before image
  assignment after API reloads.

## 2026-06-12

- Bound shared response state to one active connection, canceling replaced
  searches and ignoring callbacks from stale connections.

## 2026-06-10

- Added successful-status, JSON MIME, 1 MiB response-size, and idempotent
  completion guards to the iTunes search client with focused assertions.
- Added pinned, read-only macOS hosted project validation for `make check` and
  `SwiftExample.xcodeproj` parsing without API or artwork requests.
- Cleared the network activity indicator when the results view disappears before
  API completion.
- Added a GitHub Actions workflow that runs the static `make check` baseline
  with Python 3.12 for pushes and pull requests.

## 2026-06-09

- Added local `make lint`, `make test`, and `make build` gate aliases for the
  static Swift sample baseline.
- Centralized API completion so parsed and empty result paths clear the retained
  response buffer after notifying the delegate.
- Routed API result UI updates through a main-thread guard before table reloads
  and network activity indicator changes.
- Added result array tests for accepted API arrays and malformed payloads that
  should clear stale table data.
- Moved artwork image fetches into an async artwork loader that clears reused
  image views and applies images only to matching visible cells.

## 2026-06-08

- Hardened iTunes search URL construction so malformed search text returns an empty result set instead of force-unwrapping.
- Replaced connection failure logging, forced JSON parsing, and forced table/image casts with empty-result or optional handling.
- Guarded table indexes before reading parsed result rows.
- Restricted artwork URL loading to HTTPS `mzstatic.com` hosts from the iTunes response.
- Added artwork URL tests for allowed `mzstatic.com` hosts and rejected schemes/hosts.
- Removed the unused location framework import from the first-party networking sample.
- Moved the Xcode scheme into shared project data, disabled location simulation, and ignored per-user Xcode state.
- Added `make check` with a static baseline for Xcode project wiring, plist/storyboard/asset parsing, public endpoint guardrails, and no-crash networking checks.
