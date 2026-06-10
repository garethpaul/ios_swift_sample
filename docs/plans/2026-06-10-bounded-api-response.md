# Bounded API Response

status: completed

## Problem

The iTunes search client accepts every URL response and appends response bytes
without a size limit before JSON parsing. Rejected or canceled connections can
also reach more than one delegate completion path.

## Scope

- Accept only successful HTTP responses with JSON-compatible MIME types.
- Reject declared and streamed response bodies larger than 1 MiB.
- Cancel rejected connections and clear retained bytes.
- Make result delivery idempotent for each request.
- Add focused response-validation and size-boundary assertions.
- Keep live API calls, artwork downloads, signing, and simulator interaction out
  of CI.

## Verification

- `make lint`
- `make test`
- `make build`
- `make check`
- mutation checks for response-size and idempotent-completion guards
- `git diff --check`
