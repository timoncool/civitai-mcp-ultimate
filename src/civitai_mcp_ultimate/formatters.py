"""Markdown formatters for Civitai API responses.

All output is human-readable markdown, bilingual (EN/RU).
"""

from typing import Any

from .i18n import (
    L_BASE_MODEL,
    L_COMMENTS,
    L_CREATED,
    L_CREATOR,
    L_DOWNLOAD,
    L_DOWNLOADS,
    L_FAVORITES,
    L_FILES,
    L_GENERATION_PARAMS,
    L_NEGATIVE_PROMPT,
    L_NO_RESULTS,
    L_PROMPT,
    L_RATING,
    L_REACTIONS,
    L_TAGS,
    L_TRIGGER_WORDS,
    L_TYPE,
    L_VERSION,
)


def format_file_size(size_kb: float) -> str:
    """Format file size from KB to human readable."""
    if size_kb >= 1024 * 1024:
        return f"{size_kb / 1024 / 1024:.2f} GB"
    if size_kb >= 1024:
        return f"{size_kb / 1024:.1f} MB"
    return f"{size_kb:.0f} KB"


def format_model_card(model: dict[str, Any]) -> str:
    """Format a model as a markdown card."""
    stats = model.get("stats", {})
    creator = model.get("creator", {})
    tags = model.get("tags", [])
    if isinstance(tags, list) and tags and isinstance(tags[0], dict):
        tags = [tag["name"] for tag in tags]

    lines = [
        f"## {model['name']} (ID: {model['id']})",
        "",
        f"**{L_TYPE}**: {model.get('type', '?')} | **{L_BASE_MODEL}**: {_get_base_model(model)}",
        f"**{L_CREATOR}**: {creator.get('username', '?')}",
        f"**{L_RATING}**: {stats.get('rating', 0):.1f} ({stats.get('ratingCount', 0)})"
        if "rating" in stats
        else f"**Thumbs Up**: {stats.get('thumbsUpCount', 0)}",
        f"**{L_DOWNLOADS}**: {stats.get('downloadCount', 0):,} | **{L_FAVORITES}**: {stats.get('favoriteCount', stats.get('thumbsUpCount', 0)):,}",
    ]

    if tags:
        lines.append(f"**{L_TAGS}**: {', '.join(tags[:10])}")

    # Latest version
    versions = model.get("modelVersions", [])
    if versions:
        v = versions[0]
        lines.append("")
        lines.append(f"### {L_VERSION}: {v.get('name', '?')} (ID: {v.get('id')})")
        lines.append(f"- **{L_BASE_MODEL}**: {v.get('baseModel', '?')}")
        if v.get("trainedWords"):
            lines.append(f"- **{L_TRIGGER_WORDS}**: {', '.join(v['trainedWords'])}")
        lines.append(f"- **{L_CREATED}**: {v.get('publishedAt', v.get('createdAt', '?'))[:10]}")

        # Files
        for f in v.get("files", [])[:3]:
            size = format_file_size(f.get("sizeKB", 0))
            fmt = f.get("metadata", {}).get("format", "?")
            fp = f.get("metadata", {}).get("fp", "?")
            lines.append(f"- **{L_FILES}**: {f.get('name', '?')} ({size}, {fmt}, {fp})")
            lines.append(f"  - **{L_DOWNLOAD}**: `{f.get('downloadUrl', '?')}`")

    return "\n".join(lines)


def format_model_list(models: list[dict[str, Any]]) -> str:
    """Format a list of models as compact cards."""
    if not models:
        return L_NO_RESULTS
    return "\n\n---\n\n".join(format_model_short(m) for m in models)


def format_model_short(model: dict[str, Any]) -> str:
    """Format a model as a short one-liner card."""
    stats = model.get("stats", {})
    creator = model.get("creator", {})
    dl = stats.get("downloadCount", 0)
    thumbs = stats.get("thumbsUpCount", 0)

    base_model = _get_base_model(model)

    return (
        f"**{model['name']}** (ID: {model['id']}) — {model.get('type', '?')}\n"
        f"  {L_CREATOR}: {creator.get('username', '?')} | "
        f"{L_BASE_MODEL}: {base_model} | "
        f"{L_DOWNLOADS}: {dl:,} | Thumbs: {thumbs:,}"
    )


def format_image(image: dict[str, Any], include_prompt: bool = True) -> str:
    """Format an image with metadata and generation params."""
    stats = image.get("stats", {})
    meta = image.get("meta") or {}

    lines = [
        f"### Image ID: {image.get('id', '?')}",
        f"**URL**: {image.get('url', '?')}",
        f"**Size**: {image.get('width', '?')}x{image.get('height', '?')}",
        f"**NSFW**: {image.get('nsfwLevel', image.get('nsfw', '?'))}",
        f"**{L_CREATOR}**: {image.get('username', '?')}",
    ]

    # Stats
    reaction_parts = []
    for key in ["heartCount", "likeCount", "laughCount", "cryCount"]:
        val = stats.get(key, 0)
        if val > 0:
            emoji_map = {"heartCount": "Heart", "likeCount": "Like", "laughCount": "Laugh", "cryCount": "Cry"}
            reaction_parts.append(f"{emoji_map.get(key, key)}: {val}")
    if reaction_parts:
        lines.append(f"**{L_REACTIONS}**: {', '.join(reaction_parts)}")
    if stats.get("commentCount", 0) > 0:
        lines.append(f"**{L_COMMENTS}**: {stats['commentCount']}")

    # Generation params
    if include_prompt and meta:
        lines.append("")
        lines.append(f"#### {L_GENERATION_PARAMS}")
        if meta.get("prompt"):
            lines.append(f"**{L_PROMPT}**: {meta['prompt'][:500]}")
        if meta.get("negativePrompt"):
            lines.append(f"**{L_NEGATIVE_PROMPT}**: {meta['negativePrompt'][:300]}")
        # Other params
        params = []
        for key in ["steps", "sampler", "cfgScale", "seed", "Size", "Model", "Clip skip"]:
            alt_key = key.replace(" ", "").lower()
            val = meta.get(key) or meta.get(alt_key)
            if val:
                params.append(f"{key}: {val}")
        if params:
            lines.append(f"**Params**: {' | '.join(params)}")

        # LoRAs used
        lora_hashes = meta.get("resources", [])
        if lora_hashes:
            lora_lines = []
            for r in lora_hashes:
                if r.get("type") in ("lora", "LORA"):
                    lora_lines.append(f"  - {r.get('name', '?')} (weight: {r.get('weight', '?')})")
            if lora_lines:
                lines.append(f"**LoRAs used**:")
                lines.extend(lora_lines)

    return "\n".join(lines)


def format_image_list(images: list[dict[str, Any]], include_prompts: bool = True) -> str:
    """Format a list of images."""
    if not images:
        return L_NO_RESULTS
    return "\n\n---\n\n".join(format_image(img, include_prompt=include_prompts) for img in images)


def format_creator(creator: dict[str, Any]) -> str:
    """Format a creator entry."""
    return f"**{creator.get('username', '?')}** — {creator.get('modelCount', 0)} models"


def format_tag(tag: dict[str, Any]) -> str:
    """Format a tag entry."""
    return f"**{tag.get('name', '?')}** ({tag.get('modelCount', 0)} models)"


def format_download_info(
    model: dict[str, Any],
    version: dict[str, Any],
    api_key: str = "",
    comfyui_path: str = "",
) -> str:
    """Format download info with curl/PowerShell commands."""
    model_type = model.get("type", "Other")
    lines = [
        f"## {L_DOWNLOAD}: {model['name']} — {version.get('name', '?')}",
        "",
    ]

    for f in version.get("files", []):
        url = f.get("downloadUrl", "")
        auth_url = f"{url}?token={api_key}" if api_key else url
        name = f.get("name", "model")
        size = format_file_size(f.get("sizeKB", 0))

        lines.append(f"### {name} ({size})")
        lines.append(f"**URL**: `{auth_url}`")

        # curl command
        lines.append(f"\n**curl**:")
        lines.append(f"```bash")
        lines.append(f'curl -L -o "{name}" "{auth_url}"')
        lines.append(f"```")

        # PowerShell command
        lines.append(f"\n**PowerShell**:")
        lines.append(f"```powershell")
        lines.append(f'Invoke-WebRequest -Uri "{auth_url}" -OutFile "{name}"')
        lines.append(f"```")

        # ComfyUI path
        if comfyui_path:
            from .types import COMFYUI_FOLDER_MAP

            subfolder = COMFYUI_FOLDER_MAP.get(model_type, "other")
            target = f"{comfyui_path}/{subfolder}/{name}"
            lines.append(f"\n**ComfyUI path**: `{target}`")
            lines.append(f"```bash")
            lines.append(f'curl -L -o "{target}" "{auth_url}"')
            lines.append(f"```")

        # Hash
        hashes = f.get("hashes", {})
        if hashes.get("SHA256"):
            lines.append(f"\n**SHA256**: `{hashes['SHA256']}`")

    return "\n".join(lines)


def _get_base_model(model: dict[str, Any]) -> str:
    """Extract base model from model or its latest version."""
    versions = model.get("modelVersions", [])
    if versions:
        return versions[0].get("baseModel", "?")
    return "?"
