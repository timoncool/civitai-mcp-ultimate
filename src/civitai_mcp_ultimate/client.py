"""Async HTTP client for Civitai REST API v1.

Uses Bearer token auth (not query param) for security.
Includes retry with backoff for rate limits (429).
"""

import asyncio
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


class CivitaiError(Exception):
    """Base exception for Civitai API errors."""


class CivitaiRateLimitError(CivitaiError):
    """Raised when rate limit is exhausted after all retries."""


class CivitaiNotFoundError(CivitaiError):
    """Raised when a resource is not found (404)."""


def _strip_invisible(text: str) -> str:
    """Strip zero-width and invisible Unicode characters that break Windows terminals."""
    return re.sub(r"[\u200b\u200c\u200d\u200e\u200f\ufeff\u2060\u2028\u2029]", "", text)


def _sanitize_response(obj: Any) -> Any:
    """Recursively strip invisible chars from all strings in API response."""
    if isinstance(obj, str):
        return _strip_invisible(obj)
    if isinstance(obj, dict):
        return {k: _sanitize_response(v) for k, v in obj.items()}
    if isinstance(obj, list):
        return [_sanitize_response(item) for item in obj]
    return obj


def _sanitize_query(query: str | None) -> str | None:
    """Sanitize search query — remove chars that break Civitai API text search.

    Civitai API text search fails on: | () [] {}
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
        """Make GET request to Civitai API with retry on 429.

        Raises:
            CivitaiNotFoundError: if 404
            CivitaiRateLimitError: if 429 after all retries
            httpx.HTTPStatusError: on other HTTP errors
            httpx.TimeoutException: on timeout after all retries
        """
        client = await self._get_client()
        url = f"{API_BASE}/{endpoint.lstrip('/')}"

        # Build query string using stdlib urlencode with doseq=True
        if params:
            clean_params: dict[str, Any] = {}
            for k, v in params.items():
                if v is None:
                    continue
                if isinstance(v, bool):
                    clean_params[k] = str(v).lower()
                elif isinstance(v, list):
                    clean_params[k] = [str(item) for item in v]
                else:
                    clean_params[k] = str(v)

            if clean_params:
                url = f"{url}?{urlencode(clean_params, doseq=True)}"

        for attempt in range(MAX_RETRIES):
            try:
                response = await client.get(url)

                if response.status_code == 429:
                    if attempt < MAX_RETRIES - 1:
                        wait = 2 ** (attempt + 1)
                        logger.warning(f"Rate limited (429), waiting {wait}s (attempt {attempt + 1}/{MAX_RETRIES})")
                        await asyncio.sleep(wait)
                        continue
                    raise CivitaiRateLimitError(
                        f"Rate limited after {MAX_RETRIES} retries. Try again later."
                    )

                if response.status_code == 404:
                    raise CivitaiNotFoundError(f"Not found: {endpoint}")

                response.raise_for_status()
                return _sanitize_response(response.json())

            except httpx.TimeoutException:
                if attempt < MAX_RETRIES - 1:
                    logger.warning(f"Timeout, retrying (attempt {attempt + 1}/{MAX_RETRIES})")
                    continue
                raise
            except (CivitaiNotFoundError, CivitaiRateLimitError):
                raise
            except httpx.HTTPStatusError as e:
                logger.error(f"HTTP error {e.response.status_code}: {e.response.text[:200]}")
                raise

        raise CivitaiRateLimitError(f"Exhausted {MAX_RETRIES} retries")
