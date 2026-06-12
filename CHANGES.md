# Changes

## 2026-06-10

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
