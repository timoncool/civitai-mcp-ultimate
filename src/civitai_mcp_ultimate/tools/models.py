"""Model-related MCP tools."""

from typing import Optional

import httpx

from ..client import CivitaiClient, CivitaiNotFoundError, CivitaiRateLimitError, _sanitize_query
from ..formatters import format_file_size, format_model_card, format_model_list


async def search_models(
    client: CivitaiClient,
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

    Find checkpoints, LoRAs, ControlNets and more. Filter by type, base model,
    creator, tags. Sort by downloads, rating, or newest.

    Tips:
    - Search by username (creator) is most reliable
    - Model names with special chars may not match — use simple keywords
    - If you know the model ID, use get_model instead
    """
    sanitized_query = _sanitize_query(query)
    params: dict = {
        "query": sanitized_query,
        "tag": tag,
        "username": username,
        "sort": sort,
        "period": period,
        "limit": min(limit, 100),
    }
    # Civitai API doesn't allow page param with query search — cursor-based only
    if not sanitized_query:
        params["page"] = page
    if types:
        params["types"] = types
    if base_model:
        params["baseModels"] = [base_model]
    if nsfw is not None:
        params["nsfw"] = nsfw
    if ids:
        params["ids"] = ids
    if favorites is not None:
        params["favorites"] = favorites
    if hidden is not None:
        params["hidden"] = hidden
    if primary_file_only is not None:
        params["primaryFileOnly"] = primary_file_only
    if allow_commercial_use:
        params["allowCommercialUse"] = allow_commercial_use
    if supports_generation is not None:
        params["supportsGeneration"] = supports_generation
    if allow_no_credit is not None:
        params["allowNoCredit"] = allow_no_credit
    if allow_derivatives is not None:
        params["allowDerivatives"] = allow_derivatives
    if allow_different_licenses is not None:
        params["allowDifferentLicenses"] = allow_different_licenses

    try:
        data = await client.get("models", params)
    except CivitaiRateLimitError:
        return "Rate limited by Civitai API. Please try again in a few seconds."
    except CivitaiNotFoundError:
        return "Civitai API endpoint not found."
    except httpx.TimeoutException:
        return "Civitai API timed out. Please try again."
    except httpx.HTTPStatusError as e:
        return f"Civitai API error: HTTP {e.response.status_code}"

    items = data.get("items", [])
    meta = data.get("metadata", {})

    if not items:
        return f"No models found for query='{query}', types={types}, base_model={base_model}"

    result = format_model_list(items)
    total = meta.get("totalItems", "?")
    result += f"\n\n---\n_Page {meta.get('currentPage', page)} | Total: {total}_"
    return result


async def get_model(client: CivitaiClient, model_id: int) -> str:
    """Get detailed information about a specific model by its ID.

    Returns full model info: description, all versions, files, trigger words,
    stats, creator, tags, download URLs.
    """
    try:
        data = await client.get(f"models/{model_id}")
    except CivitaiNotFoundError:
        return f"Model {model_id} not found"
    except CivitaiRateLimitError:
        return "Rate limited by Civitai API. Please try again in a few seconds."
    except httpx.TimeoutException:
        return "Civitai API timed out. Please try again."
    except httpx.HTTPStatusError as e:
        return f"Civitai API error: HTTP {e.response.status_code}"
    return format_model_card(data)


async def get_model_version(client: CivitaiClient, version_id: int) -> str:
    """Get details about a specific model version.

    Returns: download URLs, trigger words, base model, files, example images.
    """
    try:
        data = await client.get(f"model-versions/{version_id}")
    except CivitaiNotFoundError:
        return f"Model version {version_id} not found"
    except CivitaiRateLimitError:
        return "Rate limited by Civitai API. Please try again in a few seconds."
    except httpx.TimeoutException:
        return "Civitai API timed out. Please try again."
    except httpx.HTTPStatusError as e:
        return f"Civitai API error: HTTP {e.response.status_code}"
    return _format_version(data)


def _format_version(v: dict) -> str:
    """Format a version dict as markdown."""
    created = str(v.get("publishedAt") or v.get("createdAt") or "?")
    lines = [
        f"## {v.get('name', '?')} (Version ID: {v.get('id', '?')})",
        f"**Model ID**: {v.get('modelId', '?')}",
        f"**Base Model**: {v.get('baseModel', '?')}",
        f"**Created**: {created[:10]}",
    ]
    if v.get("trainedWords"):
        lines.append(f"**Trigger Words**: {', '.join(v['trainedWords'])}")
    if v.get("description"):
        desc = v["description"][:300]
        lines.append(f"**Description**: {desc}")

    for f in v.get("files", [])[:5]:
        size = format_file_size(f.get("sizeKB", 0))
        meta = f.get("metadata", {})
        fmt = meta.get("format", "?")
        fp = meta.get("fp", "?")
        fsize = meta.get("size", "?")
        primary = " [PRIMARY]" if f.get("primary") else ""
        lines.append(f"\n**File**: {f.get('name', '?')} ({size}, {fmt}, {fp}, {fsize}){primary}")
        lines.append(f"  Download: `{f.get('downloadUrl', '?')}`")
        # Security scan
        pickle_scan = f.get("pickleScanResult")
        virus_scan = f.get("virusScanResult")
        if pickle_scan or virus_scan:
            lines.append(f"  Scan: pickle={pickle_scan or '?'}, virus={virus_scan or '?'}")
        # Hashes
        hashes = f.get("hashes", {})
        hash_parts = [f"{ht}: {hashes[ht]}" for ht in ["SHA256", "AutoV2"] if hashes.get(ht)]
        if hash_parts:
            lines.append(f"  Hashes: {' | '.join(hash_parts)}")

    return "\n".join(lines)


async def get_model_version_by_hash(client: CivitaiClient, hash: str) -> str:
    """Find a model version by its file hash (SHA256, AutoV2, CRC32)."""
    try:
        data = await client.get(f"model-versions/by-hash/{hash}")
    except CivitaiNotFoundError:
        return f"No model found for hash {hash}"
    except CivitaiRateLimitError:
        return "Rate limited by Civitai API. Please try again in a few seconds."
    except httpx.TimeoutException:
        return "Civitai API timed out. Please try again."
    except httpx.HTTPStatusError as e:
        return f"Civitai API error: HTTP {e.response.status_code}"
    return _format_version(data)


async def get_top_checkpoints(
    client: CivitaiClient,
    base_model: str = "SDXL 1.0",
    period: str = "Month",
    sort: str = "Most Downloaded",
    limit: int = 10,
) -> str:
    """Get top checkpoint models for a specific base model.

    Great for finding the best SDXL, Flux, Pony, or Illustrious checkpoints.
    """
    return await search_models(
        client,
        types=["Checkpoint"],
        base_model=base_model,
        sort=sort,
        period=period,
        limit=limit,
    )


async def get_top_loras(
    client: CivitaiClient,
    base_model: str = "SDXL 1.0",
    period: str = "Month",
    sort: str = "Most Downloaded",
    limit: int = 10,
    nsfw: Optional[bool] = None,
) -> str:
    """Get top LoRA models for a specific base model.

    Find the most popular LoRAs for SDXL, Flux, Pony, Illustrious etc.
    """
    return await search_models(
        client,
        types=["LORA"],
        base_model=base_model,
        sort=sort,
        period=period,
        limit=limit,
        nsfw=nsfw,
    )
