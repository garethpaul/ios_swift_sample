---
title: Search Response Authority Boundary
date: 2026-06-14
status: completed
execution: code
---

## Context

The iTunes search client validates response status, declared size, and media
type, but `NSURLConnection` can follow redirects before delivering the final
response. A successful JSON response from an unexpected authority or path can
therefore reach the shared response buffer and result parser.

## Requirements

- Require the final search response URL to use HTTPS, `itunes.apple.com`, no
  userinfo, no explicit port, no fragment, and the exact `/search` path.
- Apply the authority boundary before declared-size and media-type acceptance or
  response-body accumulation.
- Preserve the current request URL, query parameters, connection ownership,
  1 MiB limit, accepted media types, and failure completion behavior.
- Add focused XCTest declarations and mutation-sensitive static contracts for
  accepted and rejected final response URLs.
- Synchronize repository guidance and record truthful verification evidence.

## Non-Goals

- Replacing `NSURLConnection` or modernizing the legacy Swift toolchain.
- Disabling redirects through a new connection delegate policy.
- Changing search terms, response schema, artwork loading, or UI behavior.
- Claiming live iTunes, simulator, device, or Xcode execution from Linux.

## Verification Plan

- Run shell/Python syntax checks, all four Make gates, and the external-directory
  Make gate.
- Reject mutations that weaken scheme, host, userinfo, port, path, fragment,
  helper invocation, focused tests, or completed-plan evidence.
- Audit the exact diff, generated artifacts, protected project/workflow files,
  whitespace, conflict markers, and changed-line credential patterns.
- Take one bounded exact-head pull-request and security-alert snapshot without
  polling.

## Work Completed

- Added one trusted final-search URL helper covering HTTPS,
  `itunes.apple.com`, absent userinfo/port/fragment, and the exact `/search`
  path.
- Required every successful search response to pass that helper before declared
  size, media-type, or body-chunk acceptance.
- Added accepted-query and rejected authority/path XCTest declarations,
  mutation-sensitive static contracts, and synchronized repository guidance.

## Verification Completed

- Python syntax and all four Make gates passed the complete static baseline; the
  external-directory Make gate also passed.
- Nine hostile mutations were rejected across scheme, host, userinfo/port,
  path, fragment, helper invocation, focused test, and completed-plan weakening.
- The checker confirmed the maintained XCTest declarations and project wiring;
  xcodebuild was unavailable on Linux, so no XCTest, simulator, or device run is
  claimed.
- Exact diff, generated-artifact, protected project/workflow, whitespace,
  conflict-marker, and changed-line credential audits passed.
- No live iTunes request, artwork request, simulator, or device flow was
  performed.
- The hosted pull-request and security-alert result is recorded against the
  exact pushed head in the external engineering tracker.
