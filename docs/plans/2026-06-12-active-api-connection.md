# Active API Connection

status: completed

## Context

`APIController` stores one response buffer, accepted-response flag, and
completion flag, but does not retain the `NSURLConnection` that owns that
state. Starting another search before the first request finishes can allow old
callbacks to append to or complete the new request.

## Completed Scope

- Retain the active connection and cancel it before starting a new search.
- Ignore response, data, failure, and finish callbacks from non-active
  connections.
- Clear the active connection when the current request completes.
- Preserve the 1 MiB response bound and idempotent completion behavior.
- Extend the static baseline and documentation with active-request ownership.
- Mutation-test removal of cancellation and callback identity guards.

## Verification

- `make lint`
- `make test`
- `make build`
- `make check`
- `python3 -m py_compile scripts/check-baseline.py`
- `git diff --check`
- Mutation results: removing replacement cancellation or one stale callback
  identity guard was rejected by `scripts/check-baseline.py`.
