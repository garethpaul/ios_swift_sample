# Table Index Guard Plan

status: completed

## Context

`SearchResultsViewController` renders rows from the parsed iTunes `results` array. The table view normally asks for indexes within `tableData.count`, but stale UI state or future table changes should not read beyond the parsed result array.

## Objectives

- Check the table row index before reading `tableData`.
- Preserve optional casting for parsed result rows.
- Keep missing artwork and malformed artwork URLs as empty image states.
- Extend the static baseline so table rendering keeps the index guard.

## Verification

- `make check`
- `python3 scripts/check-baseline.py`
- `git diff --check`
