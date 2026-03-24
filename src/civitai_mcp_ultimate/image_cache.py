"""Download and cache Civitai images locally for preview via Read tool.

Images are saved to ~/.civitai-mcp-cache/.
Filenames: {image_id}.{ext} — deduped, never re-downloaded.
URLs are rewritten to use width=512 thumbnail to save bandwidth.
Auto-cleanup: files older than MAX_AGE_HOURS are deleted on startup.
"""

import logging
import re
import time
from pathlib import Path

import httpx

logger = logging.getLogger(__name__)

# Cache dir: ~/.civitai-mcp-cache/
CACHE_DIR = Path.home() / ".civitai-mcp-cache"

# Max thumbnail width for preview (saves bandwidth)
PREVIEW_WIDTH = 512

# Auto-cleanup: delete cached images older than this
MAX_AGE_HOURS = 24


def _ensure_cache_dir() -> Path:
    """Create cache directory if it doesn't exist."""
    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    return CACHE_DIR


def cleanup_cache() -> int:
    """Delete cached images older than MAX_AGE_HOURS. Returns count of deleted files."""
    if not CACHE_DIR.exists():
        return 0
    cutoff = time.time() - MAX_AGE_HOURS * 3600
    deleted = 0
    for f in CACHE_DIR.iterdir():
        if f.is_file() and f.stat().st_mtime < cutoff:
            f.unlink(missing_ok=True)
            deleted += 1
    if deleted:
        logger.info(f"Cache cleanup: deleted {deleted} files older than {MAX_AGE_HOURS}h")
    return deleted


def _thumbnail_url(original_url: str, width: int = PREVIEW_WIDTH) -> str:
    """Convert Civitai image URL to thumbnail URL.

    Civitai supports width parameter in URL path:
    .../original=true/name.jpeg -> .../width=512/name.jpeg
    """
    return re.sub(r"/original=true/", f"/width={width}/", original_url)


def _ext_from_url(url: str) -> str:
    """Extract file extension from URL."""
    # Find the last segment, strip query params
    last_part = url.rstrip("/").rsplit("/", 1)[-1].split("?")[0]
    if "." in last_part:
        ext = last_part.rsplit(".", 1)[-1].lower()
        if ext in ("jpeg", "jpg", "png", "webp", "gif", "mp4"):
            return ext
    return "jpeg"


async def download_image(image_id: int | str, url: str) -> str | None:
    """Download image to cache, return local path. Skip videos.

    Returns None if download fails or file is a video.
    """
    ext = _ext_from_url(url)

    # Skip videos — can't preview via Read tool
    if ext == "mp4":
        return None

    cache_dir = _ensure_cache_dir()
    local_path = cache_dir / f"{image_id}.{ext}"

    # Already cached
    if local_path.exists() and local_path.stat().st_size > 0:
        return str(local_path)

    # Download thumbnail
    thumb_url = _thumbnail_url(url)
    try:
        async with httpx.AsyncClient(timeout=15.0, follow_redirects=True) as client:
            resp = await client.get(thumb_url)
            if resp.status_code == 200 and len(resp.content) > 100:
                local_path.write_bytes(resp.content)
                return str(local_path)
            else:
                logger.warning(f"Failed to download image {image_id}: HTTP {resp.status_code}")
                return None
    except Exception as e:
        logger.warning(f"Failed to download image {image_id}: {e}")
        return None


async def download_images(images: list[dict]) -> dict[int | str, str]:
    """Download multiple images, return {image_id: local_path} map."""
    import asyncio

    results: dict[int | str, str] = {}
    tasks = []

    for img in images:
        img_id = img.get("id")
        url = img.get("url")
        if img_id and url:
            tasks.append((img_id, download_image(img_id, url)))

    if not tasks:
        return results

    # Download concurrently (max 5 at a time)
    sem = asyncio.Semaphore(5)

    async def _download(img_id, coro):
        async with sem:
            path = await coro
            if path:
                results[img_id] = path

    await asyncio.gather(*(_download(img_id, coro) for img_id, coro in tasks))
    return results
