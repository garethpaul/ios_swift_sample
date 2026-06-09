# Changes

## 2026-06-08

- Hardened iTunes search URL construction so malformed search text returns an empty result set instead of force-unwrapping.
- Replaced connection failure logging, forced JSON parsing, and forced table/image casts with empty-result or optional handling.
- Guarded table indexes before reading parsed result rows.
- Restricted artwork URL loading to HTTPS `mzstatic.com` hosts from the iTunes response.
- Removed the unused location framework import from the first-party networking sample.
- Moved the Xcode scheme into shared project data, disabled location simulation, and ignored per-user Xcode state.
- Added `make check` with a static baseline for Xcode project wiring, plist/storyboard/asset parsing, public endpoint guardrails, and no-crash networking checks.
