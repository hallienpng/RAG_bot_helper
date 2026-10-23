"""Модуль 4b. Telegram-бот на aiogram 3.

Запуск: python bot.py (нужен TELEGRAM_BOT_TOKEN в .env, токен выдаёт @BotFather)
"""

import asyncio
import logging

from aiogram import Bot, Dispatcher, F
from aiogram.filters import Command, CommandStart
from aiogram.types import Message

from rag_bot.config import settings
from rag_bot.pipeline import RAGPipeline

TELEGRAM_MESSAGE_LIMIT = 4096

dp = Dispatcher()
pipeline: RAGPipeline | None = None


@dp.message(CommandStart())
async def start(message: Message) -> None:
    await message.answer(
        "Привет! Я отвечаю на вопросы по базе знаний.\n"
        "Просто напишите вопрос. Команды: /help, /reload."
    )


@dp.message(Command("help"))
async def help_command(message: Message) -> None:
    await message.answer(
        "Я ищу ответ в документах базы знаний и формулирую его с помощью языковой модели.\n"
        "/reload — перечитать документы после их обновления."
    )


@dp.message(Command("reload"))
async def reload_command(message: Message) -> None:
    count = await asyncio.to_thread(pipeline.reload)
    await message.answer(f"База знаний перечитана, фрагментов: {count}")


@dp.message(F.text)
async def handle_question(message: Message) -> None:
    await message.bot.send_chat_action(message.chat.id, "typing")
    try:
        answer = await asyncio.to_thread(pipeline.ask, message.text)
    except Exception:
        logging.exception("Ошибка при ответе на вопрос")
        answer = "Не получилось ответить: произошла ошибка. Попробуйте позже."
    for start in range(0, len(answer), TELEGRAM_MESSAGE_LIMIT):
        await message.answer(answer[start : start + TELEGRAM_MESSAGE_LIMIT])


async def main() -> None:
    global pipeline
    if not settings.telegram_token:
        raise SystemExit("Не задан TELEGRAM_BOT_TOKEN. Скопируйте .env.example в .env и заполните его.")
    logging.basicConfig(level=logging.INFO)
    pipeline = RAGPipeline()
    logging.info("База знаний загружена: %d фрагментов", len(pipeline.retriever.chunks))
    await dp.start_polling(Bot(token=settings.telegram_token))


if __name__ == "__main__":
    asyncio.run(main())
