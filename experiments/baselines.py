"""Baselines and comparison methods: Jaccard overlap, majority intent, k-NN intent.

Owner: Vinh. Contract: INTERFACE.md section 7.6.
"""
from __future__ import annotations

import sys
from pathlib import Path
from typing import Any

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

Document = dict[str, Any]
Ranked = list[tuple[Document, float]]


class JaccardRetriever:
    """Same ``rank``/``search`` contract as ``starter.retrieval.Retriever``."""

    def __init__(self, documents: list[Document], threshold: float = 0.0) -> None:
        self.documents = documents
        self.threshold = threshold
        raise NotImplementedError("Implement JaccardRetriever.__init__")

    def rank(self, query: str) -> Ranked:
        """All documents scored by |Q & D| / |Q | D| over token sets, highest first."""
        raise NotImplementedError("Implement JaccardRetriever.rank()")

    def search(self, query: str, top_k: int = 3) -> Ranked:
        """Same abstain rules as ``Retriever.search``."""
        raise NotImplementedError("Implement JaccardRetriever.search()")


def majority_intent(documents: list[Document]) -> str:
    """Most frequent intent; ties go to the earliest intent in ``INTENTS``."""
    raise NotImplementedError("Implement majority_intent()")


def knn_intent(ranked: Ranked, k: int, exclude_id: str | None = None) -> tuple[str, float]:
    """k-NN intent vote over the top-``k`` of ``ranked`` (skipping ``exclude_id``).

    Score-weighted vote; confidence = winning score / total score of the k docs.
    ``k=1`` is the ``top1_doc`` fallback used by ``student_core``.
    """
    raise NotImplementedError("Implement knn_intent()")
