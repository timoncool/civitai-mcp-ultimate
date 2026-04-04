"""Persistent history of downloaded/used Civitai resources.

Tracks which models were downloaded and which images were used (e.g. sent to Pikabu),
so the system can avoid recommending duplicates.

Storage: <project_root>/data/history.json
Override with CIVITAI_MCP_DATA_DIR env var.
"""

import json
import logging
import os
import time
from pathlib import Path
from typing import Optional

logger = logging.getLogger(__name__)

# Project root = 3 levels up from this file (src/civitai_mcp_ultimate/history.py)
_PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent

# Data dir: project_root/data/ by default, override with env var
HISTORY_DIR = Path(os.getenv("CIVITAI_MCP_DATA_DIR", str(_PROJECT_ROOT / "data")))
HISTORY_FILE = HISTORY_DIR / "history.json"


def _ensure_dir() -> None:
    HISTORY_DIR.mkdir(parents=True, exist_ok=True)


def _load() -> dict:
    """Load history from disk. Returns empty structure if missing/corrupt."""
    if not HISTORY_FILE.exists():
        return {"downloads": {}, "images": {}}
    try:
        data = json.loads(HISTORY_FILE.read_text(encoding="utf-8"))
        # Ensure both keys exist
        data.setdefault("downloads", {})
        data.setdefault("images", {})
        return data
    except (json.JSONDecodeError, OSError) as e:
        logger.warning(f"History file corrupt, resetting: {e}")
        return {"downloads": {}, "images": {}}


def _save(data: dict) -> None:
    """Write history to disk."""
    _ensure_dir()
    HISTORY_FILE.write_text(
        json.dumps(data, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )


# ── Downloads ──────────────────────────────────────────────────


def record_download(
    version_id: int,
    model_id: Optional[int] = None,
    model_name: Optional[str] = None,
    filename: Optional[str] = None,
) -> None:
    """Record that a model version was downloaded / download info was requested."""
    data = _load()
    key = str(version_id)
    data["downloads"][key] = {
        "version_id": version_id,
        "model_id": model_id,
        "model_name": model_name,
        "filename": filename,
        "timestamp": time.time(),
        "iso": time.strftime("%Y-%m-%d %H:%M:%S"),
    }
    _save(data)
    logger.info(f"History: recorded download version_id={version_id}")


def is_downloaded(version_id: int) -> bool:
    """Check if a version was already downloaded."""
    data = _load()
    return str(version_id) in data["downloads"]


def get_downloaded() -> list[dict]:
    """Get all downloaded versions, newest first."""
    data = _load()
    items = list(data["downloads"].values())
    items.sort(key=lambda x: x.get("timestamp", 0), reverse=True)
    return items


# ── Images ─────────────────────────────────────────────────────


def record_image(
    image_id: int,
    action: str = "browsed",
    context: Optional[str] = None,
    url: Optional[str] = None,
) -> None:
    """Record that an image was used.

    action: "browsed", "sent_to_pikabu", "sent_to_telegram", "used_prompt", etc.
    context: free-text note, e.g. "posted to pikabu community X".
    """
    data = _load()
    key = str(image_id)
    existing = data["images"].get(key, {})

    # Keep history of actions (append, don't overwrite)
    actions = existing.get("actions", [])
    actions.append({
        "action": action,
        "context": context,
        "timestamp": time.time(),
        "iso": time.strftime("%Y-%m-%d %H:%M:%S"),
    })

    data["images"][key] = {
        "image_id": image_id,
        "url": url or existing.get("url"),
        "first_seen": existing.get("first_seen", time.time()),
        "actions": actions,
    }
    _save(data)
    logger.info(f"History: recorded image {image_id} action={action}")


def record_images_batch(image_ids: list[int], action: str = "browsed") -> None:
    """Record multiple images at once (batch, single disk write)."""
    if not image_ids:
        return
    data = _load()
    now = time.time()
    iso = time.strftime("%Y-%m-%d %H:%M:%S")
    for image_id in image_ids:
        key = str(image_id)
        existing = data["images"].get(key, {})
        actions = existing.get("actions", [])
        actions.append({"action": action, "timestamp": now, "iso": iso})
        data["images"][key] = {
            "image_id": image_id,
            "url": existing.get("url"),
            "first_seen": existing.get("first_seen", now),
            "actions": actions,
        }
    _save(data)
    logger.info(f"History: recorded {len(image_ids)} images action={action}")


def is_image_used(image_id: int) -> bool:
    """Check if an image was already used."""
    data = _load()
    return str(image_id) in data["images"]


def get_used_image_ids() -> set[int]:
    """Get set of all used image IDs."""
    data = _load()
    return {int(k) for k in data["images"]}


def get_used_images() -> list[dict]:
    """Get all used images with their action history, newest first."""
    data = _load()
    items = list(data["images"].values())
    items.sort(key=lambda x: x.get("first_seen", 0), reverse=True)
    return items


# ── General ────────────────────────────────────────────────────


def get_full_history() -> dict:
    """Get full history data."""
    return _load()


def get_stats() -> dict:
    """Get summary stats."""
    data = _load()
    return {
        "total_downloads": len(data["downloads"]),
        "total_images": len(data["images"]),
    }


def clear_history(what: str = "all") -> str:
    """Clear history. what: 'all', 'downloads', 'images'."""
    data = _load()
    if what == "all":
        data = {"downloads": {}, "images": {}}
    elif what == "downloads":
        data["downloads"] = {}
    elif what == "images":
        data["images"] = {}
    else:
        return f"Unknown category: {what}. Use 'all', 'downloads', or 'images'."
    _save(data)
    return f"History cleared: {what}"
