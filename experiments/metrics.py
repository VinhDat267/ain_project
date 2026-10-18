"""Ranking metrics for a single query with exactly one relevant document.

Owner: Vinh (V07). Definitions: INTERFACE.md section 7.2.
"""
from __future__ import annotations

from collections.abc import Sequence


def _check_k(k: int) -> None:
    if k <= 0:
        raise ValueError(f"k must be positive, got {k}")


def reciprocal_rank(ranked_ids: Sequence[str], expected_id: str, k: int = 10) -> float:
    """``1 / rank`` of ``expected_id`` within the first ``k`` ids, else 0."""
    _check_k(k)
    for position, doc_id in enumerate(ranked_ids[:k], start=1):
        if doc_id == expected_id:
            return 1.0 / position
    return 0.0


def hit_at_k(ranked_ids: Sequence[str], expected_id: str, k: int) -> int:
    """1 if ``expected_id`` is among the first ``k`` ids, else 0."""
    _check_k(k)
    return int(expected_id in ranked_ids[:k])


def precision_at_k(ranked_ids: Sequence[str], expected_id: str, k: int) -> float:
    """Relevant ids in the first ``k`` divided by ``k`` (at most 1/k here)."""
    return hit_at_k(ranked_ids, expected_id, k) / k
