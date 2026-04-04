"""Civitai MCP Ultimate — FastMCP server with all tools.

Usage:
    claude mcp add civitai-mcp-ultimate -- uvx civitai-mcp-ultimate

Environment:
    CIVITAI_API_KEY — your Civitai API key (required for NSFW + higher rate limits)
    CIVITAI_MCP_LANG — output language: en (default) | ru
    COMFYUI_MODELS_PATH — path to ComfyUI models dir (for download_info)
    MEILISEARCH_KEY — Meilisearch API key (optional, has default public key)
"""

from contextlib import asynccontextmanager
from typing import Optional

from fastmcp import FastMCP

from .client import CivitaiClient
from .types import BaseModel_, ImageSort, ModelSort, ModelType, NsfwLevel, Period

client = CivitaiClient()


@asynccontextmanager
async def lifespan(server):
    """Manage client lifecycle + cache cleanup."""
    from .image_cache import cleanup_cache

    cleanup_cache()
    yield
    await client.close()
    # Close Meilisearch client if it was initialized
    from .tools.models import _meili
    if _meili:
        await _meili.close()


mcp = FastMCP(
    name="civitai-mcp-ultimate",
    instructions=(
        "Ultimate MCP server for Civitai — search models, browse top images/videos with prompts, "
        "download LoRAs/Checkpoints, analyze trends.\n\n"
        "IMPORTANT — Usage History:\n"
        "- All browsed images/videos and downloaded models are automatically recorded in history.\n"
        "- When fetching content for publishing (Pikabu, Telegram, etc.), ALWAYS set exclude_used=true "
        "and requester='pikabu'/'telegram'/etc. to avoid duplicate posts.\n"
        "- After successfully publishing content, call mark_as_used with the image IDs and requester.\n"
        "- Use get_history to check what was already used before starting a publishing workflow.\n"
        "- History is persistent across sessions (stored in data/history.json)."
    ),
    lifespan=lifespan,
)


# ═══════════════════════════════════════════════════════════════
# MODEL TOOLS
# ═══════════════════════════════════════════════════════════════


@mcp.tool
async def search_models(
    query: Optional[str] = None,
    types: Optional[list[str]] = None,
    base_model: Optional[str] = None,
    tag: Optional[str] = None,
    username: Optional[str] = None,
    sort: str = "Most Downloaded",
    period: str = "AllTime",
    nsfw: Optional[bool] = None,
    limit: int = 20,
    page: int = 1,
    ids: Optional[list[int]] = None,
    favorites: Optional[bool] = None,
    hidden: Optional[bool] = None,
    primary_file_only: Optional[bool] = None,
    allow_commercial_use: Optional[list[str]] = None,
    supports_generation: Optional[bool] = None,
    allow_no_credit: Optional[bool] = None,
    allow_derivatives: Optional[bool] = None,
    allow_different_licenses: Optional[bool] = None,
) -> str:
    """Search for AI models on Civitai with flexible filters.

    Uses Meilisearch for text queries (fast, accurate results).
    Falls back to REST API for filter-only queries, batch IDs, favorites, etc.

    Find checkpoints, LoRAs, ControlNets and more.
    Types: Checkpoint, LORA, LoCon, TextualInversion, Hypernetwork, Controlnet, Poses, VAE, Upscaler, Wildcards, MotionModule, Workflows, Other.
    Base models: SD 1.5, SDXL 1.0, Flux.1 D, Flux.2 D, Pony, Illustrious, NoobAI, Hunyuan 1, Kolors, Chroma, ZImageBase, etc.
    Sort: Highest Rated, Most Downloaded, Most Collected, Most Comments, Most Tipped, Newest.
    Period: AllTime, Year, Month, Week, Day (REST API only).
    Commercial use filter: None, Image, Rent, RentCivit, Sell (REST API only).

    Tips: text search works best via Meilisearch. Use get_model if you know the ID.
    Set favorites=true or hidden=true to filter your own models (requires API key, REST API).
    Set ids to fetch specific models by ID in batch (REST API).
    """
    from .tools.models import search_models as _search

    return await _search(
        client, query, types, base_model, tag, username, sort, period, nsfw, limit, page,
        ids, favorites, hidden, primary_file_only, allow_commercial_use, supports_generation,
        allow_no_credit, allow_derivatives, allow_different_licenses,
    )


@mcp.tool
async def get_model(model_id: int) -> str:
    """Get detailed info about a specific model by ID.

    Returns: description, all versions, files, trigger words, stats, creator, tags, download URLs.
    """
    from .tools.models import get_model as _get

    return await _get(client, model_id)


@mcp.tool
async def get_model_version(version_id: int) -> str:
    """Get details about a specific model version by version ID.

    Returns: download URLs, trigger words, base model, files, example images.
    """
    from .tools.models import get_model_version as _get

    return await _get(client, version_id)


@mcp.tool
async def get_model_version_by_hash(hash: str) -> str:
    """Find a model version by its file hash (SHA256, AutoV2, CRC32, BLAKE3)."""
    from .tools.models import get_model_version_by_hash as _get

    return await _get(client, hash)


@mcp.tool
async def get_top_checkpoints(
    base_model: str = "SDXL 1.0",
    period: str = "Month",
    sort: str = "Most Downloaded",
    limit: int = 10,
) -> str:
    """Get top checkpoint models for a specific base model.

    Best for finding SDXL, Flux, Pony, Illustrious checkpoints.
    Base models: SD 1.5, SDXL 1.0, Flux.1 D, Flux.2 D, Pony, Pony V7, Illustrious, NoobAI, Chroma, HiDream, etc.
    """
    from .tools.models import get_top_checkpoints as _get

    return await _get(client, base_model, period, sort, limit)


@mcp.tool
async def get_top_loras(
    base_model: str = "SDXL 1.0",
    period: str = "Month",
    sort: str = "Most Downloaded",
    limit: int = 10,
    nsfw: Optional[bool] = None,
) -> str:
    """Get top LoRA models for a specific base model.

    Find the most popular LoRAs for SDXL, Flux, Pony, Illustrious.
    Set nsfw=true to include NSFW LoRAs (requires API key).
    """
    from .tools.models import get_top_loras as _get

    return await _get(client, base_model, period, sort, limit, nsfw)


# ═══════════════════════════════════════════════════════════════
# IMAGE TOOLS
# ═══════════════════════════════════════════════════════════════


@mcp.tool
async def browse_images(
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

    Sort: Most Reactions, Most Comments, Most Collected, Newest, Oldest.
    NSFW filter: None, Soft, Mature, X.
    content_type: "image" or "video".
    browsing_level: "PG", "PG-13", "R", "X", "XXX" (comma-separated for multiple).
    tag: filter by tag (e.g. "anime", "animal", "architecture").
    base_model: filter by base model (e.g. "Flux.1 D", "SDXL 1.0", "Pony").
    tools: filter by tool (e.g. "ComfyUI", "Automatic1111").
    techniques: filter by technique (e.g. "txt2img", "img2img").
    has_meta: true = only with generation metadata.
    made_on_site: true = only generated on Civitai.
    originals_only/remixes_only: filter originals vs remixes.
    exclude_used: true = skip images/videos already in history (avoid duplicates).
    requester: who is requesting (e.g. "pikabu", "telegram", "scheduled:daily-post"). Always specify when fetching content for another MCP tool.
    Previews are cached locally for viewing via Read tool.
    """
    from .tools.images import browse_images as _browse

    return await _browse(
        client, model_id, model_version_id, post_id, username, nsfw, sort, period, limit, page,
        content_type, browsing_level, tag, base_model, tools, techniques,
        has_meta, made_on_site, originals_only, remixes_only,
        exclude_used, requester,
    )


@mcp.tool
async def get_top_images(
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
    exclude_used: true = skip images/videos already in history (avoid duplicate posts).
    requester: who is requesting (e.g. "pikabu", "telegram", "scheduled:daily-post"). Always specify for publishing workflows.
    Previews cached locally for Read tool.
    """
    from .tools.images import get_top_images as _get

    return await _get(
        client, sort, period, nsfw, limit, content_type, browsing_level,
        tag, base_model, tools, techniques, has_meta, made_on_site,
        originals_only, remixes_only, exclude_used, requester,
    )


@mcp.tool
async def get_model_images(
    model_id: int,
    limit: int = 5,
    exclude_used: Optional[bool] = None,
    requester: Optional[str] = None,
) -> str:
    """Get example images generated with a specific model.

    Returns images with full generation params: prompt, negative prompt,
    steps, CFG, sampler, seed, LoRAs used. Learn how to use a model well.
    exclude_used: true = skip already-used images.
    requester: who is requesting (e.g. "pikabu", "telegram").
    """
    from .tools.images import get_model_images as _get

    return await _get(client, model_id, limit, exclude_used, requester)


@mcp.tool
async def get_image_generation_data(
    model_id: int,
    sort: str = "Most Reactions",
    limit: int = 3,
    exclude_used: Optional[bool] = None,
    requester: Optional[str] = None,
) -> str:
    """Get full generation parameters from top images of a model.

    Focused on extracting the best prompts, settings, and LoRA combinations.
    Only returns images that have generation metadata.
    exclude_used: true = skip already-used images.
    requester: who is requesting (e.g. "pikabu", "telegram").
    """
    from .tools.images import get_image_generation_data as _get

    return await _get(client, model_id, sort, limit, exclude_used, requester)


# ═══════════════════════════════════════════════════════════════
# CREATOR & TAG TOOLS
# ═══════════════════════════════════════════════════════════════


@mcp.tool
async def get_creators(
    query: Optional[str] = None,
    limit: int = 20,
    page: int = 1,
) -> str:
    """Browse and search model creators on Civitai."""
    from .tools.creators import get_creators as _get

    return await _get(client, query, limit, page)


@mcp.tool
async def get_tags(
    query: Optional[str] = None,
    limit: int = 20,
    page: int = 1,
) -> str:
    """Browse and search model tags. Use tags in search_models filter."""
    from .tools.creators import get_tags as _get

    return await _get(client, query, limit, page)


# ═══════════════════════════════════════════════════════════════
# DOWNLOAD TOOLS
# ═══════════════════════════════════════════════════════════════


@mcp.tool
async def get_download_url(version_id: int) -> str:
    """Get authenticated download URL for a model version."""
    from .tools.downloads import get_download_url as _get

    return await _get(client, version_id)


@mcp.tool
async def get_download_info(
    model_id: int,
    version_id: Optional[int] = None,
    comfyui_path: Optional[str] = None,
) -> str:
    """Get download URLs + curl/PowerShell commands for a model.

    If version_id not specified, uses latest version.
    Set comfyui_path to auto-map to correct ComfyUI model directory.
    Generates ready-to-paste download commands with authentication.
    """
    from .tools.downloads import get_download_info as _get

    return await _get(client, model_id, version_id, comfyui_path)


# ═══════════════════════════════════════════════════════════════
# HISTORY TOOLS
# ═══════════════════════════════════════════════════════════════


@mcp.tool
async def get_history(
    what: str = "all",
    limit: int = 50,
) -> str:
    """View history of downloaded models and used images/videos.

    what: "all" (summary), "downloads" (downloaded models), "images" (used images/videos).
    Use this to check what was already used before fetching new content.
    """
    from .history import get_downloaded, get_stats, get_used_images

    if what == "downloads":
        items = get_downloaded()[:limit]
        if not items:
            return "No downloads in history."
        lines = ["## Download History\n"]
        for d in items:
            lines.append(
                f"- **v{d['version_id']}** — {d.get('model_name', '?')} "
                f"(`{d.get('filename', '?')}`) — {d.get('iso', '?')}"
            )
        return "\n".join(lines)

    if what == "images":
        items = get_used_images()[:limit]
        if not items:
            return "No images/videos in history."
        lines = ["## Image/Video History\n"]
        for img in items:
            actions = img.get("actions", [])
            last_action = actions[-1] if actions else {}
            lines.append(
                f"- **Image {img['image_id']}** — "
                f"{last_action.get('action', '?')} — {last_action.get('iso', '?')}"
                + (f" — {last_action.get('context', '')}" if last_action.get('context') else "")
            )
        return "\n".join(lines)

    # Summary
    stats = get_stats()
    downloads = get_downloaded()[:5]
    images = get_used_images()[:5]

    lines = [
        "## History Summary\n",
        f"**Downloads**: {stats['total_downloads']} models",
        f"**Images/Videos**: {stats['total_images']} items\n",
    ]
    if downloads:
        lines.append("### Recent Downloads")
        for d in downloads:
            lines.append(f"- v{d['version_id']} — {d.get('model_name', '?')} — {d.get('iso', '?')}")
    if images:
        lines.append("\n### Recent Images/Videos")
        for img in images:
            actions = img.get("actions", [])
            last = actions[-1] if actions else {}
            lines.append(f"- Image {img['image_id']} — {last.get('action', '?')} — {last.get('iso', '?')}")

    return "\n".join(lines)


@mcp.tool
async def mark_as_used(
    image_ids: list[int],
    action: str = "sent",
    requester: Optional[str] = None,
    context: Optional[str] = None,
) -> str:
    """Mark images/videos as used (e.g. after sending to Pikabu, Telegram, etc.).

    Call this AFTER successfully publishing content to another platform.
    image_ids: list of Civitai image IDs that were used.
    action: what was done — "sent_to_pikabu", "sent_to_telegram", "posted", etc.
    requester: which MCP/tool used this (e.g. "pikabu", "telegram").
    context: optional note (e.g. "posted to community Stable Diffusion").
    """
    from .history import record_image

    for img_id in image_ids:
        full_action = f"{action}:{requester}" if requester else action
        record_image(img_id, action=full_action, context=context)

    return f"Marked {len(image_ids)} items as used (action: {action}, requester: {requester or 'unknown'})."


@mcp.tool
async def clear_history(what: str = "all") -> str:
    """Clear usage history. Use with caution!

    what: "all" (everything), "downloads" (only downloads), "images" (only images/videos).
    """
    from .history import clear_history as _clear

    return _clear(what)


# ═══════════════════════════════════════════════════════════════
# ENTRY POINT
# ═══════════════════════════════════════════════════════════════


def main():
    """Run the MCP server."""
    mcp.run()


if __name__ == "__main__":
    main()
