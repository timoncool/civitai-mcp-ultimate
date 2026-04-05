# TRAIL Support

This MCP server implements the [TRAIL protocol](https://github.com/timoncool/trail-spec) (Tracking Records Across Isolated Logs) for cross-MCP content tracking.

## Conformance Level: Standard

## Tools
- `get_trail` — query the content log
- `mark_trail` — write entries explicitly
- `get_trail_stats` — summary statistics

## Auto-logging
The `browse_images`, `get_top_images`, and `mark_as_used` tools integrate with TRAIL when `requester` is provided.
