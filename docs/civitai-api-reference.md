# Civitai REST API v1 — Complete Reference

> Source: https://developer.civitai.com/docs/api/public-rest + https://github.com/civitai/civitai/wiki/REST-API-Reference
> Parsed: 2026-03-24
> Status: "This is still in active development and will be updated once more endpoints are made available."

## Base URL

```
https://civitai.com/api/v1
```

## Authentication

Two methods:

```
# Header (recommended)
Authorization: Bearer {api_key}

# Query parameter
?token={api_key}
```

API keys: https://civitai.com/user/account

Authentication is required for:
- NSFW content access (Mature/X levels)
- Downloading creator-restricted models
- Favorites/hidden filters
- Higher rate limits

---

## Endpoints

### 1. GET /api/v1/models

Search and filter AI models.

#### Query Parameters

| Name | Type | Default | Description |
|------|------|---------|-------------|
| `limit` | number | 100 | Results per page (1-100) |
| `page` | number | 1 | Page number. **Cannot be used with `query`** — Civitai uses cursor-based pagination for text search |
| `query` | string | | Search by model name |
| `tag` | string | | Filter by tag name |
| `username` | string | | Filter by creator username |
| `types` | enum[] | | Model types (see below) |
| `sort` | enum | | `Highest Rated`, `Most Downloaded`, `Newest` |
| `period` | enum | | `AllTime`, `Year`, `Month`, `Week`, `Day` |
| `nsfw` | boolean | | `false` = exclude NSFW |
| `favorites` | boolean | | Auth user's favorites (requires token) |
| `hidden` | boolean | | Auth user's hidden models (requires token) |
| `primaryFileOnly` | boolean | | Include only primary file per model |
| `allowNoCredit` | boolean | | Filter by credit requirements |
| `allowDerivatives` | boolean | | Filter by derivative permissions |
| `allowDifferentLicenses` | boolean | | Filter by license flexibility |
| `allowCommercialUse` | enum[] | | `None`, `Image`, `Rent`, `RentCivit`, `Sell` |
| `supportsGeneration` | boolean | | Filter generation-capable models |
| `ids` | number[] | | Specific model IDs |
| `baseModels` | string[] | | Base model filter (see below) |

#### Model Types (enum)

Documented: `Checkpoint`, `TextualInversion`, `Hypernetwork`, `AestheticGradient`, `LORA`, `Controlnet`, `Poses`

Undocumented but working: `LoCon`, `VAE`, `Upscaler`, `Wildcards`, `MotionModule`, `Other`, `Workflows`

#### Base Models (verified working)

Standard: `SD 1.5`, `SDXL 1.0`, `Flux.1 D`, `Flux.2 D`, `Pony`, `Pony V7`
Anime: `Illustrious`, `NoobAI`
Other: `Chroma`, `HiDream`, `AuraFlow`, `Kolors`, `Hunyuan 1`
Speed: `SDXL Lightning`, `SDXL Hyper`, `SD 1.5 LCM`, `SD 1.5 Hyper`
New: `ZImageBase`

#### Response Schema

```json
{
  "items": [
    {
      "id": 12345,
      "name": "Model Name",
      "description": "<p>HTML description</p>",
      "type": "Checkpoint",
      "nsfw": false,
      "tags": ["tag1", "tag2"],
      "mode": null,
      "creator": {
        "username": "creator_name",
        "image": "https://..."
      },
      "stats": {
        "downloadCount": 1000,
        "favoriteCount": 500,
        "commentCount": 50,
        "ratingCount": 100,
        "rating": 4.8,
        "thumbsUpCount": 500
      },
      "modelVersions": [
        {
          "id": 67890,
          "name": "v1.0",
          "description": "Changelog",
          "baseModel": "SDXL 1.0",
          "createdAt": "2024-01-01T00:00:00.000Z",
          "publishedAt": "2024-01-01T00:00:00.000Z",
          "downloadUrl": "https://civitai.com/api/download/models/67890",
          "trainedWords": ["trigger1", "trigger2"],
          "files": [
            {
              "name": "model.safetensors",
              "sizeKB": 2048000,
              "downloadUrl": "https://civitai.com/api/download/models/67890",
              "primary": true,
              "pickleScanResult": "Success",
              "virusScanResult": "Success",
              "scannedAt": "2024-01-01T00:00:00.000Z",
              "metadata": {
                "fp": "fp16",
                "size": "pruned",
                "format": "SafeTensor"
              },
              "hashes": {
                "AutoV1": "...",
                "AutoV2": "...",
                "SHA256": "...",
                "CRC32": "...",
                "BLAKE3": "..."
              }
            }
          ],
          "images": [
            {
              "id": "111",
              "url": "https://image.civitai.com/...",
              "nsfw": "None",
              "width": 1024,
              "height": 1024,
              "hash": "blurhash_string",
              "meta": {
                "prompt": "...",
                "negativePrompt": "...",
                "steps": 20,
                "sampler": "Euler",
                "cfgScale": 7,
                "seed": 12345,
                "Size": "1024x1024",
                "Model": "model_name",
                "resources": [
                  {"type": "lora", "name": "lora_name", "weight": 0.8}
                ]
              }
            }
          ],
          "stats": {
            "downloadCount": 500,
            "ratingCount": 50,
            "rating": 4.9
          }
        }
      ]
    }
  ],
  "metadata": {
    "totalItems": 1000,
    "currentPage": 1,
    "pageSize": 100,
    "totalPages": 10,
    "nextPage": "https://civitai.com/api/v1/models?page=2",
    "prevPage": null
  }
}
```

---

### 2. GET /api/v1/models/:modelId

Get detailed info about a specific model.

**Path Parameters**: `modelId` (number)

**Response**: Same as single item from `/models`

---

### 3. GET /api/v1/model-versions/:modelVersionId

Get model version details.

**Path Parameters**: `modelVersionId` (number)

**Response**: Single model version object (same as `modelVersions[]` item)

---

### 4. GET /api/v1/model-versions/by-hash/:hash

Find model version by file hash.

**Path Parameters**: `hash` (string) — SHA256, AutoV2, CRC32, or BLAKE3

**Response**: Single model version object

---

### 5. GET /api/v1/images

Browse AI-generated images.

#### Query Parameters

| Name | Type | Default | Description |
|------|------|---------|-------------|
| `limit` | number | 100 | Results per page (0-200) |
| `postId` | number | | Filter by post ID |
| `modelId` | number | | Filter by model (gallery) |
| `modelVersionId` | number | | Filter by model version |
| `username` | string | | Filter by creator |
| `nsfw` | enum | | `None`, `Soft`, `Mature`, `X` |
| `sort` | enum | | `Most Reactions`, `Most Comments`, `Most Collected`, `Newest`, `Oldest` |
| `period` | enum | | `AllTime`, `Year`, `Month`, `Week`, `Day` |
| `page` | number | | Page number |

**Note**: Image endpoint uses cursor-based pagination since July 2, 2023. `metadata.nextCursor` is provided.

**Additional sort values** (undocumented but working): `Most Collected`, `Oldest`

#### Response Schema

```json
{
  "items": [
    {
      "id": 12345,
      "url": "https://image.civitai.com/xG1nkqKTMzGDvpLrqFT7WA/.../original=true/...",
      "hash": "blurhash_string",
      "width": 1024,
      "height": 1536,
      "nsfw": false,
      "nsfwLevel": "None",
      "createdAt": "2024-01-01T00:00:00.000Z",
      "postId": 1000,
      "modelVersionIds": [67890],
      "username": "creator_name",
      "stats": {
        "cryCount": 0,
        "laughCount": 5,
        "likeCount": 10,
        "heartCount": 50,
        "commentCount": 3
      },
      "meta": {
        "prompt": "full prompt text...",
        "negativePrompt": "negative prompt...",
        "steps": 20,
        "sampler": "Euler",
        "cfgScale": 7,
        "seed": 12345,
        "Size": "1024x1536",
        "Model": "model_name",
        "Clip skip": "2",
        "resources": [
          {"type": "lora", "name": "lora_name", "weight": 0.8}
        ]
      }
    }
  ],
  "metadata": {
    "nextCursor": 12344,
    "currentPage": 1,
    "pageSize": 100,
    "nextPage": "https://civitai.com/api/v1/images?cursor=12344"
  }
}
```

---

### 6. GET /api/v1/creators

Browse model creators.

#### Query Parameters

| Name | Type | Default | Description |
|------|------|---------|-------------|
| `limit` | number | 20 | Results per page (0-200, 0=all) |
| `page` | number | 1 | Page number |
| `query` | string | | Filter by username |

#### Response Schema

```json
{
  "items": [
    {
      "username": "creator_name",
      "modelCount": 42,
      "link": "https://civitai.com/api/v1/models?username=creator_name"
    }
  ],
  "metadata": {
    "totalItems": 1000,
    "currentPage": 1,
    "pageSize": 20,
    "totalPages": 50,
    "nextPage": "...",
    "prevPage": "..."
  }
}
```

---

### 7. GET /api/v1/tags

Browse model tags.

#### Query Parameters

| Name | Type | Default | Description |
|------|------|---------|-------------|
| `limit` | number | 20 | Results per page |
| `page` | number | 1 | Page number |
| `query` | string | | Search tags |

#### Response Schema

```json
{
  "items": [
    {
      "name": "anime",
      "modelCount": 5000,
      "link": "https://civitai.com/api/v1/models?tag=anime"
    }
  ],
  "metadata": { "..." }
}
```

---

## Download URLs

Model files are downloaded via:
```
https://civitai.com/api/download/models/{modelVersionId}
```

Authentication:
```bash
# curl
curl -L -H "Authorization: Bearer $CIVITAI_API_KEY" -o "model.safetensors" "https://civitai.com/api/download/models/67890"

# wget (note --content-disposition flag)
wget --content-disposition -H "Authorization: Bearer $CIVITAI_API_KEY" "https://civitai.com/api/download/models/67890"

# PowerShell
Invoke-WebRequest -Uri "https://civitai.com/api/download/models/67890" -Headers @{"Authorization"="Bearer $env:CIVITAI_API_KEY"} -OutFile "model.safetensors"
```

---

## Rate Limits

- Unauthenticated: ~2 req/sec (undocumented, varies)
- Authenticated: Higher limits (exact values undocumented)
- Response code: 429 Too Many Requests
- Recommended: exponential backoff with 2/4/8s delays

---

## NSFW Levels

| Level | Description |
|-------|-------------|
| `None` | Safe for work |
| `Soft` | Suggestive |
| `Mature` | Adult content |
| `X` | Explicit content |

Accessing `Mature` and `X` content requires Bearer authentication.

---

## Known API Quirks (verified 2026-03-24)

1. **`page` + `query` conflict**: Cannot use `page` param with `query` search. API returns 400. Use cursor-based pagination for text search.
2. **`Most Reactions` sort cursor bug**: Returns null cursor, preventing pagination beyond first page.
3. **`/creators` is slow**: Can take 30+ seconds to respond.
4. **Zero-width characters**: API returns invisible Unicode chars (\u200b etc.) in some tag names.
5. **`baseModels` is array**: Must be sent as array, not string: `baseModels[]=SDXL+1.0`
6. **`types` is array**: Same — `types[]=Checkpoint&types[]=LORA`
7. **Image `meta` can be null**: Not all images have generation metadata.
8. **`createdAt` format varies**: Sometimes ISO string, sometimes other formats.

---

## Endpoints NOT in Public API (as of 2026-03-24)

These exist in the Civitai web app but are NOT part of the public REST API:
- Collections (GET /api/v1/collections) — NOT public
- Bounties — NOT public
- Posts — NOT public
- Articles — NOT public
- User profiles — NOT public
- Comments — NOT public
- Notifications — NOT public
- Generation (use official `civitai-py` SDK instead)

---

## Coverage by civitai-mcp-ultimate

| Endpoint | MCP Tool(s) | Status |
|----------|-------------|--------|
| GET /models | `search_models`, `get_top_checkpoints`, `get_top_loras` | Covered |
| GET /models/:id | `get_model` | Covered |
| GET /model-versions/:id | `get_model_version` | Covered |
| GET /model-versions/by-hash/:hash | `get_model_version_by_hash` | Covered |
| GET /images | `browse_images`, `get_top_images`, `get_model_images`, `get_image_generation_data` | Covered |
| GET /creators | `get_creators` | Covered |
| GET /tags | `get_tags` | Covered |
| Download URLs | `get_download_url`, `get_download_info` | Covered |

**Result: 100% of public API v1 endpoints are covered by 14 MCP tools.**
