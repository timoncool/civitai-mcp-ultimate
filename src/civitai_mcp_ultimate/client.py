"""Async HTTP client for Civitai REST API v1.

Uses Bearer token auth (not query param) for security.
Includes retry with backoff for rate limits (429).
"""

import logging
import os
import re
from typing import Any
from urllib.parse import urlencode

import httpx

logger = logging.getLogger(__name__)

API_BASE = "https://civitai.com/api/v1"
TIMEOUT = 30.0
MAX_RETRIES = 3


def _sanitize_query(query: str | None) -> str | None:
    """Sanitize search query — remove chars that break Civitai API text search.

    Civitai API text search fails on: | () [] {}
    Learned from Yi-luo-hua/civitai-mcp-server analysis.
    """
    if not query:
        return query
    return re.sub(r"[|()\[\]{}]", " ", query).strip()


class CivitaiClient:
    """Async client for Civitai REST API v1."""

    def __init__(self, api_key: str | None = None):
        self.api_key = api_key or os.getenv("CIVITAI_API_KEY", "")
        self._client: httpx.AsyncClient | None = None

    async def _get_client(self) -> httpx.AsyncClient:
        if self._client is None or self._client.is_closed:
            headers = {"User-Agent": "civitai-mcp-ultimate/0.1.0"}
            if self.api_key:
                headers["Authorization"] = f"Bearer {self.api_key}"
            self._client = httpx.AsyncClient(
                timeout=TIMEOUT,
                headers=headers,
                follow_redirects=True,
            )
        return self._client

    async def close(self):
        if self._client and not self._client.is_closed:
            await self._client.aclose()

    async def get(self, endpoint: str, params: dict[str, Any] | None = None) -> dict[str, Any]:
        """Make GET request to Civitai API with retry on 429."""
        client = await self._get_client()
        url = f"{API_BASE}/{endpoint.lstrip('/')}"

        # Filter None values and build query string
        if params:
            clean_params: dict[str, Any] = {}
            for k, v in params.items():
                if v is None:
                    continue
                if isinstance(v, bool):
                    clean_params[k] = str(v).lower()
                elif isinstance(v, list):
                    # Civitai API expects repeated params: types=LORA&types=Checkpoint
                    for item in v:
                        clean_params.setdefault(k, [])
                        if isinstance(clean_params[k], list):
                            clean_params[k].append(str(item))
                        else:
                            clean_params[k] = [clean_params[k], str(item)]
                else:
                    clean_params[k] = v

            if clean_params:
                query_parts = []
                for k, v in clean_params.items():
                    if isinstance(v, list):
                        for item in v:
                            query_parts.append(f"{k}={urlencode_value(item)}")
                    else:
                        query_parts.append(f"{k}={urlencode_value(v)}")
                url = f"{url}?{'&'.join(query_parts)}"

        import asyncio

        for attempt in range(MAX_RETRIES):
            try:
                response = await client.get(url)

                if response.status_code == 429:
                    wait = 2 ** (attempt + 1)
                    logger.warning(f"Rate limited (429), waiting {wait}s (attempt {attempt + 1}/{MAX_RETRIES})")
                    await asyncio.sleep(wait)
                    continue

                if response.status_code == 404:
                    return {"error": "not_found", "status": 404}

                response.raise_for_status()
                return response.json()

            except httpx.TimeoutException:
                if attempt < MAX_RETRIES - 1:
                    logger.warning(f"Timeout, retrying (attempt {attempt + 1}/{MAX_RETRIES})")
                    continue
                raise
            except httpx.HTTPStatusError as e:
                logger.error(f"HTTP error {e.response.status_code}: {e.response.text[:200]}")
                raise

        return {"error": "max_retries_exceeded"}


def urlencode_value(v: Any) -> str:
    """URL-encode a single value."""
    from urllib.parse import quote

    return quote(str(v), safe="")
