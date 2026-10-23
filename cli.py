"""Модуль 4a. Консольный чат — для быстрой отладки без Telegram.

Запуск: python cli.py
"""

from rag_bot.pipeline import RAGPipeline


def main() -> None:
    pipeline = RAGPipeline()
    print(f"База знаний загружена: {len(pipeline.retriever.chunks)} фрагментов.")
    print("Задайте вопрос (пустая строка или 'exit' — выход, '/reload' — перечитать базу).\n")

    while True:
        try:
            question = input("Вы: ").strip()
        except (EOFError, KeyboardInterrupt):
            break
        if not question or question.lower() in {"exit", "quit", "выход"}:
            break
        if question == "/reload":
            print(f"Бот: база перечитана, фрагментов: {pipeline.reload()}\n")
            continue
        print(f"Бот: {pipeline.ask(question)}\n")


if __name__ == "__main__":
    main()
