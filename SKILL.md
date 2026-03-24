---
name: civitai-mcp-ultimate
description: Ultimate MCP server for Civitai — search models, browse top images with prompts, download LoRAs/Checkpoints, analyze trends. Use when user asks about AI models, LoRAs, checkpoints, Stable Diffusion, Flux, image generation prompts, or Civitai.
---

# Civitai MCP Ultimate — 14 Tools Reference

## Quick Tool Map

| Goal | Tool | Key Params |
|------|------|-----------|
| Find models by name | `search_models` | `query`, `types`, `base_model` |
| Find models by creator | `search_models` | `username` (most reliable) |
| Batch fetch by IDs | `search_models` | `ids=[123, 456]` |
| Full model details | `get_model` | `model_id` |
| Version details + hashes | `get_model_version` | `version_id` |
| Identify model from file | `get_model_version_by_hash` | SHA256/AutoV2/CRC32/BLAKE3 |
| Top checkpoints | `get_top_checkpoints` | `base_model`, `period` |
| Top LoRAs | `get_top_loras` | `base_model`, `nsfw` |
| Browse images | `browse_images` | `model_id`, `username`, `nsfw` |
| Trending images | `get_top_images` | `sort`, `period` |
| Example images for model | `get_model_images` | `model_id` |
| Extract best prompts | `get_image_generation_data` | `model_id` |
| Download URL | `get_download_url` | `version_id` |
| Download commands | `get_download_info` | `model_id`, `comfyui_path` |

## Workflows

### 1. Find the Best LoRA for a Style

```
get_top_loras(base_model="Flux.1 D", period="Week", limit=10)
  -> pick model_id
get_model(model_id=ID)
  -> read trigger words, description, versions
get_image_generation_data(model_id=ID, limit=5)
  -> extract prompts, settings, LoRA weight
get_download_info(model_id=ID, comfyui_path="C:/ComfyUI/models")
  -> ready-to-paste curl/wget/PowerShell
```

### 2. Prompt Mining (Steal Great Prompts)

```
get_top_images(sort="Most Reactions", period="Week", limit=10)
  -> find images with best reactions
  -> each image has: prompt, negative prompt, steps, CFG, sampler, seed, LoRAs
```

Or for a specific model:
```
get_image_generation_data(model_id=ID, sort="Most Reactions", limit=5)
  -> only images WITH metadata (filtered)
```

### 3. Download Model to ComfyUI

```
get_download_info(model_id=858800, comfyui_path="D:/ComfyUI/models")
```
Returns:
- curl command with auth header
- wget with `--content-disposition`
- PowerShell `Invoke-WebRequest`
- Target folder (auto-mapped: LORA -> loras/, Checkpoint -> checkpoints/)
- All hashes (SHA256, AutoV2, CRC32, BLAKE3)
- Scan results (pickle/virus)

### 4. Identify Unknown .safetensors File

```
get_model_version_by_hash(hash="E837144C55")  # AutoV2 hash
  -> returns model name, version, trigger words, base model
```

### 5. Compare Models by Popularity

```
get_top_checkpoints(base_model="Flux.1 D", period="Month", sort="Most Downloaded", limit=20)
get_top_checkpoints(base_model="SDXL 1.0", period="Month", sort="Most Downloaded", limit=20)
```

### 6. Find NSFW Content

Requires `CIVITAI_API_KEY` env var.
```
get_top_loras(base_model="Pony", nsfw=true, period="Week")
browse_images(nsfw="X", sort="Most Reactions", period="Week")
```

## Enum Cheat Sheet

### Model Types
`Checkpoint`, `LORA`, `LoCon`, `TextualInversion`, `Hypernetwork`, `Controlnet`, `Poses`, `VAE`, `Upscaler`, `Wildcards`, `MotionModule`, `Workflows`, `Other`

### Base Models (most common)
| Category | Values |
|----------|--------|
| SD 1.x | `SD 1.5`, `SD 1.5 LCM`, `SD 1.5 Hyper` |
| SDXL | `SDXL 1.0`, `SDXL Lightning`, `SDXL Hyper` |
| Flux | `Flux.1 S`, `Flux.1 D`, `Flux.1 Kontext`, `Flux.2 D` |
| Anime | `Pony`, `Pony V7`, `Illustrious`, `NoobAI`, `Anima` |
| Other | `Chroma`, `HiDream`, `Hunyuan 1`, `Kolors`, `ZImageBase` |
| Video | `CogVideoX`, `Hunyuan Video`, `LTXV`, `Wan Video 14B t2v` |

### Sort
- Models: `Highest Rated`, `Most Downloaded`, `Newest`
- Images: `Most Reactions`, `Most Comments`, `Most Collected`, `Newest`, `Oldest`

### Period
`AllTime`, `Year`, `Month`, `Week`, `Day`

### NSFW Levels
`None`, `Soft`, `Mature`, `X`

### ComfyUI Folder Mapping
`Checkpoint` -> `checkpoints/`, `LORA`/`LoCon` -> `loras/`, `TextualInversion` -> `embeddings/`, `Controlnet` -> `controlnet/`, `VAE` -> `vae/`, `Upscaler` -> `upscale_models/`

## Known Quirks

1. **search_models + query + types**: Civitai uses cursor pagination when `query` is set, `page` param is ignored. Don't combine `query` with `page > 1`.
2. **search_models by username**: Most reliable search method. Always prefer `username="CreatorName"` over `query`.
3. **get_creators**: Civitai endpoint is slow (30s+) and may return 500. Not critical — use `search_models(username=...)` instead.
4. **"Most Reactions" sort**: May have cursor pagination bugs on Civitai side (null cursor). Fallback to "Most Downloaded".
5. **License filters** (`allow_no_credit`, `allow_derivatives`): Civitai API may return 400 (Zod validation). Exposed but unreliable.
6. **Image generation data**: Not all images have metadata. `get_image_generation_data` filters to only images WITH prompts.

## Environment Variables

```
CIVITAI_API_KEY     — Civitai API key (NSFW access + higher rate limits)
CIVITAI_MCP_LANG    — en (default) | ru
COMFYUI_MODELS_PATH — default ComfyUI models path for download_info
```
