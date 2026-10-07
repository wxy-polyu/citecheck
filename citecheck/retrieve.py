"""BM25, embedding search, and reciprocal rank fusion."""

from __future__ import annotations

import os
import re
from dataclasses import dataclass, field

from dotenv import load_dotenv

from citecheck.ingest import Chunk
from citecheck.llm import ROOT

TOKEN = re.compile(r"[a-z0-9]+")
RRF_K = 60
DEFAULT_EMBEDDING_MODEL = "all-MiniLM-L6-v2"
_MODEL_CACHE: dict[str, object] = {}


def embedding_model_name() -> str:
    load_dotenv(ROOT / ".env")
    return os.getenv("EMBEDDING_MODEL", DEFAULT_EMBEDDING_MODEL).strip() or DEFAULT_EMBEDDING_MODEL


def tokenize(text: str) -> list[str]:
    return TOKEN.findall(text.lower())


@dataclass
class BM25Index:
    chunks: list[Chunk]
    _index: object = field(init=False)

    def __post_init__(self) -> None:
        from rank_bm25 import BM25Okapi

        corpus = [tokenize(chunk.text) or ["empty"] for chunk in self.chunks]
        self._index = BM25Okapi(corpus) if corpus else None

    def search(self, query: str, k: int) -> list[tuple[Chunk, float]]:
        if not self.chunks or self._index is None:
            return []
        scores = list(self._index.get_scores(tokenize(query)))
        order = sorted(range(len(scores)), key=scores.__getitem__, reverse=True)
        return [(self.chunks[index], float(scores[index])) for index in order[:k]]


@dataclass
class EmbeddingIndex:
    chunks: list[Chunk]
    model_name: str = DEFAULT_EMBEDDING_MODEL
    _matrix: object = field(init=False, default=None)
    _model: object = field(init=False, default=None)

    def __post_init__(self) -> None:
        if not self.chunks:
            return
        self._model = _embedding_model(self.model_name)
        self._matrix = self._model.encode(
            [chunk.text for chunk in self.chunks],
            normalize_embeddings=True,
        )

    def search(self, query: str, k: int) -> list[tuple[Chunk, float]]:
        if not self.chunks or self._matrix is None:
            return []
        import numpy as np

        query_vector = self._model.encode([query], normalize_embeddings=True)[0]
        scores = np.asarray(self._matrix) @ np.asarray(query_vector)
        order = np.argsort(-scores)[:k]
        return [(self.chunks[int(index)], float(scores[int(index)])) for index in order]


def reciprocal_rank_fusion(
    rankings: list[list[Chunk]],
    *,
    k: int = RRF_K,
    top_n: int = 5,
) -> list[Chunk]:
    """Merge rankings by reciprocal rank. Scores are not shown to the verifier."""
    scores: dict[str, float] = {}
    chunks: dict[str, Chunk] = {}
    for ranking in rankings:
        for rank, chunk in enumerate(ranking, start=1):
            chunks[chunk.chunk_id] = chunk
            scores[chunk.chunk_id] = scores.get(chunk.chunk_id, 0.0) + 1.0 / (k + rank)
    ordered = sorted(scores, key=scores.__getitem__, reverse=True)
    return [chunks[chunk_id] for chunk_id in ordered[:top_n]]


class Retriever:
    """Search chunks with BM25, embeddings, or both."""

    def __init__(
        self,
        chunks: list[Chunk],
        *,
        mode: str = "hybrid",
        embedding_model: str | None = None,
    ) -> None:
        if mode not in {"hybrid", "bm25", "embedding"}:
            raise ValueError(f"Unknown retriever mode: {mode}")
        self.chunks = chunks
        self.mode = mode
        self.bm25 = BM25Index(chunks) if mode in {"hybrid", "bm25"} else None
        self.embed = (
            EmbeddingIndex(chunks, embedding_model or embedding_model_name())
            if mode in {"hybrid", "embedding"}
            else None
        )

    def search(self, query: str, k: int = 5, mode: str | None = None) -> list[Chunk]:
        mode = mode or self.mode
        if not self.chunks:
            return []
        pool = max(k * 4, 20)
        if mode == "bm25":
            if self.bm25 is None:
                raise ValueError("BM25 index was not built.")
            return [chunk for chunk, _score in self.bm25.search(query, k)]
        if mode == "embedding":
            if self.embed is None:
                raise ValueError("Embedding index was not built.")
            return [chunk for chunk, _score in self.embed.search(query, k)]
        if self.bm25 is None or self.embed is None:
            raise ValueError("Hybrid search needs both indexes.")
        bm25_hits = [chunk for chunk, _score in self.bm25.search(query, pool)]
        embed_hits = [chunk for chunk, _score in self.embed.search(query, pool)]
        return reciprocal_rank_fusion([bm25_hits, embed_hits], top_n=k)


def _embedding_model(name: str) -> object:
    if name not in _MODEL_CACHE:
        from sentence_transformers import SentenceTransformer

        _MODEL_CACHE[name] = SentenceTransformer(name)
    return _MODEL_CACHE[name]
