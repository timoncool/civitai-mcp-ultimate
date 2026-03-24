"""Image-related MCP tools — browse, search, get prompts."""

from typing import Optional

import httpx

from ..client import CivitaiClient, CivitaiNotFoundError, CivitaiRateLimitError
from ..formatters import format_image, format_image_list


async def browse_images(
    client: CivitaiClient,
    model_id: Optional[int] = None,
    model_version_id: Optional[int] = None,
    username: Optional[str] = None,
    nsfw: Optional[str] = None,
    sort: str = "Most Reactions",
    period: str = "Month",
    limit: int = 10,
    page: Optional[int] = None,
) -> str:
    """Browse AI-generated images on Civitai.

    Filter by model, creator, NSFW level. Sort by reactions, comments, or date.
    Returns images with URLs, stats, and generation parameters (prompts).
    """
    params: dict = {
        "modelId": model_id,
        "modelVersionId": model_version_id,
        "username": username,
        "nsfw": nsfw,
        "sort": sort,
        "period": period,
        "limit": min(limit, 200),
        "page": page,
    }
    try:
        data = await client.get("images", params)
    except CivitaiRateLimitError:
        return "Rate limited by Civitai API. Please try again in a few seconds."
    except CivitaiNotFoundError:
        return "Civitai images endpoint not found."
    except httpx.TimeoutException:
        return "Civitai API timed out. Please try again."
    items = data.get("items", [])
    if not items:
        return "No images found with these filters."
    return format_image_list(items, include_prompts=True)


async def get_top_images(
    client: CivitaiClient,
    sort: str = "Most Reactions",
    period: str = "Month",
    nsfw: Optional[str] = None,
    limit: int = 10,
) -> str:
    """Get top images from Civitai by reactions, comments, or collections.

    Perfect for finding the best prompts and generation parameters.
    Sort options: Most Reactions, Most Comments, Most Collected, Newest, Oldest.
    Period: Day, Week, Month, Year, AllTime.
    """
    return await browse_images(
        client,
        sort=sort,
        period=period,
        nsfw=nsfw,
        limit=limit,
    )


async def get_model_images(
    client: CivitaiClient,
    model_id: int,
    limit: int = 5,
) -> str:
    """Get example images generated with a specific model.

    Returns images with full generation parameters: prompt, negative prompt,
    steps, CFG, sampler, seed, and LoRAs used. Great for learning how to
    use a model effectively.
    """
    return await browse_images(
        client,
        model_id=model_id,
        sort="Most Reactions",
        period="AllTime",
        limit=limit,
    )


async def get_image_generation_data(
    client: CivitaiClient,
    model_id: int,
    sort: str = "Most Reactions",
    limit: int = 3,
) -> str:
    """Get full generation parameters from top images of a model.

    Focused on extracting the best prompts, settings, and LoRA combinations
    used by the community. Use this to learn optimal generation parameters.
    """
    params = {
        "modelId": model_id,
        "sort": sort,
        "period": "AllTime",
        "limit": min(limit, 20),
    }
    try:
        data = await client.get("images", params)
    except CivitaiRateLimitError:
        return "Rate limited by Civitai API. Please try again in a few seconds."
    except CivitaiNotFoundError:
        return "Civitai images endpoint not found."
    except httpx.TimeoutException:
        return "Civitai API timed out. Please try again."
    items = data.get("items", [])
    if not items:
        return f"No images found for model {model_id}"

    # Only include images that have generation metadata
    with_meta = [img for img in items if img.get("meta")]
    if not with_meta:
        return f"Found {len(items)} images but none have generation metadata."

    return format_image_list(with_meta, include_prompts=True)
