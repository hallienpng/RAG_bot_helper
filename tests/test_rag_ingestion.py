import tempfile
import unittest
from pathlib import Path

from rag_ingestion import load_and_chunk


class TestRagIngestionLongWord(unittest.TestCase):
    def test_long_word_without_spaces_exceeds_chunk_size(self):
        with tempfile.TemporaryDirectory() as tmp:
            doc = Path(tmp) / "doc.txt"
            doc.write_text("x" * 2500, encoding="utf-8")

            chunks = load_and_chunk(tmp, chunk_size=1000, chunk_overlap=100)

            self.assertEqual(len(chunks), 3)
            self.assertTrue(all(len(c["text"]) <= 1000 for c in chunks))
            self.assertEqual([c["chunk_index"] for c in chunks], [0, 1, 2])
            self.assertEqual([c["source"] for c in chunks], ["doc.txt"] * 3)
            # Соседние чанки пересекаются на chunk_overlap символов.
            self.assertEqual(chunks[0]["text"][-100:], chunks[1]["text"][:100])
            self.assertEqual(chunks[1]["text"][-100:], chunks[2]["text"][:100])


if __name__ == "__main__":
    unittest.main()
