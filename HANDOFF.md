# Handoff Report: civitai-mcp-ultimate — Session 2 (2026-03-24)

## Project Summary

**civitai-mcp-ultimate** — open-source MCP сервер для полного доступа к Civitai API.
Python 3.10+ / FastMCP 3.x / httpx async. **14 тулов**, bilingual (EN/RU), NSFW поддержка.
**100% покрытие Civitai public REST API v1** — все 7 эндпоинтов, все параметры.

## Links

- **GitHub**: https://github.com/timoncool/civitai-mcp-ultimate
- **Local path**: `D:/Projects/TEMP/civitai-mcp-ultimate/`
- **API docs (local)**: `docs/civitai-api-reference.md` (433 строки — полная справка с quirks)
- **Design spec**: `D:/Projects/TEMP/docs/superpowers/specs/2026-03-24-civitai-mcp-ultimate-design.md`

## API Key

```
CIVITAI_API_KEY=00e54501ce1a4f64800996934dddd1c2
```

## Architecture (1444 LOC)

```
src/civitai_mcp_ultimate/
├── __init__.py          # Public exports: CivitaiClient, exceptions, __version__
├── py.typed             # PEP 561 marker
├── server.py (298)      # FastMCP server, 14 @mcp.tool, lifespan hook
├── client.py (159)      # Async httpx, Bearer auth, retry+backoff, asyncio.Lock, connection recovery
├── types.py (135)       # Enums: ModelType(14), BaseModel_(34), ImageSort(5), Period(5), NsfwLevel(4), CommercialUse(5), COMFYUI_FOLDER_MAP
├── formatters.py (277)  # Markdown formatters, bilingual, scan results, all hashes, wget
├── i18n.py (32)         # t("EN", "RU") helper, CIVITAI_MCP_LANG env
└── tools/
    ├── models.py (234)  # search_models(19 params!), get_model, get_model_version, by_hash, top_checkpoints, top_loras
    ├── images.py (138)  # browse_images(+postId, +nextCursor), get_top_images, get_model_images, get_image_generation_data
    ├── creators.py (66) # get_creators, get_tags
    └── downloads.py (91) # get_download_url, get_download_info (curl+wget+PowerShell+ComfyUI)
```

## 14 MCP Tools — Full Feature Matrix

### Models (6)
| Tool | Key Features |
|------|-------------|
| `search_models` | **19 params**: query, types, base_model, tag, username, sort, period, nsfw, ids (batch), favorites, hidden, primaryFileOnly, allowCommercialUse, supportsGeneration, allowNoCredit, allowDerivatives, allowDifferentLicenses, limit, page |
| `get_model` | Full details + mode(Archived/TakenDown) + scan results (pickle/virus) |
| `get_model_version` | Files with fp/format/size + hashes(SHA256+AutoV2) + scan results |
| `get_model_version_by_hash` | SHA256/AutoV2/CRC32/BLAKE3 |
| `get_top_checkpoints` | By base model, period, sort |
| `get_top_loras` | By base model + nsfw filter |

### Images (4)
| Tool | Key Features |
|------|-------------|
| `browse_images` | +postId, +nextCursor pagination, +createdAt, +modelVersionIds |
| `get_top_images` | Sort: Most Reactions/Comments/Collected/Newest/Oldest |
| `get_model_images` | Example images with full prompts + LoRA weights |
| `get_image_generation_data` | Only images with metadata (filtered) |

### Other (4)
| Tool | Key Features |
|------|-------------|
| `get_creators` | Search by username, pagination |
| `get_tags` | Search tags, pagination |
| `get_download_url` | Authenticated download URLs |
| `get_download_info` | curl + wget(--content-disposition) + PowerShell + ComfyUI path + all hashes + scan results |

## Code Review History (7 rounds, ~30 issues)

| Round | # | Highlights |
|-------|---|-----------|
| 1 | 9 | API key exposure, URL encoding, silent errors, copy-paste bugs |
| 2 | 2 | NameError auth_url, unhandled exceptions |
| 3 | 3 | FastMCP 3.x compat, query+page bug, zero-width Unicode |
| 4 | 7 | Missing HTTPStatusError handlers, int timestamps, phantom pydantic dep |
| 5 | 8 | asyncio.Lock, connection recovery, lifespan, py.typed, __all__ exports |
| 6 | 16 | **Full API audit**: missing enums (Workflows, ZImageBase), 9 missing params, scan results, all hashes, wget, nextCursor, postId, modelVersionIds, mode |
| 7 | 3 | 3 unreachable params in wrapper, f-string lint (F541), postId/createdAt in images |

## Git History (11 commits)

```
726ce2f Fix round 7: expose 3 missing params, fix f-strings, add image fields
871ba59 Full API coverage audit: 16 discrepancies fixed
75203a1 Add complete Civitai API v1 reference documentation
abf8b4a Fix round 5 review: connection recovery, lifecycle, packaging
6496c03 Fix re-review issues: missing HTTPStatusError handlers + curl path
0d33626 Fix 7 code review issues
020ae45 Strip invisible Unicode chars from API responses
7e3a11d Fix FastMCP 3.x compat + Civitai query pagination bug
10525cc Fix re-review issues + add timeout handling
c587035 Fix all code review issues (9 fixes)
0c29789 Initial release: civitai-mcp-ultimate v0.1.0
```

## What's DONE

1. All 14 tools implemented and tested via Python (real API calls)
2. 100% Civitai public API v1 coverage (verified against docs)
3. 7 rounds of code review — all issues fixed
4. API documentation parsed: `docs/civitai-api-reference.md` (433 lines)
5. MCP server registered in Claude Code (`claude mcp add civitai`)
6. README with author credits + cross-links to other projects
7. pyproject.toml: fastmcp>=3.0.0, dev deps, py.typed, hatchling build
8. Connection recovery: asyncio.Lock, _force_recreate_client, RemoteProtocolError
9. Lifespan hook for clean httpx client shutdown
10. Output: all hashes, scan results, wget, postId, createdAt, modelVersionIds, nextCursor

## What's NOT Done Yet

1. **Live MCP test** — рестартнуть Claude Code, вызвать тулы через MCP протокол (сейчас тестировали через Python)
2. **SKILL.md** — инструкции для агента как виртуозно использовать все 14 тулов
3. **PyPI publish** — `hatch build && hatch publish` (pyproject.toml готов)
4. **Smithery/Glama** — зарегистрировать в каталогах MCP серверов
5. **Image display** — скачивать картинки и показывать через Read tool (отложено)
6. **Tests** — pytest с мокнутыми API responses
7. **CI/CD** — GitHub Actions

## MCP Connection (already configured)

```bash
# Уже добавлено в Claude Code local config:
claude mcp add civitai -e CIVITAI_API_KEY=00e54501ce1a4f64800996934dddd1c2 -- python -m civitai_mcp_ultimate.server
```

После рестарта Claude Code тулы появятся как `mcp__civitai__search_models` и т.д.

## Environment Variables

```bash
CIVITAI_API_KEY=00e54501ce1a4f64800996934dddd1c2  # NSFW + higher rate limits
CIVITAI_MCP_LANG=ru                                 # Optional: en (default) | ru
COMFYUI_MODELS_PATH=                                # Optional: ComfyUI path mapping
```

## Known Limitations

- `allowNoCredit`/`allowDerivatives`/`allowDifferentLicenses` — Civitai API returns 400 (Zod expects boolean, gets string). Exposed but may not work.
- `Most Reactions` sort — cursor pagination bug in Civitai API (null cursor)
- `/creators` endpoint slow (30s+) — timeout handling added
- i18n frozen at import time (MCP server starts fresh each time — OK)
- No image generation (use official civitai-py SDK)

## Research (from Session 1)

Analyzed 4 existing MCP servers + 3 SDKs. Wrote from scratch: existing servers had unverified params, would need 80%+ rewrite.

## Key Files

| File | What |
|------|------|
| `docs/civitai-api-reference.md` | Full API reference with quirks |
| `src/civitai_mcp_ultimate/server.py` | All 14 tool declarations |
| `src/civitai_mcp_ultimate/types.py` | All enums (model types, base models, etc.) |
| `pyproject.toml` | Packaging config, ready for PyPI |
| `README.md` | Docs + credits + cross-links |
