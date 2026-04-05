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
    .../width=1024/name.jpeg -> .../width=512/name.jpeg
    """
    # Handle both /original=true/ and /width=\d+/ patterns
    result = re.sub(r"/original=true/", f"/width={width}/", original_url)
    if result == original_url:
        result = re.sub(r"/width=\d+/", f"/width={width}/", original_url)
    return result


def _ext_from_url(url: str) -> str:
    """Extract file extension from URL."""
    # Find the last segment, strip query params
    last_part = url.rstrip("/").rsplit("/", 1)[-1].split("?")[0]
    if "." in last_part:
        ext = last_part.rsplit(".", 1)[-1].lower()
        if ext in ("jpeg", "jpg", "png", "webp", "gif", "mp4", "webm"):
            return ext
    return "jpeg"


def _extract_video_thumbnail(video_path: Path, thumb_path: Path) -> bool:
    """Extract first frame from video using ffmpeg as webp. Returns True on success."""
    import subprocess
    try:
        result = subprocess.run(
            ["ffmpeg", "-y", "-i", str(video_path), "-vframes", "1", "-q:v", "2", str(thumb_path)],
            capture_output=True, timeout=15,
        )
        return result.returncode == 0 and thumb_path.exists() and thumb_path.stat().st_size > 0
    except (subprocess.TimeoutExpired, FileNotFoundError) as e:
        logger.warning(f"ffmpeg thumbnail extraction failed: {e}")
        return False


async def download_image(image_id: int | str, url: str) -> str | tuple[str, str] | None:
    """Download image/video to cache, return local path(s).

    Images: returns path to 512px thumbnail.
    Videos: returns (video_path, thumb_path) tuple — both the video file and a webp thumbnail.
    Returns None if download fails.
    """
    ext = _ext_from_url(url)
    cache_dir = _ensure_cache_dir()
    is_video = ext in ("mp4", "webm")

    if is_video:
        video_path = cache_dir / f"{image_id}.{ext}"
        thumb_path = cache_dir / f"{image_id}_thumb.webp"

        # Already cached — return both
        if video_path.exists() and thumb_path.exists() and thumb_path.stat().st_size > 0:
            return str(video_path), str(thumb_path)

        # Download video
        try:
            if not (video_path.exists() and video_path.stat().st_size > 0):
                async with httpx.AsyncClient(timeout=60, follow_redirects=True) as client:
                    resp = await client.get(url)
                    if resp.status_code != 200 or len(resp.content) < 100:
                        logger.warning(f"Failed to download video {image_id}: HTTP {resp.status_code}")
                        return None
                    video_path.write_bytes(resp.content)

            # Extract thumbnail
            if _extract_video_thumbnail(video_path, thumb_path):
                return str(video_path), str(thumb_path)
            else:
                logger.warning(f"Failed to extract thumbnail for video {image_id}")
                return str(video_path), None
        except Exception as e:
            logger.warning(f"Failed to download video {image_id}: {e}")
            return None
    else:
        # For images: download 512px thumbnail
        local_path = cache_dir / f"{image_id}.{ext}"
        if local_path.exists() and local_path.stat().st_size > 0:
            return str(local_path)

        download_url = _thumbnail_url(url)
        try:
            async with httpx.AsyncClient(timeout=15, follow_redirects=True) as client:
                resp = await client.get(download_url)
                if resp.status_code == 200 and len(resp.content) > 100:
                    local_path.write_bytes(resp.content)
                    return str(local_path)
                else:
                    logger.warning(f"Failed to download {image_id}: HTTP {resp.status_code}")
                    return None
        except Exception as e:
            logger.warning(f"Failed to download {image_id}: {e}")
            return None


async def download_images(images: list[dict]) -> dict[int | str, str | tuple[str, str]]:
    """Download multiple images/videos, return {image_id: path_or_tuple} map.

    For images: {id: "path/to/image.jpg"}
    For videos: {id: ("path/to/video.mp4", "path/to/thumb.webp")}
    """
    import asyncio

    results: dict[int | str, str | tuple[str, str]] = {}
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
