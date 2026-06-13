## iOS Swift Sample Vision

This document explains the current state and direction of the project.
Project overview and developer docs: [`README.md`](README.md)

iOS Swift Sample is a basic Swift app that sends an HTTP request, parses JSON,
and renders the response in a table view.

The repository is useful as a compact beginner sample for networking, JSON
handling, and table rendering in an older Swift project. Project context lives
in [`README.md`](README.md).

The goal is to keep the sample clear, runnable, and focused on the request to
table-view flow.

Current baseline: `make lint`, `make test`, `make build`, and `make check` run
`scripts/check-baseline.py` to verify the legacy Xcode project shape, committed
plists, storyboard and asset parsing, public HTTPS iTunes endpoint usage,
URL/connection/JSON failure handling, API completion cleanup, main thread UI
result handling, network activity indicator lifecycle, optional table rendering,
result array tests, async artwork loading, credential guardrails, and
documentation.
GitHub Actions runs the same static baseline with Python 3.12 for pushes and
pull requests.

The current focus is:

Priority:

- Preserve the `ApiController` network request and table rendering behavior
- Keep malformed URLs, failed connections, invalid JSON, missing results, and
  missing artwork from crashing the sample
- Clear the retained response buffer after parsed or empty API completion
- Bound successful JSON-compatible API responses to 1 MiB and one completion
- Keep shared response state owned by one active connection and ignore stale callbacks
- Keep API result UI updates on the main thread
- Clear the network activity indicator when the results view disappears
- Guard table indexes before reading parsed result rows
- Keep result array tests covering accepted payloads and malformed payloads that
  clear stale table data
- Keep async artwork loading off the main thread and guarded against cell reuse
- Keep artwork result identity aligned with the current API row after reloads
- Keep bounded artwork responses limited to successful JPEG or PNG bodies of
  at most 1 MiB and one completion
- Keep artwork loading restricted to HTTPS `mzstatic.com` URLs from the iTunes response
- Keep artwork URL tests covering allowed hosts and rejected schemes/hosts
- Keep screenshot and README aligned with app behavior
- Avoid hardcoded private endpoints or credentials
- Keep `make lint`, `make test`, `make build`, and `make check` available as
  local verification gates
- Keep hosted project validation pinned and read-only on macOS through
  `SwiftExample.xcodeproj` parsing and `make check`
- Maintain a small Xcode project structure

Next priorities:

- Add setup and endpoint configuration notes
- Modernize Swift networking and JSON parsing in a dedicated pass
- Add tests or manual checks for success, empty, and failure responses
- Clarify expected response shape in docs

Contribution rules:

- One PR = one focused networking, table view, build, or documentation change.
- Verify the table renders after API or storyboard changes.
- Run `make lint`, `make test`, `make build`, and `make check` before pushing
  source, plist, storyboard, asset, Xcode project, or security documentation
  changes.
- Keep credentials and signing files out of git.
- Document endpoint and response-shape changes.
- Keep parsed artwork URL host and scheme boundaries explicit.

## Security

Canonical security policy and reporting:

- [`SECURITY.md`](SECURITY.md)

Network samples should not embed private credentials or send user data to
undocumented endpoints. Use HTTPS and documented configuration for future API
work. Keep failure handling explicit and avoid logging private data.

## What We Will Not Merge (For Now)

- Hardcoded private API keys or endpoints
- Network behavior without failure handling
- Broad Swift migration mixed with sample behavior changes
- Generated signing material

This list is a roadmap guardrail, not a permanent rule.
Strong user demand and strong technical rationale can change it.
