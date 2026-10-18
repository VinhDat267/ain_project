"""BM25 ranking, implemented from first principles, used only as a comparison (E7).

Owner: Vinh (V13). Contract: INTERFACE.md section 5.5.
The product keeps TF-IDF + cosine (the brief asks for a cosine threshold);
BM25 scores are not bounded to [0, 1], so it is compared on ranking metrics only.
"""
from __future__ import annotations

import math
from collections import Counter
from typing import Any, Literal

from .preprocess import tokenize

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
        self.documents = list(documents)
        self.k1 = k1
        self.b = b
        self.index_field = index_field
        self.threshold = threshold

        doc_tokens = [tokenize(doc[index_field], remove_stopwords=True) for doc in self.documents]
        self._term_freqs = [Counter(tokens) for tokens in doc_tokens]
        self._doc_lengths = [len(tokens) for tokens in doc_tokens]
        n_docs = len(self.documents)
        self._avg_length = sum(self._doc_lengths) / n_docs if n_docs else 0.0

        doc_freq = Counter(term for term_freq in self._term_freqs for term in term_freq)
        self._idf = {
            term: math.log((n_docs - df + 0.5) / (df + 0.5) + 1.0)
            for term, df in doc_freq.items()
        }

    def score(self, query: str) -> list[float]:
        """BM25 score of every document for ``query``, in document order."""
        terms = sorted(set(tokenize(query if isinstance(query, str) else "", remove_stopwords=True)))
        scores = []
        for term_freq, length in zip(self._term_freqs, self._doc_lengths):
            length_ratio = length / self._avg_length if self._avg_length else 1.0
            saturation = self.k1 * (1.0 - self.b + self.b * length_ratio)
            total = 0.0
            for term in terms:
                f = term_freq.get(term, 0)
                if f:
                    total += self._idf[term] * f * (self.k1 + 1.0) / (f + saturation)
            scores.append(total)
        return scores

    def rank(self, query: str) -> Ranked:
        """All documents with their BM25 score, highest first; ties broken by ``id`` ascending."""
        results = list(zip(self.documents, self.score(query)))
        results.sort(key=lambda item: (-item[1], item[0]["id"]))
        return results

    def search(self, query: str, top_k: int = 3) -> Ranked:
        """``rank(query)[:top_k]``, or ``[]`` when ``top_k <= 0``, the top score is 0, or below ``threshold``."""
        if top_k <= 0:
            return []
        ranked = self.rank(query)
        if not ranked or ranked[0][1] <= 0.0 or ranked[0][1] < self.threshold:
            return []
        return ranked[:top_k]
