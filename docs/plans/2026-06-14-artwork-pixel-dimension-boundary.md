# Artwork Pixel Dimension Boundary

status: completed

## Summary

Reject downloaded artwork with invalid or excessive pixel dimensions before it is assigned to a table cell. Preserve the existing response-size, trusted-host, media-type, row-identity, and main-thread publication boundaries.

## Problem Frame

Artwork downloads are capped at 1 MiB, but compressed PNG or JPEG data can still describe very large pixel dimensions. Passing such an image into the visible cell path can create disproportionate decode and rendering memory pressure despite the transport byte limit.

## Requirements

- **R1:** Artwork must have positive dimensions no larger than 8192 pixels on either axis.
- **R2:** Total artwork pixels must not exceed 16 megapixels, using overflow-safe arithmetic.
- **R3:** Dimension validation must occur after image construction but before cell assignment and layout.
- **R4:** Existing response-size, status, media-type, redirect-host, current-row identity, and main-thread UI contracts must remain unchanged.
- **R5:** Verification must record unavailable simulator/device image-decoding coverage truthfully.

## Key Technical Decisions

- **Two-dimensional bound:** Combine per-axis and total-pixel caps so extreme aspect ratios and oversized square images both fail closed.
- **Division-based product check:** Validate `width <= maximumPixelCount / height` after positive bounds instead of multiplying untrusted dimensions.
- **Pre-publication guard:** Inspect the constructed image's Core Graphics dimensions before assigning it to the reusable cell.

## Implementation Units

### U1: Add artwork dimension validation

**Files:**
- `SwiftExample/ViewController.swift`

Add constants and reusable dimension/image validators, then gate the existing background image path before main-thread cell publication.

### U2: Add boundary and mutation coverage

**Files:**
- `SwiftExampleTests/SwiftExampleTests.swift`
- `scripts/check-baseline.py`

Cover zero, exact-limit, axis-overflow, and total-pixel-overflow cases. Require validation ordering before cell assignment and reject weakened constants or unsafe multiplication.

### U3: Record completed evidence

**Files:**
- `docs/plans/2026-06-14-artwork-pixel-dimension-boundary.md`
- `README.md`
- `CHANGES.md`
- `SECURITY.md`
- `VISION.md`
- `AGENTS.md`

Record the image-memory boundary, actual local verification, unavailable platform coverage, and completed plan status.

## Validation

- Run `make check`, `make lint`, `make test`, and `make build` from the checkout.
- Run `make check` through the absolute Makefile path from `/tmp`.
- Reject isolated mutations that remove positive bounds, axis caps, total-pixel division, image integration, tests, or completed evidence.
- Audit the exact intended diff for whitespace, conflicts, generated artifacts, signing material, and credentials.

## Verification Results

- `make check`, `make lint`, `make test`, and `make build` passed the maintained static baseline; Xcode was unavailable on this Linux host.
- The external `make -f /absolute/path/to/Makefile check` gate passed from `/tmp`.
- All six isolated hostile mutations were rejected when they removed positive bounds, changed the axis limit, replaced overflow-safe division, bypassed image integration, weakened the total-pixel limit, or removed the total-pixel test.
- No credentials or signing material were used or added, and no API or artwork network request was executed locally.
- Simulator and physical-device image parsing, decode, rendering, and memory behavior remain unverified and are not claimed.

## Risks

- UIKit image parsing and decode behavior cannot be executed on Linux; hosted macOS XCTest and later device verification remain required.
- The limits are intentionally conservative for 60-point artwork and may need explicit review if the sample later displays high-resolution media.
