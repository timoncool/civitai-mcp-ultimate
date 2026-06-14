"""Creator and tag tools."""

from typing import Optional

import httpx

from ..client import CivitaiClient, CivitaiError, CivitaiRateLimitError
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
    except CivitaiError as e:
        return f"Civitai API error: {e}"
    except httpx.HTTPStatusError as e:
        return f"Civitai API error: HTTP {e.response.status_code}"
    items = data.get("items", [])
    if not items:
        return "No creators found."
    return "\n".join(format_creator(c) for c in items)


async def lookup_users(
    client: CivitaiClient,
    ids: Optional[list[int]] = None,
    query: Optional[str] = None,
    limit: int = 20,
) -> str:
    """Look up Civitai users by ID or username prefix.

    Provide `ids` to resolve specific user IDs, or `query` for username prefix search.
    Without either, returns the first 20 users (not recommended).
    """
    params: dict = {}
    if ids:
        params["ids"] = ",".join(str(i) for i in ids)
    if query:
        params["query"] = query
    params["limit"] = min(limit, 100)

    try:
        data = await client.get("users", params)
    except CivitaiRateLimitError:
        return "Rate limited by Civitai API. Please try again in a few seconds."
    except httpx.TimeoutException:
        return "Civitai API timed out. Please try again."
    except CivitaiError as e:
        return f"Civitai API error: {e}"
    except httpx.HTTPStatusError as e:
        return f"Civitai API error: HTTP {e.response.status_code}"

    items = data.get("items", data) if isinstance(data, dict) else data
    if not items:
        return "No users found."

    lines = []
    for u in items:
        nsfw = u.get("avatarNsfw", "None")
        lines.append(f"**{u.get('username', '?')}** (ID: {u.get('id', '?')}) — avatar NSFW: {nsfw}")
    return "\n".join(lines)


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
    except CivitaiError as e:
        return f"Civitai API error: {e}"
    except httpx.HTTPStatusError as e:
        return f"Civitai API error: HTTP {e.response.status_code}"
    items = data.get("items", [])
    if not items:
        return "No tags found."
    return "\n".join(format_tag(t) for t in items)
