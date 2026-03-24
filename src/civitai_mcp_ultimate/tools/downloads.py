"""Download-related MCP tools."""

import os
from typing import Optional

import httpx

from ..client import CivitaiClient, CivitaiNotFoundError, CivitaiRateLimitError
from ..formatters import format_download_info


async def get_download_url(
    client: CivitaiClient,
    version_id: int,
) -> str:
    """Get download URL for a model version.

    Returns download links. Use Authorization header for authenticated access.
    """
    try:
        data = await client.get(f"model-versions/{version_id}")
    except CivitaiNotFoundError:
        return f"Version {version_id} not found"
    except CivitaiRateLimitError:
        return "Rate limited. Try again later."
    except httpx.TimeoutException:
        return "Civitai API timed out. Please try again."
    except httpx.HTTPStatusError as e:
        return f"Civitai API error: HTTP {e.response.status_code}"

    files = data.get("files", [])
    if not files:
        return f"No files found for version {version_id}"

    lines = []
    for f in files:
        url = f.get("downloadUrl", "")
        lines.append(f"**{f.get('name', '?')}**: `{url}`")
    lines.append("")
    lines.append('_Use `curl -H "Authorization: Bearer $CIVITAI_API_KEY"` for authenticated downloads._')
    return "\n".join(lines)


async def get_download_info(
    client: CivitaiClient,
    model_id: int,
    version_id: Optional[int] = None,
    comfyui_path: Optional[str] = None,
) -> str:
    """Get download URLs and ready-to-use commands for a model.

    Returns curl and PowerShell download commands with authentication.
    Optionally maps to ComfyUI model directories.

    If version_id is not specified, uses the latest version.
    """
    try:
        model_data = await client.get(f"models/{model_id}")
    except CivitaiNotFoundError:
        return f"Model {model_id} not found"
    except CivitaiRateLimitError:
        return "Rate limited. Try again later."
    except httpx.TimeoutException:
        return "Civitai API timed out. Please try again."
    except httpx.HTTPStatusError as e:
        return f"Civitai API error: HTTP {e.response.status_code}"

    versions = model_data.get("modelVersions", [])
    if not versions:
        return f"Model {model_id} has no versions"

    if version_id:
        version = next((v for v in versions if v["id"] == version_id), None)
        if not version:
            # Fetch directly
            try:
                version = await client.get(f"model-versions/{version_id}")
            except CivitaiNotFoundError:
                return f"Version {version_id} not found"
            except (CivitaiRateLimitError, httpx.TimeoutException, httpx.HTTPStatusError):
                return f"Failed to fetch version {version_id}"
    else:
        version = versions[0]

    comfyui = comfyui_path or os.getenv("COMFYUI_MODELS_PATH", "")

    return format_download_info(
        model=model_data,
        version=version,
        comfyui_path=comfyui,
    )
