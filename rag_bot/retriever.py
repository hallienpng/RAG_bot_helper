"""Модуль 2. Индексация чанков и поиск самых релевантных фрагментов под вопрос.

Сейчас используется TF-IDF по символьным n-граммам: работает без GPU и внешних API
и неплохо справляется с русской морфологией. Позже можно заменить на эмбеддинги
(sentence-transformers / OpenAI embeddings) и векторную БД (Chroma, FAISS),
сохранив интерфейс метода search().
"""

from dataclasses import dataclass

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from rag_bot.loader import Chunk


@dataclass
class SearchResult:
    chunk: Chunk
    score: float


class TfidfRetriever:
    def __init__(self, chunks: list[Chunk]):
        if not chunks:
            raise ValueError("База знаний пуста: добавьте файлы .txt/.md/.pdf в папку knowledge_base")
        self.chunks = chunks
        self.vectorizer = TfidfVectorizer(analyzer="char_wb", ngram_range=(2, 5), lowercase=True)
        self.matrix = self.vectorizer.fit_transform(c.text for c in chunks)

    def search(self, query: str, top_k: int, min_score: float = 0.0) -> list[SearchResult]:
        query_vec = self.vectorizer.transform([query])
        scores = cosine_similarity(query_vec, self.matrix)[0]
        best = scores.argsort()[::-1][:top_k]
        return [
            SearchResult(chunk=self.chunks[i], score=float(scores[i]))
            for i in best
            if scores[i] >= min_score
        ]
