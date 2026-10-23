# RAG_bot_helper

Чат-бот (Telegram + консоль), который отвечает на вопросы по базе документов с помощью RAG (Retrieval-Augmented Generation): находит подходящие фрагменты документов и передаёт их языковой модели, чтобы она сформулировала ответ со ссылкой на источник.

## Быстрый старт

```bash
git clone https://github.com/hallienpng/RAG_bot_helper.git .
python3 -m venv venv
source venv/bin/activate          # Windows: venv\Scripts\activate
pip3 install -r requirements.txt
cp .env.example .env              # заполнить ключи (можно оставить пустыми для проверки)

python cli.py                     # консольный чат
python bot.py                     # Telegram-бот (нужен TELEGRAM_BOT_TOKEN от @BotFather)
python -m pytest -q               # тесты
```

Без `LLM_API_KEY` бот работает в упрощённом режиме: вместо сгенерированного ответа показывает найденные фрагменты. Это удобно для проверки поиска. Подойдёт любой OpenAI-совместимый API: OpenAI, локальная Ollama, OpenRouter (примеры в `.env.example`).

## Как это устроено

```
вопрос ─► retriever: поиск top-k фрагментов ─► generator: LLM формулирует ответ ─► пользователю
              ▲
knowledge_base/*.md|txt|pdf ─► loader: разбиение на чанки
```

| Файл | Модуль | Что делает |
|---|---|---|
| `rag_bot/loader.py` | 1. Загрузка | Читает .txt/.md/.pdf, режет на чанки по заголовкам и абзацам |
| `rag_bot/retriever.py` | 2. Поиск | TF-IDF по символьным n-граммам + косинусное сходство |
| `rag_bot/generator.py` | 3. Генерация | Промпт + запрос к LLM, режим без LLM |
| `bot.py`, `cli.py` | 4. Интерфейс | Telegram-бот (aiogram 3) и консольный чат |
| `rag_bot/pipeline.py` | — | Связывает модули 1–3 |
| `rag_bot/config.py` | — | Настройки из `.env` |

## Предлагаемое распределение ролей (4 участника)

Каждый развивает свой модуль, не меняя его публичный интерфейс (`load_chunks`, `search`, `answer`, `RAGPipeline.ask`), чтобы не ломать чужие части.

1. **Данные и загрузка.** Наполнить `knowledge_base/` реальными документами по теме бота, добавить форматы (.docx, .html), улучшить разбиение на чанки.
2. **Поиск.** Заменить TF-IDF на эмбеддинги (sentence-transformers) и векторную БД (Chroma/FAISS), сравнить качество на наборе тестовых вопросов.
3. **LLM и промпты.** Подобрать модель (Ollama/OpenAI/GigaChat), доработать промпт, добавить историю диалога.
4. **Интерфейс и инфраструктура.** Telegram-бот: кнопки, обратная связь (👍/👎), логирование; Docker, деплой.

## Работа в команде

- Перед началом работы: `git pull`.
- Новую библиотеку ставим через `pip install ...`, затем обновляем `pip freeze > requirements.txt`. При конфликте в `requirements.txt` оставляем строки обеих сторон и для каждого пакета одну (более новую) версию.
- Секреты храним только в `.env` (он в `.gitignore`), в git идёт `.env.example`.

## Инструменты для ИИ-агента

- **Skill** `.claude/skills/knowledge-base/SKILL.md`: как добавить документ в базу знаний и проверить, что бот по нему отвечает. В Claude Code вызывается командой `/knowledge-base` или автоматически.
- **MCP-сервер** `.mcp.json` → [Context7](https://context7.com): актуальная документация библиотек (aiogram, openai, scikit-learn) прямо в агенте. При первом открытии проекта Claude Code попросит разрешить сервер, статус можно посмотреть командой `/mcp`.
