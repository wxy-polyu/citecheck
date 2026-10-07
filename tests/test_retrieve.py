"""BM25 and rank fusion. These tests do not download an embedding model."""

import unittest

from citecheck.ingest import Chunk
from citecheck.retrieve import Retriever, reciprocal_rank_fusion


def chunk(chunk_id: str, text: str) -> Chunk:
    return Chunk(chunk_id, "paper", "Paper", "Method", 1, 0, text)


class RetrieveTest(unittest.TestCase):
    def test_bm25_finds_the_exact_term(self) -> None:
        chunks = [
            chunk("a", "The introduction discusses earlier widget counters."),
            chunk("b", "On Widget-100, WidgetNet reaches 91 percent accuracy."),
            chunk("c", "Training uses the Widget-100 dataset for 12 epochs."),
        ]
        hits = Retriever(chunks, mode="bm25").search("91 percent accuracy", k=1)
        self.assertEqual(hits[0].chunk_id, "b")

    def test_reciprocal_rank_fusion_prefers_a_chunk_in_both_lists(self) -> None:
        first = chunk("a", "a")
        second = chunk("b", "b")
        third = chunk("c", "c")
        fused = reciprocal_rank_fusion([[first, second], [second, third]], top_n=3)
        self.assertEqual(fused[0].chunk_id, "b")


if __name__ == "__main__":
    unittest.main()
