"""Настройки проекта. Значения берутся из переменных окружения / файла .env."""

import os
from dataclasses import dataclass
from pathlib import Path

from dotenv import load_dotenv

PROJECT_ROOT = Path(__file__).resolve().parent.parent
load_dotenv(PROJECT_ROOT / ".env")


@dataclass(frozen=True)
class Settings:
    # База знаний
    knowledge_dir: Path = PROJECT_ROOT / os.getenv("KNOWLEDGE_DIR", "knowledge_base")
    chunk_size: int = int(os.getenv("CHUNK_SIZE", "800"))
    chunk_overlap: int = int(os.getenv("CHUNK_OVERLAP", "150"))
    top_k: int = int(os.getenv("TOP_K", "4"))
    min_score: float = float(os.getenv("MIN_SCORE", "0.05"))

    # LLM (любой OpenAI-совместимый API: OpenAI, Ollama, OpenRouter, ...)
    llm_api_key: str = os.getenv("LLM_API_KEY", "")
    llm_base_url: str | None = os.getenv("LLM_BASE_URL") or None
    llm_model: str = os.getenv("LLM_MODEL", "gpt-4o-mini")
    llm_temperature: float = float(os.getenv("LLM_TEMPERATURE", "0.2"))

    # Telegram
    telegram_token: str = os.getenv("TELEGRAM_BOT_TOKEN", "")


settings = Settings()
