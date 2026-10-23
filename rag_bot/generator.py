"""Модуль 3. Генерация ответа языковой моделью по найденным фрагментам.

Работает с любым OpenAI-совместимым API. Если LLM_API_KEY не задан,
бот не падает, а возвращает найденные фрагменты как есть (режим без LLM).
"""

from openai import OpenAI

from rag_bot.retriever import SearchResult

SYSTEM_PROMPT = (
    "Ты — помощник, который отвечает на вопросы пользователей строго по предоставленному контексту. "
    "Отвечай на русском языке, кратко и по делу. "
    "Если в контексте нет ответа, честно скажи, что не нашёл информации в базе знаний. "
    "В конце укажи источники в формате [имя файла]."
)


def build_context(results: list[SearchResult]) -> str:
    return "\n\n---\n\n".join(f"[{r.chunk.source}]\n{r.chunk.text}" for r in results)


class Generator:
    def __init__(self, api_key: str, base_url: str | None, model: str, temperature: float):
        self.model = model
        self.temperature = temperature
        self.client = OpenAI(api_key=api_key, base_url=base_url) if api_key else None

    def answer(self, question: str, results: list[SearchResult]) -> str:
        if not results:
            return "В базе знаний не нашлось ничего похожего на ваш вопрос. Попробуйте переформулировать."

        if self.client is None:
            return self._fallback_answer(results)

        response = self.client.chat.completions.create(
            model=self.model,
            temperature=self.temperature,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": f"Контекст:\n{build_context(results)}\n\nВопрос: {question}"},
            ],
        )
        return response.choices[0].message.content.strip()

    @staticmethod
    def _fallback_answer(results: list[SearchResult]) -> str:
        parts = ["LLM не подключена (нет LLM_API_KEY), поэтому привожу найденные фрагменты:"]
        for r in results:
            parts.append(f"• [{r.chunk.source}] (релевантность {r.score:.2f})\n{r.chunk.text}")
        return "\n\n".join(parts)
