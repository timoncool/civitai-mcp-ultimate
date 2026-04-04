"""Image-related MCP tools — browse, search, get prompts."""

import logging
from typing import Optional

import httpx

from ..client import CivitaiClient, CivitaiNotFoundError, CivitaiRateLimitError
from ..formatters import format_image, format_image_list
from ..history import get_used_image_ids, record_images_batch
from ..image_cache import download_images
from ..types import parse_browsing_level

logger = logging.getLogger(__name__)


async def _resolve_model_version_ids(client: CivitaiClient, model_id: int) -> list[int]:
    """Resolve model_id to list of version IDs via API.

    Civitai /images endpoint ignores modelId param — only modelVersionId works.
    So we fetch the model first to get its version IDs.
    Returns version IDs ordered newest-first (same as Civitai API).
    """
    try:
        data = await client.get(f"models/{model_id}")
        versions = data.get("modelVersions", [])
        return [v["id"] for v in versions if v.get("id")]
    except Exception as e:
        logger.warning(f"Failed to resolve version IDs for model {model_id}: {e}")
        return []


async def _format_with_downloads(
    images: list[dict],
    include_prompts: bool = True,
) -> str:
    """Format images + download them to cache, append local paths."""
    result = format_image_list(images, include_prompts=include_prompts)

    # Download in background, attach local paths
    cached = await download_images(images)
    if cached:
        result += "\n\n---\n**Cached previews** (use Read tool to view):\n"
        for img_id, path in cached.items():
            result += f"- Image {img_id}: `{path}`\n"

    return result


async def browse_images(
    client: CivitaiClient,
    model_id: Optional[int] = None,
    model_version_id: Optional[int] = None,
    post_id: Optional[int] = None,
    username: Optional[str] = None,
    nsfw: Optional[str] = None,
    sort: str = "Most Reactions",
    period: str = "Month",
    limit: int = 10,
    page: Optional[int] = None,
    content_type: Optional[str] = None,
    browsing_level: Optional[str] = None,
    tag: Optional[str] = None,
    base_model: Optional[str] = None,
    tools: Optional[str] = None,
    techniques: Optional[str] = None,
    has_meta: Optional[bool] = None,
    made_on_site: Optional[bool] = None,
    originals_only: Optional[bool] = None,
    remixes_only: Optional[bool] = None,
    exclude_used: Optional[bool] = None,
    requester: Optional[str] = None,
) -> str:
    """Browse AI-generated images/videos on Civitai.

    Filters: model, creator, post, NSFW level, tag, base model, tools, techniques.
    Sort: Most Reactions, Most Comments, Most Collected, Newest, Oldest.
    content_type: "image" or "video".
    browsing_level: "PG", "PG-13", "R", "X", "XXX" (comma-separated for multiple).
    tag: filter by tag (e.g. "anime", "animal", "architecture").
    base_model: filter by base model (e.g. "Flux.1 D", "SDXL 1.0").
    tools: filter by tool used (e.g. "ComfyUI", "Automatic1111").
    techniques: filter by technique (e.g. "txt2img", "img2img").
    has_meta: true = only images with generation metadata.
    made_on_site: true = only images generated on Civitai.
    originals_only: true = exclude remixes.
    remixes_only: true = only remixes.
    """
    # Civitai /images API ignores modelId — only modelVersionId works.
    # Auto-resolve model_id to version IDs when modelVersionId not provided.
    resolved_version_id = model_version_id
    if model_id and not model_version_id:
        version_ids = await _resolve_model_version_ids(client, model_id)
        if version_ids:
            # Use the latest (first) version
            resolved_version_id = version_ids[0]
            logger.info(f"Resolved model {model_id} -> version {resolved_version_id}")
        else:
            logger.warning(f"Could not resolve model {model_id} to version ID, modelId filter may not work")

    params: dict = {
        "modelVersionId": resolved_version_id,
        "postId": post_id,
        "username": username,
        "nsfw": nsfw,
        "sort": sort,
        "period": period,
        "limit": min(limit, 200),
        "page": page,
    }
    # Undocumented but working params (verified 2026-03-24)
    if content_type:
        params["type"] = content_type.lower().strip()
    if browsing_level:
        params["browsingLevel"] = parse_browsing_level(browsing_level)
    if tag:
        params["tag"] = tag
    if base_model:
        params["baseModel"] = base_model
    if tools:
        params["tools"] = tools
    if techniques:
        params["techniques"] = techniques
    if has_meta is not None:
        params["hasMeta"] = has_meta
    if made_on_site is not None:
        params["madeOnSite"] = made_on_site
    if originals_only is not None:
        params["originalsOnly"] = originals_only
    if remixes_only is not None:
        params["remixesOnly"] = remixes_only

    try:
        data = await client.get("images", params)
    except CivitaiRateLimitError:
        return "Rate limited by Civitai API. Please try again in a few seconds."
    except CivitaiNotFoundError:
        return "Civitai images endpoint not found."
    except httpx.TimeoutException:
        return "Civitai API timed out. Please try again."
    except httpx.HTTPStatusError as e:
        return f"Civitai API error: HTTP {e.response.status_code}"
    items = data.get("items", [])
    if not items:
        ct_label = content_type or "content"
        return f"No {ct_label} found with these filters."

    # Filter out already-used images/videos if requested
    skipped = 0
    if exclude_used:
        used_ids = get_used_image_ids()
        original_count = len(items)
        items = [img for img in items if img.get("id") not in used_ids]
        skipped = original_count - len(items)
        if not items:
            return f"All {original_count} results were already used. Try different filters or set exclude_used=false."

    # Record browsed images/videos in history
    image_ids = [img["id"] for img in items if img.get("id")]
    action = f"browsed_for:{requester}" if requester else "browsed"
    record_images_batch(image_ids, action=action)

    result = await _format_with_downloads(items, include_prompts=True)

    if skipped:
        result = f"**Filtered out {skipped} already-used items.**\n\n" + result

    # Surface cursor for pagination
    meta = data.get("metadata", {})
    if meta.get("nextCursor"):
        result += f"\n\n---\n_Next cursor: {meta['nextCursor']}_"
    return result


async def get_top_images(
    client: CivitaiClient,
    sort: str = "Most Reactions",
    period: str = "Month",
    nsfw: Optional[str] = None,
    limit: int = 10,
    content_type: Optional[str] = None,
    browsing_level: Optional[str] = None,
    tag: Optional[str] = None,
    base_model: Optional[str] = None,
    tools: Optional[str] = None,
    techniques: Optional[str] = None,
    has_meta: Optional[bool] = None,
    made_on_site: Optional[bool] = None,
    originals_only: Optional[bool] = None,
    remixes_only: Optional[bool] = None,
    exclude_used: Optional[bool] = None,
    requester: Optional[str] = None,
) -> str:
    """Get top images/videos from Civitai — best for finding great prompts.

    Sort: Most Reactions, Most Comments, Most Collected, Newest, Oldest.
    Period: Day, Week, Month, Year, AllTime.
    content_type: "image" or "video".
    browsing_level: "PG", "PG-13", "R", "X", "XXX" (comma-separated).
    tag/base_model/tools/techniques: additional filters.
    has_meta/made_on_site/originals_only/remixes_only: boolean modifiers.
    exclude_used: true = skip images/videos already in history.
    requester: who requested this (e.g. "pikabu", "telegram", "scheduled:daily-post").
    """
    return await browse_images(
        client,
        sort=sort,
        period=period,
        nsfw=nsfw,
        limit=limit,
        content_type=content_type,
        browsing_level=browsing_level,
        tag=tag,
        base_model=base_model,
        tools=tools,
        techniques=techniques,
        has_meta=has_meta,
        made_on_site=made_on_site,
        originals_only=originals_only,
        remixes_only=remixes_only,
        exclude_used=exclude_used,
        requester=requester,
    )


async def get_model_images(
    client: CivitaiClient,
    model_id: int,
    limit: int = 5,
    exclude_used: Optional[bool] = None,
    requester: Optional[str] = None,
) -> str:
    """Get example images generated with a specific model.

    exclude_used: true = skip images/videos already in history.
    requester: who requested this (e.g. "pikabu", "telegram").
    """
    return await browse_images(
        client,
        model_id=model_id,
        sort="Most Reactions",
        period="AllTime",
        limit=limit,
        exclude_used=exclude_used,
        requester=requester,
    )


async def get_image_generation_data(
    client: CivitaiClient,
    model_id: int,
    sort: str = "Most Reactions",
    limit: int = 3,
    exclude_used: Optional[bool] = None,
    requester: Optional[str] = None,
) -> str:
    """Get full generation parameters from top images of a model.

    exclude_used: true = skip images/videos already in history.
    requester: who requested this (e.g. "pikabu", "telegram").
    """
    return await browse_images(
        client,
        model_id=model_id,
        sort=sort,
        period="AllTime",
        limit=limit,
        has_meta=True,
        exclude_used=exclude_used,
        requester=requester,
    )
