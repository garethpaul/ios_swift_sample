# Artwork Authority Boundary

status: pending

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

## Planned Verification

- Run all four Make gates from the repository root and `make check` through the
  absolute Makefile path from an external directory.
- Compile the checker and run diff, generated-artifact, and changed-line
  credential audits.
- Reject isolated mutations that restore userinfo or explicit-port acceptance,
  remove focused tests, or falsify plan completion evidence.
