# Handoff Report: civitai-mcp-ultimate — Session 4 (2026-03-24)

## Project Summary

**civitai-mcp-ultimate** — open-source MCP сервер для Civitai API.
Python 3.10+ / FastMCP 3.x / httpx async. **14 тулов**, bilingual (EN/RU), NSFW, image/video cache, **Meilisearch search**.
**PyPI**: https://pypi.org/project/civitai-mcp-ultimate/

## Links

- **GitHub**: https://github.com/timoncool/civitai-mcp-ultimate
- **PyPI**: https://pypi.org/project/civitai-mcp-ultimate/
- **Local**: `D:/Projects/TEMP/civitai-mcp-ultimate/`
- **SKILL.md**: Agent guide with 12 recipes, cheat sheet, quirks
- **API docs**: `docs/civitai-api-reference.md`

## Credentials

```
CIVITAI_API_KEY=00e54501ce1a4f64800996934dddd1c2
MEILISEARCH_KEY=8c46eb2508e21db1e9828a97968d91ab1ca1caa5f70a00e88a2ba1e286603b61
PyPI token: stored in memory (see MEMORY.md)
```

## What's DONE in Session 4

### 1. Meilisearch Search Integration (MAIN FEATURE)
- `search_models(query=...)` now uses Meilisearch for text queries
- REST API `/v1/models?query=` is broken since May 2025 (issue #1729)
- Meilisearch endpoint: `POST https://search-new.civitai.com/multi-search`
- Public search-only key built into code (source: gallery-dl, scromfyUI_Nodes)
- **Smart routing**: text query → Meilisearch, filter-only → REST API
- **Fallback**: if Meilisearch fails, falls back to REST API
- Meilisearch filters supported: `type`, `version.baseModel`, `tags.name`, `user.username`, `nsfwLevel`
- Meilisearch sort: `metrics.downloadCount`, `metrics.thumbsUpCount`, `metrics.collectedCount`, `metrics.commentCount`, `metrics.tippedAmountCount`, `createdAt`
- New module: `src/civitai_mcp_ultimate/meilisearch.py`
- **Key fix**: `query + types + base_model` now works! (was broken via REST API)

### 2. Version 0.2.0
- Bumped in pyproject.toml, __init__.py, client.py User-Agent, meilisearch.py User-Agent
- Updated README, SKILL.md, HANDOFF.md

## What's DONE in Session 3

### 1. Live MCP Test — 13/14 работают
- `get_creators` — HTTP 500 Civitai side

### 2. SKILL.md — 12 recipes + полный cheat sheet

### 3. PyPI 0.1.0 опубликован

### 4. Glama — отправлен на review

### 5. Image/Video Cache
- Автоскачивание в `~/.civitai-mcp-cache/` (images 512px, videos original)
- Автоочистка 24ч при старте

### 6. Undocumented API params (все проверены curl)
- `type=image/video`, `browsingLevel`, `tag`, `baseModel`, `tools`, `techniques`
- `hasMeta`, `madeOnSite`, `originalsOnly`, `remixesOnly`

### 7. CRITICAL DISCOVERY: REST API search is broken → FIXED via Meilisearch in session 4

## Architecture

```
src/civitai_mcp_ultimate/
├── server.py         # 14 @mcp.tool, lifespan + cache cleanup
├── client.py         # httpx async, Bearer auth, retry, connection recovery
├── meilisearch.py    # Meilisearch client + formatter (NEW in 0.2.0)
├── types.py          # Enums + browsingLevel bitmask parser
├── formatters.py     # Markdown output, bilingual
├── i18n.py           # EN/RU
├── image_cache.py    # Download + cache images/videos, 24h auto-cleanup
└── tools/
    ├── models.py     # search_models (Meilisearch + REST), get_model, versions, hash, top
    ├── images.py     # browse_images(19p!), top, model_images, gen_data
    ├── creators.py   # get_creators, get_tags
    └── downloads.py  # download_url, download_info
```

## What's NOT Done

1. **PyPI 0.2.0 publish** — code ready, need to build + upload
2. **MCP restart test** — new params (content_type, browsing_level, etc.) not tested via MCP yet
3. **Tests** — pytest
4. **CI/CD** — GitHub Actions
5. **Glama review** — waiting

## Known Issues

- REST API `/v1/models?query=` — broken, returns irrelevant results (Civitai bug #1729) → **MITIGATED via Meilisearch**
- `get_creators` — Civitai returns 500
- `get_model_images` = `browse_images(model_id)` — no author vs community split
- Windows cp1251 — need `PYTHONIOENCODING=utf-8` for Python direct testing

## Meilisearch Details

- **URL**: `https://search-new.civitai.com/multi-search`
- **Index**: `models_v9`
- **Key**: `8c46eb2508e21db1e9828a97968d91ab1ca1caa5f70a00e88a2ba1e286603b61` (public, search-only)
- **Source**: gallery-dl (`mikf/gallery-dl`), scromfyUI_Nodes — both open-source
- **Filterable**: `type`, `version.baseModel`, `tags.name`, `user.username`, `nsfwLevel`, `category.name`, `availability`, `canGenerate`, `fileFormats`, `checkpointType`, `status`, `minor`, `id`, `hashes`, `user.id`, `versions.baseModel`, `versions.hashes`, `versions.id`, `lastVersionAtUnix`, `poi`
- **Sortable**: `createdAt`, `id`, `metrics.collectedCount`, `metrics.commentCount`, `metrics.downloadCount`, `metrics.favoriteCount`, `metrics.thumbsUpCount`, `metrics.tippedAmountCount`
