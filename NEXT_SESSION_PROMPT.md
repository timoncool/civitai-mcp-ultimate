# Copy-paste this as the first message in the next Claude Code session:

---

Продолжаем работу над civitai-mcp-ultimate. Прочитай HANDOFF.md в D:/Projects/TEMP/civitai-mcp-ultimate/HANDOFF.md — там полное описание проекта: архитектура, 14 тулов, 7 раундов code review, что сделано, что нет.

Задачи на эту сессию:

1. **Протестировать MCP тулы вживую** — MCP уже подключён к Claude Code:
   - `claude mcp add civitai -e CIVITAI_API_KEY=00e54501ce1a4f64800996934dddd1c2 -- python -m civitai_mcp_ultimate.server`
   - После рестарта тулы доступны как `mcp__civitai__*`
   - Проверить: search_models, get_top_loras (Flux.1 D), get_top_images (Most Reactions, Week), get_model_images, get_download_info
   - Проверить NSFW доступ

2. **Написать SKILL.md** — инструкция для агента как виртуозно использовать все 14 тулов:
   - Workflow: как искать модели → смотреть картинки → брать промпты → скачивать
   - Примеры реальных сценариев (найти лору для стиля, prompt mining, скачать в ComfyUI)
   - Чит-шит enum значений
   - Референс: docs/civitai-api-reference.md

3. **Опубликовать на PyPI**:
   - `pip install hatch` если нет
   - `hatch build && hatch publish`
   - Нужен PyPI token (спросить у юзера)
   - Проверить что `uvx civitai-mcp-ultimate` работает

4. **Зарегистрировать в каталогах**:
   - Smithery (smithery.ai)
   - Glama (glama.ai)
   - mcp.run если есть

5. **Запушить финальные изменения** на GitHub (README с credits уже обновлён)

Repo: https://github.com/timoncool/civitai-mcp-ultimate
Local: D:/Projects/TEMP/civitai-mcp-ultimate/
API key: CIVITAI_API_KEY=00e54501ce1a4f64800996934dddd1c2
