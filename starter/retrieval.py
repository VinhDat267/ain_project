"""Retrieval module: TF-IDF vectors + cosine similarity over FAQ/notice documents.

Owner: Viet Anh. Contract: INTERFACE.md section 5.
Write TF-IDF and cosine yourself (Python/numpy). scikit-learn may only be
used to cross-check scores in tests or notebooks, never in this module.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Literal

Document = dict[str, Any]
Ranked = list[tuple[Document, float]]


@dataclass(frozen=True)
class RetrievalConfig:
    """Every knob the experiments are allowed to turn (INTERFACE.md 5.2)."""

    analyzer: Literal["word", "char", "hybrid"] = "word"
    index_field: Literal["question", "text"] = "text"
    word_ngram_range: tuple[int, int] = (1, 1)
    char_ngram_range: tuple[int, int] = (3, 5)
    remove_stopwords: bool = True
    sublinear_tf: bool = False
    hybrid_alpha: float = 0.5
    threshold: float = 0.0


class Retriever:
    """Index ``documents`` once in ``__init__``, then answer queries."""

    def __init__(self, documents: list[Document], config: RetrievalConfig = RetrievalConfig()) -> None:
        self.documents = documents
        self.config = config
        raise NotImplementedError("Build the TF-IDF index in Retriever.__init__")

    def rank(self, query: str) -> Ranked:
        """Return ALL documents with their raw cosine score, highest first.

        No threshold is applied. Ties are broken by ``id`` ascending.
        Scores lie in [0, 1].
        """
        raise NotImplementedError("Implement Retriever.rank()")

    def search(self, query: str, top_k: int = 3) -> Ranked:
        """Return ``rank(query)[:top_k]``, or ``[]`` to abstain.

        Abstain when ``top_k <= 0``, when the top-1 score is 0 (no known
        terms), or when the top-1 score is below ``config.threshold``.
        """
        raise NotImplementedError("Implement Retriever.search()")

    def explain(self, query: str, doc_id: str, top_n: int = 5) -> list[tuple[str, float]]:
        """Return the ``top_n`` features contributing most to the score of ``doc_id``.

        Each item is ``(feature, contribution)`` sorted descending; with
        L2-normalised vectors the contributions of all features sum to the
        cosine score. Sprint 2.
        """
        raise NotImplementedError("Implement Retriever.explain()")
