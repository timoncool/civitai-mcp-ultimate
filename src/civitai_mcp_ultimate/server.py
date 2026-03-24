"""Civitai MCP Ultimate — FastMCP server with all tools.

Usage:
    claude mcp add civitai-mcp-ultimate -- uvx civitai-mcp-ultimate

Environment:
    CIVITAI_API_KEY — your Civitai API key (required for NSFW + higher rate limits)
    CIVITAI_MCP_LANG — output language: en (default) | ru
    COMFYUI_MODELS_PATH — path to ComfyUI models dir (for download_info)
"""

from contextlib import asynccontextmanager
from typing import Optional

from fastmcp import FastMCP

from .client import CivitaiClient
from .types import BaseModel_, ImageSort, ModelSort, ModelType, NsfwLevel, Period

client = CivitaiClient()


@asynccontextmanager
async def lifespan(server):
    """Manage client lifecycle."""
    yield
    await client.close()


mcp = FastMCP(
    name="civitai-mcp-ultimate",
    instructions="Ultimate MCP server for Civitai — search models, browse top images with prompts, download LoRAs/Checkpoints, analyze trends.",
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
) -> str:
    """Search for AI models on Civitai with flexible filters.

    Find checkpoints, LoRAs, ControlNets and more.
    Types: Checkpoint, LORA, LoCon, TextualInversion, Hypernetwork, Controlnet, Poses, VAE, Upscaler, Wildcards, MotionModule, Other.
    Base models: SD 1.5, SDXL 1.0, Flux.1 D, Flux.2 D, Pony, Illustrious, NoobAI, Hunyuan 1, Kolors, Chroma, etc.
    Sort: Highest Rated, Most Downloaded, Newest.
    Period: AllTime, Year, Month, Week, Day.

    Tips: search by username is most reliable. Use get_model if you know the ID.
    Note: page parameter is ignored when query is specified (Civitai uses cursor-based pagination for text search).
    """
    from .tools.models import search_models as _search

    return await _search(client, query, types, base_model, tag, username, sort, period, nsfw, limit, page)


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
    username: Optional[str] = None,
    nsfw: Optional[str] = None,
    sort: str = "Most Reactions",
    period: str = "Month",
    limit: int = 10,
    page: Optional[int] = None,
) -> str:
    """Browse AI-generated images on Civitai.

    Filter by model, creator, NSFW level.
    Sort: Most Reactions, Most Comments, Most Collected, Newest, Oldest.
    NSFW filter: None, Soft, Mature, X.
    Returns images with URLs, stats, and full generation parameters.
    """
    from .tools.images import browse_images as _browse

    return await _browse(client, model_id, model_version_id, username, nsfw, sort, period, limit, page)


@mcp.tool
async def get_top_images(
    sort: str = "Most Reactions",
    period: str = "Month",
    nsfw: Optional[str] = None,
    limit: int = 10,
) -> str:
    """Get top images from Civitai — best for finding great prompts.

    Sort: Most Reactions, Most Comments, Most Collected, Newest, Oldest.
    Period: Day, Week, Month, Year, AllTime.
    Set nsfw to filter NSFW level.
    """
    from .tools.images import get_top_images as _get

    return await _get(client, sort, period, nsfw, limit)


@mcp.tool
async def get_model_images(model_id: int, limit: int = 5) -> str:
    """Get example images generated with a specific model.

    Returns images with full generation params: prompt, negative prompt,
    steps, CFG, sampler, seed, LoRAs used. Learn how to use a model well.
    """
    from .tools.images import get_model_images as _get

    return await _get(client, model_id, limit)


@mcp.tool
async def get_image_generation_data(
    model_id: int,
    sort: str = "Most Reactions",
    limit: int = 3,
) -> str:
    """Get full generation parameters from top images of a model.

    Focused on extracting the best prompts, settings, and LoRA combinations.
    Only returns images that have generation metadata.
    """
    from .tools.images import get_image_generation_data as _get

    return await _get(client, model_id, sort, limit)


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
# ENTRY POINT
# ═══════════════════════════════════════════════════════════════


def main():
    """Run the MCP server."""
    mcp.run()


if __name__ == "__main__":
    main()
