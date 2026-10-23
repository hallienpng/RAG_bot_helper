import argparse
import sys
from pathlib import Path


def _split_into_chunks(text, chunk_size, chunk_overlap):
    chunks = []
    start = 0
    length = len(text)

    while start < length:
        end = min(start + chunk_size, length)

        if end < length:
            boundary = text.rfind(" ", start, end)
            if boundary > start:
                end = boundary

        chunk = text[start:end].strip()
        if chunk:
            chunks.append(chunk)

        if end >= length:
            break

        next_start = end - chunk_overlap
        if next_start <= start:
            next_start = end
        start = next_start

    return chunks


def load_and_chunk(folder_path, chunk_size=1000, chunk_overlap=200):
    root = Path(folder_path)

    if not root.exists():
        raise FileNotFoundError(f"Папка не найдена: {root}")
    if not root.is_dir():
        raise NotADirectoryError(f"Путь не является папкой: {root}")

    if not isinstance(chunk_size, int) or not isinstance(chunk_overlap, int):
        raise TypeError("chunk_size и chunk_overlap должны быть целыми числами")
    if not 0 <= chunk_overlap < chunk_size:
        raise ValueError(
            "Некорректное перекрытие: требуется 0 <= chunk_overlap < chunk_size, "
            f"получено chunk_size={chunk_size}, chunk_overlap={chunk_overlap}"
        )

    chunks = []
    for path in sorted(root.rglob("*")):
        if not path.is_file():
            continue
        if path.suffix.lower() not in (".txt", ".md"):
            continue

        source = path.relative_to(root).as_posix()
        text = path.read_text(encoding="utf-8-sig")
        if not text.strip():
            continue

        for index, chunk_text in enumerate(
            _split_into_chunks(text, chunk_size, chunk_overlap)
        ):
            chunks.append(
                {
                    "text": chunk_text,
                    "source": source,
                    "chunk_index": index,
                }
            )

    return chunks


def main(argv=None):
    parser = argparse.ArgumentParser(
        description="Загрузка текстовых документов и разбиение на фрагменты"
    )
    parser.add_argument("folder_path", help="Путь к папке с документами .txt и .md")
    parser.add_argument("--chunk-size", type=int, default=1000)
    parser.add_argument("--chunk-overlap", type=int, default=200)
    args = parser.parse_args(argv)

    try:
        chunks = load_and_chunk(
            args.folder_path, args.chunk_size, args.chunk_overlap
        )
    except (FileNotFoundError, NotADirectoryError, ValueError, TypeError) as error:
        print(f"Ошибка: {error}", file=sys.stderr)
        return 1

    documents = sorted({chunk["source"] for chunk in chunks})
    print(f"Документов: {len(documents)}")
    print(f"Фрагментов: {len(chunks)}")

    if chunks:
        example = chunks[0]
        print("Пример фрагмента:")
        print(f"  source: {example['source']}")
        print(f"  chunk_index: {example['chunk_index']}")
        example_text = example["text"][:200]
        safe_text = example_text.encode(
            sys.stdout.encoding or "utf-8", errors="replace"
        ).decode(sys.stdout.encoding or "utf-8")
        print(f"  text: {safe_text}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
