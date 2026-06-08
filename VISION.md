## iOS Swift Sample Vision

iOS Swift Sample is a basic Swift app that sends an HTTP request, parses JSON,
and renders the response in a table view.

The repository is useful as a compact beginner sample for networking, JSON
handling, and table rendering in an older Swift project. Project context lives
in [`README.md`](README.md).

The goal is to keep the sample clear, runnable, and focused on the request to
table-view flow.

The current focus is:

Priority:

- Preserve the `ApiController` network request and table rendering behavior
- Keep screenshot and README aligned with app behavior
- Avoid hardcoded private endpoints or credentials
- Maintain a small Xcode project structure

Next priorities:

- Add setup and endpoint configuration notes
- Modernize Swift networking and JSON parsing in a dedicated pass
- Add tests or manual checks for success, empty, and failure responses
- Clarify expected response shape in docs

Contribution rules:

- One PR = one focused networking, table view, build, or documentation change.
- Verify the table renders after API or storyboard changes.
- Keep credentials and signing files out of git.
- Document endpoint and response-shape changes.

## Security

Canonical security policy and reporting:

- [`SECURITY.md`](SECURITY.md)


Network samples should not embed private credentials or send user data to
undocumented endpoints. Use HTTPS and documented configuration for future API
work.

## What We Will Not Merge (For Now)

- Hardcoded private API keys or endpoints
- Network behavior without failure handling
- Broad Swift migration mixed with sample behavior changes
- Generated signing material

This list is a roadmap guardrail, not a permanent rule.
Strong user demand and strong technical rationale can change it.
