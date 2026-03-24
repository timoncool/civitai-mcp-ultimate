# civitai-mcp-ultimate

[![PyPI](https://img.shields.io/pypi/v/civitai-mcp-ultimate)](https://pypi.org/project/civitai-mcp-ultimate/)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](https://opensource.org/licenses/MIT)
[![MCP](https://img.shields.io/badge/MCP-compatible-purple.svg)](https://modelcontextprotocol.io/)

**The most complete MCP server for [Civitai](https://civitai.com) API.** Search models, browse top images with prompts, download LoRAs/Checkpoints, analyze trends — all from your AI assistant.

> All API parameters verified against real Civitai API on 2026-03-24. No guessing, no copying from broken implementations.

---

## Features

- **Search models** — Checkpoints, LoRAs, ControlNets with 40+ base model filters (SD 1.5 → Flux.2)
- **Top images with prompts** — sort by reactions, comments, collections. Get full generation params
- **Download commands** — curl/PowerShell commands with auth, ComfyUI path auto-mapping
- **NSFW support** — full NSFW access with API key (None/Soft/Mature/X filtering)
- **Bilingual output** — English and Russian (`CIVITAI_MCP_LANG=ru`)
- **Async & fast** — httpx async client, retry with backoff on rate limits
- **14 tools** covering 100% of the Civitai public REST API v1

---

## Quick Start

### Claude Code
```bash
claude mcp add civitai -- uvx civitai-mcp-ultimate

# Set your API key
export CIVITAI_API_KEY=your_key_here
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
| `search_models` | Search with filters: type, base model, tag, creator, sort, period, NSFW |
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

## Другие open-source проекты

| Проект | Описание |
|--------|----------|
| [Foundation Music Lab](https://github.com/timoncool/Foundation-Music-Lab) | Генерация музыки + таймлайн-редактор |
| [VibeVoice ASR](https://github.com/timoncool/VibeVoice_ASR_portable_ru) | Распознавание речи (ASR) |
| [LavaSR](https://github.com/timoncool/LavaSR_portable) | Портативный ASR на базе Faster-Whisper |
| [Bulka](https://github.com/timoncool/Bulka) | Браузерный синтезатор live-coded музыки |
| [mock.dog](https://github.com/timoncool/mock.dog) | AI-генератор мокапов для маркетплейсов |

## License

MIT

---

> **Если проект полезен — поставьте звездочку!**

---

# README.ru.md

## civitai-mcp-ultimate

**Самый полный MCP сервер для [Civitai](https://civitai.com) API.** Ищите модели, просматривайте топовые картинки с промптами, скачивайте LoRA/Checkpoints, анализируйте тренды — прямо из AI-ассистента.

### Быстрый старт

```bash
claude mcp add civitai -- uvx civitai-mcp-ultimate
export CIVITAI_API_KEY=ваш_ключ
export CIVITAI_MCP_LANG=ru
```

### Примеры использования

```
> Найди топовые Flux LoRA за месяц
> Покажи лучшие SDXL чекпоинты
> Дай промпты для модели 12345
> Скачай эту LoRA в мой ComfyUI
> Найди NSFW LoRA для Illustrious по реакциям
```
