"""Связка модулей: загрузка → поиск → генерация. Этим классом пользуются все интерфейсы."""

from rag_bot.config import Settings, settings as default_settings
from rag_bot.generator import Generator
from rag_bot.loader import load_chunks
from rag_bot.retriever import TfidfRetriever


class RAGPipeline:
    def __init__(self, settings: Settings = default_settings):
        self.settings = settings
        self.generator = Generator(
            api_key=settings.llm_api_key,
            base_url=settings.llm_base_url,
            model=settings.llm_model,
            temperature=settings.llm_temperature,
        )
        self.reload()

    def reload(self) -> int:
        """Перечитывает базу знаний. Возвращает количество проиндексированных чанков. """
        chunks = load_chunks(self.settings.knowledge_dir, self.settings.chunk_size, self.settings.chunk_overlap)
        self.retriever = TfidfRetriever(chunks)
        return len(chunks)

    def ask(self, question: str) -> str:
        results = self.retriever.search(question, self.settings.top_k, self.settings.min_score)
        return self.generator.answer(question, results)
