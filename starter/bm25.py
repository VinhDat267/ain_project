"""BM25 ranking, implemented from first principles, used only as a comparison (E7).

Owner: Vinh (V13). Contract: INTERFACE.md section 5.5.
The product keeps TF-IDF + cosine (the brief asks for a cosine threshold);
BM25 scores are not bounded to [0, 1], so it is compared on ranking metrics only.
"""
from __future__ import annotations

from typing import Any, Literal

Document = dict[str, Any]
Ranked = list[tuple[Document, float]]


class BM25Retriever:
    """Okapi BM25 over the FAQ/notice corpus, with the same rank/search contract as Retriever."""

    def __init__(
        self,
        documents: list[Document],
        k1: float = 1.5,
        b: float = 0.75,
        index_field: Literal["question", "text"] = "text",
        threshold: float = 0.0,
    ) -> None:
        self.documents = documents
        self.k1 = k1
        self.b = b
        self.index_field = index_field
        self.threshold = threshold
        raise NotImplementedError("Build the BM25 index in BM25Retriever.__init__")

    def rank(self, query: str) -> Ranked:
        """All documents with their BM25 score, highest first; ties broken by ``id`` ascending."""
        raise NotImplementedError("Implement BM25Retriever.rank()")

    def search(self, query: str, top_k: int = 3) -> Ranked:
        """``rank(query)[:top_k]``, or ``[]`` when ``top_k <= 0``, the top score is 0, or below ``threshold``."""
        raise NotImplementedError("Implement BM25Retriever.search()")
