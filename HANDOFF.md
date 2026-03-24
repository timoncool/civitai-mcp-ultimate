# Handoff Report: civitai-mcp-ultimate

## Project Summary

**civitai-mcp-ultimate** — open-source MCP сервер для полного доступа к Civitai API.
Написан с нуля на Python + FastMCP. 15 тулов, bilingual (EN/RU), NSFW поддержка.

## Links

- **GitHub**: https://github.com/timoncool/civitai-mcp-ultimate
- **Local path**: `D:/Projects/TEMP/civitai-mcp-ultimate/`
- **Design spec**: `D:/Projects/TEMP/docs/superpowers/specs/2026-03-24-civitai-mcp-ultimate-design.md`
- **Civitai API docs**: https://developer.civitai.com/docs/api/public-rest
- **Civitai API wiki**: https://github.com/civitai/civitai/wiki/REST-API-Reference

## API Key

```
CIVITAI_API_KEY=00e54501ce1a4f64800996934dddd1c2
```

## Stack

- Python 3.10+ / FastMCP / httpx (async) / Pydantic v2
- pyproject.toml с hatchling build
- Установка: `pip install -e .` (local) или `uvx civitai-mcp-ultimate` (после PyPI publish)

## Architecture

```
src/civitai_mcp_ultimate/
├── server.py          # FastMCP server, 15 @mcp.tool registrations
├── client.py          # Async httpx client, Bearer auth, retry on 429/timeout
├── types.py           # Enums: ModelType, BaseModel_, ImageSort, Period, NsfwLevel, COMFYUI_FOLDER_MAP
├── formatters.py      # Markdown formatters (bilingual via i18n.py)
├── i18n.py            # t("EN", "RU") helper, CIVITAI_MCP_LANG env var
└── tools/
    ├── models.py      # search_models, get_model, get_model_version, get_model_version_by_hash, get_top_checkpoints, get_top_loras
    ├── images.py      # browse_images, get_top_images, get_model_images, get_image_generation_data
    ├── creators.py    # get_creators, get_tags
    └── downloads.py   # get_download_url, get_download_info
```

## 15 Tools

### Models (6)
| Tool | Purpose |
|------|---------|
| `search_models` | Search with filters: type, base_model, tag, username, sort, period, nsfw |
| `get_model` | Full model details by ID |
| `get_model_version` | Version details: files, trigger words, download URLs |
| `get_model_version_by_hash` | Find model by file hash |
| `get_top_checkpoints` | Top checkpoints by base model (SDXL, Flux, Pony...) |
| `get_top_loras` | Top LoRAs by base model |

### Images (4)
| Tool | Purpose |
|------|---------|
| `browse_images` | Browse with sort: Most Reactions/Comments/Collected/Newest/Oldest |
| `get_top_images` | Top images by reactions/comments — best for prompt mining |
| `get_model_images` | Example images for a model with full prompts |
| `get_image_generation_data` | Full gen params from top images (only with metadata) |

### Creators & Tags (2)
| Tool | Purpose |
|------|---------|
| `get_creators` | Browse/search creators |
| `get_tags` | Browse/search tags |

### Downloads (2)
| Tool | Purpose |
|------|---------|
| `get_download_url` | Authenticated download URL |
| `get_download_info` | curl/PowerShell commands + ComfyUI path mapping |

## API Verification Results (2026-03-24)

All params tested with real API calls:

- **baseModels**: ALL work (SD 1.5, SDXL 1.0, Flux.1 D, Flux.2 D, Pony, Pony V7, Illustrious, NoobAI, Chroma, HiDream, AuraFlow, Kolors, Hunyuan 1, SDXL Lightning/Hyper, SD 1.5 LCM/Hyper)
- **Model types**: ALL work (including undocumented LoCon, VAE, Upscaler, Wildcards, MotionModule, Other)
- **Image sort**: ALL 5 work (Most Reactions, Most Comments, Most Collected, Newest, Oldest)
- **NSFW**: Works with Bearer auth (None/Soft/Mature/X)
- **Bearer auth**: Works (not query param token)

## Code Review History

### Round 1 — 9 issues found, all fixed:
1. CRITICAL: API key exposed in output → uses $CIVITAI_API_KEY placeholder now
2. CRITICAL: Manual URL encoding → stdlib urlencode(doseq=True)
3. CRITICAL: max_retries_exceeded silently swallowed → raises CivitaiRateLimitError
4. HIGH: Redundant second API call in get_model_version_by_hash → formats directly
5. HIGH: L_DOWNLOADS copy-paste bug → fixed
6. MEDIUM: baseModels string → list
7. LOW: asyncio import inside function → top-level
8. MEDIUM: KeyError on missing name/id → .get()
9. MEDIUM: TypeError on None createdAt → or-chaining

### Round 2 — 2 new issues found, all fixed:
1. CRITICAL: NameError auth_url in ComfyUI curl command → uses url + Bearer header
2. IMPORTANT: Unhandled exceptions in images/creators/tags tools → all now catch CivitaiRateLimitError, CivitaiNotFoundError, httpx.TimeoutException

## Git History

```
10525cc Fix re-review issues + add timeout handling
c587035 Fix all code review issues (9 fixes)
0c29789 Initial release: civitai-mcp-ultimate v0.1.0
```

## What's NOT Done Yet

1. **Connect to Claude Code** — `claude mcp add civitai -- python -m civitai_mcp_ultimate.server`
2. **Test all 15 tools live** through MCP (not just Python calls)
3. **Image display via Read tool** — show image previews (like Runware MCP does)
4. **SKILL.md** — usage instructions for Claude
5. **PyPI publish** — `hatch build && hatch publish`
6. **Smithery/Glama registration**
7. **Tests** — pytest with mocked API responses
8. **CI/CD** — GitHub Actions for lint + test + publish

## Environment Variables

```bash
CIVITAI_API_KEY=00e54501ce1a4f64800996934dddd1c2  # Required for NSFW + higher rate limits
CIVITAI_MCP_LANG=ru                                 # Optional: en (default) | ru
COMFYUI_MODELS_PATH=                                # Optional: for download_info ComfyUI mapping
```

## Known Limitations

- Civitai API is read-only (no POST endpoints public yet)
- `/creators` endpoint is slow (30s+ sometimes) — timeout handling added
- `Most Reactions` sort has cursor pagination bug in Civitai API (returns null cursor)
- i18n labels are set at import time (not dynamic — restart needed to change language)
- No image generation (use official civitai-py SDK separately)

## Research Done

### Existing MCP servers analyzed:
1. **Cicatriiz/civitai-mcp-server** (TypeScript) — 14 tools, 10 stars, prototype quality, no tests
2. **waura/civitai-mcp-server** (Python/FastMCP) — 15 tools, tests, but unverified enum values
3. **Yi-luo-hua/civitai-mcp-server** (TypeScript) — 6 tools, best UX (mutex, sanitization, formatters)
4. **mrsions/ImageSearch-MCP** (JS) — only image search, uses unofficial API

### Official Civitai SDKs:
- **civitai-py** (PyPI) — only image generation, not REST API browse
- **civitai** (npm) — only image generation
- **civitai-api** (PyPI, unofficial) — sync+async REST client

### Decision: wrote from scratch because:
- Existing servers had unverified API params
- Would need to rewrite 80%+ of any fork
- 400 lines of code = no time savings from forking
- Clean architecture for our use cases
