<div align="center">

# civitai-mcp-ultimate

**The most complete MCP server for [Civitai](https://civitai.com) API — search models, browse images with prompts, download LoRAs/Checkpoints, analyze trends.**

[![Stars](https://img.shields.io/github/stars/timoncool/civitai-mcp-ultimate?style=flat-square)](https://github.com/timoncool/civitai-mcp-ultimate/stargazers)
[![PyPI](https://img.shields.io/pypi/v/civitai-mcp-ultimate?style=flat-square)](https://pypi.org/project/civitai-mcp-ultimate/)
[![License](https://img.shields.io/github/license/timoncool/civitai-mcp-ultimate?style=flat-square)](LICENSE)
[![TRAIL](https://img.shields.io/badge/TRAIL-v2.1-6366f1?style=flat-square)](https://github.com/timoncool/trail-spec)

</div>

All from your AI assistant. 14 tools covering 100% of the Civitai public REST API v1.

> All API parameters verified against real Civitai API on 2026-03-24. No guessing, no copying from broken implementations.

---

## Features

- **Meilisearch-powered search** — fast, accurate text search (Civitai REST API search is broken since May 2025)
- **Search models** — Checkpoints, LoRAs, ControlNets with 40+ base model filters (SD 1.5 → Flux.2)
- **Top images with prompts** — sort by reactions, comments, collections. Get full generation params
- **Download commands** — curl/PowerShell commands with auth, ComfyUI path auto-mapping
- **NSFW support** — full NSFW access with API key (None/Soft/Mature/X filtering)
- **Image/video cache** — auto-download previews to `~/.civitai-mcp-cache/`, 24h auto-cleanup
- **Bilingual output** — English and Russian (`CIVITAI_MCP_LANG=ru`)
- **Async & fast** — httpx async client, retry with backoff on rate limits
- **14 tools** covering 100% of the Civitai public REST API v1

---

## Quick Start

### Install from PyPI

```bash
pip install civitai-mcp-ultimate
```

### Claude Code
```bash
claude mcp add civitai -e CIVITAI_API_KEY=your_key_here -- uvx civitai-mcp-ultimate
```

### Claude Desktop

Add to `claude_desktop_config.json`:
```json
{
  "mcpServers": {
    "civitai": {
      "command": "uvx",
      "args": ["civitai-mcp-ultimate"],
      "env": {
        "CIVITAI_API_KEY": "your_key_here"
      }
    }
  }
}
```

### pip
```bash
pip install civitai-mcp-ultimate
civitai-mcp-ultimate
```

---

## Tools

### Models (6 tools)

| Tool | Description |
|------|-------------|
| `search_models` | Search via Meilisearch (text) or REST API (filters). Type, base model, tag, creator, sort |
| `get_model` | Full model details by ID |
| `get_model_version` | Version details: files, trigger words, download URLs |
| `get_model_version_by_hash` | Find model by file hash |
| `get_top_checkpoints` | Top checkpoints by base model (SDXL, Flux, Pony...) |
| `get_top_loras` | Top LoRAs by base model |

### Images (4 tools)

| Tool | Description |
|------|-------------|
| `browse_images` | Browse images with filters and sorting |
| `get_top_images` | Top images by reactions/comments/collections |
| `get_model_images` | Example images for a model with prompts |
| `get_image_generation_data` | Full generation params from top images |

### Creators & Tags (2 tools)

| Tool | Description |
|------|-------------|
| `get_creators` | Browse/search model creators |
| `get_tags` | Browse/search model tags |

### Downloads (2 tools)

| Tool | Description |
|------|-------------|
| `get_download_url` | Authenticated download URL |
| `get_download_info` | Download commands (curl/PowerShell) + ComfyUI path mapping |

---

## Supported Filters

### Base Models (all verified working)

SD 1.5, SD 1.5 LCM, SD 1.5 Hyper, SD 2.0, SD 2.1, SDXL 1.0, SDXL Lightning, SDXL Hyper, Flux.1 S, Flux.1 D, Flux.1 Krea, Flux.1 Kontext, Flux.2 D, Flux.2 Klein 9B/4B, Pony, Pony V7, Illustrious, NoobAI, Anima, ZImageBase, AuraFlow, Chroma, HiDream, Hunyuan 1, Kolors, PixArt a/E, Lumina, CogVideoX, Hunyuan Video, LTXV/LTXV2, Mochi, Wan Video (all variants)

### Model Types
Checkpoint, LORA, LoCon, TextualInversion, Hypernetwork, Controlnet, Poses, AestheticGradient, Wildcards, MotionModule, VAE, Upscaler, Workflows, Other

### Image Sort
Most Reactions, Most Comments, Most Collected, Newest, Oldest

---

## Configuration

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `CIVITAI_API_KEY` | Recommended | — | API key for NSFW access + higher rate limits |
| `CIVITAI_MCP_LANG` | No | `en` | Output language: `en` or `ru` |
| `COMFYUI_MODELS_PATH` | No | — | ComfyUI models path for download commands |
| `MEILISEARCH_KEY` | No | built-in | Meilisearch search-only key (public, has default) |

Get your API key: [Civitai Account Settings](https://civitai.com/user/account)

---

## Examples

```
> Search for the top Flux LoRAs this month
> Show me the most popular SDXL checkpoints
> Get the best prompts for model 12345
> Give me download commands for this LoRA into my ComfyUI
> Find NSFW LoRAs for Illustrious sorted by reactions
```

---

## Development

```bash
git clone https://github.com/timoncool/civitai-mcp-ultimate
cd civitai-mcp-ultimate
pip install -e ".[dev]"
pytest
```

---

## Автор

**Nerual Dreming** ([t.me/nerual_dreming](https://t.me/nerual_dreming)) — [neuro-cartel.com](https://neuro-cartel.com) | основатель [ArtGeneration.me](https://artgeneration.me)

## Other Projects by [@timoncool](https://github.com/timoncool)

| Project | Description |
|---------|-------------|
| [telegram-api-mcp](https://github.com/timoncool/telegram-api-mcp) | Full Telegram Bot API as MCP server |
| [trail-spec](https://github.com/timoncool/trail-spec) | TRAIL — cross-MCP content tracking protocol |
| [ACE-Step Studio](https://github.com/timoncool/ACE-Step-Studio) | AI music studio — songs, vocals, covers, videos |
| [VideoSOS](https://github.com/timoncool/videosos) | AI video production in the browser |
| [Bulka](https://github.com/timoncool/Bulka) | Live-coding music platform |
| [GitLife](https://github.com/timoncool/gitlife) | Your life in weeks — interactive calendar |

## Support the Author

I build open-source software and do AI research. Most of what I create is free and available to everyone. Your donations help me keep creating without worrying about where the next meal comes from =)

**[All donation methods](https://github.com/timoncool/ACE-Step-Studio/blob/master/DONATE.md)** | **[dalink.to/nerual_dreming](https://dalink.to/nerual_dreming)** | **[boosty.to/neuro_art](https://boosty.to/neuro_art)**

- **BTC:** `1E7dHL22RpyhJGVpcvKdbyZgksSYkYeEBC`
- **ETH (ERC20):** `0xb5db65adf478983186d4897ba92fe2c25c594a0c`
- **USDT (TRC20):** `TQST9Lp2TjK6FiVkn4fwfGUee7NmkxEE7C`


## Star History

<a href="https://www.star-history.com/?repos=timoncool%2Fcivitai-mcp-ultimate&type=date&legend=top-left">
 <picture>
   <source media="(prefers-color-scheme: dark)" srcset="https://api.star-history.com/svg?repos=timoncool/civitai-mcp-ultimate&type=date&theme=dark&legend=top-left" />
   <source media="(prefers-color-scheme: light)" srcset="https://api.star-history.com/svg?repos=timoncool/civitai-mcp-ultimate&type=date&legend=top-left" />
   <img alt="Star History Chart" src="https://api.star-history.com/svg?repos=timoncool/civitai-mcp-ultimate&type=date&legend=top-left" />
 </picture>
</a>

## License

MIT
