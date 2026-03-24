# Handoff Report: civitai-mcp-ultimate — Session 3 (2026-03-24)

## Project Summary

**civitai-mcp-ultimate** — open-source MCP сервер для Civitai API.
Python 3.10+ / FastMCP 3.x / httpx async. **14 тулов**, bilingual (EN/RU), NSFW, image/video cache.
**PyPI**: https://pypi.org/project/civitai-mcp-ultimate/0.1.0/

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

## What's DONE in Session 3

### 1. Live MCP Test — 13/14 работают
- `get_creators` — HTTP 500 Civitai side

### 2. SKILL.md — 12 recipes + полный cheat sheet
- Top image by likes, top video by comments, top model, NSFW, anime+ComfyUI, etc.

### 3. PyPI 0.1.0 опубликован
- `pip install civitai-mcp-ultimate` / `uvx civitai-mcp-ultimate`

### 4. Glama — отправлен на review
- Smithery перешли на hosted-only, smithery.yaml добавлен но не зарегистрирован

### 5. Image/Video Cache
- Автоскачивание в `~/.civitai-mcp-cache/` (images 512px, videos original)
- Автоочистка 24ч при старте
- Локальные пути в выводе для Read tool

### 6. Undocumented API params (все проверены curl)
- `type=image/video` — content type filter
- `browsingLevel=1/2/4/8/16` — PG/PG-13/R/X/XXX bitmask
- `tag` — filter by tag (anime, animal, etc.)
- `baseModel` — filter images by base model
- `tools` — filter by tool (ComfyUI)
- `techniques` — filter by technique (txt2img)
- `hasMeta` / `madeOnSite` / `originalsOnly` / `remixesOnly` — boolean modifiers
- New base models: Qwen, SD 1.4, ZImageTurbo, Wan Video 2.2 variants

### 7. CRITICAL DISCOVERY: REST API search is broken
- `/api/v1/models?query=...` возвращает нерелевантные результаты (баг с мая 2025, issue #1729)
- Сайт и расширения используют **Meilisearch**: `https://search-new.civitai.com/multi-search`
- Публичный search-only ключ: `8c46eb2508e21db1e9828a97968d91ab1ca1caa5f70a00e88a2ba1e286603b61`
- Проверено: возвращает "[Anima] Fix Hands lora", "Flux Fix Hands" — правильные результаты
- Источник ключа: gallery-dl (`mikf/gallery-dl`) и scromfyUI_Nodes

## Architecture

```
src/civitai_mcp_ultimate/
├── server.py         # 14 @mcp.tool, lifespan + cache cleanup
├── client.py         # httpx async, Bearer auth, retry, connection recovery
├── types.py          # Enums + browsingLevel bitmask parser
├── formatters.py     # Markdown output, bilingual
├── i18n.py           # EN/RU
├── image_cache.py    # Download + cache images/videos, 24h auto-cleanup
└── tools/
    ├── models.py     # search_models(19p), get_model, versions, hash, top
    ├── images.py     # browse_images(19p!), top, model_images, gen_data
    ├── creators.py   # get_creators, get_tags
    └── downloads.py  # download_url, download_info
```

## Git Commits (session 3)

```
8e6a41f Update SKILL.md with all recipes, filters, and quirks
f41c03f Add all image filters: browsing_level, tag, base_model, tools, techniques, modifiers
e0d2314 Document undocumented type=image/video param
8099176 Use Civitai API type param instead of client-side filter
4f5affc Add content_type filter
e7a7443 Download videos too, not just images
5a19ccc Add image cache: auto-download previews + 24h auto-cleanup
292059c Add smithery.yaml
47b8a76 Add PyPI install instructions to README
12068e7 Add SKILL.md
```

## What's NOT Done

1. **Meilisearch search** — PRIORITY. REST API query broken. Need new search_models via Meilisearch
2. **PyPI 0.2.0** — 0.1.0 doesn't have session 3 features
3. **MCP restart test** — new params (content_type, browsing_level, etc.) not tested via MCP yet
4. **Tests** — pytest
5. **CI/CD** — GitHub Actions
6. **Glama review** — waiting

## Known Issues

- REST API `/v1/models?query=` — broken, returns irrelevant results (Civitai bug #1729)
- `search_models(query=..., types=..., base_model=...)` — combining query with filters returns empty
- `get_creators` — Civitai returns 500
- `get_model_images` = `browse_images(model_id)` — no author vs community split
- Windows cp1251 — need `PYTHONIOENCODING=utf-8` for Python direct testing
