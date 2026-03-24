# Copy-paste this as the first message in the next Claude Code session:

---

Продолжаем работу над civitai-mcp-ultimate. Прочитай HANDOFF.md в D:/Projects/TEMP/civitai-mcp-ultimate/HANDOFF.md

Главная задача: **Добавить Meilisearch поиск** — REST API `/api/v1/models?query=...` сломан (возвращает нерелевантные результаты, известный баг с мая 2025). Сайт и все расширения (gallery-dl, scromfyUI_Nodes) используют Meilisearch:

```
POST https://search-new.civitai.com/multi-search
Authorization: Bearer 8c46eb2508e21db1e9828a97968d91ab1ca1caa5f70a00e88a2ba1e286603b61
Content-Type: application/json

{"queries":[{"q":"hands fix","indexUid":"models_v9","limit":5,"sort":["stats.thumbsUpCountAllTime:desc"]}]}
```

Ключ публичный (search-only), проверен — работает.

Задачи:
1. **Добавить Meilisearch search** — `search_models_smart` тул или заменить текущий search_models
   - Поддержать фильтры: type, baseModel, nsfw/browsingLevel, sort
   - Форматировать результаты в наш markdown формат
   - Индексы: `models_v9` (модели), `images_v6` (картинки)
2. **Тест MCP тулов после рестарта** — content_type, browsing_level, tag, base_model, tools, techniques, has_meta, image cache — всё добавлено в session 3, но MCP процесс не перезапускался
3. **Обновить SKILL.md, docs, README** с Meilisearch инфой
4. **PyPI 0.2.0** — текущая 0.1.0 не содержит session 3 фичи
   - `hatch build && hatch publish`
   - PyPI token: спросить у юзера или взять из memory
5. **Проверить Glama** — подали на review в session 3

Repo: https://github.com/timoncool/civitai-mcp-ultimate
Local: D:/Projects/TEMP/civitai-mcp-ultimate/
API key: CIVITAI_API_KEY=00e54501ce1a4f64800996934dddd1c2
Meilisearch key: 8c46eb2508e21db1e9828a97968d91ab1ca1caa5f70a00e88a2ba1e286603b61
