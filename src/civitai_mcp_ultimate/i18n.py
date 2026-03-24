"""Bilingual strings (EN/RU) for tool output formatting."""

import os

LANG = os.getenv("CIVITAI_MCP_LANG", "en").lower()


def t(en: str, ru: str) -> str:
    """Return localized string based on CIVITAI_MCP_LANG env var."""
    return ru if LANG == "ru" else en


# Common labels
L_TYPE = t("Type", "Тип")
L_CREATOR = t("Creator", "Автор")
L_RATING = t("Rating", "Рейтинг")
L_DOWNLOADS = t("Downloads", "Скачивания")
L_FAVORITES = t("Favorites", "Избранное")
L_TAGS = t("Tags", "Теги")
L_BASE_MODEL = t("Base Model", "Базовая модель")
L_TRIGGER_WORDS = t("Trigger Words", "Триггер-слова")
L_FILES = t("Files", "Файлы")
L_DOWNLOAD = t("Download", "Скачать")
L_VERSION = t("Version", "Версия")
L_CREATED = t("Created", "Создано")
L_COMMENTS = t("Comments", "Комментарии")
L_REACTIONS = t("Reactions", "Реакции")
L_PROMPT = t("Prompt", "Промпт")
L_NEGATIVE_PROMPT = t("Negative Prompt", "Негативный промпт")
L_NO_RESULTS = t("No results found", "Ничего не найдено")
L_MODEL_NOT_FOUND = t("Model not found", "Модель не найдена")
L_GENERATION_PARAMS = t("Generation Parameters", "Параметры генерации")
