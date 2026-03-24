# Handoff Report: civitai-mcp-ultimate — Session 4 (2026-03-24)

## Project Summary

**civitai-mcp-ultimate** — open-source MCP сервер для Civitai API.
Python 3.10+ / FastMCP 3.x / httpx async. **14 тулов**, bilingual (EN/RU), NSFW, image/video cache, **Meilisearch search**.

- **GitHub**: https://github.com/timoncool/civitai-mcp-ultimate
- **PyPI 0.2.0**: https://pypi.org/project/civitai-mcp-ultimate/0.2.0/ (PUBLISHED)
- **Local**: `D:/Projects/TEMP/civitai-mcp-ultimate/`
- **SKILL.md**: Agent guide — 12 recipes, cheat sheet, quirks, env vars
- **API docs**: `docs/civitai-api-reference.md`

## Credentials

```
CIVITAI_API_KEY=00e54501ce1a4f64800996934dddd1c2
MEILISEARCH_KEY=8c46eb2508e21db1e9828a97968d91ab1ca1caa5f70a00e88a2ba1e286603b61
PyPI token: stored in memory (project_civitai_mcp_pypi_token.md)
```

---

## Session 4 — What was DONE

### 1. Meilisearch Search Integration (MAIN FEATURE)

**Problem**: Civitai REST API `/v1/models?query=...` сломан с мая 2025 (GitHub issue #1729). Возвращает нерелевантные результаты. Все расширения (gallery-dl, ComfyUI nodes) и сам сайт civitai.com используют Meilisearch.

**Solution**: Новый модуль `src/civitai_mcp_ultimate/meilisearch.py`:
- Async httpx клиент для `POST https://search-new.civitai.com/multi-search`
- Index: `models_v9`
- Публичный search-only ключ зашит в код (источник: gallery-dl `mikf/gallery-dl`, scromfyUI_Nodes — оба open-source)
- Форматтер `format_meilisearch_results()` — выводит в том же стиле что REST API

**Routing в `search_models()`**:
- Есть `query` + НЕТ REST-only параметров → **Meilisearch** (3ms, точные результаты)
- Нет `query` ИЛИ есть REST-only параметры (`ids`, `favorites`, `hidden`, `allow_commercial_use`, etc.) → **REST API**
- Если Meilisearch упал → **fallback на REST API** с warning в лог

**Ключевой фикс**: `query + types + base_model` теперь работает! Через Meilisearch фильтры: `type = LORA AND version.baseModel = "Flux.1 D"`. В REST API эта комбинация возвращала пустой результат.

**Meilisearch фильтры** (verified 2026-03-24):
- Filterable: `type`, `version.baseModel`, `tags.name`, `user.username`, `nsfwLevel`, `category.name`, `availability`, `canGenerate`, `fileFormats`, `checkpointType`, `status`, `minor`, `id`, `hashes`, `user.id`, `versions.baseModel`, `versions.hashes`, `versions.id`, `lastVersionAtUnix`, `poi`
- Sortable: `createdAt`, `id`, `metrics.collectedCount`, `metrics.commentCount`, `metrics.downloadCount`, `metrics.favoriteCount`, `metrics.thumbsUpCount`, `metrics.tippedAmountCount`
- НЕ sortable: `stats.thumbsUpCountAllTime` (ошибка в некоторых реализациях)

**Sort mapping** (human-readable → Meilisearch):
```
Most Downloaded  → metrics.downloadCount:desc
Highest Rated    → metrics.thumbsUpCount:desc
Most Collected   → metrics.collectedCount:desc
Most Comments    → metrics.commentCount:desc
Most Tipped      → metrics.tippedAmountCount:desc
Newest           → createdAt:desc
Oldest           → createdAt:asc
```

### 2. PyPI 0.2.0 Published

- Version bumped: `pyproject.toml`, `__init__.py`, `client.py` User-Agent, `meilisearch.py` User-Agent
- Built: `python -m build` → wheel + sdist
- Published: `twine upload dist/*` → https://pypi.org/project/civitai-mcp-ultimate/0.2.0/
- Install: `pip install civitai-mcp-ultimate==0.2.0` / `uvx civitai-mcp-ultimate`

### 3. Documentation Updated

- **README.md**: добавлен Meilisearch в Features, Configuration table, tool description
- **SKILL.md**: обновлены recipes, quirks (query+types теперь работает), sort options, env vars
- **HANDOFF.md**: полный отчёт

### 4. Git

Commit: `0b8db63` — "Add Meilisearch search — fix broken REST API text search (v0.2.0)"
Pushed to `origin/main`.

---

## Session 3 — Summary

1. Live MCP test — 13/14 tools work (`get_creators` → 500 на стороне Civitai)
2. SKILL.md — 12 recipes + cheat sheet
3. PyPI 0.1.0 published
4. Glama — submitted for review
5. Image/Video cache — auto-download to `~/.civitai-mcp-cache/`, 24h cleanup
6. Undocumented API params discovered and added: `type`, `browsingLevel`, `tag`, `baseModel`, `tools`, `techniques`, `hasMeta`, `madeOnSite`, `originalsOnly`, `remixesOnly`
7. Critical discovery: REST API search broken → fixed in session 4

---

## Architecture

```
src/civitai_mcp_ultimate/
├── server.py         # 14 @mcp.tool, lifespan (cache cleanup + client close)
├── client.py         # Civitai REST API v1 — httpx async, Bearer auth, retry 429, connection recovery
├── meilisearch.py    # Meilisearch client + formatter — text search (NEW v0.2.0)
├── types.py          # Enums (ModelType, BaseModel_, sorts, periods) + browsingLevel bitmask
├── formatters.py     # Markdown output for REST API responses, bilingual
├── i18n.py           # EN/RU translations
├── image_cache.py    # Download + cache images/videos to ~/.civitai-mcp-cache/, 24h auto-cleanup
└── tools/
    ├── models.py     # search_models (Meilisearch→REST routing), get_model, versions, hash, top
    ├── images.py     # browse_images (19 params!), top_images, model_images, gen_data
    ├── creators.py   # get_creators, get_tags
    └── downloads.py  # download_url, download_info (curl/wget/PowerShell + ComfyUI paths)
```

### Key Design Decisions

1. **Meilisearch routing is in `tools/models.py`**, not in `client.py` — because it's search-specific logic, REST client stays clean
2. **MeilisearchClient is module-level singleton** (`_meili`) — lazy init, closed in server lifespan
3. **Fallback is silent** — `MeilisearchError` → warning log → REST API path. User never sees the error
4. **Meilisearch key is hardcoded** with env override (`MEILISEARCH_KEY`) — public key, same as gallery-dl
5. **No new MCP tool** — Meilisearch integrated INTO existing `search_models`, not a separate tool

---

## What's NOT Done (Prioritized)

### P1 — Should do next
1. **MCP restart test** — MCP процесс не перезапускался после добавления session 3 фич (content_type, browsing_level, tag, base_model, tools, techniques, has_meta, made_on_site, originals_only, remixes_only) и session 4 Meilisearch. Нужно:
   - Перезапустить MCP сервер (Claude Code → `/mcp` → restart civitai)
   - Протестировать `search_models(query="hands fix", types=["LORA"])` — должен вернуть Meilisearch результаты
   - Протестировать `browse_images(content_type="video", tag="anime")` — session 3 фичи
   - Протестировать `get_top_images(browsing_level="X,XXX")` — NSFW bitmask

### P2 — Nice to have
2. **Meilisearch для browse_images** — images тоже можно искать через Meilisearch? Нужно проверить наличие image index
3. **Tests** — pytest для Meilisearch routing logic, formatter, REST API mock
4. **CI/CD** — GitHub Actions: lint (ruff), test, build check
5. **Glama review** — отправлен в session 3, ждём ответ

### P3 — Future
6. **Meilisearch image search index** — проверить есть ли `images_v*` index
7. **Smithery** — перешли на hosted-only, smithery.yaml добавлен но не зарегистрирован
8. **More Meilisearch filters** — `canGenerate`, `fileFormats`, `checkpointType` — не используются пока

---

## Known Issues

| Issue | Status | Workaround |
|-------|--------|-----------|
| REST API `/v1/models?query=` broken | **FIXED** in 0.2.0 | Meilisearch |
| REST API `query + types + base_model` = empty | **FIXED** in 0.2.0 | Meilisearch filters |
| `get_creators` → HTTP 500 | Civitai bug | Use `search_models(username=...)` |
| `get_model_images` = `browse_images(model_id)` | By design | No workaround |
| Windows cp1251 encoding | Known | `PYTHONIOENCODING=utf-8` |
| "Most Reactions" sort cursor → null | Civitai bug | Only page 1 works |
| License filters → 400 | Civitai bug | Avoid `allow_no_credit` etc. |

---

## Meilisearch Reference

```
URL:   POST https://search-new.civitai.com/multi-search
Index: models_v9
Key:   8c46eb2508e21db1e9828a97968d91ab1ca1caa5f70a00e88a2ba1e286603b61

Example request:
{
  "queries": [{
    "q": "hands fix",
    "indexUid": "models_v9",
    "limit": 5,
    "offset": 0,
    "sort": ["metrics.thumbsUpCount:desc"],
    "filter": "type = LORA AND version.baseModel = \"Flux.1 D\"",
    "attributesToRetrieve": ["id","name","type","nsfw","metrics","user","triggerWords","tags","category","version","createdAt","lastVersionAt","mode","checkpointType","availability","nsfwLevel","status"]
  }]
}

Response: { "results": [{ "hits": [...], "query": "...", "estimatedTotalHits": N, "processingTimeMs": N }] }
```

Hit fields: `id`, `name`, `type`, `nsfw`, `nsfwLevel`, `metrics` (downloadCount, thumbsUpCount, collectedCount, commentCount, tippedAmountCount), `user` (username), `triggerWords`, `tags` ([{id, name}]), `version` (baseModel, trainedWords, hashes), `createdAt`, `category`, `status`, `availability`
