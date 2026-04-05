"""trail.py — TRAIL Protocol v2.1 (Tracking Records Across Isolated Logs)

Reference implementation for Python MCP servers.
https://github.com/timoncool/trail-spec

Usage:
    from trail import Trail

    trail = Trail("./data", server="my-mcp-server")
    await trail.append(content_id="civitai:image:12345", action="posted", requester="daily-post")
    entries, total = await trail.query(content_id="civitai:image:12345")
"""

import json
import asyncio
from pathlib import Path
from datetime import datetime, timezone
from typing import Any


class Trail:
    """TRAIL-compatible content log. Append-only JSONL."""

    FILENAME = "trail.jsonl"
    VERSION = 2

    def __init__(self, data_dir: str | Path, server: str | None = None):
        self._path = Path(data_dir) / self.FILENAME
        self._lock = asyncio.Lock()
        self._server = server
        self._path.parent.mkdir(parents=True, exist_ok=True)

    async def append(
        self,
        content_id: str,
        action: str,
        requester: str,
        details: dict[str, Any] | None = None,
        trace_id: str | None = None,
        server: str | None = None,
        entry_id: str | None = None,
        caused_by: str | None = None,
        tags: list[str] | None = None,
    ) -> dict:
        """Append an event to the trail.

        Args:
            content_id: Content ID in format source:type:id (e.g. "civitai:image:12345")
            action: Action — fetched, selected, posted, failed, skipped, delegated, evaluated, guarded, etc.
            requester: Requester — workflow or scheduler task ID
            details: Optional platform-specific details
            trace_id: Optional trace correlation ID (groups entries across servers)
            server: Optional server name (overrides constructor default)
            entry_id: Optional unique entry identifier
            caused_by: Optional entry_id of the causing entry
            tags: Optional free-form labels for filtering
        """
        entry: dict[str, Any] = {
            "version": self.VERSION,
            "timestamp": datetime.now(timezone.utc).isoformat(timespec="milliseconds").replace("+00:00", "Z"),
            "content_id": content_id,
            "action": action,
            "requester": requester,
        }
        srv = server or self._server
        if srv:
            entry["server"] = srv
        if details is not None:
            entry["details"] = details
        if trace_id:
            entry["trace_id"] = trace_id
        if entry_id:
            entry["entry_id"] = entry_id
        if caused_by:
            entry["caused_by"] = caused_by
        if tags:
            entry["tags"] = tags

        async with self._lock:
            with open(self._path, "a", encoding="utf-8") as f:
                f.write(json.dumps(entry, ensure_ascii=False) + "\n")

        return entry

    async def query(
        self,
        content_id: str | None = None,
        action: str | list[str] | None = None,
        requester: str | None = None,
        trace_id: str | None = None,
        server: str | None = None,
        tags: list[str] | None = None,
        since: str | None = None,
        limit: int = 50,
        offset: int = 0,
    ) -> tuple[list[dict], int]:
        """Query the trail with filters. Returns (entries_newest_first, total_count).

        Args:
            content_id: Filter by content ID (exact match or prefix)
            action: Filter by action (string or list of strings for multi-action filtering)
            requester: Filter by requester
            trace_id: Filter by trace ID
            server: Filter by server name
            tags: Filter entries that have ALL specified tags
            since: ISO 8601 timestamp — only return entries after this time
            limit: Max entries to return (0 = unlimited)
            offset: Number of entries to skip (for pagination)
        """
        if not self._path.exists():
            return [], 0

        action_set = {action} if isinstance(action, str) else set(action) if action else None

        entries = []
        with open(self._path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    entry = json.loads(line)
                except json.JSONDecodeError:
                    continue

                entry_cid = entry.get("content_id", "")
                if content_id and entry_cid != content_id and not (content_id.endswith(":") and entry_cid.startswith(content_id)):
                    continue
                if action_set and entry.get("action") not in action_set:
                    continue
                if requester and entry.get("requester") != requester:
                    continue
                if trace_id and entry.get("trace_id") != trace_id:
                    continue
                if server and entry.get("server") != server:
                    continue
                if tags and not all(t in entry.get("tags", []) for t in tags):
                    continue
                if since and entry.get("timestamp", "") < since:
                    continue

                entries.append(entry)

        total = len(entries)
        result = list(reversed(entries))
        if offset:
            result = result[offset:]
        if limit:
            result = result[:limit]
        return result, total

    async def stats(
        self,
        requester: str | None = None,
        since: str | None = None,
    ) -> dict:
        """Get summary statistics for the trail.

        Returns:
            Dict with total_entries, by_action, unique_content_ids, first_entry, last_entry
        """
        entries, _ = await self.query(requester=requester, since=since, limit=0)
        by_action: dict[str, int] = {}
        cids: set[str] = set()
        timestamps: list[str] = []

        for e in entries:
            act = e.get("action", "unknown")
            by_action[act] = by_action.get(act, 0) + 1
            cids.add(e.get("content_id", ""))
            timestamps.append(e.get("timestamp", ""))

        return {
            "total_entries": len(entries),
            "by_action": by_action,
            "unique_content_ids": len(cids),
            "first_entry": min(timestamps) if timestamps else None,
            "last_entry": max(timestamps) if timestamps else None,
        }

    async def is_used(self, content_id: str, requester: str | None = None) -> bool:
        """Check if content was already posted."""
        entries, _ = await self.query(
            content_id=content_id, action="posted", requester=requester, limit=1
        )
        return len(entries) > 0

    async def get_used_ids(self, requester: str | None = None) -> set[str]:
        """Get set of all posted content IDs."""
        entries, _ = await self.query(action="posted", requester=requester, limit=0)
        return {e["content_id"] for e in entries}
