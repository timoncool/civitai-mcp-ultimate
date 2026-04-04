"""Meilisearch client for Civitai model search.

Civitai's REST API /v1/models?query=... is broken since May 2025 (issue #1729).
The site and all extensions (gallery-dl, ComfyUI nodes) use Meilisearch instead.
Public search-only key — no auth needed beyond the Bearer token.
"""

import asyncio
import logging
import os
from typing import Any, Optional

import httpx

logger = logging.getLogger(__name__)

MEILISEARCH_URL = "https://search-new.civitai.com/multi-search"
MEILISEARCH_INDEX = "models_v9"
MEILISEARCH_DEFAULT_KEY = "8c46eb2508e21db1e9828a97968d91ab1ca1caa5f70a00e88a2ba1e286603b61"
TIMEOUT = 15.0

# Sortable attributes (verified 2026-03-24)
SORT_MAP: dict[str, str] = {
    "Most Downloaded": "metrics.downloadCount:desc",
    "Highest Rated": "metrics.thumbsUpCount:desc",
    "Most Collected": "metrics.collectedCount:desc",
    "Most Comments": "metrics.commentCount:desc",
    "Most Tipped": "metrics.tippedAmountCount:desc",
    "Newest": "createdAt:desc",
    "Oldest": "createdAt:asc",
}

# Fields we actually need (skip cosmetics, hashes, etc.)
ATTRIBUTES_TO_RETRIEVE = [
    "id", "name", "type", "nsfw", "nsfwLevel", "status",
    "metrics", "user", "triggerWords", "tags", "category",
    "version", "createdAt", "lastVersionAt", "mode",
    "checkpointType", "availability",
]


def _escape_meili(value: str) -> str:
    """Escape double quotes in Meilisearch filter values."""
    return value.replace('\\', '\\\\').replace('"', '\\"')


class MeilisearchError(Exception):
    """Meilisearch search error."""


class MeilisearchClient:
    """Async client for Civitai Meilisearch."""

    def __init__(self, api_key: str | None = None):
        self.api_key = api_key or os.getenv("MEILISEARCH_KEY", MEILISEARCH_DEFAULT_KEY)
        self._client: httpx.AsyncClient | None = None
        self._lock = asyncio.Lock()

    async def _get_client(self) -> httpx.AsyncClient:
        async with self._lock:
            if self._client is None or self._client.is_closed:
                self._client = httpx.AsyncClient(
                    timeout=TIMEOUT,
                    headers={
                        "Authorization": f"Bearer {self.api_key}",
                        "Content-Type": "application/json",
                        "User-Agent": "civitai-mcp-ultimate/0.3.0",
                    },
                )
            return self._client

    async def close(self):
        if self._client and not self._client.is_closed:
            await self._client.aclose()

    async def search(
        self,
        query: str,
        types: Optional[list[str]] = None,
        base_model: Optional[str] = None,
        tag: Optional[str] = None,
        username: Optional[str] = None,
        sort: str = "Most Downloaded",
        nsfw: Optional[bool] = None,
        limit: int = 20,
        offset: int = 0,
    ) -> dict[str, Any]:
        """Search models via Meilisearch.

        Returns dict with 'hits', 'query', 'estimatedTotalHits', 'processingTimeMs'.
        """
        # Build filter parts
        filters: list[str] = []
        if types:
            if len(types) == 1:
                filters.append(f'type = "{_escape_meili(types[0])}"')
            else:
                parts = " OR ".join(f'type = "{_escape_meili(t)}"' for t in types)
                filters.append(f"({parts})")
        if base_model:
            filters.append(f'version.baseModel = "{_escape_meili(base_model)}"')
        if tag:
            filters.append(f'tags.name = "{_escape_meili(tag.lower())}"')
        if username:
            filters.append(f'user.username = "{_escape_meili(username)}"')
        if nsfw is False:
            filters.append("nsfwLevel = 1")

        # Build sort
        sort_field = SORT_MAP.get(sort, "metrics.downloadCount:desc")

        body: dict[str, Any] = {
            "q": query,
            "indexUid": MEILISEARCH_INDEX,
            "limit": min(limit, 100),
            "offset": offset,
            "sort": [sort_field],
            "attributesToRetrieve": ATTRIBUTES_TO_RETRIEVE,
        }
        if filters:
            body["filter"] = " AND ".join(filters)

        client = await self._get_client()
        try:
            response = await client.post(MEILISEARCH_URL, json={"queries": [body]})
            response.raise_for_status()
            data = response.json()
            return data["results"][0]
        except httpx.TimeoutException:
            raise MeilisearchError("Meilisearch timed out")
        except httpx.HTTPStatusError as e:
            raise MeilisearchError(f"Meilisearch HTTP {e.response.status_code}: {e.response.text[:200]}")
        except (KeyError, IndexError) as e:
            raise MeilisearchError(f"Unexpected Meilisearch response: {e}")


def format_meilisearch_hit(hit: dict[str, Any]) -> str:
    """Format a Meilisearch hit as a compact model card (same style as REST API)."""
    metrics = hit.get("metrics", {})
    user = hit.get("user", {})
    version = hit.get("version", {})
    tags = hit.get("tags", [])

    dl = metrics.get("downloadCount", 0)
    thumbs = metrics.get("thumbsUpCount", 0)
    base_model = version.get("baseModel", "?") if version else "?"

    lines = [
        f"**{hit.get('name', '?')}** (ID: {hit.get('id', '?')}) — {hit.get('type', '?')}",
        f"  Creator: {user.get('username', '?')} | "
        f"Base Model: {base_model} | "
        f"Downloads: {dl:,} | Thumbs: {thumbs:,}",
    ]

    # Trigger words
    trigger_words = hit.get("triggerWords")
    if not trigger_words and version:
        trigger_words = version.get("trainedWords")
    if trigger_words:
        words = ", ".join(str(w).strip() for w in trigger_words[:5])
        lines.append(f"  Trigger: {words}")

    # Tags (top 5)
    if tags:
        tag_names = [t["name"] for t in tags[:5]] if isinstance(tags[0], dict) else tags[:5]
        lines.append(f"  Tags: {', '.join(tag_names)}")

    return "\n".join(lines)


def format_meilisearch_results(result: dict[str, Any]) -> str:
    """Format Meilisearch search results as markdown."""
    hits = result.get("hits", [])
    if not hits:
        return f"No models found for query '{result.get('query', '?')}'"

    cards = [format_meilisearch_hit(hit) for hit in hits]
    total = result.get("estimatedTotalHits", "?")
    ms = result.get("processingTimeMs", "?")

    output = "\n\n---\n\n".join(cards)
    output += f"\n\n---\n_Meilisearch | {total} total | {ms}ms_"
    return output
