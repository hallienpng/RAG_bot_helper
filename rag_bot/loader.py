"""Модуль 1. Загрузка документов базы знаний и разбиение их на фрагменты (чанки)."""

from dataclasses import dataclass
from pathlib import Path

from pypdf import PdfReader

SUPPORTED_EXTENSIONS = {".txt", ".md", ".pdf"}


@dataclass
class Chunk:
    text: str
    source: str  # имя файла, из которого взят фрагмент


def read_file(path: Path) -> str:
    if path.suffix.lower() == ".pdf":
        reader = PdfReader(path)
        return "\n\n".join(page.extract_text() or "" for page in reader.pages)
    return path.read_text(encoding="utf-8")


def split_text(text: str, chunk_size: int, overlap: int) -> list[str]:
    """Собирает абзацы в чанки не длиннее chunk_size символов.

    Слишком длинные абзацы режутся скользящим окном с перекрытием overlap,
    чтобы мысль на границе двух чанков не терялась.
    """
    paragraphs = [p.strip() for p in text.split("\n\n") if p.strip()]
    chunks: list[str] = []
    current = ""

    for paragraph in paragraphs:
        if len(paragraph) > chunk_size:
            if current:
                chunks.append(current)
                current = ""
            step = max(chunk_size - overlap, 1)
            for start in range(0, len(paragraph), step):
                chunks.append(paragraph[start : start + chunk_size])
            continue

        # Заголовок markdown начинает новый чанк, чтобы не отрываться от своего раздела
        if paragraph.startswith("#") and current:
            chunks.append(current)
            current = paragraph
        elif len(current) + len(paragraph) + 2 <= chunk_size:
            current = f"{current}\n\n{paragraph}" if current else paragraph
        else:
            chunks.append(current)
            current = paragraph

    if current:
        chunks.append(current)
    return chunks


def load_chunks(knowledge_dir: Path, chunk_size: int, overlap: int) -> list[Chunk]:
    if not knowledge_dir.exists():
        raise FileNotFoundError(f"Папка с базой знаний не найдена: {knowledge_dir}")

    chunks: list[Chunk] = []
    for path in sorted(knowledge_dir.rglob("*")):
        if path.suffix.lower() not in SUPPORTED_EXTENSIONS:
            continue
        source = str(path.relative_to(knowledge_dir))
        for piece in split_text(read_file(path), chunk_size, overlap):
            chunks.append(Chunk(text=piece, source=source))
    return chunks
