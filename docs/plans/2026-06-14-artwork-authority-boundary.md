# Artwork Authority Boundary

status: completed

## Context

Artwork URL validation requires HTTPS and an `mzstatic.com` host, but currently
accepts embedded userinfo and explicit ports. Those authority components are
outside the intended public artwork endpoint boundary and must be rejected for
both initial and final response URLs.

## Requirements

- Reject artwork URLs containing a username, password, or explicit port.
- Preserve HTTPS and exact/subdomain `mzstatic.com` host acceptance.
- Apply the same authority policy to initial URL parsing and final response URL
  validation.
- Add focused XCTest source cases and mutation-sensitive static contracts.

## Scope Boundaries

- Do not change API endpoints, artwork size or pixel limits, caching, table
  rendering, or dependency versions.
- Do not make live iTunes or artwork requests during validation.
- Do not claim simulator or device behavior on Linux.

## Work Completed

- Rejected artwork URLs with a username, password, or explicit port in the
  shared initial and final response URL predicate.
- Added focused XCTest source cases for userinfo and explicit-port rejection.
- Extended static contracts and project documentation for the authority limit.

## Verification Completed

- Python checker compilation passed. Before this completion record was added,
  the baseline reached only the expected pending-plan evidence failure.
- `make lint`, `make test`, `make build`, and `make check` passed from the
  repository root; `make check` also passed through the absolute Makefile path.
- Six isolated hostile mutations were rejected: restoring username, password,
  or explicit-port acceptance; hiding the focused XCTest source case; reverting
  the plan to pending; and erasing hostile-mutation verification evidence.
- Xcode was unavailable on this Linux host, so simulator, device, and live
  artwork requests are not claimed.
