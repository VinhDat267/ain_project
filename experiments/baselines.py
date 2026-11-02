"""Baselines and comparison methods: Jaccard overlap, majority intent, k-NN intent.

Owner: Vinh (V09). Contract: INTERFACE.md section 7.6.
"""
from __future__ import annotations

import sys
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any, Optional

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from starter.intent import INTENTS  # noqa: E402
from starter.preprocess import tokenize  # noqa: E402

Document = dict[str, Any]
Ranked = list[tuple[Document, float]]


class JaccardRetriever:
    """Same ``rank``/``search`` contract as ``starter.retrieval.Retriever``."""

    def __init__(self, documents: list[Document], threshold: float = 0.0) -> None:
        self.documents = list(documents)
        self.threshold = threshold
        self._doc_tokens = [set(tokenize(doc["text"], remove_stopwords=True)) for doc in self.documents]

    def rank(self, query: str) -> Ranked:
        """All documents scored by |Q & D| / |Q | D| over token sets, highest first."""
        q_tokens = set(tokenize(query if isinstance(query, str) else "", remove_stopwords=True))
        results: Ranked = []
        for doc, d_tokens in zip(self.documents, self._doc_tokens):
            union = q_tokens | d_tokens
            score = len(q_tokens & d_tokens) / len(union) if union else 0.0
            results.append((doc, score))
        results.sort(key=lambda item: (-item[1], item[0]["id"]))
        return results

    def search(self, query: str, top_k: int = 3) -> Ranked:
        """Same abstain rules as ``Retriever.search``."""
        if top_k <= 0:
            return []
        ranked = self.rank(query)
        if not ranked or ranked[0][1] <= 0.0 or ranked[0][1] < self.threshold:
            return []
        return ranked[:top_k]


def _first_by_intent_order(candidates: set[str]) -> str:
    """Deterministic tie-break: the earliest of ``candidates`` in ``INTENTS``."""
    for intent in INTENTS:
        if intent in candidates:
            return intent
    return sorted(candidates)[0]


def majority_intent(documents: list[Document]) -> str:
    """Most frequent intent; ties go to the earliest intent in ``INTENTS``."""
    counts = Counter(doc["intent"] for doc in documents)
    if not counts:
        return INTENTS[0]
    best = max(counts.values())
    return _first_by_intent_order({intent for intent, n in counts.items() if n == best})


def knn_intent(ranked: Ranked, k: int, exclude_id: Optional[str] = None) -> tuple[str, float]:
    """k-NN intent vote over the top-``k`` of ``ranked`` (skipping ``exclude_id``).

    Score-weighted vote; confidence = winning score / total score of the k docs.
    ``k=1`` is the ``top1_doc`` fallback used by ``student_core``.
    """
    if k <= 0:
        raise ValueError(f"k must be positive, got {k}")
    neighbours = [(doc, score) for doc, score in ranked if doc["id"] != exclude_id][:k]
    votes: dict[str, float] = defaultdict(float)
    for doc, score in neighbours:
        votes[doc["intent"]] += score
    total = sum(votes.values())
    if total <= 0.0:
        return majority_intent([doc for doc, _ in ranked]), 0.0
    best = max(votes.values())
    winner = _first_by_intent_order({intent for intent, v in votes.items() if v == best})
    return winner, votes[winner] / total
