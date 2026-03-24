"""Download-related MCP tools."""

import os
from typing import Optional

from ..client import CivitaiClient
from ..formatters import format_download_info


async def get_download_url(
    client: CivitaiClient,
    version_id: int,
) -> str:
    """Get authenticated download URL for a model version.

    Returns direct download link with API token for authenticated access.
    """
    data = await client.get(f"model-versions/{version_id}")
    if data.get("error") == "not_found":
        return f"Version {version_id} not found"

    api_key = client.api_key or ""
    files = data.get("files", [])
    if not files:
        return f"No files found for version {version_id}"

    lines = []
    for f in files:
        url = f.get("downloadUrl", "")
        auth_url = f"{url}?token={api_key}" if api_key else url
        lines.append(f"**{f.get('name', '?')}**: `{auth_url}`")
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
    model_data = await client.get(f"models/{model_id}")
    if model_data.get("error") == "not_found":
        return f"Model {model_id} not found"

    versions = model_data.get("modelVersions", [])
    if not versions:
        return f"Model {model_id} has no versions"

    if version_id:
        version = next((v for v in versions if v["id"] == version_id), None)
        if not version:
            # Fetch directly
            version = await client.get(f"model-versions/{version_id}")
            if version.get("error") == "not_found":
                return f"Version {version_id} not found"
    else:
        version = versions[0]

    comfyui = comfyui_path or os.getenv("COMFYUI_MODELS_PATH", "")

    return format_download_info(
        model=model_data,
        version=version,
        api_key=client.api_key or "",
        comfyui_path=comfyui,
    )
