# Active API Connection

status: completed

## Context

`APIController` stores one response buffer, accepted-response flag, and
completion flag, but does not retain the `NSURLConnection` that owns that
state. Starting another search before the first request finishes can allow old
callbacks to append to or complete the new request.

## Work Completed

- Retain the active connection and cancel it before starting a new search.
- Ignore response, data, failure, and finish callbacks from non-active
  connections.
- Clear the active connection when the current request completes.
- Preserve the 1 MiB response bound and idempotent completion behavior.
- Extend the static baseline and documentation with active-request ownership.
- Mutation-test removal of cancellation and callback identity guards.

## Verification Completed

- Local `make check`, `make lint`, `make test`, and `make build` passed. The
  local environment did not provide `xcodebuild`, so these runs exercised the
  complete static baseline and reported the legacy hosted-Xcode boundary.
- `python3 -m py_compile scripts/check-baseline.py` and `git diff --check`
  passed.
- Hostile mutations changing the plan status, inserting an unfinished-work
  marker, falsifying a run ID, removing replacement cancellation, or removing
  a stale callback identity guard were rejected.
- The implementation push Check run `27395635063` completed successfully for
  commit `ffd99e770c2fcf3923af8a527b60c3f58274b52a`.
- The implementation pull-request Check run `27395639989` completed
  successfully for commit `ffd99e770c2fcf3923af8a527b60c3f58274b52a` and
  parsed the legacy Xcode project on hosted macOS.
- The post-merge push Check run `27395656424` completed successfully for
  commit `5a179a2125db621355b8a9e062a9de20d1ac875d`.
- The CodeQL setup run `27402323954` completed successfully for commit
  `5a179a2125db621355b8a9e062a9de20d1ac875d`.
- Request ownership preserves `activeConnection?.cancel()` before replacement,
  and all four delegate callbacks preserve
  `if !isActiveConnection(connection)` before mutating request state.
