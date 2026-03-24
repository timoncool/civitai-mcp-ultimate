"""Civitai API types — enums and Pydantic models.

All enum values verified against real Civitai API on 2026-03-24.
"""

from enum import Enum


class ModelType(str, Enum):
    """Model types supported by Civitai API."""

    CHECKPOINT = "Checkpoint"
    LORA = "LORA"
    LOCON = "LoCon"
    TEXTUAL_INVERSION = "TextualInversion"
    HYPERNETWORK = "Hypernetwork"
    CONTROLNET = "Controlnet"
    POSES = "Poses"
    AESTHETIC_GRADIENT = "AestheticGradient"
    WILDCARDS = "Wildcards"
    MOTION_MODULE = "MotionModule"
    VAE = "VAE"
    UPSCALER = "Upscaler"
    WORKFLOWS = "Workflows"
    OTHER = "Other"


class BaseModel_(str, Enum):
    """Base model filters. All verified working via API 2026-03-24."""

    # Stable Diffusion 1.x
    SD_15 = "SD 1.5"
    SD_15_LCM = "SD 1.5 LCM"
    SD_15_HYPER = "SD 1.5 Hyper"
    # Stable Diffusion 2.x
    SD_20 = "SD 2.0"
    SD_21 = "SD 2.1"
    # SDXL
    SDXL_10 = "SDXL 1.0"
    SDXL_LIGHTNING = "SDXL Lightning"
    SDXL_HYPER = "SDXL Hyper"
    # Flux
    FLUX_1_S = "Flux.1 S"
    FLUX_1_D = "Flux.1 D"
    FLUX_1_KREA = "Flux.1 Krea"
    FLUX_1_KONTEXT = "Flux.1 Kontext"
    FLUX_2_D = "Flux.2 D"
    FLUX_2_KLEIN_9B = "Flux.2 Klein 9B"
    FLUX_2_KLEIN_9B_BASE = "Flux.2 Klein 9B-base"
    FLUX_2_KLEIN_4B = "Flux.2 Klein 4B"
    FLUX_2_KLEIN_4B_BASE = "Flux.2 Klein 4B-base"
    # Pony / Illustrious / Anime
    PONY = "Pony"
    PONY_V7 = "Pony V7"
    ILLUSTRIOUS = "Illustrious"
    NOOBAI = "NoobAI"
    ANIMA = "Anima"
    # Z-Image
    ZIMAGE_BASE = "ZImageBase"
    # Other image models
    AURAFLOW = "AuraFlow"
    CHROMA = "Chroma"
    HIDREAM = "HiDream"
    HUNYUAN_1 = "Hunyuan 1"
    KOLORS = "Kolors"
    PIXART_A = "PixArt a"
    PIXART_E = "PixArt E"
    LUMINA = "Lumina"
    # Video models
    COGVIDEOX = "CogVideoX"
    HUNYUAN_VIDEO = "Hunyuan Video"
    LTXV = "LTXV"
    LTXV2 = "LTXV2"
    LTXV_23 = "LTXV 2.3"
    MOCHI = "Mochi"
    WAN_VIDEO_13B_T2V = "Wan Video 1.3B t2v"
    WAN_VIDEO_14B_T2V = "Wan Video 14B t2v"
    WAN_VIDEO_25_I2V = "Wan Video 2.5 I2V"
    WAN_VIDEO_25_T2V = "Wan Video 2.5 T2V"


class ModelSort(str, Enum):
    HIGHEST_RATED = "Highest Rated"
    MOST_DOWNLOADED = "Most Downloaded"
    NEWEST = "Newest"


class ImageSort(str, Enum):
    """All verified working via API 2026-03-24."""

    MOST_REACTIONS = "Most Reactions"
    MOST_COMMENTS = "Most Comments"
    MOST_COLLECTED = "Most Collected"
    NEWEST = "Newest"
    OLDEST = "Oldest"


class Period(str, Enum):
    ALL_TIME = "AllTime"
    YEAR = "Year"
    MONTH = "Month"
    WEEK = "Week"
    DAY = "Day"


class NsfwLevel(str, Enum):
    NONE = "None"
    SOFT = "Soft"
    MATURE = "Mature"
    X = "X"


class CommercialUse(str, Enum):
    NONE = "None"
    IMAGE = "Image"
    RENT = "Rent"
    RENT_CIVIT = "RentCivit"
    SELL = "Sell"


# ComfyUI model type -> subfolder mapping
COMFYUI_FOLDER_MAP: dict[str, str] = {
    "Checkpoint": "checkpoints",
    "LORA": "loras",
    "LoCon": "loras",
    "TextualInversion": "embeddings",
    "Hypernetwork": "hypernetworks",
    "Controlnet": "controlnet",
    "VAE": "vae",
    "Upscaler": "upscale_models",
    "Poses": "poses",
    "AestheticGradient": "aesthetic_gradients",
    "MotionModule": "animatediff_motion_lora",
    "Wildcards": "wildcards",
}
