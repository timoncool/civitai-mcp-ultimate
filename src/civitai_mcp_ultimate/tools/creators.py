"""Creator and tag tools."""

from typing import Optional

import httpx

from ..client import CivitaiClient, CivitaiRateLimitError
from ..formatters import format_creator, format_tag


async def get_creators(
    client: CivitaiClient,
    query: Optional[str] = None,
    limit: int = 20,
    page: int = 1,
) -> str:
    """Browse and search model creators on Civitai.

    Returns creator usernames and their model counts.
    """
    params = {
        "query": query,
        "limit": min(limit, 200),
        "page": page,
    }
    try:
        data = await client.get("creators", params)
    except CivitaiRateLimitError:
        return "Rate limited by Civitai API. Please try again in a few seconds."
    except httpx.TimeoutException:
        return "Civitai API timed out. Please try again."
    except httpx.HTTPStatusError as e:
        return f"Civitai API error: HTTP {e.response.status_code}"
    items = data.get("items", [])
    if not items:
        return "No creators found."
    return "\n".join(format_creator(c) for c in items)


async def get_tags(
    client: CivitaiClient,
    query: Optional[str] = None,
    limit: int = 20,
    page: int = 1,
) -> str:
    """Browse and search model tags on Civitai.

    Returns tag names and model counts. Use tags in search_models filter.
    """
    params = {
        "query": query,
        "limit": min(limit, 200),
        "page": page,
    }
    try:
        data = await client.get("tags", params)
    except CivitaiRateLimitError:
        return "Rate limited by Civitai API. Please try again in a few seconds."
    except httpx.TimeoutException:
        return "Civitai API timed out. Please try again."
    except httpx.HTTPStatusError as e:
        return f"Civitai API error: HTTP {e.response.status_code}"
    items = data.get("items", [])
    if not items:
        return "No tags found."
    return "\n".join(format_tag(t) for t in items)
