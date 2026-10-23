from pathlib import Path

from rag_bot.config import Settings
from rag_bot.loader import load_chunks, split_text
from rag_bot.pipeline import RAGPipeline


def test_split_text_respects_chunk_size():
    text = "\n\n".join(["абзац " * 20] * 10 + ["x" * 2000])
    chunks = split_text(text, chunk_size=300, overlap=50)
    assert chunks
    assert all(len(c) <= 300 for c in chunks)


def test_load_chunks_reads_supported_files(tmp_path: Path):
    (tmp_path / "a.md").write_text("Первый документ.", encoding="utf-8")
    (tmp_path / "b.txt").write_text("Второй документ.", encoding="utf-8")
    (tmp_path / "image.png").write_bytes(b"\x89PNG")
    chunks = load_chunks(tmp_path, chunk_size=500, overlap=50)
    assert sorted(c.source for c in chunks) == ["a.md", "b.txt"]


def test_pipeline_finds_relevant_fragment_without_llm(tmp_path: Path):
    (tmp_path / "cats.md").write_text("Кошки любят спать на подоконнике и ловить мышей.", encoding="utf-8")
    (tmp_path / "python.md").write_text("Python — язык программирования с динамической типизацией.", encoding="utf-8")
    pipeline = RAGPipeline(Settings(knowledge_dir=tmp_path, llm_api_key="", top_k=1))

    answer = pipeline.ask("Где спят кошки?")

    assert "cats.md" in answer
    assert "python.md" not in answer
