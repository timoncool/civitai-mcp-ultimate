"""Creator and tag tools."""

from typing import Optional

from ..client import CivitaiClient
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
    data = await client.get("creators", params)
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
    data = await client.get("tags", params)
    items = data.get("items", [])
    if not items:
        return "No tags found."
    return "\n".join(format_tag(t) for t in items)
