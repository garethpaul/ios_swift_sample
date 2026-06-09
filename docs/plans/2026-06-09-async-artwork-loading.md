# Async Artwork Loading

status: completed

## Context

Table cells loaded artwork with `NSData(contentsOfURL:)` during cell
construction. Even with trusted `mzstatic.com` URL filtering, that synchronous
fetch could block table rendering and could leave reused cells showing stale
images.

## Completed Scope

- Cleared reused cell image views before loading artwork.
- Moved artwork data fetches onto a background queue.
- Applied loaded images on the main queue only when the cell still represents
  the original index path.
- Kept HTTPS `mzstatic.com` artwork URL validation unchanged.
- Extended the static baseline and docs so async artwork loading stays guarded.

## Verification

- `make check`
- `git diff --check`
